import pandas as pd
import json
import os
import numpy as np
import shutil
from aero import Aero

def load_excel(path):

    sheet_name = '審査用シート'
    launch_data = pd.read_excel(path, sheet_name=sheet_name, skiprows=1, nrows=9, usecols='E:F', header=None, index_col=0).transpose()
    rocket_data = pd.read_excel(path, sheet_name=sheet_name, skiprows=11, nrows=45, usecols='E:F', header=None, index_col=0).transpose()
    
    sheet_name = '団体入力シート'
    fuel_data  = pd.read_excel(path, sheet_name=sheet_name, skiprows=22, nrows=2, usecols='C:D', header=None, index_col=0).transpose()
    model_name = pd.read_excel(path, sheet_name=sheet_name, skiprows=3, nrows=1, usecols='D', header=None, index_col=None).to_numpy()
    model_name = str(model_name[0, 0])
    
    return model_name, launch_data, rocket_data, fuel_data

def __set_config(model_name, number_site, launch_data, rocket_data, fuel_data, wind_info, multi_cond, path_result, path_thrust):

    json_config = {}

    ###############################################################################################
    # Solver
    ###############################################################################################
    json_config['Solver'] = {} 
    json_config['Solver']['Name'] = model_name
    json_config['Solver']['Result Filepath'] = path_result
    json_config['Solver']['Time Step [sec]'] = 0.001
    
    ###############################################################################################
    # Multi Solver
    ###############################################################################################
    json_config['Multi Solver'] = {} 
    json_config['Multi Solver']['Minimum Wind Speed [m/s]'] = multi_cond['Minimum Wind Speed [m/s]']
    json_config['Multi Solver']['Step Wind Speed [m/s]']    = multi_cond['Step Wind Speed [m/s]']
    json_config['Multi Solver']['Number of Wind Speed']     = multi_cond['Number of Wind Speed']
    json_config['Multi Solver']['Number of Wind Azimuth']   = multi_cond['Number of Wind Azimuth']
    json_config['Multi Solver']['Base Wind Azimuth [deg]']  = multi_cond['Base Wind Azimuth [deg]']

    ###############################################################################################
    # Wind
    ###############################################################################################
    json_config['Wind'] = {} 

    exist_wind_file = wind_info['Wind File Exist']
    json_config['Wind']['Wind File Exist'] = exist_wind_file
    if exist_wind_file:
        wind_file = path_result + os.sep + model_name + '_wind.csv'
        json_config['Wind']['Wind File'] = wind_file
        shutil.copy(wind_info['Wind File'], wind_file)
    else:
        json_config['Wind']['Wind File'] = ''
    
    json_config['Wind']['Wind Model']                  = 'law'
    json_config['Wind']['Wind Power Law Coefficient']  = launch_data['べき指数'].to_numpy()[0]
    json_config['Wind']['Wind Speed [m/s]']            = wind_info['Wind Speed [m/s]']
    json_config['Wind']['Wind Azimuth [deg]']          = wind_info['Wind Azimuth [deg]']
    json_config['Wind']['Wind Reference Altitude [m]'] = launch_data['べき法則基準高度'].to_numpy()[0]
    
    ###############################################################################################
    # Atmosphere
    ###############################################################################################
    json_config['Atmosphere'] = {}
    json_config['Atmosphere']['Temperature at 0 m [℃]'] = 15.

    ###############################################################################################
    # Launch Condition
    ###############################################################################################
    json_config['Launch Condition'] = {}
    json_config['Launch Condition']['Date'] = '2021/11/6 8:30:00.0'
    json_config['Launch Condition']['Site'] = number_site # TODO: select
    json_config['Launch Condition']['Launch lat'] = launch_data['射点緯度'].to_numpy()[0]
    json_config['Launch Condition']['Launch lon'] = launch_data['射点経度'].to_numpy()[0]
    json_config['Launch Condition']['Launch height'] = launch_data['海面高度'].to_numpy()[0]
    json_config['Launch Condition']['Input Magnetic Azimuth [deg]'] = launch_data['磁気偏角'].to_numpy()[0]
    json_config['Launch Condition']['Launch Azimuth [deg]'] = launch_data['ランチャ方位角'].to_numpy()[0]
    json_config['Launch Condition']['Launch Elevation [deg]'] = launch_data['射角'].to_numpy()[0]
    json_config['Launch Condition']['Launcher Rail Length [m]'] = launch_data['レール長さ'].to_numpy()[0]
    json_config['Launch Condition']['Tip-Off Calculation Exist'] = False
    json_config['Launch Condition']['Safety Area Exist'] = True
    
    # ###############################################################################################
    #  Structure
    # ###############################################################################################
    json_config['Structure'] = {}
    json_config['Structure']['Length [m]'] = rocket_data['全長'].to_numpy()[0] * 1.e-3
    json_config['Structure']['Diameter [m]'] = rocket_data['代表直径'].to_numpy()[0] * 1.e-3
    json_config['Structure']['Dry Mass [kg]'] = rocket_data['乾燥質量'].to_numpy()[0]
    json_config['Structure']['Dry Length-C.G. from Nosetip [m]'] = rocket_data['乾燥重心（先端から）'].to_numpy()[0] * 1.e-3
    json_config['Structure']['Dry Moment of Inertia Roll-Axis [kg*m^2]'] = rocket_data['ロール慣性モーメント'].to_numpy()[0]
    json_config['Structure']['Dry Moment of Inertia  Pitch-Axis [kg*m^2]'] = rocket_data['ピッチヨー慣性モーメント'].to_numpy()[0]
    json_config['Structure']['Upper Launch Lug [m]'] = rocket_data['乾燥重心（先端から）'].to_numpy()[0] * 1.e-3
    json_config['Structure']['Lower Launch Lug [m]'] = rocket_data['乾燥重心（先端から）'].to_numpy()[0] * 1.e-3
    
    ###############################################################################################
    # Engine
    ###############################################################################################
    lcg_fuel = rocket_data['燃料重心（後端から）'].to_numpy()[0] * 1.e-3
    l_fuel = 2. * lcg_fuel
    lcg_ox_bef = rocket_data['酸化剤重心（後端から）'].to_numpy()[0] * 1.e-3
    ltank_end = rocket_data['タンク口金位置'].to_numpy()[0] * 1.e-3
    l_tank = 2. * (lcg_ox_bef - ltank_end)
    rho_ox =  800.0 # [kg/m3]
    vol_tank = rocket_data['酸化剤質量'].to_numpy()[0] / rho_ox * 1.e6
    d_tank = np.sqrt(vol_tank * 1.e-6 / l_tank / np.pi) * 2. * 1.e3
    d_out_fuel = d_tank
    rho_fuel = 1.e3 # [kg/m3]
    m_fuel_bef = fuel_data['燃焼前燃料質量'].to_numpy()[0]
    m_fuel_aft = fuel_data['燃焼後燃料質量'].to_numpy()[0]
    d_in_fuel = d_out_fuel - np.sqrt(m_fuel_bef / (rho_fuel * 0.25 * np.pi)) * 1e3

    thrust_file = path_result + os.sep + model_name + '_thrust.csv'
    shutil.copy(path_thrust, thrust_file)
    
    json_config['Engine'] = {}
    json_config['Engine']['Thrust Curve'] = thrust_file
    json_config['Engine']['Nozzle Exit Diameter [mm]'] = rocket_data['ノズル出力径'].to_numpy()[0]
    json_config['Engine']['Burn Time [sec]'] = rocket_data['燃焼時間'].to_numpy()[0]
    json_config['Engine']['Tank Volume [cc]'] = vol_tank
    json_config['Engine']['Oxidizer Density [kg/m^3]'] = rho_ox
    json_config['Engine']['Length Fuel-C.G. from End [m]'] = lcg_fuel
    json_config['Engine']['Length Tank-End from End [m]'] = ltank_end
    json_config['Engine']['Fuel Mass Before [kg]'] = m_fuel_bef
    json_config['Engine']['Fuel Mass After [kg]']  = m_fuel_aft
    json_config['Engine']['Fuel Outside Diameter [mm]'] = d_out_fuel
    json_config['Engine']['Fuel Inside Diameter [mm]'] = d_in_fuel
    json_config['Engine']['Tank Diameter [mm]'] = d_tank
    json_config['Engine']['Fuel Length [m]'] = l_fuel
    json_config['Engine']['Tank Length [m]'] = l_tank

    ###############################################################################################
    # Aero
    ###############################################################################################
    json_config['Aero'] = {}
    json_config['Aero']['Cd File Exist'] = False
    json_config['Aero']['Constant Cd'] = rocket_data['軸力係数'].to_numpy()[0]
    json_config['Aero']['CNa File Exist'] = False
    json_config['Aero']['Constant CNa'] = rocket_data['法線力傾斜'].to_numpy()[0]
    json_config['Aero']['Length-C.P. File Exist'] = False
    json_config['Aero']['Constant Length-C.P. from Nosetip [m]'] = rocket_data['圧力中心位置（先端から）'].to_numpy()[0] * 1.e-3
    json_config['Aero']['Roll Dumping Moment Coefficient Clp'] = rocket_data['ロール減衰モーメント係数'].to_numpy()[0]
    json_config['Aero']['Pitch Dumping Moment Coefficient Cmq'] = rocket_data['ピッチヨー減衰モーメント係数'].to_numpy()[0]

    shappe_nose = rocket_data['ノーズ形状'].to_numpy()[0]
    l_nose      = rocket_data['ノーズ長さ'].to_numpy()[0] * 1.e-03
    offset_fin  = rocket_data['フィンオフセット長さ'].to_numpy()[0] * 1.e-03
    root_fin    = rocket_data['翼根コード長'].to_numpy()[0] * 1.e-03
    tip_fin     = rocket_data['翼端コード長'].to_numpy()[0] * 1.e-03
    leading_fin = rocket_data['翼前縁部後退長さ'].to_numpy()[0] * 1.e-03
    span_fin    = rocket_data['半スパン'].to_numpy()[0] * 1.e-03
    
    __check_aero(path_result, length=json_config['Structure']['Length [m]'], diameter=json_config['Structure']['Diameter [m]'], Xcg=json_config['Structure']['Dry Length-C.G. from Nosetip [m]'],
                 shape_nose=shappe_nose, l_nose=l_nose, offset_fin=offset_fin, root_fin=root_fin, tip_fin=tip_fin, leading_fin=leading_fin, span_fin=span_fin, 
                 Xcp=json_config['Aero']['Constant Length-C.P. from Nosetip [m]'], CNa=json_config['Aero']['Constant CNa'], Cmq=json_config['Aero']['Pitch Dumping Moment Coefficient Cmq'], Clp=json_config['Aero']['Roll Dumping Moment Coefficient Clp'])

    ###############################################################################################
    # Payload
    ###############################################################################################
    
    def calc_CdS(mass, vel_descent):
        rho_air = 1.225 # [kg/m3]
        g_air = 9.80665 # [m/s2]
        return mass * g_air / (0.5 * vel_descent**2. * rho_air)
    
    vel_payload = rocket_data['ペイロードパラシュート'].to_numpy()[0]
    json_config['Payload'] = {}
    if type(vel_payload) == str or vel_payload <= 0.0:
        json_config['Payload']['Payload Exist'] = False
        json_config['Payload']['Mass [kg]'] = 0.0
        json_config['Payload']['Parachute CdS [m2]'] = 0.0
        m_payload = 0.
    else:
        m_payload = rocket_data['ペイロード質量'].to_numpy()[0]
        json_config['Payload']['Payload Exist'] = True
        json_config['Payload']['Mass [kg]'] = m_payload
        json_config['Payload']['Parachute CdS [m2]'] = calc_CdS(m_payload, vel_payload)
    
    ###############################################################################################
    # Parachute
    ###############################################################################################
    vel_descent_1st = rocket_data['1段目パラシュート'].to_numpy()[0]
    vel_descent_2nd = rocket_data['2段目パラシュート'].to_numpy()[0]
    time_2nd = rocket_data['2段目パラシュート開傘時刻'].to_numpy()[0]
    m_aft = rocket_data['燃焼終了時機体質量'].to_numpy()[0] - m_payload
    
    json_config['Parachute'] = {}
    json_config['Parachute']['1st Parachute CdS [m2]'] = calc_CdS(m_aft, vel_descent_1st)
    json_config['Parachute']['Parachute Opening Lag [sec]'] = 0.0
    if type(vel_descent_2nd) == str or vel_descent_2nd <= 0.0:
        json_config['Parachute']['2nd Parachute Exist'] = False
        json_config['Parachute']['2nd Parachute CdS [m2]'] = 0.0
        json_config['Parachute']['2nd Parachute Opening Altitude [m]'] = 0.0
        json_config['Parachute']['2nd Parachute Timer Mode'] = False
        json_config['Parachute']['2nd Timer [s]'] = 0.0
    else:
        json_config['Parachute']['2nd Parachute Exist'] = True
        json_config['Parachute']['2nd Parachute CdS [m2]'] = calc_CdS(m_aft, vel_descent_2nd)
        json_config['Parachute']['2nd Parachute Opening Altitude [m]'] = 0.0
        json_config['Parachute']['2nd Parachute Timer Mode'] = True
        json_config['Parachute']['2nd Timer [s]'] = time_2nd
    
    json.dump(json_config, open(path_result + os.sep + model_name + '_config.json', mode='w', encoding='utf-8'), indent=4, ensure_ascii=False)

