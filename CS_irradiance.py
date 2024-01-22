import pandas as pd
import numpy as np
from tqdm import tqdm
import time

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
    times = pd.date_range('2021-06-01', '2021-06-30', freq='1min', tz='Europe/Helsinki')
    location = Location(60.45, 22.29, 'Europe/Helsinki', 50, name='Turku')
    cs = location.get_clearsky(times) # Get clear sky data
    solar_position = location.get_solarposition(times)
    print("Initializing complete!")
    print(cs)
    print("Modelling system 1")
    system = PVSystem(surface_tilt=90, surface_azimuth=90,
                        module_parameters=sandia_module,
                        inverter_parameters=cec_inverter,
                        temperature_model_parameters=temperature_model_parameters)

    result = system.get_irradiance(solar_zenith=solar_position['zenith'], solar_azimuth=solar_position['azimuth'], 
                                        dni=cs['dni'], ghi=cs['ghi'], dhi=cs['dhi'], dni_extra=None,
                                        airmass=None, albedo=None, model='haydavies')
    print("Modelling system 1 - Complete!")

    print("Modelling system 2")
    system2 = PVSystem(surface_tilt=30, surface_azimuth=180,
                        module_parameters=sandia_module,
                        inverter_parameters=cec_inverter,
                        temperature_model_parameters=temperature_model_parameters)

    result2 = system2.get_irradiance(solar_zenith=solar_position['zenith'], solar_azimuth=solar_position['azimuth'], 
                                        dni=cs['dni'], ghi=cs['ghi'], dhi=cs['dhi'], dni_extra=None,
                                        airmass=None, albedo=None, model='haydavies')
    print("Modelling system 2 - Complete!")

    print("Modelling system 3")
    system3 = PVSystem(surface_tilt=90, surface_azimuth=270,
                        module_parameters=sandia_module,
                        inverter_parameters=cec_inverter,
                        temperature_model_parameters=temperature_model_parameters)

    result3 = system3.get_irradiance(solar_zenith=solar_position['zenith'], solar_azimuth=solar_position['azimuth'], 
                                        dni=cs['dni'], ghi=cs['ghi'], dhi=cs['dhi'], dni_extra=None,
                                        airmass=None, albedo=None, model='haydavies')
    print("Modelling system 3 - Complete!")

    print('System 1: Tilt = 90, Azimuth = 90')
    print(result)
    print('System 2: Tilt = 30, Azimuth = 180')
    print(result2)
    print('System 3: Tilt = 90, Azimuth = 270')
    print(result3)

    print("plotting...")
    plt.plot(result['poa_global'], label='POA global East')
    plt.plot(result2['poa_global'], label='POA global South')
    plt.plot(result3['poa_global'], label='POA global West')
    plt.legend()
    plt.show()
    print("Plotting completed!")

    print("Finished.")