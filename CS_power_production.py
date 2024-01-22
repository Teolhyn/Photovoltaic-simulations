import pandas as pd
import numpy as np
from tqdm import tqdm
import time

from scipy import integrate

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# pvlib imports
import pvlib
from pvlib.pvsystem import PVSystem, FixedMount
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS


# Parameters -------------------------------------------------------------------------------------

use_weather_data = False
use_clear_sky = True
sur_az = 180
sur_tilt = 30
tz = 'Etc/GMT+3'
lat = 60.45
lon = 22.29

# ------------------------------------------------------------------------------------------------

# Temporary

# load some module and inverter specifications
sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')

cec_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')

sandia_module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']

cec_inverter = cec_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']

temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

if __name__ == '__main__':
    print("Initializing time arrays and calculating clear sky conditions and solar positions based on location")    
    times = pd.date_range('2021-01-01', '2021-12-31', freq='1min', tz='Etc/GMT-2')
    location = Location(60.45, 22.29, 'Etc/GMT-2', 50, name='Turku')
    cs = location.get_clearsky(times) # Get clear sky data
    solar_position = location.get_solarposition(times)
    print("Initializing complete!")

    print("Modelling system 1")
    system = PVSystem(surface_tilt=90, surface_azimuth=90,
                        module_parameters=sandia_module,
                        inverter_parameters=cec_inverter,
                        temperature_model_parameters=temperature_model_parameters)
    
    mc = ModelChain(system, location)

    mc.run_model(cs)
    print("Modelling system 1 - Complete!")

    print("Modelling system 2")
    system2 = PVSystem(surface_tilt=30, surface_azimuth=180,
                        module_parameters=sandia_module,
                        inverter_parameters=cec_inverter,
                        temperature_model_parameters=temperature_model_parameters)
    
    mc2 = ModelChain(system2, location)

    mc2.run_model(cs)
    print("Modelling system 2 - Complete!")

    print("Modelling system 3")
    system3 = PVSystem(surface_tilt=90, surface_azimuth=270,
                        module_parameters=sandia_module,
                        inverter_parameters=cec_inverter,
                        temperature_model_parameters=temperature_model_parameters)
    
    mc3 = ModelChain(system3, location)

    mc3.run_model(cs)
    print("Modelling system 3 - Complete!")

    print(mc.results.ac)

    '''
    plt.plot(mc.results.ac, label=('Az90,Tilt90'))
    plt.plot(mc2.results.ac, label=('Az180,Tilt30'))
    plt.plot(mc3.results.ac, label=('Az270,Tilt90'))
    plt.legend()
    plt.ylabel("AC Power (W)")
    plt.show()
    '''


