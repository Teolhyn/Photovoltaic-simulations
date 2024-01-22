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


def solar_model(ghi : int = 1050, 
                dni : int = 1000, 
                dhi : int = 100, 
                temp_air : int = 30, 
                wind_speed : int = 5, 
                surface_azimuth : int = 180, 
                surface_tilt : int = 30, 
                dt = '20170401 1200-0700'):

    temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

    # load some module and inverter specifications
    sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')

    cec_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')

    sandia_module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']

    cec_inverter = cec_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']


    # Create Location object, a Mount object, a PVSystem object, and a ModelChain object
    location = Location(latitude=lat, longitude=lon)

    system = PVSystem(surface_tilt=surface_tilt, surface_azimuth=surface_azimuth,
                      module_parameters=sandia_module,
                      inverter_parameters=cec_inverter,
                      temperature_model_parameters=temperature_model_parameters)
    
    mc = ModelChain(system, location)


    # Weather data
    weather = pd.DataFrame([[ghi, dni, dhi, temp_air, wind_speed]],
                           columns=['ghi', 'dni', 'dhi', 'temp_air', 'wind_speed'],
                           index=[pd.Timestamp(dt)])
    

    # Run the model
    mc.run_model(weather)

    return mc.results.ac

if __name__ == '__main__':

    if use_weather_data:
        
        weather_data = pd.read_csv('IrrData2019_StarkeDFC_230704.csv')
        power_result = []
        timepoints = []

        for row in tqdm(weather_data.to_dict(orient='records')):
            loop_start_time = time.time()
            ac = (solar_model(ghi=row['GHI'], dni=row['DNI'], dhi=row['DHI'], temp_air=row['Tamb'],
                            wind_speed=row['WS'], surface_azimuth=sur_az, surface_tilt=sur_tilt, dt=row['dt']))
            
            if ac.iloc[0] < 0:
                ac.iloc[0] = 0

            power_result.append(ac.iloc[0])
            timepoints.append(ac.keys()[0])
            loop_end_time = time.time()
            # print("Loop took", (loop_end_time - loop_start_time), "s to complete!")

        size = 3
        plt.scatter(timepoints, power_result, label='AC Power', s=size)
        plt.scatter(timepoints, weather_data.loc[:len(timepoints)-1,'GHI'], label='GHI', s=size)
        plt.scatter(timepoints, weather_data.loc[:len(timepoints)-1,'DNI'], label='DNI', s=size)
        plt.scatter(timepoints, weather_data.loc[:len(timepoints)-1,'DHI'], label='DHI', s=size)
        plt.legend(loc='upper left')
        plt.show()

        # Saving data to csv
        file = pd.DataFrame(timepoints, columns=['Timestamp'])
        file.insert(1,"AC Power (W)", power_result)

        file = file.round({'AC Power (W)' : 2})

        file.to_csv(path_or_buf="Simulation_result_Az"+str(sur_az)+"Tilt"+str(sur_tilt)+".csv",mode='w', index=False, decimal='.')
        print("Files saved succesfully!")

    if use_clear_sky:
        
        times = pd.date_range('2021-01-01', '2021-12-31', freq='1min', tz='Europe/Helsinki')
        location = Location(60.45, 22.29, 'Europe/Helsinki', 50, name='Turku')
        cs = location.get_clearsky(times) # Get clear sky data
        solar_position = location.get_solarposition(times)


        system = PVSystem(surface_tilt=90, surface_azimuth=90,
                          module_parameters=sandia_module,
                          inverter_parameters=cec_inverter,
                          temperature_model_parameters=temperature_model_parameters)

        result = system.get_irradiance(solar_zenith=solar_position['zenith'], solar_azimuth=solar_position['azimuth'], 
                                         dni=cs['dni'], ghi=cs['ghi'], dhi=cs['dhi'], dni_extra=None,
                                         airmass=None, albedo=None, model='haydavies')
        

        system2 = PVSystem(surface_tilt=30, surface_azimuth=180,
                          module_parameters=sandia_module,
                          inverter_parameters=cec_inverter,
                          temperature_model_parameters=temperature_model_parameters)

        result2 = system2.get_irradiance(solar_zenith=solar_position['zenith'], solar_azimuth=solar_position['azimuth'], 
                                         dni=cs['dni'], ghi=cs['ghi'], dhi=cs['dhi'], dni_extra=None,
                                         airmass=None, albedo=None, model='haydavies')
        

        system3 = PVSystem(surface_tilt=90, surface_azimuth=270,
                          module_parameters=sandia_module,
                          inverter_parameters=cec_inverter,
                          temperature_model_parameters=temperature_model_parameters)

        result3 = system3.get_irradiance(solar_zenith=solar_position['zenith'], solar_azimuth=solar_position['azimuth'], 
                                         dni=cs['dni'], ghi=cs['ghi'], dhi=cs['dhi'], dni_extra=None,
                                         airmass=None, albedo=None, model='haydavies')
        

        print(result[500:505])
        print(result2[500:505])
        print(result3[500:505])

        plt.plot(result['poa_direct'], label='East')
        plt.plot(result2['poa_direct'], label='South')
        plt.plot(result3['poa_direct'], label='West')
        plt.show()