def __check_aero(path, length, diameter, Xcg, shape_nose, l_nose, offset_fin, root_fin, tip_fin, leading_fin, span_fin, Xcp, CNa, Cmq, Clp):

    aero = Aero(length, diameter, Xcg, shape_nose, l_nose, offset_fin, root_fin, tip_fin, leading_fin, span_fin, )
    aero.plot(path)
    aero.output(path, Xcp, CNa, Cmq, Clp)

def __input_path(type_file, surfix=''):

    print(type_file)
    __arg_input = input(' Enter Absolute Path: \n  >> ').strip()
    
    while(not (os.path.exists(__arg_input) and __arg_input.endswith(surfix))):
        __arg_input = input(' Error! Please Enter Path Again!! \n  >> ').strip()

    return __arg_input

def __select_wind():

    mode = input('Select Wind Mode [0 or 1] \n 0: Power Law, 1: Input Wind File \n >> ')
    if mode == '0':
        exit_wind_file = False
        path_wind = ''
        speed_ref = __input_path('Reference Wind Speed')
        azimuth_ref = __input_path('Reference Wind Azimuth')
    else:
        exit_wind_file = True
        path_wind = __input_path('Wind File Path')
        speed_ref = 0.
        azimuth_ref = 0.

    wind_info = {}
    wind_info['Wind File Exist'] = exit_wind_file
    wind_info['Wind File'] = path_wind
    wind_info['Wind Speed [m/s]'] = speed_ref
    wind_info['Wind Azimuth [deg]'] = azimuth_ref

    return wind_info

