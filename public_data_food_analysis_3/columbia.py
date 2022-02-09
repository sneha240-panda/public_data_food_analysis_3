# AUTOGENERATED! DO NOT EDIT! File to edit: 01_columbia.ipynb (unless otherwise specified).

__all__ = ['read_logging_data', 'get_phase_duration', 'caloric_entries', 'mean_daily_eating_duration',
           'std_daily_eating_duration', 'earliest_entry', 'find_percentiles', 'logging_day_counts',
           'good_lwa_day_counts', 'make_table']

# Cell
import glob
import pandas as pd
import numpy as np
import datetime
import public_data_food_analysis_3.core as pdfa

# Cell
def read_logging_data(folder_path):
    """
    @param folder_path: folder name that contains the participants' data.
    read all participants data in the data folder into a data frame. The files should be csv format start with yrt921 and contain
    _food_data in the middle
    """
    data_lst = glob.glob('{}/yrt*_food_data*.csv'.format(folder_path))
    dfs = []
    for x in data_lst:
        dfs.append(pd.read_csv(x))
    df = pd.concat(dfs)
    return df.reset_index(drop=True)


# Cell
def get_phase_duration(df):
    """
    @params df: information dataframe that contains columns: Start_Day, End_day
    Calculate the studys days for each phase, include the start and end date.
    """
    df['phase_duration'] = df['End_day'] - df['Start_Day']+ pd.Timedelta("1 days")
    return df

# Cell
def caloric_entries(df, start_date='not_defined', end_date='not_defined'):
    """
    Description:\n
        This is a function that counts the number of food or beverage loggings.

    Input:\n
        - df : food_logging data.
        - start_date : start date of the period of counting.
        - end_date : end date of the period of counting.

    Output:\n
        - a float representing the number of caloric entries.

    Requirement:\n
        - 'date' column existed in the df.
    """
    if pd.isnull(start_date) or pd.isnull(end_date):
        return np.nan
    if start_date=='not_defined':
        start_date = df['date'].min()
    if end_date=='not_defined':
        end_date = df['date'].max()
    df = df[(df['date']>=start_date) & (df['date']<=end_date)]
    return df[df['food_type'].isin(['f','b'])].shape[0]

# Cell
def mean_daily_eating_duration(df, col, start_date=None, end_date=None):
    """
    Description:\n
        This is a function that calculates the mean daily eating window, which is defined as the duration of first and last caloric intake.

    Input:\n
        - df : food_logging data.
        - col : contains the float time data for each logging.
        - start_date : start date of the period of calculation.
        - end_date : end date of the period of calculation.

    Output:\n
        - a float representing the mean daily eating window.

    Requirement:\n
        - 'date' column existed in the df.
        - float time is calculated.
    """
    if pd.isnull(start_date) or pd.isnull(end_date):
        return np.nan
    if start_date==None:
        start_date = df['date'].min()
    if end_date==None:
        end_date = df['date'].max()
    df = df[(df['date']>=start_date) & (df['date']<=end_date)]
    df = df[df['food_type'].isin(['f','b'])]
    breakfast_time = df.groupby('date').agg(min)
    dinner_time = df.groupby('date').agg(max)
    return (dinner_time[col]-breakfast_time[col]).mean()

# Cell
def std_daily_eating_duration(df, col, start_date=None, end_date=None):
    """
    Description:\n
        This function calculates the standard deviation of daily eating window, which is defined as the duration between the first and last caloric intake.

    Input:\n
        - df : food_logging data.
        - col : contains the float time data for each logging.
        - start_date : start date of the period of calculation.
        - end_date : end date of the period of calculation.

    Output:\n
        - a float representing the standard deviation of daily eating window.

    Requirement:\n
        - 'date' column existed in the df.
        - float time is calculated.
    """
    if pd.isnull(start_date) or pd.isnull(end_date):
        return np.nan
    if start_date==None:
        start_date = df['date'].min()
    if end_date==None:
        end_date = df['date'].max()
    df = df[(df['date']>=start_date) & (df['date']<=end_date)]
    df = df[df['food_type'].isin(['f','b'])]
    breakfast_time = df.groupby('date').agg(min)
    dinner_time = df.groupby('date').agg(max)

    return (dinner_time[col]-breakfast_time[col]).std()

# Cell
def earliest_entry(df,col, start_date=None, end_date=None):
    """
    Description:\n
        This function calculates the earliest first calorie on any day in the study period.
    Input:\n
        - df : food_logging data.
        - col : contains information of logging time in float.
        - start_date : start date of the period of calculation.
        - end_date : end date of the period of calculation.

    Output:\n
        - the earliest caloric time in float on any day in the study period.

    Requirement:\n
        - 'date' column existed in the df.

    """
    # if start_date or end_date is missing, return nan
    if pd.isnull(start_date) or pd.isnull(end_date):
        return np.nan
    # if there is no input on start_date or end_date, use earliest date and latest date
    if start_date==None:
        start_date = df['date'].min()
    if end_date==None:
        end_date = df['date'].max()

    df = df[(df['date']>=start_date) & (df['date']<=end_date)]

    return df[col].min()

