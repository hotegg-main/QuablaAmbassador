'''
Calculate Aero Parameters based on Barrowman Method
'''

import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

class Component:

    def __init__(self):
        
        self.Xcp = 0.
        self.CNa = 0.
        self.Cmq = 0.
        self.Cnr = 0.
        self.Clp = 0.

        # self.length = 0.
        # Distance from nose-tip
        self.distance = 0.

    def calc_Cmq(self, Xcg, length_all):
        '''
        length : Full length of rocket
        '''

        self.Cmq = - 4. * (.5 * self.CNa * ((self.Xcp - Xcg) / length_all) ** 2)
        self.Cnr = self.Cmq

class NoseCone(Component):

    def __init__(self, shape: str, length: float, diameter: float):
        
        super().__init__()

        coeff_CP = self._get_CP_coeff(shape, ratio_slender=length/diameter)

        # self.length   = length
        self.distance = 0.

        self.CNa = 2.
        self.Xcp = length * coeff_CP

    def _get_CP_coeff(self, shape, ratio_slender):

        coeff_CP = 0.0

        if shape == 'Cone':
            coeff_CP = 2. / 3.

        elif shape == 'Parabolic':
            coeff_CP = .5

        elif shape == 'Ogive':
            coeff_CP = 1. - (  (8. * ratio_slender ** 2 / 3.) 
                             + ((4. * ratio_slender ** 2 - 1.) ** 2 / 4.) 
                             - (((4. * ratio_slender ** 2 - 1.) * (4. * ratio_slender ** 2 + 1.) ** 2 / (16. * ratio_slender)) * np.arcsin(4. * ratio_slender / (4. * ratio_slender ** 2 + 1.))))

        return coeff_CP
    
class Fin(Component):

    def __init__(self, root, tip, leading, span, diameter, distance, length_all):

        super().__init__()

        self.distance = distance
        
        mid_chord_line = self.__get_mid_chord(root, tip, leading, span)
        CNa_single = 16.0 * (span / diameter) ** 2 / (1.0 + np.sqrt(1.0 + (2.0 * mid_chord_line / (root + tip)) ** 2))
        inter_factor = 1.0 + 0.5 * diameter / (0.5 * diameter + span)
        self.CNa = CNa_single * inter_factor

        ratio_taper = tip / root
        mean_aero_cord = 2.0 / 3.0 * root * (1 + ratio_taper ** 2 / (1.0 + ratio_taper))
        self.Xcp = self.distance + (leading * (root + 2.0 * tip) / (3.0 * (root + tip))) + mean_aero_cord / 4.0

        self.Clp = -4.0 * 2.0 * (span + 0.5 * diameter) ** 4 / (np.pi * length_all ** 2 * (0.25 * diameter ** 2 * np.pi))

    def __get_mid_chord(self, Cr, Ct, Cle, span):

        if Cle+0.5*Ct == 0.5*Cr:
            return span
        elif Cle+0.5*Ct > 0.5*Cr:
            return np.sqrt(span ** 2 + (0.5 * Ct + Cle - 0.5 * Cr) ** 2)
        else:
            return np.sqrt(span ** 2 + (0.5 * Cr - Cle - 0.5 * Ct) ** 2)
        
