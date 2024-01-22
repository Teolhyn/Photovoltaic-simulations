import pandas as pd
import numpy as np
from tqdm import tqdm
import time
from datetime import datetime, timedelta
import os

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

import numpy as np

# pvlib imports
import pvlib
from pvlib.pvsystem import PVSystem, FixedMount
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

start_time = time.time()
# Parameters -------------------------------------------------------------------------------------

use_weather_data = False
use_clear_sky = True
sur_az = 180
sur_tilt = 30
tz = 'Europe/Helsinki'
lat = 60.45
lon = 22.29
# Panel 1
az1 = 90
tilt1 = 90
# Panel 2
az2 = 180
tilt2 = 30
# Panel 3
az3 = 270
tilt3 = 90

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

# Temporary

# load some module and inverter specifications
sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')

cec_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')

sandia_module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']

cec_inverter = cec_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']

temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

if __name__ == '__main__':
    print("Initializing...")    
    location = Location(60.45, 22.29, 'Europe/Helsinki', 50, name='Turku')
 
    weather = pd.read_csv('IrrData2019_StarkeDFC_230704.csv')
    datetimes = weather['dt']
    times = pd.DatetimeIndex(datetimes, tz=tz)

    weather.drop(columns=['dt_orig', 'dt'], axis=1, inplace=True)
    weather = weather.rename(columns={'GHI' : 'ghi', 'DNI' : 'dni', 'DHI' : 'dhi', 'Tamb' : 'temp_air', 
                                      'SunAz' : 'solar_azimuth', 'appZ' : 'apparent_zenith', 'WS' : 'wind_speed'})

    weather = weather.set_index(times)
    weather.index.name = None
    print(weather)

    print("Initialization complete!")

    print("Modelling system 1")
    system = PVSystem(surface_tilt=tilt1, surface_azimuth=az1,
                        module_parameters=sandia_module,
                        inverter_parameters=cec_inverter,
                        temperature_model_parameters=temperature_model_parameters)
    
    mc = ModelChain(system, location)

    print("MODEL 1:")
    print(mc)

    mc.run_model(weather)
    print("Modelling system 1 - Complete!")

    print("Modelling system 2")
    system2 = PVSystem(surface_tilt=tilt2, surface_azimuth=az2,
                        module_parameters=sandia_module,
                        inverter_parameters=cec_inverter,
                        temperature_model_parameters=temperature_model_parameters)
    
    mc2 = ModelChain(system2, location)

    print("MODEL 2:")
    print(mc2)

    mc2.run_model(weather)
    print("Modelling system 2 - Complete!")

    print("Modelling system 3")
    system3 = PVSystem(surface_tilt=tilt3, surface_azimuth=az3,
                        module_parameters=sandia_module,
                        inverter_parameters=cec_inverter,
                        temperature_model_parameters=temperature_model_parameters)
    
    mc3 = ModelChain(system3, location)

    print("MODEL 3:")
    print(mc3)

    mc3.run_model(weather)
    print("Modelling system 3 - Complete!")

    '''
    print(mc.results.ac)

    end_time = time.time()
    print("Simulation finished in: ", "{:.2f}".format(end_time - start_time), "seconds.")

    plt.plot(mc.results.ac, label=("Az: "+str(az1)+", Tilt: "+str(tilt1)))
    plt.plot(mc2.results.ac, label=("Az: "+str(az2)+", Tilt: "+str(tilt2)),)
    plt.plot(mc3.results.ac, label=("Az: "+str(az3)+", Tilt: "+str(tilt3)),)
    #plt.plot(weather['ghi'], label=('GHI'))
    plt.legend()
    plt.ylabel("AC Power (W)")
    plt.show()

    # Save the results
    file1 = pd.DataFrame(mc.results.ac)
    file1.to_csv(path_or_buf="Simulation_result_Az"+str(az1)+"Tilt"+str(tilt1)+".csv",mode='w', decimal='.', header=['AC Power (W)'])
    print("Files saved succesfully!")
    '''

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    resolution = '1min'

    months = {'January' : 1, 'February' : 2, 'March' : 3, 'April' : 4, 'May' : 5, 'June' : 6, 'July' : 7, 'August' : 8, 'September' : 9, 'October' : 10, 'November' : 11, 'December' : 12}
    df_by_month = {}
    df_by_month_avg = {}
    average_powers = {}
    
    # Create a new directory for the results
    parent_dir = r"C:\\Users\\teolhyn\\Desktop\\REALSOLAR\\My Research\\Simulations\\Results"
    directory = str("RW_" + time.strftime("%Y_%m_%d_%H-%M"))
    path = os.path.join(parent_dir, directory)
    os.mkdir(path)

    for i in [mc, mc2, mc3]:
        for month in months:

            df = pd.DataFrame(i.results.ac, columns=['Power']) # Creates DataFrame from results
            df_by_month[month] = df[df.index.month == months[month]] # Splits DataFrames by month to dictionary, where keys are 'df_[monthname]'
            # Calculate average day profile of months and save them to dictionary
            df_by_month_avg[month] = df_by_month[month].set_axis(df_by_month[month].index + pd.offsets.MonthEnd(0)).resample(resolution)['Power'].mean()
            df_by_month_avg[month].index = pd.to_datetime(df_by_month_avg[month].index).strftime('%H:%M') # Format datetimes to HH:MM
            
            # File saving
            if i == mc:
                s = 'E'
            if i == mc2:
                s = 'S'
            if i == mc3:
                s = 'W'
            path_child = str(str(months[month]) + s + month + "_production.csv")
            path_new = os.path.join(path, path_child) # Path for whole months production

            path_child_avg = str(str(months[month]) + s + month + "_avg_production.csv")
            path_new_avg = os.path.join(path, path_child_avg) # Path for avg day production

            df_by_month[month].to_csv(path_new)
            df_by_month_avg[month].to_csv(path_new_avg)