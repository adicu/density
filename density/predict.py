import datetime

import numpy as np
import pandas as pd


SELECT = """
    SELECT d.client_count, d.dump_time,
           r.id AS group_id, r.name AS group_name,
           b.id AS parent_id, b.name AS building_name
    FROM density_data d
    JOIN routers r ON r.id = d.group_id
    JOIN buildings b ON b.id = r.building_id"""

FULL_CAP_DATA = {
    'Architectural and Fine Arts Library 1': 27,
    'Architectural and Fine Arts Library 2': 362,
    'Architectural and Fine Arts Library 3': 220,
    'Butler Library 2': 729,
    'Butler Library 3': 438,
    'Butler Library 4': 414,
    'Butler Library 301': 292,
    'Butler Library 5': 236,
    'Butler Library 6': 255,
    'Butler Library stk': 245,
    "JJ's Place": 185,
    'John Jay Dining Hall': 319,
    'Lehman Library 2': 213,
    'Lehman Library 3': 700,
    'Lerner 1': 168,
    'Lerner 2': 362,
    'Lerner 3': 357,
    'Lerner 4': 354,
    'Lerner 5': 373,
    'Roone Arledge Auditorium': 923,
    'Science and Engineering Library': 234,
    'Starr East Asian Library': 257,
    'Uris/Watson Library': 1046,
}


def db_to_pandas(cursor):
    """ Return occupancy data as pandas dataframe
    column dtypes:
        building_name: string
        group_id: int64
        group_name: category
        parent_id: category
        client_count: int64
        time_point: string
    index: DateTimeIndex -- dump_time
    Parameters
    ----------
    cursor: cursor for our DB
        Connection to db
    Returns
    -------
    pandas.DataFrame
        Density data in a Dataframe
    """
    today = datetime.datetime.today()
    day_of_week = today.weekday()
    week_of_year = today.isocalendar()[1]

    # construct SQL query to fetch only the data we need
    query = ' WHERE extract(WEEK from d.dump_time) = ' + \
            '{} AND extract(DOW from d.dump_time) = '.format(week_of_year) + \
            '{}'.format(day_of_week)
    cursor.execute(SELECT + query)
    raw_data = cursor.fetchall()

    # convert fetched data to a pandas dataframe
    df = pd.DataFrame(raw_data) \
           .set_index("dump_time") \
           .assign(group_name=lambda df: df["group_name"].astype('category'),
                   parent_id=lambda df: df["parent_id"].astype('category'))

    # add a new time point column to the datafram
    time_points = zip(df.index.hour, df.index.minute)
    time_points = ["{}:{}".format(x[0], x[1]) for x in time_points]
    df["time_point"] = time_points

    return df


def predict_today(past_data):
    """Return a dataframes of predicted counts for today
    where the indexs are timestamps of the day and columns are locations
    Parameters
    ----------
    past_data: pandas.DataFrama
        a dictionary of dataframes of density data where the keys are
        days of the week
    Returns
    -------
    pandas.DataFrame
        Dataframe containing predicted counts for 96 today's timepoints
    """
    results, locs = [], []
    std = []
    
    for group in np.unique(past_data["group_name"]):
        locs.append(group)

        # gets all rows for unique 'group'
        group_data = past_data[past_data["group_name"] == group]

        # get only client count and time point for each 'group' for all 4 years
        group_data = group_data[["client_count", "time_point"]]

        # average counts by time for each location
        group_result = group_data.groupby("time_point").mean()
         
        # convert capacity count to percentage
        group_result = np.divide(group_result, FULL_CAP_DATA[group])

        results.append(group_result.transpose())


    result = pd.concat(results)  # combine the data for all locations
    result.index = locs
    result = result.transpose()  # time points indexes and locations columns
    print(result.head())

    old_indexes = result.index
    new_indexes = []
    
    # make sure all time index has the same string format
    for index in old_indexes:
        splited = index.split(":")
        leading, trailing = splited[0], splited[1]
        if len(leading) == 1:
            leading = "0" + leading
        new_index = "{}:{}".format(leading, trailing)
        new_indexes.append(new_index)

    result.index = new_indexes
    result = result.sort_index()

    return result

