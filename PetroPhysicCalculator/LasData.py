import numpy as np
import lasio

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
