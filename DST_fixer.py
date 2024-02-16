import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def dst_fixer(dates, dsv=1):
    """ This function removes dayligth saving times from a datetime time series.
        In case of Finnish data, it returns datetime in UTC+02 (winter time).
        ------------------------------------------------------------------------
        Inputs:
        dates: Time series object with dst. List, Numpy Array or Pandas Series.
                Items are datetime objects.
        dsv: (1 or -1) This parameter defines if the time series object starts
            with summer time or winter time. If time series starts with summer
            time, use 1, if winter time, use -1.
        ------------------------------------------------------------------------
        Returns:
        Numpy Array with removed daylight saving times. Datetimes are datetime
        objects
    """
    # Below datetimes for dst begin and end times. New datetimes can be added
    # if timeseries are from longer time periods.

    b2017 = datetime(2017, 3, 26, 3, 0, 0)
    e2017 = datetime(2017, 10, 29, 4, 0, 0)
    b2018 = datetime(2018, 3, 25, 3, 0, 0)
    e2018 = datetime(2018, 10, 28, 4, 0, 0)
    b2019 = datetime(2019, 3, 31, 3, 0, 0)
    e2019 = datetime(2019, 10, 27, 4, 0, 0)
    b2020 = datetime(2020, 3, 29, 3, 0, 0)
    e2020 = datetime(2020, 10, 25, 4, 0, 0)
    b2021 = datetime(2021, 3, 28, 3, 0, 0)

    times = [b2017, e2017, b2018, e2018, b2019, e2019, b2020, e2020, b2021]
    dates_np = np.array(dates)
    dates_np = np.array(dates_np, dtype='M8[ms]').astype('O')
    i = -1 # Iterator used to track the index of datetime item in a loop

    first = dates_np[0]
    last = dates_np[-1]

    # List for dst begin and end times. Only relevant datetimes are included
    times_use = [time for time in times if (time >= first and time <= last)]

    # Initialize a variable that keeps track of a datetime handled in previous iteration
    last_time = first - timedelta(minutes=1)

    # Initialize a variable that tracks if the next dst datetime is first summer time
    # day in that year
    if dsv == 1:
        first_summer_day = False
    elif dsv == -1:
        first_summer_day = True

    # Loop iterates through datetimes and checks that the date is smaller than the next
    # dst begin or end date and that the datetime is smaller than the previous datetime.
    # When dst begin or end date is met, dsv changes to on (1) or off (-1) and that begin
    # or end date is removed from the list.
    for date in dates_np:
        i += 1
        try:
            if date <= times_use[0] and date >= last_time - timedelta(minutes = 30): # 30 minutes difference is used for timeshifts
                #print(date, '|', times_use[0], '|', dsv)                            # caused by malfunctions
                if dsv == 1:
                    dates_np[i] = date - timedelta(hours=1)
                    if first_summer_day:
                        dates_np[i-1] = dates_np[i-1] - timedelta(hours=1)
                        first_summer_day = False
            else:
                dsv *= -1
                times_use.pop(0)
                if not first_summer_day:
                    first_summer_day = True
        except IndexError:
            break
        last_time = date
    # If last datetimes are in dsv, remove dsv-hours from the rest of the dates
    if dsv == 1:
        dates_np[i-1:] = dates_np[i-1:] - timedelta(hours=1)

    return dates_np



if __name__ == '__main__':
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    #df = pd.read_csv('SolarLab/SolarLab/EM3.csv')
    df = pd.DataFrame({'datetime':['2018-3-25 01:00:00', '2018-3-25 02:30:00', '2018-3-25 02:50:00', '2018-3-25 04:00:00', '2018-3-25 05:00:00']})
    df.datetime = pd.to_datetime(df.datetime)

    f = dst_fixer(df.datetime, dsv=-1)

    print(f)