import tkinter
from tkinter import *
import tkinter.filedialog
import tkinter.ttk as ttk
from tkinter import filedialog
import numpy as np
import os

class Gui:

    def __init__(self):

        ###########################################################################################
        # Main Window
        ###########################################################################################
        self.root = tkinter.Tk()
        self.root.title('Quabla Config Creator')
        self.root.geometry('800x480')

        ###########################################################################################
        # Font
        ###########################################################################################
        style = ttk.Style()
        style.configure('myButton1.TButton', font=('', 15, 'bold'), padding=[10])

        ###########################################################################################
        # Layout
        ###########################################################################################
        frame_left  = ttk.Frame(self.root, padding=3.)
        frame_right = ttk.Frame(self.root, padding=3.)
        frame_left.grid(  row=0, column=0, sticky=tkinter.N)
        frame_right.grid( row=0, column=1, sticky=tkinter.N)
        
        self.frame_dialog_excel = ttk.Frame(frame_left,  padding=5.)
        self.frame_thrust_curve = ttk.Frame(frame_left,  padding=5.)
        self.frame_result       = ttk.Frame(frame_left,  padding=5.)
        self.frame_launch_site  = ttk.Frame(frame_left,  padding=5.)
        self.frame_wind         = ttk.Frame(frame_right, padding=5.)
        self.frame_dialog_excel.grid( row=0, column=0, sticky=tkinter.N)
        self.frame_thrust_curve.grid( row=1, column=0, sticky=tkinter.N)
        self.frame_result.grid(       row=2, column=0, sticky=tkinter.N)
        self.frame_launch_site.grid(  row=3, column=0, sticky=tkinter.N+tkinter.W)
        self.frame_wind.grid(         row=0)

        ###########################################################################################
        # Variables
        ###########################################################################################
        self.var_model = tkinter.StringVar(value='')

        ###########################################################################################
        # Frame Settings
        ###########################################################################################
        self.set_dialog_excel()
        self.set_frame_thrust_curve()
        self.set_frame_result()
        self.set_frame_wind()
        self.set_frame_launch()

        ###########################################################################################
        # Button
        ###########################################################################################
        self.set_create_button(pos=[120., 400.])

        self.root.mainloop()

    def set_dialog_excel(self):

        self.var_path_config = tkinter.StringVar()
        self.var_path_dir_config = tkinter.StringVar(value='./')

        add_label(self.frame_dialog_excel, text='Input Rocket Configuration (.xlsx)', row=0, col=0)
        add_entry(self.frame_dialog_excel, row=1, col=0, var_text=self.var_path_config)
        add_button(self.frame_dialog_excel, text='Browse', row=1, col=1, command=lambda: browse_file_search(self.var_path_config, self.var_path_dir_config))
        
    def set_frame_thrust_curve(self):

        self.var_path_thrust = tkinter.StringVar(value='sample/thrust.csv')

        add_label(self.frame_thrust_curve, text='Input Thrust Curve (.csv)', row=0)
        add_entry(self.frame_thrust_curve, var_text=self.var_path_thrust, row=1, col=0)
        add_button(self.frame_thrust_curve, text='Browse', row=1, col=1,command=lambda: browse_file(self.var_path_thrust, self.var_path_dir_config))
        
    def set_frame_result(self):

        self.var_path_result = tkinter.StringVar(value='sample')

        add_label(self.frame_result, text='Input Result Directory', row=0)
        add_entry(self.frame_result, var_text=self.var_path_result, row=1, col=0)
        add_button(self.frame_result, text='Browse', row=1, col=1, command=lambda: browse_folder(self.var_path_result, self.var_path_dir_config))

    def set_frame_launch(self):

        self.var_site = tkinter.StringVar(value=1)
        site_list = np.arange(1, 11, 1, dtype=int).tolist()

        add_label(self.frame_launch_site, text='Select Launch Site Index: ', row=0)
        add_combobox(self.frame_launch_site, items=site_list, var_text=self.var_site,row=0, col=1)

    def set_frame_wind(self):

        azimuth_list = np.arange(4, 68, 4, dtype=int).tolist()
        speed_list   = np.arange(1, 21, 1, dtype=int).tolist()

        # Wind Model
        self.var_exist_wind_file    = tkinter.BooleanVar(value=False)
        self.var_path_wind_file     = tkinter.StringVar(value='')
        # Power Law
        self.var_pow_speed   = tkinter.DoubleVar(value=3.0)
        self.var_pow_azimuth = tkinter.DoubleVar(value=0.0)
        # Multi Condition
        self.var_num_azimuth  = tkinter.IntVar(    value=azimuth_list[2])
        self.var_num_speed    = tkinter.IntVar(    value=speed_list[6])
        self.var_min_speed    = tkinter.DoubleVar( value=1.0)
        self.var_step_speed   = tkinter.DoubleVar( value=1.0)
        self.var_base_azimuth = tkinter.DoubleVar( value=0.0)
        
        # Wind Model
        add_label(self.frame_wind, text='Select Wind Model', row=0, columnspan=2)
        add_label(self.frame_wind, text='  ', row=1, col=0, rowspan=3)
        add_label(self.frame_wind, text='Input Wind File(.csv)', row=2, col=1)
        add_entry(self.frame_wind, row=3, col=1, var_text=self.var_path_wind_file)
        button = add_button(self.frame_wind, text='Browse', row=3, col=2, command=lambda: browse_file(self.var_path_wind_file, self.var_path_dir_config))
        button['state'] = 'disable'
        add_checkbutton(self.frame_wind, text='Input Wind File?', variable=self.var_exist_wind_file, row=1, col=1, command=lambda: change_button_state(self.var_exist_wind_file, button))
        
        # Multi Condition
        sub_frame_power = ttk.Frame(self.frame_wind)
        sub_frame_power.grid(row=4, column=0, columnspan=2, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S)
        
        add_label(sub_frame_power, text='Power Law',row=0, col=0, columnspan=2)
        add_label(sub_frame_power, text='  ',row=1, col=0, rowspan=3)
        row = 1
        add_label(sub_frame_power, text='Wind Speed: ',row=row, col=1)
        add_entry(sub_frame_power, row=row, col=2, var_text=self.var_pow_speed, width=5, state='normal')
        add_label(sub_frame_power, text='m/s',row=row, col=3)
        row += 1
        add_label(sub_frame_power, text='Wind Azimuth: ',row=row, col=1)
        add_entry(sub_frame_power, row=row, col=2, var_text=self.var_pow_azimuth, width=5, state='normal')
        add_label(sub_frame_power, text='deg',row=row, col=3)
        
        # Multi Condition
        sub_frame_multi = ttk.Frame(self.frame_wind)
        sub_frame_multi.grid(row=5, column=0, columnspan=2, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S)

        add_label(sub_frame_multi, text='Multi. Condition',row=0, col=0, columnspan=2)
        # Indent
        add_label(sub_frame_multi, text='  ',row=1, col=0, rowspan=5)

        row = 1
        add_label(sub_frame_multi, text='Minimum Wind Speed: ',row=row, col=1)
        add_entry(sub_frame_multi, row=row, col=2, var_text=self.var_min_speed, width=5, state='normal')
        add_label(sub_frame_multi, text='m/s',row=row, col=3)
        row += 1
        add_label(sub_frame_multi, text='Step Wind Speed: ',row=row, col=1)
        add_entry(sub_frame_multi, row=row, col=2, var_text=self.var_step_speed, width=5, state='normal')
        add_label(sub_frame_multi, text='m/s',row=row, col=3)
        row += 1
        add_label(sub_frame_multi, text='Number of Wind Speed: ',row=row, col=1)
        add_combobox(sub_frame_multi, items=speed_list, var_text=self.var_num_speed, row=row, col=2)
        add_label(sub_frame_multi, text='',row=row, col=3)
        row += 1
        add_label(sub_frame_multi, text='Number of Wind Azimuth: ',row=row, col=1)
        add_combobox(sub_frame_multi, items=azimuth_list, var_text=self.var_num_azimuth, row=row, col=2)
        add_label(sub_frame_multi, text='',row=row, col=3)
        row += 1
        add_label(sub_frame_multi, text='Base Wind Azimuth: ',row=row, col=1)
        add_entry(sub_frame_multi, row=row, col=2, var_text=self.var_base_azimuth, width=5, state='normal')
        add_label(sub_frame_multi, text='deg',row=row, col=3)

    def set_create_button(self, pos):

        from reader import make_json_config

        def push_button():

            param_dict = self.__convert_data()
            param_dict['Result'] = self.__create_directory(param_dict['Result'])
            make_json_config(param_dict)

        create_button = ttk.Button(self.root, text='Create', width=5, style='myButton1.TButton', padding=[10], command=push_button)
        create_button.place(x=pos[0], y=pos[1])

    # def set_load_exel_button(self):

    #     from reader import load_excel

    #     def push_button():

    #         browse_file_search(self.var_path_config, self.var_path_dir_config)
    #         model, launch, rocket, fuel = load_excel(self.var_path_config.get())
    #         self.var_model.set(model)

    def __convert_data(self):
        
        path_config = self.var_path_config.get()
        path_thrust = self.var_path_thrust.get()
        path_result = self.var_path_result.get()
        site        = self.var_site.get()
        exist_wind_file = self.var_exist_wind_file.get()
        path_wind_file  = self.var_path_wind_file.get()
        pow_speed   = self.var_pow_speed.get()
        pow_azimuth = self.var_pow_azimuth.get()
        num_azimuth  = self.var_num_azimuth.get()
        num_speed    = self.var_num_speed.get()
        min_speed    = self.var_min_speed.get()
        step_speed   = self.var_step_speed.get()
        base_azimuth = self.var_base_azimuth.get()

        params = dict()
        params['Config'] = path_config
        params['Thrust'] = path_thrust
        params['Result'] = path_result
        params['Launch Site'] = site
        params['Wind'] = {}
        params['Wind']['Wind File Exist'] = exist_wind_file
        params['Wind']['Wind File']       = path_wind_file
        params['Wind']['Wind Speed [m/s]']   = pow_speed
        params['Wind']['Wind Azimuth [deg]'] = pow_azimuth
        params['Multi Cond.'] = {}
        params['Multi Cond.']['Minimum Wind Speed [m/s]'] = min_speed
        params['Multi Cond.']['Step Wind Speed [m/s]']    = step_speed
        params['Multi Cond.']['Number of Wind Speed']     = num_speed
        params['Multi Cond.']['Number of Wind Azimuth']   = num_azimuth
        params['Multi Cond.']['Base Wind Azimuth [deg]']  = base_azimuth

        return params
    
    def __create_directory(self, dir_org):

        # dir_org = os.path.dirname(config_file)
        dir_work = dir_org + '/work'
        if os.path.exists(dir_work):
            dir_work_org = dir_work
            i = 1
            while os.path.exists(dir_work):
                dir_work = dir_work_org + '_%02d' % (i)
                i += 1
        os.mkdir(dir_work)

        return dir_work

    def boot(self):

        self.root.mainloop()

