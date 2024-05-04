# Pip install lasio, vispy and PyQt5 for it to function

import sys
import numpy as np
import lasio
from vispy import scene
from PyQt5 import QtWidgets, QtCore
from vispy.scene import LinePlot
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QSlider, QLabel, QFileDialog, QLineEdit
from vispy.scene import Grid

class LasData:
    def __init__(self):
        self.depth = np.array([])
        self.grz = np.array([])
        self.pord = np.array([])
        self.zden = np.array([])
        self.null_value = -999.25

    def read_las_file(self, filename):
        try:
            las = lasio.read(filename)
            self.depth = np.where(las['DEPT'] == self.null_value, np.nan, las['DEPT'])
            self.grz = np.where(las['GRZ'] == self.null_value, np.nan, las['GRZ'])
            self.pord = np.where(las['PORD'] == self.null_value, np.nan, las['PORD'])
            self.zden = np.where(las['ZDEN'] == self.null_value, np.nan, las['ZDEN'])
        except Exception as e:
            print(f"Error reading LAS file: {e}")
            # Reset data if the file is not read properly
            self.__init__()


# Main window class
class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.las_data = LasData()
        self.init_ui()
        self.min_depth = 0
        self.max_depth = 0


    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Create VisPy canvas for plotting
        self.canvas = scene.SceneCanvas(keys='interactive')
        self.view = self.canvas.central_widget.add_view()

        # Add the canvas to the layout
        self.layout.addWidget(self.canvas.native)

        # Initialize the grid and views
        self.grid = Grid(parent=self.canvas.scene)
        self.canvas.central_widget.add_widget(self.grid)

        # Create views for each plot
        self.grz_view = self.grid.add_view(row=0, col=0, border_color='white')
        self.pord_view = self.grid.add_view(row=1, col=0, border_color='white')
        self.zden_view = self.grid.add_view(row=2, col=0, border_color='white')

        # Start depth slider and label
        self.start_depth_label = QLabel('Start Depth: 0')
        self.start_depth_slider = QSlider(QtCore.Qt.Horizontal)
        self.start_depth_slider.valueChanged.connect(self.update_slider_labels)
    
    # End depth slider and label
        self.end_depth_label = QLabel('End Depth: 0')
        self.end_depth_slider = QSlider(QtCore.Qt.Horizontal)
        self.end_depth_slider.valueChanged.connect(self.update_slider_labels)

    # Line edits for depth input
        self.start_depth_edit = QLineEdit(self)
        self.end_depth_edit = QLineEdit(self)

    # Add line edits to the layout
        self.layout.addWidget(QLabel('Start Depth:'))
        self.layout.addWidget(self.start_depth_edit)
        self.layout.addWidget(QLabel('End Depth:'))
        self.layout.addWidget(self.end_depth_edit)

    # Connect line edit signals
        self.start_depth_edit.editingFinished.connect(self.on_start_depth_edit)
        self.end_depth_edit.editingFinished.connect(self.on_end_depth_edit)


    # Connect the sliders' valueChanged signals to the update_slider_labels method
        self.start_depth_slider.valueChanged.connect(self.update_slider_labels)
        self.end_depth_slider.valueChanged.connect(self.update_slider_labels)

    # Also connect the sliders' valueChanged signals to the update_plot method
        self.start_depth_slider.valueChanged.connect(self.update_plot)
        self.end_depth_slider.valueChanged.connect(self.update_plot)


    # Add the labels and sliders to the layout
        self.layout.addWidget(self.start_depth_label)
        self.layout.addWidget(self.start_depth_slider)
        self.layout.addWidget(self.end_depth_label)
        self.layout.addWidget(self.end_depth_slider)


        # Add a button to open LAS file
        self.open_button = QPushButton('Open LAS File')
        self.open_button.clicked.connect(self.open_las_file)
        self.layout.addWidget(self.open_button)

        # Add a label to show average values
        self.avg_label = QLabel('')
        self.layout.addWidget(self.avg_label)

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
        zden_scale_factor = 100  # Adjust this as needed
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
            grz_plot = LinePlot(np.column_stack((depth_clean, grz_clean)), color='blue', width=0.5)
            self.grz_view.add(grz_plot)

            pord_plot = LinePlot(np.column_stack((depth_clean, pord_clean)), color='green', width=0.5)
            self.pord_view.add(pord_plot)

            zden_plot = LinePlot(np.column_stack((depth_clean, zden_clean_scaled)), color='red', width=0.5)
            self.zden_view.add(zden_plot)

    # Set view properties
        for view in [self.grz_view, self.pord_view, self.zden_view]:
            view.camera.set_range(y=(self.max_depth, self.min_depth))
            view.border_color = (0.5, 0.5, 0.5, 1)
            

    # Update canvas
        self.canvas.app.process_events()
        self.canvas.update()
        

    def update_slider_labels(self):
    # Get the slider values as floating-point numbers
        start_depth = self.start_depth_slider.value() / 100.0  # Assuming you've scaled the values by 100
        end_depth = self.end_depth_slider.value() / 100.0      # Adjust the divisor according to your scale factor

    # Update the labels with the current slider values, formatted to two decimal places
        self.start_depth_label.setText(f'Start Depth: {start_depth:.2f}')
        self.end_depth_label.setText(f'End Depth: {end_depth:.2f}')


# Run the application
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