def __get_multi_cond():

    speed_min = input('Minimum Wind Speed [m/s] : \n >> ')
    speed_step = input('Step Wind Speed [m/s] : \n >> ')
    num_speed = input('Number of Wind Speed : \n >> ')
    num_azimuth = input('Number of Wind Azimuth : \n >> ')
    
    multi_cond = {}
    multi_cond['Minimum Wind Speed [m/s]'] = speed_min
    multi_cond['Step Wind Speed [m/s]']    = speed_step
    multi_cond['Number of Wind Speed']     = num_speed
    multi_cond['Number of Wind Azimuth']   = num_azimuth
    multi_cond['Base Wind Azimuth [deg]']  = 0.

    return multi_cond

def __debug():

    print('STATUS: DEBUG')

    path_src = __input_path('Config file Excel', '.xlsx')
    path_thrust = __input_path('Thrust Data in csv', '.csv')
    wind = __select_wind()
    multi_cond = __get_multi_cond()
    path_result = __input_path('Result Path')
    site = input('Enter Launch Site: \n >> ')
    model, launch, rocket, fuel = load_excel(path_src)
    __set_config(model, site, launch, rocket, fuel, wind, multi_cond, path_result, path_thrust)

def make_json_config(params):

    path_src    = params['Config']
    path_thrust = params['Thrust']
    wind_info   = params['Wind']
    path_result = params['Result']
    site        = params['Launch Site']
    multi_cond  = params['Multi Cond.']
    model, launch, rocket, fuel = load_excel(path_src)
    __set_config(model, site, launch, rocket, fuel, wind_info, multi_cond, path_result, path_thrust)

if __name__=='__main__':

    print('Hello World!')

    __debug()

    print('Have a Good Day!')