def add_label(master, text, row, col=0, rowspan=1, columnspan=1):

    label = ttk.Label(master, text=text, padding=1)
    label.grid(row=row, column=col, sticky=tkinter.W, rowspan=rowspan, columnspan=columnspan)
    return label

def add_entry(master, row, col, var_text, width=30, state='readonly'):

    entry = ttk.Entry(master, textvariable=var_text, width=width, state=state)
    entry.grid(row=row, column=col, sticky=tkinter.W)
    return entry

def add_button(master, text, row, col, command=None):

    button = ttk.Button(master, text=text, command=command)
    button.grid(row=row,column=col, sticky=tkinter.W)
    return button

def add_combobox(master, items, var_text, row=0, col=0, current=0):

    combobox = ttk.Combobox(master, values=items, textvariable=var_text, state='readonly', width=5)
    combobox.current(current)
    combobox.grid(row=row, column=col, sticky=tkinter.W)
    return combobox

def add_checkbutton(master, text, variable, row=0, col=0, command=None):

    checkbutton = ttk.Checkbutton(master=master, text=text, variable=variable, onvalue=True, offvalue=False, command=command)
    checkbutton.grid(row=row, column=col, sticky=tkinter.W)
    return checkbutton

def browse_file_search(var_path_file: tkinter.StringVar, var_path_dir: tkinter.StringVar):

    path_file = filedialog.askopenfilename(initialdir='./', filetypes=[('エクセル形式ファイル', '*.xlsx')])
    var_path_file.set(path_file)
    var_path_dir.set(os.path.dirname(path_file))

def browse_file(var_path_file: tkinter.StringVar, var_path_dir: tkinter.StringVar, file_type=[('csv形式ファイル', '*.csv')]):

    path_file = filedialog.askopenfilename(initialdir=var_path_dir.get(), filetypes=file_type)
    var_path_file.set(path_file)

def browse_folder(var_text: tkinter.StringVar, var_path_dir: tkinter.StringVar):

    path = filedialog.askdirectory(initialdir=var_path_dir.get())
    var_text.set(path)

def change_button_state(flag, button):

    if flag.get():
        button['state'] = 'normal'

    else:
        button['state'] = 'disable'

def __test():

    test = Gui()

if __name__=='__main__':

    print('Hello World!')

    __test()

    print('Have a Good Day!!')