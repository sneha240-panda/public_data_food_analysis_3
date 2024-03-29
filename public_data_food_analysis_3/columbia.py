# AUTOGENERATED! DO NOT EDIT! File to edit: 01_columbia.ipynb (unless otherwise specified).

__all__ = ['read_logging_data', 'get_phase_duration', 'caloric_entries', 'mean_daily_eating_duration',
           'std_daily_eating_duration', 'earliest_entry', 'find_percentiles', 'logging_day_counts',
           'good_lwa_day_counts', 'find_missing_logging_days', 'make_table']

# Cell
import glob
import pandas as pd
import numpy as np
import datetime
import public_data_food_analysis_3.core as pdfa

# Cell
def read_logging_data(folder_path):
    """
    Description:\n
        This function reads all csv files in the folder_path folder into one dataframe. The files should be csv format and the name of each file should start with yrt and contain
    _food_data in the middle.

    Input:\n
        - folder_path(string) : path to the folder that contain the data.

    Output:\n
        - a dataframe contains all the csv files in the folder given.

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
    Description:\n
        This is a function that calculates the studys days for each phase, include the start and end date.

    Input:\n
        - df(pandas df) : information dataframe that contains columns: Start_Day, End_day

    Output:\n
        - a dataframe contains the phase_duration column.

    Requirement:\n
        - 'Start_day' and 'End_day' column existed in the df.
    """
    df['phase_duration'] = df['End_day'] - df['Start_Day']+ pd.Timedelta("1 days")
    return df

# Cell
def caloric_entries(df, start_date='not_defined', end_date='not_defined'):
    """
    Description:\n
        This is a function that counts the number of food or beverage loggings.

    Input:\n
        - df(pandas df) : food_logging data.
        - start_date(datetime.date object) : start date of the period of counting. If not defined, it will be automatically set to be the earliest date in df.
        - end_date(datetime.date object) : end date of the period of counting. If not defined, it will be automatically set to be the latest date in df.

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
def mean_daily_eating_duration(df, col, start_date='not_defined', end_date='not_defined'):
    """
    Description:\n
        This is a function that calculates the mean daily eating window, which is defined as the duration of first and last caloric intake.

    Input:\n
        - df(pandas df) : food_logging data.
        - col(column existed in df, string) : contains the float time data for each logging.
        - start_date(datetime.date object) : start date of the period of calculation. If not defined, it will be automatically set to be the earliest date in df.
        - end_date(datetime.date object) : end date of the period of calculation. If not defined, it will be automatically set to be the latest date in df.

    Output:\n
        - a float representing the mean daily eating window.

    Requirement:\n
        - 'date' column existed in the df.
        - float time is calculated.
    """
    if pd.isnull(start_date) or pd.isnull(end_date):
        return np.nan
    if start_date=='not_defined':
        start_date = df['date'].min()
    if end_date=='not_defined':
        end_date = df['date'].max()
    df = df[(df['date']>=start_date) & (df['date']<=end_date)]
    df = df[df['food_type'].isin(['f','b'])]
    breakfast_time = df.groupby('date').agg(min)
    dinner_time = df.groupby('date').agg(max)
    return (dinner_time[col]-breakfast_time[col]).mean()

# Cell
def std_daily_eating_duration(df, col, start_date='not_defined', end_date='not_defined'):
    """
    Description:\n
        This function calculates the standard deviation of daily eating window, which is defined as the duration between the first and last caloric intake.

    Input:\n
        - df(pandas df) : food_logging data.
        - col(column existed in df, string) : contains the float time data for each logging.
        - start_date(datetime.date object) : start date of the period of calculation. If not defined, it will be automatically set to be the earliest date in df.
        - end_date(datetime.date object) : end date of the period of calculation. If not defined, it will be automatically set to be the latest date in df.

    Output:\n
        - a float representing the standard deviation of daily eating window.

    Requirement:\n
        - 'date' column existed in the df.
        - float time is calculated.
    """
    if pd.isnull(start_date) or pd.isnull(end_date):
        return np.nan
    if start_date=='not_defined':
        start_date = df['date'].min()
    if end_date=='not_defined':
        end_date = df['date'].max()
    df = df[(df['date']>=start_date) & (df['date']<=end_date)]
    df = df[df['food_type'].isin(['f','b'])]
    breakfast_time = df.groupby('date').agg(min)
    dinner_time = df.groupby('date').agg(max)

    return (dinner_time[col]-breakfast_time[col]).std()

# Cell
def earliest_entry(df,col, start_date='not_defined', end_date='not_defined'):
    """
    Description:\n
        This function calculates the earliest first calorie on any day in the study period.
    Input:\n
        - df(pandas df) : food_logging data.
        - col(column existed in df, string) : contains information of logging time in float.
        - start_date(datetime.date object) : start date of the period of calculation. If not defined, it will be automatically set to be the earliest date in df.
        - end_date(datetime.date object) : end date of the period of calculation. If not defined, it will be automatically set to be the latest date in df.

    Output:\n
        - the earliest caloric time in float on any day in the study period.

    Requirement:\n
        - 'date' column existed in the df.

    """
    # if start_date or end_date is missing, return nan
    if pd.isnull(start_date) or pd.isnull(end_date):
        return np.nan
    # if there is no input on start_date or end_date, use earliest date and latest date
    if start_date=='not_defined':
        start_date = df['date'].min()
    if end_date=='not_defined':
        end_date = df['date'].max()

    df = df[(df['date']>=start_date) & (df['date']<=end_date)]

    return df[col].min()

# Cell
def find_percentiles(df, col, percentiles, start_date='not_defined', end_date='not_defined'):
    """
    Description:\n
        This function calculates the percentiles of the given column with specified percentiles.
    Input:\n
        - df(pandas df) : food_logging data.
        - col(column existed in df, string) : contains information of logging time in float.
        - start_date(datatime.date object) : start date of the period of calculation. If not defined, it will be automatically set to be the earliest date in df.
        - end_date(datetime.date object) : end date of the period of calculation. If not defined, it will be automatically set to be the latest date in df.

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
    if start_date=='not_defined':
        start_date = df['date'].min()
    if end_date=='not_defined':
        end_date = df['date'].max()

    df = df[(df['date']>=start_date) & (df['date']<=end_date)]
    return df[col].describe(percentiles=percentiles)

