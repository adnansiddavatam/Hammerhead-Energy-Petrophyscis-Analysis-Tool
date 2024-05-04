import numpy as np
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, 
    QFileDialog, QLineEdit, QGridLayout
)
from PySide6.QtCore import Qt
from vispy import scene
from vispy.scene import LinePlot, Grid
from LasData import LasData

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.las_data = LasData()
        self.init_ui()
        self.min_depth = 0
        self.max_depth = 0

    def init_ui(self):
        main_layout = QHBoxLayout(self)  # Main layout is horizontal now
        self.layout = QVBoxLayout(self)

    # Create VisPy canvas for plotting
        self.canvas = scene.SceneCanvas(keys='interactive')
        self.view = self.canvas.central_widget.add_view()

    # Add the canvas to the layout
        self.layout.addWidget(self.canvas.native)

        # Initialize the grid and views
        self.grid = Grid(parent=self.canvas.scene)
        self.canvas.central_widget.add_widget(self.grid)

        # Create views for each plot, each in its own row
        self.grz_view = self.grid.add_view(row=0, col=0, border_color='white')
        self.pord_view = self.grid.add_view(row=0, col=1, border_color='white')
        self.zden_view = self.grid.add_view(row=0, col=2, border_color='white')

        print(f'ViewBox: size={self.grz_view.size}, pos={self.grz_view.pos}')
        print(f'ViewBox: size={self.pord_view.size}, pos={self.pord_view.pos}')
        print(f'ViewBox: size={self.zden_view.size}, pos={self.zden_view.pos}')

        main_layout.addLayout(self.layout)  # Add graph layout to main layout

        # Right side layout for controls
        controls_layout = QVBoxLayout()

        # Start depth slider and label
        self.start_depth_label = QLabel('Start Depth: 0')
        self.start_depth_slider = QSlider(Qt.Vertical)
        self.start_depth_slider.valueChanged.connect(self.update_slider_labels)
        self.start_depth_slider.valueChanged.connect(self.update_plot)

        # End depth slider and label
        self.end_depth_label = QLabel('End Depth: 0')
        self.end_depth_slider = QSlider(Qt.Vertical)
        self.end_depth_slider.valueChanged.connect(self.update_slider_labels)
        self.end_depth_slider.valueChanged.connect(self.update_plot)

        # Line edits for depth input
        self.start_depth_edit = QLineEdit()
        self.end_depth_edit = QLineEdit()

        # Arrange controls in grid layout
        grid_controls_layout = QGridLayout()
        grid_controls_layout.addWidget(QLabel('Start Depth:'), 0, 0)
        grid_controls_layout.addWidget(self.start_depth_edit, 0, 1)
        grid_controls_layout.addWidget(self.start_depth_slider, 2, 0, 1, 2)
        grid_controls_layout.addWidget(QLabel('End Depth:'), 1, 0)
        grid_controls_layout.addWidget(self.end_depth_edit, 1, 1)
        grid_controls_layout.addWidget(self.end_depth_slider, 2, 1, 1, 2)

        # Add controls grid layout to controls layout
        controls_layout.addLayout(grid_controls_layout)

        # Open LAS file button
        self.open_button = QPushButton('Open LAS File')
        self.open_button.clicked.connect(self.open_las_file)
        controls_layout.addWidget(self.open_button)

        # Average values label
        self.avg_label = QLabel('')
        controls_layout.addWidget(self.avg_label)

        # Add controls layout to main layout
        main_layout.addLayout(controls_layout)

        # Set main layout to the widget
        self.setLayout(main_layout)

        self.start_depth_edit.editingFinished.connect(self.on_start_depth_edit)
        self.end_depth_edit.editingFinished.connect(self.on_end_depth_edit)



    def open_las_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open LAS File', '', 'LAS Files (*.las)')
        if file_path:
            self.las_data.read_las_file(file_path)
            self.setup_sliders()
            self.update_plot()
    
    def setup_sliders(self):
        scale_factor = 100  # Adjust this based on the expected range of depth values
        min_depth = int(np.nanmin(self.las_data.depth) * scale_factor)
        max_depth = int(np.nanmax(self.las_data.depth) * scale_factor)
        self.start_depth_slider.setRange(min_depth, max_depth)
        self.end_depth_slider.setRange(min_depth, max_depth)
        self.start_depth_slider.setValue(min_depth)
        self.end_depth_slider.setValue(max_depth)
        self.update_slider_labels()
        self.min_depth = np.nanmin(self.las_data.depth)  # Store the minimum depth
        self.max_depth = np.nanmax(self.las_data.depth)  # Store the maximum depth

    def on_start_depth_edit(self):
        # Handle start depth line edit
        try:
            depth = float(self.start_depth_edit.text()) * 100  # Multiply by scale factor
            self.start_depth_slider.setValue(int(depth))
            self.update_plot()
        except ValueError:
            pass  # Handle invalid input
    
    def on_end_depth_edit(self):
        # Handle end depth line edit
        try:
            depth = float(self.end_depth_edit.text()) * 100  # Multiply by scale factor
            self.end_depth_slider.setValue(int(depth))
            self.update_plot()
        except ValueError:
            pass  # Handle invalid input

    def update_plot(self):
        start_depth = self.start_depth_slider.value() / 100.0  # Adjust based on your scaling
        end_depth = self.end_depth_slider.value() / 100.0      # Adjust based on your scaling

        print(f"Updating plot for depth range: {start_depth} to {end_depth}")
        # Apply the mask for the selected depth range
        mask = (self.las_data.depth >= start_depth) & (self.las_data.depth <= end_depth)
        depth_range = self.las_data.depth[mask]
        grz_range = self.las_data.grz[mask]
        pord_range = self.las_data.pord[mask]
        zden_range = self.las_data.zden[mask]

        print(f"Filtered data lengths: Depth-{len(depth_range)}, GRZ-{len(grz_range)}, PORD-{len(pord_range)}, ZDEN-{len(zden_range)}")

        # Filter out non-NaN values
        valid_data_mask = ~np.isnan(depth_range) & ~np.isnan(grz_range) & ~np.isnan(pord_range) & ~np.isnan(zden_range)
        depth_clean = depth_range[valid_data_mask]
        grz_clean = grz_range[valid_data_mask]
        pord_clean = pord_range[valid_data_mask]
        zden_clean = zden_range[valid_data_mask]

        # Scale ZDEN values
        zden_scale_factor = 1  # Adjust this as needed
        zden_clean_scaled = zden_clean / zden_scale_factor

        # Calculate averages within the selected depth range
        avg_grz = np.nanmean(grz_clean) if len(grz_clean) > 0 else np.nan
        avg_pord = np.nanmean(pord_clean) if len(pord_clean) > 0 else np.nan
        avg_zden = np.nanmean(zden_clean) if len(zden_clean) > 0 else np.nan
        # Update the average values label
        self.avg_label.setText(f'Avg GRZ: {avg_grz:.2f}\nAvg PORD: {avg_pord:.2f}\nAvg ZDEN: {avg_zden:.2f}')


        # Clear the existing plots from the views
        for view in [self.grz_view, self.pord_view, self.zden_view]:
            view.children.clear()

        # Create and add new plots to respective views
        if len(depth_clean) > 0:
            grz_plot = LinePlot(np.column_stack((grz_clean, depth_clean)), color='blue', width=0.5)
            self.grz_view.add(grz_plot)

            pord_plot = LinePlot(np.column_stack((pord_clean, depth_clean)), color='green', width=0.5)
            self.pord_view.add(pord_plot)

            zden_plot = LinePlot(np.column_stack((zden_clean_scaled, depth_clean)), color='red', width=0.5)
            self.zden_view.add(zden_plot)

         # Set the correct range for the plots
        grz_x_min, grz_x_max = np.nanmin(grz_clean), np.nanmax(grz_clean)
        pord_x_min, pord_x_max = np.nanmin(pord_clean), np.nanmax(pord_clean)
        zden_x_min, zden_x_max = np.nanmin(zden_clean_scaled), np.nanmax(zden_clean_scaled)
        y_min, y_max = np.nanmin(depth_clean), np.nanmax(depth_clean)

        self.grz_view.camera = 'panzoom'
        self.grz_view.camera.set_range(x=(grz_x_min, grz_x_max), y=(y_min, y_max))
        self.pord_view.camera = 'panzoom'
        self.pord_view.camera.set_range(x=(pord_x_min, pord_x_max), y=(y_min, y_max))
        self.zden_view.camera = 'panzoom'
        self.zden_view.camera.set_range(x=(zden_x_min, zden_x_max), y=(y_min, y_max))
        
    # Update canvas
        self.canvas.app.process_events()
        self.canvas.update()
        self.update_slider_labels()

    def update_slider_labels(self):
    # Get the slider values as floating-point numbers
        start_depth = self.start_depth_slider.value() / 100.0  # Assuming you've scaled the values by 100
        end_depth = self.end_depth_slider.value() / 100.0      # Adjust the divisor according to your scale factor

        print(f"Debug: Start Depth Slider Value: {self.start_depth_slider.value()}")
        print(f"Debug: End Depth Slider Value: {self.end_depth_slider.value()}")
        print(f"Debug: Start Depth: {start_depth}")
        print(f"Debug: End Depth: {end_depth}")

    # Update the labels with the current slider values, formatted to two decimal places
        self.start_depth_label.setText(f'Start Depth: {start_depth:.2f}')
        self.end_depth_label.setText(f'End Depth: {end_depth:.2f}')