class Aero():

    def __init__(self, length, diameter, Xcg, shappe_nose, l_nose, offset_fin, root_fin, tip_fin, leading_fin, span_fin):
        
        self.nose = NoseCone(shappe_nose, l_nose, diameter)
        self.fin  = Fin(root_fin, tip_fin, leading_fin, span_fin, diameter, length-(offset_fin+root_fin), length)

        self.length = length
        self.diameter = diameter
        self.Xcg = Xcg

        self.l_nose = l_nose
        self.l_body = length - (l_nose + offset_fin+root_fin)

        self.offset_fin = offset_fin
        self.root_fin = root_fin
        self.tip_fin = tip_fin
        self.leading_fin = leading_fin
        self.span_fin = span_fin

        self.components = [self.nose, self.fin]

        self.__assembly()

    def __assembly(self):

        self.Xcp = 0.
        self.CNa = 0.
        self.Cmq = 0.
        self.Cnr = 0.
        self.Clp = 0.

        for obj in self.components:

            obj.calc_Cmq(self.Xcg, self.length)

            self.Xcp += obj.Xcp * obj.CNa
            self.CNa += obj.CNa
            self.Cmq += obj.Cmq
            self.Cnr += obj.Cnr
            self.Clp += obj.Clp

        self.Xcp /= self.CNa

        print('Xcp = ', self.Xcp)
        print('CNa = ', self.CNa)
        print('Cmq = ', self.Cmq)
        print('Cnr = ', self.Cnr)
        print('Clp = ', self.Clp)

    def output(self, path, Xcp, CNa, Cmq, Clp):

        name_index  = ['Xcp [m]', 'CNa [1/rad]', 'Cmq [1/rad]', 'Clp [1/rad]']
        name_column = ['Input', 'Barrowman', 'Error [%]']

        data_aero = np.zeros((len(name_index), len(name_column)))

        data_aero[:, 0] = np.array([Xcp, CNa, Cmq, Clp])
        data_aero[:, 1] = np.array([self.Xcp, self.CNa, self.Cmq, self.Clp])
        data_aero[:, 2] = np.abs(data_aero[:, 0] - data_aero[:, 1])

        for i in range(len(name_index)):
            data_aero[i, 2] *= np.abs(100. / data_aero[i, 1])

        pd.DataFrame(data=data_aero, index=name_index, columns=name_column).to_csv(path + os.sep + 'aero_check.csv')

    def plot(self, ax: plt.Axes):

        x_nose_top = 0.
        x_nose_bot = self.l_nose
        y_nose_top = 0.
        y_nose_bot = .5 * self.diameter

        x_body_top = x_nose_bot
        x_body_bot = x_body_top + self.l_body
        y_body_top = y_nose_bot
        y_body_bot = y_body_top

        x_fin_top = x_body_bot
        x_fin_1   = x_fin_top + self.leading_fin
        x_fin_2   = x_fin_1 + self.tip_fin
        x_fin_bot = x_fin_top + self.root_fin
        y_fin_top = .5 * self.diameter
        y_fin_1   = y_fin_top + self.span_fin
        y_fin_2   = y_fin_1
        y_fin_bot = y_fin_top

        x_end = self.length
        y_end = 0.

        # x_list = [x_nose_top, x_nose_bot, x_body_bot, x_fin_bot, x_end]
        x_list = [x_nose_top, x_nose_bot, x_body_bot, x_end, x_end]
        y_list_up = [y_nose_top, y_nose_bot, y_body_bot, y_fin_bot, y_end]
        y_list_down = [- y for y in y_list_up]

        x_nose_list = [x_fin_top, x_fin_1, x_fin_2, x_fin_bot]
        y_nose_list_up = [y_fin_top, y_fin_1, y_fin_2, y_fin_bot]
        y_nose_list_down = [- y for y in y_nose_list_up]
        
        ax.plot(x_list, y_list_up, color='black')
        ax.plot(x_list, y_list_down, color='black')
        ax.plot(x_nose_list, y_nose_list_down, color='black')
        ax.plot(x_nose_list, y_nose_list_up, color='black')
        ax.set_ylim(ymin=- 3.5*y_fin_1, ymax=3.5*y_fin_1)
        ax.axhline(0.0, color='gray', linewidth=3, linestyle='--', alpha=0.3)
        ax.scatter(self.Xcp, 0., marker='o', color='gold', s=80, label='C.P.(Barrowman-Method)')
        ax.set_aspect('equal')
        ax.grid()

def __debug():

    diameter = 146.0       *1.e-03
    length   = 1920.0      *1.e-03

    Xcg      = 1180.0      *1.e-03

    shappe_nose = 'Ogive'
    l_nose      = 200.0    *1.e-03

    offset_fin  = 0.0      *1.e-03
    root_fin    = 210.0    *1.e-03
    tip_fin     = 50.0     *1.e-03
    leading_fin = 160.0    *1.e-03
    span_fin    = 130.0    *1.e-03

    aero = Aero(length, diameter, Xcg, shappe_nose, l_nose, offset_fin, root_fin, tip_fin, leading_fin, span_fin)
    aero.plot('./')
    aero.output('./', Xcp=1.41744, CNa=8.78, Cmq=-2.95, Clp=-0.1)

if __name__=='__main__':

    print('Hello World!')

    __debug()

    print('Have a Good Day!')