# Cell
def logging_day_counts(df, start_date='not_defined', end_date='not_defined'):
    """
    Description:\n
        This function calculates the number of days that contains any loggings.
    Input:\n
        - df : food_logging data.
        - start_date : start date of the period of calculation. If not defined, it will be automatically set to be the earliest date in df.
        - end_date : end date of the period of calculation. If not defined, it will be automatically set to be the latest date in df.

    Output:\n
        - an integer that represents the number of logging days.

    Requirement:\n
        - 'date' column existed in the df.
    """
    # if start_date or end_date is missing, return nan
    if pd.isnull(start_date) or pd.isnull(end_date):
        return np.nan
    # if there is no input on start_date or end_date, use earliest date and latest date
    if start_date=='not_defined':
        start_date = df['date'].min()
    if end_date=='not_defined':
        end_date = df['date'].max()

    df = df[(df['date']>=start_date) & (df['date']<=end_date)]

    return df.date.nunique()

# Cell
def good_lwa_day_counts(df, window_start, window_end, min_log_num=2, min_seperation=5, buffer_time= '15 minutes',h=4, start_date='not_defined', end_date='not_defined'):
    """
    Description:\n
        This function calculates the number of good logging days, good window days, outside window days and adherent days. Good logging day is defined as a day that the person makes at least min_log_num number of loggings and the time separation between the earliest and the latest logging are greater than min_seperation.\n
        A good window day is defined as a date that all the food loggings are within the assigned restricted window. An adherent day is defined as a date that is both a good logging day and a good window day.
    Input:\n
        - df(pandas df): food_logging data.
        - window_start(datetime.time object): start time of the restriction window.
        - window_end(datetime.time object): end time of the restriction window.
        - min_log_num(count, int): minimum number of loggings to qualify a day as a good logging day
        - min_seperation(hours, int): minimum period of separation between earliest and latest loggings to qualify a day as a good logging day
        - buffer_time(time in string that can be passed into pd.Timedelta()): wiggle room for to be added/subtracted on the ends of windows.
        - h(hours, int): hours to be pushed back
        - start_date(datetime.date object): start date of the period for calculation. If not defined, it will be automatically set to be the earliest date in df.
        - end_date(datetime.date object): end date of the period for calculation. If not defined, it will be automatically set to be the latest date in df.
    Output:\n
        - a list that represents the number of good logging days, good window days, outside window days and adherent days.
    Requirement:\n
        - 'date' column existed in the df.
        - float time is calculated.
    """
    # if start_date or end_date is missing, return nan
    if pd.isnull(start_date) or pd.isnull(end_date):
        return [np.nan,np.nan,np.nan,np.nan], [[],[],[]]

    # if window start or window end are nan, make the windows the same as control's window time.
    if pd.isnull(window_start):
        window_start = datetime.time(0,0)
    if pd.isnull(window_end):
        window_end = datetime.time(23,59)

    # if there is no input on start_date or end_date, use earliest date and latest date
    if start_date=='not_defined':
        start_date = df['date'].min()
    if end_date=='not_defined':
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
    cur_dates = df['date'].sort_values(ascending = True).unique()
    for aday in cur_dates:
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
    good_logging_by_date = [cur_dates[i] for i, x in enumerate(good_logging_count) if x == False]

    good_window_days = (in_window_count==daily_count)
    good_window_day_counts = good_window_days.sum()
    good_window_by_date = [cur_dates[i] for i, x in enumerate(good_window_days) if x == False]

    outside_window_days = in_window_count.size - good_window_days.sum()
    good_logging_days = good_logging_count.sum()
    if good_logging_count.size == 0:
        adherent_day_counts = 0
        adherent_days_by_date = []
    else:
        adherent_days = (good_logging_count & (in_window_count==daily_count))
        adherent_days_by_date = [cur_dates[i] for i, x in enumerate(adherent_days) if x == False]
        adherent_day_counts = adherent_days.sum()

    rows = [good_logging_days, good_window_day_counts, outside_window_days, adherent_day_counts]
    bad_dates = (good_logging_by_date, good_window_by_date, adherent_days_by_date)

    return rows, bad_dates