# Cell
def find_percentiles(df, col, percentiles, start_date=None, end_date=None):
    """
    Description:\n
        This function calculates the percentiles of the given column with specified percentiles.
    Input:\n
        - df : food_logging data.
        - col : contains information of logging time in float.
        - start_date : start date of the period of calculation.
        - end_date : end date of the period of calculation.

    Output:\n
        - a pd series data contains information of percentiles and also basic descriptive information such as count, mean, std, etc.

    Requirement:\n
        - 'date' column existed in the df.
        - float time is calculated.
    """
    # if start_date or end_date is missing, return nan
    if pd.isnull(start_date) or pd.isnull(end_date):
        return np.nan
    # if there is no input on start_date or end_date, use earliest date and latest date
    if start_date==None:
        start_date = df['date'].min()
    if end_date==None:
        end_date = df['date'].max()

    df = df[(df['date']>=start_date) & (df['date']<=end_date)]
    return df[col].describe(percentiles=percentiles)

# Cell
def logging_day_counts(df, start_date=None, end_date=None):
    """
    Description:\n
        This function calculates the number of days that contains any loggings.
    Input:\n
        - df : food_logging data.
        - start_date : start date of the period of calculation.
        - end_date : end date of the period of calculation.

    Output:\n
        - an integer that represents the number of logging days.

    Requirement:\n
        - 'date' column existed in the df.
    """
    # if start_date or end_date is missing, return nan
    if pd.isnull(start_date) or pd.isnull(end_date):
        return np.nan
    # if there is no input on start_date or end_date, use earliest date and latest date
    if start_date==None:
        start_date = df['date'].min()
    if end_date==None:
        end_date = df['date'].max()

    df = df[(df['date']>=start_date) & (df['date']<=end_date)]

    return df.date.nunique()

# Cell
def good_lwa_day_counts(df, window_start, window_end, min_log_num=2, min_seperation=5, buffer_time= '15 minutes',h=4, start_date=None, end_date=None):
    """
    Description:\n
        This function calculates the number of good logging days, good window days, outside window days and adherent days.
    Input:\n
        - df: food_logging data.
        - window_start: start time of the restriction window
        - window_end: end time of the restriction window
        - min_log_num: minimum number of loggings to qualify a day as a good logging day
        - min_seperation: minimum period of separation between earliest and latest loggings to qualify a day as a good logging day
        - buffer_time: wiggle room for to be added/subtracted on the ends of windows.
        - h: hours to be pushed back
        - start_date : start date of the period of calculation.
        - end_date : end date of the period of calculation.

    Output:\n
        - a list that represents the number of good logging days, good window days, outside window days and adherent days.

    Requirement:\n
        - 'date' column existed in the df.
        - float time is calculated.
    """
    # if start_date or end_date is missing, return nan
    if pd.isnull(start_date) or pd.isnull(end_date):
        return [np.nan,np.nan,np.nan,np.nan]
    # if there is no input on start_date or end_date, use earliest date and latest date
    if start_date==None:
        start_date = df['date'].min()
    if end_date==None:
        end_date = df['date'].max()

    # helper function to determine a good logging
    def good_logging(float_time_series):
        if len(float_time_series.values) >= min_log_num and (max(float_time_series.values) - min(float_time_series.values)) >= min_seperation:
            return True
        else:
            return False

    df = df[(df['date']>=start_date) & (df['date']<=end_date)]
    df = df[df['food_type'].isin(['f','b'])]
    df['original_logtime'] = df['original_logtime'].dt.tz_localize(None)

    buffer_time = pd.Timedelta(buffer_time).total_seconds()/3600.

    in_window_count = []
    daily_count = []
    good_logging_count = []
    for aday in df['date'].sort_values(ascending = True).unique():
        window_start_daily = window_start.hour+window_start.minute/60- buffer_time
        window_end_daily = window_end.hour+window_end.minute/60 + buffer_time
        tmp = df[df['date']==aday]
        if (window_start == datetime.time(0,0)) and (window_end == datetime.time(23,59)):
            in_window_count.append(tmp[(tmp['float_time']>=window_start_daily+h) & (tmp['float_time']<=window_end_daily+h)].shape[0])
        else:
            in_window_count.append(tmp[(tmp['float_time']>=window_start_daily) & (tmp['float_time']<=window_end_daily)].shape[0])
        daily_count.append(df[df['date']==aday].shape[0])
        good_logging_count.append(good_logging(df[df['date']==aday].float_time))

    in_window_count = np.array(in_window_count)
    daily_count = np.array(daily_count)
    good_logging_count = np.array(good_logging_count)

    good_window_days = (in_window_count==daily_count).sum()
    outside_window_days = in_window_count.size - good_window_days
    good_logging_days = good_logging_count.sum()
    adherent_days = (good_logging_count & (in_window_count==daily_count)).sum()

    rows = [good_logging_days, good_window_days, outside_window_days, adherent_days]

    return rows


