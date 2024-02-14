import matplotlib.pyplot as plt


def get_monthly_profiles(data_input, years, var_names):
    """
    Function for grouping data to hours and months.

    Inputs:
        data_input: Pandas dataframe object with datetimeindex in hourly resolution
        years: List containing years from which data will be used. 
               If many years are given, an average over all years are plotted
        var_names: List of column names of data_input that will be included in the aggregation

    Output:
        hourly_mean_data: 2D numpy array (288 x number of input variables) containing hourly values over all the months 
        var_names: names of the columns of the input data that are used
    """

    data_by_year = dict()
    for year in years:
        data_y = data_input[data_input.index.year == year]
        data_by_month = dict()
        for month in data_y.index.month.unique():
            data = data_y[data_y.index.month == month]
            data_by_month[month] = data.groupby(data.index.hour)[var_names].mean()    
        data_by_year[year] = data_by_month
    data_all = []
    for year_no, year in data_by_year.items():
        data_for_year = []
        for month in year.values():
            data_for_year = data_for_year + list(month.values)
        data_all.append(data_for_year)
    
    hourly_mean_data = np.array(data_all).mean(axis=0)
    return hourly_mean_data, var_names


def plot_monthly_profiles(ax, fig, data_input, years, var_names, offset=9, offsety_scale=1, colors=[]):
    """
    Function for plotting the average daily profiles.

    Inputs:
        ax: Matplotlib Axes object in which the data is plotted
        fig: Matplotlib Figure object
        data_input: Pandas dataframe object with datetimeindex in hourly resolution
        years: List containing years from which data will be used. 
               If many years are given, an average over all years are plotted
        var_names: List of column names of data_input that will be included in the aggregation
        offset: A float value for changing the x-position the month labels
        offsety_scale: A float value for changing the y-position the month labels
        colors: List containing colors for each variable

    Output:
        ax: Matplotlib Axes object where the data was plotted
    """

    # Get the monthly data and variable names
    data, var_names = get_monthly_profiles(data_input, years, var_names)

    # Iterate through every variable in the input data
    for i in range(data.shape[1]):
        if len(colors) > 0:
            ax.plot(data[:, i], label=var_names[i], c=colors[i])
        else:
            ax.plot(data[:, i], label=var_names[i])

    # Plot vertical lines separating each month
    ylims = ax.get_ylim()
    ax.vlines(np.arange(0, 24*12, 24), ylims[0], ylims[1], colors='black', alpha=0.3, linewidth=0.4)

    # Set xlabels (hours)
    xticks = list(range(0,12*24,8))
    ax.set_xticks(xticks)
    ax.set_xticklabels((list(range(0,24))*12)[::8], fontsize=7, rotation=90)
    ax.tick_params(axis='x', length=2)

    ax.legend(loc='upper right', ncol=data.shape[1])

    # Add months to figure
    #months = ['Tammi', 'Helmi', 'Maalis', 'Huhti', 'Touko', 'Kesä', 'Heinä', 'Elo', 'Syys', 'Loka', 'Marras', 'Joulu']
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Position month labels to data. Use offset inputs to fine tune the text positions.
    y_ran = ax.get_ylim()
    for i in range(len(months)):
        y_offset = y_ran[0] - (y_ran[1]-y_ran[0])/8*offsety_scale
        ax.text(xticks[::3][i]+offset, y_offset, months[i])

    plt.tight_layout()

    return ax


def plot_monthly_profiles_windowed(data_input, years, var_names, offset=9, offsety_scale=0, colors=[]):
    """
    Function for plotting the average daily profiles as a windowed figure.

    Inputs:
        data_input: Pandas dataframe object with datetimeindex in hourly resolution
        years: List containing years from which data will be used. 
               If many years are given, an average over all years are plotted
        var_names: List of column names of data_input that will be included in the aggregation
        offset: A float value for changing the x-position the month labels
        offsety_scale: A float value for changing the y-position the month labels
        colors: List containing colors for each variable

    Output:
        ax: Matplotlib Axes object where the data was plotted
        fig: Matplotlib Figure object
    """

    # Get the monthly data and variable names
    data, var_names = get_monthly_profiles(data_input, years, var_names)
    data_windowed = []

    for i in range(12):
        if i > 0:
            data_windowed.append(data[i*24-1:i*24+24,:])
        else:    
            data_windowed.append(data[i*24:i*24+24,:])

    # Plot profiles
    plt.rc('font', size=10)
    figsize = (2244/300, 2000/300) # In pixels
    
    fig, ax = plt.subplots(3,4,figsize=figsize, sharex=True, sharey=True, gridspec_kw = {'wspace':0, 'hspace':.1})
    #months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    xticks = list(range(0,12*24,4))

    j = 0
    for a in [ax[0,0], ax[0,1], ax[0,2], ax[0,3], ax[1,0], ax[1,1], ax[1,2], ax[1,3], ax[2,0], ax[2,1], ax[2,2], ax[2,3]]:
        d = data_windowed[j]
        a.set_xticks(xticks)
        a.set_xticklabels((list(range(0,24))*12)[::4], fontsize=7, rotation=0)

        j += 1
        for i in range(0,d.shape[1]):
            a.plot(d[:, i], label=var_names[i]
                    , c=colors[i]
                    )

    ax[0,1].legend(loc='lower center', ncol=data.shape[1], bbox_to_anchor=(1,1))
    plt.tight_layout()

    return ax, fig


if __name__ == "__main__":
    # Demonstration

    import pandas as pd
    import numpy as np
    from math import pi

    daterange = pd.date_range(start='1/1/2019', end='1/1/2021', freq='1h')
    x1 = np.sin(np.arange(len(daterange))*pi/12)+(np.arange(len(daterange))/10000)**2
    x2 = np.cos(np.arange(len(daterange))*pi/12)+(np.arange(len(daterange))/10000)**2
    data = pd.DataFrame(data=np.array([x1, x2]).T, index=daterange, columns=['sin', 'cos'])
    
    fig, ax = plt.subplots(3, 1, figsize=(10,10))

    ax[0] = plot_monthly_profiles(ax=ax[0], fig=fig, data_input=data, years=[2019], var_names=['sin'])
    ax[1] = plot_monthly_profiles(ax=ax[1], fig=fig, data_input=data, years=[2020], var_names=['cos'])
    ax[2] = plot_monthly_profiles(ax=ax[2], fig=fig, data_input=data, years=[2019, 2020], var_names=['sin', 'cos'])
    plt.show()

    fig, ax = plot_monthly_profiles_windowed(data_input=data, years=[2019], var_names=['sin', 'cos'], colors=['red', 'blue'])
    plt.show()