# Cell
def find_missing_logging_days(df, start_date='not_defined', end_date='not_defined'):
    """
    Description:\n
        This function finds the days during which there's no logging within the period from start_date to end_date.
    Input:\n
        - df(panda df): food_logging data.
        - start_date(datetime.date object): start date of the period of calculation. If not defined, it will be automatically set to be the earliest date in df.
        - end_date(datetime.date object): end date of the period of calculation. If not defined, it will be automatically set to be the latest date in df.

    Output:\n
        - a list that contains all of the dates that don't contain loggings.

    Requirement:\n
        - 'date' column existed in the df.
    """
    # if start_date or end_date is missing, return nan
    if pd.isnull(start_date) or pd.isnull(end_date):
        return np.nan
    # if there is no input on start_date or end_date, use earliest date and latest date
    if start_date=='not_defined':
        start_date = df['date'].min()
    if end_date=='not_defined':
        end_date = df['date'].max()

    df = df[(df['date']>=start_date) & (df['date']<=end_date)]

    # get all the dates between two dates
    lst = []
    for x in pd.date_range(start_date.date(), end_date.date(), freq='d'):
         if x not in df['date'].unique():
                lst.append(x.date())

    return lst


# Cell
def make_table(food_data, ref_tbl, report_level=2, min_log_num=2, min_seperation=5, buffer_time= '15 minutes', h=4):
    """
    Description:\n
        This is a comprehensive function that performs all of the functionalities needed.

    Input:\n
        - food_data(panda df): food_logging data.
        - ref_tbl(panda df): table that contains window information and study phase information for each participant.
        - report_level(int): whether to print out the dates of no logging days, bad logging days, bad window days and non-adherent days for each participant. 0 - no report. 1 - report no logging days. 2 - report no logging days, bad logging days, bad window days and non adherent days.
        - h(hours): hour manipulation so that the starting and ending time for each day is more realistic.
        - min_log_num(counts): minimum number of loggings to qualify a day as a good logging day.
        - min_seperation(hours): minimum period of separation between earliest and latest loggings to qualify a day as a good logging day
        - buffer_time(time in string that can be passed into pd.Timedelta()): wiggle room for to be added/subtracted on the ends of windows.
        - h(hours): hours to be pushed back.


    Output:\n
        - df : dataframe that has all the variables needed and has the same row number as the ref_tbl.

    Requirement:\n
        - food logging data is already read from all files in the directories into a dataframe, which will be passed in as the variable food_data.
        - Columns 'Start_Day', 'End_day', 'mCC_ID', 'Eating_Window_Start', 'Eating_Window_End' existed in the ref_tbl.
        - For eating window without restriction(HABIT or TRE not in intervention period), Eating_Window_Start is 0:00, Eating_Window_End is 23:59.

    """
    df = food_data.copy()
    # preprocess to get the date and float_time column
    df['original_logtime'] = pd.to_datetime(df['original_logtime'])
    df['date'] = pdfa.find_date(df, 'original_logtime', h)
    df['float_time'] = pdfa.find_float_time(df, 'original_logtime', h)

    # get study phase duration
    result = get_phase_duration(ref_tbl)

    # reset the index of ref_tbl to avoid issues during concatenation
    ref_tbl = ref_tbl.reset_index(drop=True)

    # loop through each row and get 'caloric_entries', 'mean_daily_eating_window', 'std_daily_eating_window', 'eariliest_entry', 'logging_day_counts',
    # and 'good_logging_days', 'good_window_days', 'outside_window_days' and 'adherent_days' and find missing dates
    matrix = []
    missing_dates = {}
    bad_dates_dic = {}
    for index, row in ref_tbl.iterrows():
        id_ = row['mCC_ID']
        rows = []
        rows.append(caloric_entries(df[df['PID']==id_], row['Start_Day'],row['End_day']))
        rows.append(mean_daily_eating_duration(df[df['PID']==id_],'float_time', row['Start_Day'],row['End_day']))
        rows.append(std_daily_eating_duration(df[df['PID']==id_],'float_time', row['Start_Day'],row['End_day']))
        rows.append(earliest_entry(df[df['PID']==id_],'float_time', row['Start_Day'],row['End_day']))
        rows.append(logging_day_counts(df[df['PID']==id_], row['Start_Day'],row['End_day']))

        row_day_num, bad_dates = good_lwa_day_counts(df[df['PID']==id_]
                                           , window_start=row['Eating_Window_Start']
                                           , window_end = row['Eating_Window_End']
                                           , min_log_num=min_log_num
                                           , min_seperation=min_seperation
                                           , buffer_time= buffer_time
                                           , start_date=row['Start_Day']
                                           , end_date=row['End_day']
                                            , h=h)
        for x in row_day_num:
            rows.append(x)
        bad_logging = bad_dates[0]
        bad_window = bad_dates[1]
        non_adherent = bad_dates[2]

        if '{}_bad_logging'.format(id_) not in bad_dates_dic:
            bad_dates_dic['{}_bad_logging'.format(id_)]=bad_logging
            bad_dates_dic['{}_bad_window'.format(id_)]=bad_window
            bad_dates_dic['{}_non_adherent'.format(id_)]=non_adherent
        else:
            bad_dates_dic['{}_bad_logging'.format(id_)]+=bad_logging
            bad_dates_dic['{}_bad_window'.format(id_)]+=bad_window
            bad_dates_dic['{}_non_adherent'.format(id_)]+=non_adherent

        matrix.append(rows)
        date_lst = find_missing_logging_days(df[df['PID']==id_], row['Start_Day'],row['End_day'])
        # only consider when the result is not nan
        if isinstance(date_lst, list)==True:
            if id_ in missing_dates:
                missing_dates[id_] += date_lst
            else:
                missing_dates[id_] = date_lst

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

    # reorder the columns
    returned = returned[['mCC_ID', 'Participant_Study_ID', 'Study Phase',
       'Intervention group (TRE or HABIT)', 'Start_Day', 'End_day',
       'Eating_Window_Start','Eating_Window_End', 'phase_duration',
       'caloric_entries', 'mean_daily_eating_window', 'std_daily_eating_window',
       'earliest_entry', '2.5%', '97.5%', 'duration mid 95%',
       'logging_day_counts', '%_logging_day_counts', 'good_logging_days',
        '%_good_logging_days','good_window_days', '%_good_window_days',
        'outside_window_days','%_outside_window_days', 'adherent_days',
       '%_adherent_days']]

    if report_level == 0:
        return returned

    # print out missing dates with participant's id
    for x in missing_dates:
        if len(missing_dates[x])>0:
            print("Participant {} didn't log any food items in the following day(s):".format(x))
            for date in missing_dates[x]:
                print(date)

    if report_level == 1:
        return returned

    # print out bad logging, bad window and non-adherent dates with participant's id
    for x in bad_dates_dic:
        if len(bad_dates_dic[x])>0:
            strings = x.split('_')
            print("Participant {} have {} day(s) in the following day(s):".format(strings[0], strings[1]+' '+strings[2]))
            for date in bad_dates_dic[x]:
                print(date)

    return returned