# Cell
def make_table(food_data, ref_tbl, min_log_num=2, min_seperation=5, buffer_time= '15 minutes', h=4, start_date=None, end_date=None):
    """
    Description:\n
        This is a comprehensive function that performs all of the functionalities needed.

    Input:\n
        - food_data : food_logging data.
        - ref_tbl : table that contains window information and study phase information for each participant.
        - h : hour manipulation so that the starting and ending time for each day is more realistic.

    Output:\n
        - df : dataframe that has all the variables needed and has the same row number as the ref_tbl.

    Assumption:\n
        food_data is already read from all files in the directories into a dataframe

    """
    df = food_data.copy()
    # preprocess to get the date and float_time column
    df['original_logtime'] = pd.to_datetime(df['original_logtime'])
    df['date'] = pdfa.find_date(df, 'original_logtime', h)
    df['float_time'] = pdfa.find_float_time(df, 'original_logtime', h)

    # preprocess to make the window restriction to be correct
    eating_window_start_float = []
    eating_window_end_float = []
    for index, row in ref_tbl.iterrows():
        try:
            eating_window_start_float.append(row['Eating_Window_Start'].hour+row['Eating_Window_Start'].minute/60+h)
            eating_window_end_float.append(row['Eating_Window_End'].hour+row['Eating_Window_End'].minute/60+h)
        except:
            eating_window_start_float.append(np.nan)
            eating_window_end_float.append(np.nan)

    ref_tbl['eating_window_start_float_time'] = eating_window_start_float
    ref_tbl['eating_window_end_float_time'] = eating_window_end_float

    # get study phase duration
    result = get_phase_duration(ref_tbl)

    # loop through each row and get 'caloric_entries', 'mean_daily_eating_window', 'std_daily_eating_window', 'eariliest_entry', 'logging_day_counts',
    # and 'good_logging_days', 'good_window_days', 'outside_window_days' and 'adherent_days'
    matrix = []
    for index, row in ref_tbl.iterrows():
        id_ = row['mCC_ID']
        rows = []
        rows.append(caloric_entries(df[df['PID']==id_], row['Start_Day'],row['End_day']))
        rows.append(mean_daily_eating_duration(df[df['PID']==id_],'float_time', row['Start_Day'],row['End_day']))
        rows.append(std_daily_eating_duration(df[df['PID']==id_],'float_time', row['Start_Day'],row['End_day']))
        rows.append(earliest_entry(df[df['PID']==id_],'float_time', row['Start_Day'],row['End_day']))
        rows.append(logging_day_counts(df[df['PID']==id_], row['Start_Day'],row['End_day']))
        for x in good_lwa_day_counts(df[df['PID']==id_]
                                           , window_start=row['Eating_Window_Start']
                                           , window_end = row['Eating_Window_End']
                                           , min_log_num=min_log_num
                                           , min_seperation=min_seperation
                                           , buffer_time= buffer_time
                                           , start_date=row['Start_Day']
                                           , end_date=row['End_day']
                                            , h=h):
                                     rows.append(x)
        matrix.append(rows)

    # create a temp dataframe
    tmp = pd.DataFrame(matrix, columns = ['caloric_entries', 'mean_daily_eating_window', 'std_daily_eating_window', 'earliest_entry', 'logging_day_counts'\
                                         ,'good_logging_days', 'good_window_days', 'outside_window_days', 'adherent_days'])

    # concat these two tables
    returned = pd.concat([ref_tbl, tmp], axis=1)

    # loop through each row and get 2.5%, 97.5%, duration mid 95% column
    column_025 = []
    column_975 = []
    for index, row in ref_tbl.iterrows():
        id_ = row['mCC_ID']
        series = find_percentiles(df[df['PID']==id_], 'float_time', [.025, 0.975], row['Start_Day'], row['End_day'])
        try:
            column_025.append(series.loc['2.5%'])
        except:
            column_025.append(np.nan)
        try:
            column_975.append(series.loc['97.5%'])
        except:
            column_975.append(np.nan)
    returned['2.5%'] = column_025
    returned['97.5%'] = column_975
    returned['duration mid 95%'] = returned['97.5%'] - returned['2.5%']


    # calculate percentage for
    for x in returned.columns:
        if x in ['logging_day_counts','good_logging_days', 'good_window_days', 'outside_window_days', 'adherent_days']:
            returned['%_'+x] = returned[x]/returned['phase_duration'].dt.days


    returned = returned[['mCC_ID', 'Participant_Study_ID', 'Study Phase',
       'Intervention group (TRE or HABIT)', 'Start_Day', 'End_day',
       'Eating_Window_Start','Eating_Window_End', 'phase_duration',
       'caloric_entries', 'mean_daily_eating_window', 'std_daily_eating_window',
       'earliest_entry', '2.5%', '97.5%', 'duration mid 95%',
       'logging_day_counts', '%_logging_day_counts', 'good_logging_days',
        '%_good_logging_days','good_window_days', '%_good_window_days',
        'outside_window_days','%_outside_window_days', 'adherent_days',
       '%_adherent_days']]


    return returned