# ----------------------------------------------------------------------------

    bifacialpower = 0
    monofacialpower = 0

    resolution = '1min'


    for i in [mc, mc2, mc3]:
        df = pd.DataFrame(i.results.ac, columns=['Power'])

        df_jan = df[df.index.month == 1]
        df_feb = df[df.index.month == 2]
        df_mar = df[df.index.month == 3]
        df_apr = df[df.index.month == 4]
        df_may = df[df.index.month == 5]
        df_jun = df[df.index.month == 6]
        df_jul = df[df.index.month == 7]
        df_aug = df[df.index.month == 8]
        df_sep = df[df.index.month == 9]
        df_oct = df[df.index.month == 10]
        df_nov = df[df.index.month == 11]
        df_dec = df[df.index.month == 12]

        #plt.scatter(df_jan.set_axis(df_jan.index + pd.offsets.MonthEnd(0)).resample('5min')['Power'].mean(), label=('January'))

        df_jan_avg = df_jan.set_axis(df_jan.index + pd.offsets.MonthEnd(0)).resample('1min')['Power'].mean()
        df_feb_avg = df_feb.set_axis(df_feb.index + pd.offsets.MonthEnd(0)).resample('1min')['Power'].mean()
        df_mar_avg = df_mar.set_axis(df_mar.index + pd.offsets.MonthEnd(0)).resample('1min')['Power'].mean()
        df_apr_avg = df_apr.set_axis(df_apr.index + pd.offsets.MonthEnd(0)).resample('1min')['Power'].mean()
        df_may_avg = df_may.set_axis(df_may.index + pd.offsets.MonthEnd(0)).resample('1min')['Power'].mean()
        df_jun_avg = df_jun.set_axis(df_jun.index + pd.offsets.MonthEnd(0)).resample('1min')['Power'].mean()
        df_jul_avg = df_jul.set_axis(df_jul.index + pd.offsets.MonthEnd(0)).resample('1min')['Power'].mean()
        df_aug_avg = df_aug.set_axis(df_aug.index + pd.offsets.MonthEnd(0)).resample('1min')['Power'].mean()
        df_sep_avg = df_sep.set_axis(df_sep.index + pd.offsets.MonthEnd(0)).resample('1min')['Power'].mean()
        df_oct_avg = df_oct.set_axis(df_oct.index + pd.offsets.MonthEnd(0)).resample('1min')['Power'].mean()
        df_nov_avg = df_nov.set_axis(df_nov.index + pd.offsets.MonthEnd(0)).resample('1min')['Power'].mean()
        df_dec_avg = df_dec.set_axis(df_dec.index + pd.offsets.MonthEnd(0)).resample('1min')['Power'].mean()

        df_jan_avg.index = pd.to_datetime(df_jan_avg.index).strftime('%H:%M')
        df_feb_avg.index = pd.to_datetime(df_feb_avg.index).strftime('%H:%M')
        df_mar_avg.index = pd.to_datetime(df_mar_avg.index).strftime('%H:%M')
        df_apr_avg.index = pd.to_datetime(df_apr_avg.index).strftime('%H:%M')
        df_may_avg.index = pd.to_datetime(df_may_avg.index).strftime('%H:%M')
        df_jun_avg.index = pd.to_datetime(df_jun_avg.index).strftime('%H:%M')
        df_jul_avg.index = pd.to_datetime(df_jul_avg.index).strftime('%H:%M')
        df_aug_avg.index = pd.to_datetime(df_aug_avg.index).strftime('%H:%M')
        df_sep_avg.index = pd.to_datetime(df_sep_avg.index).strftime('%H:%M')
        df_oct_avg.index = pd.to_datetime(df_oct_avg.index).strftime('%H:%M')
        df_nov_avg.index = pd.to_datetime(df_nov_avg.index).strftime('%H:%M')
        df_dec_avg.index = pd.to_datetime(df_dec_avg.index).strftime('%H:%M')

        # Calculate total powers for bifacial and south facing monofacial

        if i == mc or i == mc3:
            bifacialpower += integrate.trapezoid(df_jul_avg)
        else:
            monofacialpower += integrate.trapezoid(df_jul_avg)


        #plt.plot(df_jan_avg,  label=('January'))
        #plt.plot(df_feb_avg, label=('February'))
        #plt.plot(df_mar_avg, label=('March'))
        #plt.plot(df_apr_avg, 'g', label=('April'))
        #plt.plot(df_may_avg, 'r', label=('May'))
        #plt.plot(df_jun_avg, 'b', label=('June'))
        plt.plot(df_jul_avg, 'c', label=('July'))
        #plt.plot(df_aug_avg, 'm', label=('August'))
        #plt.plot(df_sep_avg, 'y', label=('September'))
        #plt.plot(df_oct_avg, 'k', label=('October'))
        #plt.plot(df_nov_avg, label=('November'))
        #plt.plot(df_dec_avg, label=('December'))

    #plt.plot(weather['ghi'], label=('GHI'))
    plt.legend()
    plt.xticks(["06:00", "09:00", "12:00", "15:00", "18:00", "21:00"])
    plt.ylabel("AC Power (W)")
    plt.xlabel("Time")
    plt.show()   

    print("Bifacial average power:", bifacialpower/(24*60))
    print("Monofacial average power:", monofacialpower/(24*60))