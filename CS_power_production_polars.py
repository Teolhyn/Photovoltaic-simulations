import polars as pl
from datetime import datetime
import matplotlib.pyplot as plt

# pvlib imports
import pvlib
from pvlib.pvsystem import PVSystem
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS


# Parameters -------------------------------------------------------------------------------------

use_weather_data = False
use_clear_sky = True
sur_az = 180
sur_tilt = 30
tz = 'Etc/GMT-1' # -2 = +2
#lat = 60.45
#lon = 22.29

# ------------------------------------------------------------------------------------------------

# Temporary

# load some module and inverter specifications
sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')

cec_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')

sandia_module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']

cec_inverter = cec_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']

temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

if __name__ == '__main__':
    df_march_bifacial = {}
    df_march_monofacial = {}
    df_june_bifacial = {}
    df_june_monofacial = {}
    df_september_bifacial = {}
    df_september_monofacial = {}
    df_december_bifacial = {}
    df_december_monofacial = {}

    for lat, lon, elev, name, tz in zip([65.02, 60.45, 53.54, 48.13, 44.41, 40.42], [25.56, 22.29, 10.04, 11.55, 8.97, -3.70], [15, 25, 8, 520, 20, 650], ['Oulu', 'Turku', 'Hamburg', 'München', 'Genova', 'Madrid'], ['Etc/GMT-2', 'Etc/GMT-2', 'Etc/GMT-1', 'Etc/GMT-1', 'Etc/GMT-1', 'Etc/GMT-1']):
        print("Initializing time arrays and calculating clear sky conditions and solar positions based on location")    
        times = pl.datetime_range(datetime(2021, 1, 1), datetime(2021, 12, 31), interval='1m', time_zone=tz, eager=True)
        print(times)
        location = Location(lat, lon, tz, elev, name=name)
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

        #print(mc.results.ac)

        '''
        plt.plot(mc.results.ac, label=('Az90,Tilt90'))
        plt.plot(mc2.results.ac, label=('Az180,Tilt30'))
        plt.plot(mc3.results.ac, label=('Az270,Tilt90'))
        plt.legend()
        plt.ylabel("AC Power (W)")
        plt.show()
        '''


    # ----------------------------------------------------------------------------
        resolution = '1min'

        months = {'January' : 1, 'February' : 2, 'March' : 3, 'April' : 4, 'May' : 5, 'June' : 6, 'July' : 7, 'August' : 8, 'September' : 9, 'October' : 10, 'November' : 11, 'December' : 12}
        df_by_month = {}
        df_by_month_avg = {}
        average_powers = {}

        monofacial_avgs = {}
        bifacial_avgs = {}
        
        '''
        # Create a new directory for the results
        parent_dir = r"C:\\Users\\teolhyn\\Desktop\\REALSOLAR\\My Research\\Simulations\\Results"
        directory = str("CS_Madrid_" + time.strftime("%Y_%m_%d_%H-%M"))
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        '''


        for i in [mc, mc2, mc3]:
            for month in months:

                df = pl.DataFrame(i.results.ac, columns=['Power']) # Creates DataFrame from results
                print(df)
                df_by_month[month] = df[df.index.month == months[month]] # Splits DataFrames by month to dictionary, where keys are 'df_[monthname]'
                # Calculate average day profile of months and save them to dictionary
                df_by_month_avg[month] = df_by_month[month].set_axis(df_by_month[month].index + pl.offsets.MonthEnd(0)).resample(resolution)['Power'].mean()
                df_by_month_avg[month].index = pl.to_datetime(df_by_month_avg[month].index).strftime('%H:%M') # Format datetimes to HH:MM
                
                '''
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
                '''
            
            if (i == mc or i == mc3):
                bifacial_avgs = {k: bifacial_avgs.get(k, 0) + df_by_month_avg.get(k, 0) for k in set(bifacial_avgs) | set(df_by_month_avg)} # Sums and merges the east and west facing panels to one TODO: add bifaciality factor as now both sides are 'main' side. I think it should be done before merging.
            else:
                monofacial_avgs = {k: monofacial_avgs.get(k, 0) + df_by_month_avg.get(k, 0) for k in set(monofacial_avgs) | set(df_by_month_avg)}

        df_december_bifacial[name] = bifacial_avgs['December']
        df_december_monofacial[name] = monofacial_avgs['December']

    for name, colour in zip(['Oulu', 'Turku', 'Hamburg', 'München', 'Genova', 'Madrid'], ['r', 'g', 'b', 'c', 'm', 'y']):
        plt.plot(df_december_bifacial[name], colour, label=name)
        plt.plot(df_december_monofacial[name], colour)
    
    plt.xticks(["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"])
    plt.xlabel('Time')
    plt.ylabel('AC Power (W)')
    plt.title('Average power profile in December in clear sky conditions')
    plt.legend()
    plt.show()