def multi_predict_today(cluster1, cluster2, cluster3):
    """Return a dataframes of predicted counts for today
    where the indeces are timestamps of the day and columns are locations
    Parameters
    ----------
    past_data: pandas.DataFrama
        a dictionary of dataframes of density data where the keys are
        days of the week
    Returns
    -------
    pandas.DataFrame
        Dataframe containing predicted counts for 96 today's timepoints
    """
    results, locs = [], []
    std = []
    
    for group in np.unique(cluster1["group_name"]):
        locs.append(group)

        # gets all rows for unique 'group'
        group_data1 = cluster1[cluster1["group_name"] == group]
        group_data2 = cluster2[cluster2["group_name"] == group]
        group_data3 = cluster3[cluster3["group_name"] == group]

        # get only client count and time point for each 'group' for all 4 years
        group_data1 = group_data1[["client_count", "time_point"]]
        group_data2 = group_data2[["client_count", "time_point"]]
        group_data3 = group_data3[["client_count", "time_point"]]

        # average counts by time for each location
        group_result1 = group_data.groupby("time_point").mean()
        group_result2 = group_data.groupby("time_point").mean()
        group_result3 = group_data.groupby("time_point").mean()
         
        # convert capacity count to percentage 
        # pass in whichever group result has the lower std
        group_result = to_percentage(group_result1, group)

        results.append(group_result.transpose())


    result = pd.concat(results)  # combine the data for all locations
    result.index = locs
    result = result.transpose()  # time points indexes and locations columns
    print(result.head())

    old_indexes = result.index
    new_indexes = []
    
    # make sure all time index has the same string format
    for index in old_indexes:
        splited = index.split(":")
        leading, trailing = splited[0], splited[1]
        if len(leading) == 1:
            leading = "0" + leading
        new_index = "{}:{}".format(leading, trailing)
        new_indexes.append(new_index)

    result.index = new_indexes
    result = result.sort_index()

    return result

def to_percentage(group, name)
    return np.divide(group, FULL_CAP_DATA[name])

def categorize_data(cursor):

    """ Return data as pandas dataframe

    index: DateTimeIndex -- dump_time
    Parameters
    ----------
    cursor: cursor for our DB
        Connection to db
    Returns
    -------
    pandas.DataFrame
        Density data in a Dataframe
    """

    today = datetime.datetime.today()
    day_of_week = today.weekday()
    week_of_year = today.isocalendar()[1]
    
    # date format 2014-07-04
    # construct SQL query to fetch only the data we need
    query = " WHERE d.dump_time BETWEEN '2014-07-04 ' AND '2014-07-10 ' AND group_id = 130"

    # cluster 1 -> get all datapoints for same day for 4 years
    query1 = ' WHERE extract(WEEK from d.dump_time) = ' + \
            '{} AND extract(DOW from d.dump_time) = '.format(week_of_year) + \
            '{}'.format(day_of_week) 

    # cluster 2 -> get all data points for same date week ahead for 4 years
    query2 = ' WHERE (extract(WEEK from d.dump_time) = ' + \
            '{} AND extract(DOW from d.dump_time) = '.format(week_of_year) + \
            '{})'.format(day_of_week) + ' OR (extract(WEEK from d.dump_time) = ' + \
            '{}'.format(week_of_year + 1) + \
            ' AND extract(DOW from d.dump_time) = {}) '.format(day_of_week)

    # cluster 3 -> get all data points for same date week before for 4 years
    query3 = ' WHERE (extract(WEEK from d.dump_time) = ' + \
            '{} AND extract(DOW from d.dump_time) = '.format(week_of_year) + \
            '{})'.format(day_of_week) + ' OR (extract(WEEK from d.dump_time) = ' + \
            '{}'.format(week_of_year - 1) + \
            ' AND extract(DOW from d.dump_time) = {}) '.format(day_of_week)
    
    # cluster 4 -> get all data point for same date week before 
    query4 = ' WHERE (extract(WEEK from d.dump_time) = ' + \
            '{} AND extract(DOW from d.dump_time) = '.format(week_of_year) + \
            '{})'.format(day_of_week) + ' OR (extract(WEEK from d.dump_time) = ' + \
            '{}'.format(week_of_year + 1) + \
            ' AND extract(DOW from d.dump_time) = {}) '.format(day_of_week) + \
            ' OR (extract(WEEK from d.dump_time) = ' + \
            '{}'.format(week_of_year - 1) + \
            ' AND extract(DOW from d.dump_time) = {})'.format(day_of_week) 


    cursor.execute(SELECT + query4)
    raw_data = cursor.fetchall()

    # convert fetched data to a pandas dataframe
    df = pd.DataFrame(raw_data) \
           .set_index("dump_time") \
           .assign(group_name=lambda df: df["group_name"].astype('category'),
                   parent_id=lambda df: df["parent_id"].astype('category'))

    # add a new time point column to the datafram
    time_points = zip(df.index.hour, df.index.minute)
    time_points = ["{}:{}".format(x[0], x[1]) for x in time_points]
    df["time_point"] = time_points

    return df

def show_data(selected_data):
    
    # client_count = []
    # name = []
    # for date in selected_data.index.tolist():
    #     if str(date.time())[0:5] == '17:30':
    #         # list.append(selected_data.loc[date])
    #         print('client count upcoming')
    #         client_count.append(selected_data.loc[date]['client_count'])
    #         print(selected_data.loc[date]['client_count'])
    #         print('client count done')
    #         name.append(date)
    
    # #have a list of pandas series with data and name 
    # return (client_count, name)

    return print(selected_data)



    