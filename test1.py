import sys
import os
import ast
import numpy as np
import json
import pandas as pd
import time
from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilename
import statistics
import csv
import argparse
import nptdms
from pathlib import Path, PureWindowsPath
import sqlite3
import pandas as pd
#importing sql library
from sqlalchemy import create_engine
import plotly.graph_objects as go 
import plotly.express as px
from plotly.subplots import make_subplots
import itertools



def export_data_to_csv(bms_data=None, pms_data=None, hr_data=None, exp_log_data=None, sheet_grouping="PACKET"):
    """
    Exports all the panda data frames to seperate csvs in a directory
    :param bms_data: panda data from from the bms file
    :param pms_data: panda data from from the pms file
    :param hr_data: panda data from from the healtreport file
    :param exp_log_data: panda data from from the explorer log file
    :param sheet_grouping: either "SCRIPT", "PACKET", by default the files are imported by packet then can be sorted by
                            script with another function
    :return: No return but outputs a file
    """

    # Make a nice, timestamped directory for our csvs
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    csv_folder_name = "%s wbms_explorer_datastore" % current_time
    csv_folder = os.path.join("C:\\",  user_input_path, csv_folder_name)
    os.mkdir(csv_folder)

    # Convert everything! File names are either the packet numbers or the script names
    if bms_data is not None:
        for identifier in bms_data.keys():

            if type(identifier) is not str:
                identifier_string = "%s_%d" % (sheet_grouping.capitalize(), identifier)
            else:
                identifier_string = identifier

            sheet_name = "BMS_%s.csv" % identifier_string
            bms_data[identifier].to_csv(os.path.join(csv_folder, sheet_name))

    if pms_data is not None:
        for identifier in pms_data.keys():
            if type(identifier) is not str:
                identifier_string = "%s_%d" % (sheet_grouping.capitalize(), identifier)
            else:
                identifier_string = identifier

            sheet_name = "PMS_%s.csv" % identifier_string

            pms_data[identifier].to_csv(os.path.join(csv_folder, sheet_name))

    if hr_data is not None:
        hr_data.to_csv(os.path.join(csv_folder, "Health Report.csv"))

    if exp_log_data is not None:
        exp_log_data.to_csv(os.path.join(csv_folder, "Explorer Log.csv"))
    
    return csv_folder


def log_health_report_datastore_to_data_frame(file_path, is_hr):
    """
    Converts either the datastore log or healthReport files to a pandas dataframe
    :param file_path: path to the relevant file
    :param is_hr: bool: if it's the healthreport file, true, false otherwise
    :return:
    """
    # Combine all the triplets of data in the log into on dictionary
    line_counter = 0
    master_dict = {}
    data_dict = {}
    with open(file_path, "r") as log_file:
        for line in log_file:
            
            if line_counter != 3:
                # Group the triplet of data lines together
                line_as_dict = json.loads(line)

                if line_counter == 2:
                    try:
                        del line_as_dict["_id"]
                            
                    except KeyError:
                            continue
                    if "Data_Data_75" in line_as_dict:
                        del line_as_dict["Data_Data_75"]

                data_dict.update(line_as_dict)
                #print(len(line_as_dict))
                line_counter += 1

            if line_counter == 3:
                # Once we have a set of 3, add it to our dictionary of values
                line_counter = 0

                data_dict.update(line_as_dict)

                for key, data in data_dict.items():
                
                    try:
                        master_dict[key].append(data)
                    except KeyError:
                        master_dict[key] = [data]
                data_dict = {}

    # Convert the dictionary into a handy DataFrame, combine the MAC columns if it's a healthreport
    data_frame = pd.DataFrame(master_dict)
    # if is_hr:
    #     combine_mac(data_frame, True)

    return data_frame

user_input_path = input("please copy datastore_folder path here: ")

# if user_input_path.find("C:\"):
#     user_input_path.replace("C:\","C:\\\") #regular expression use "\" to escape :\\ ( may has special meaning in python)

health_report_data = log_health_report_datastore_to_data_frame(os.path.join(user_input_path, "healthReport"), True)


csv_folder_path = export_data_to_csv(None, None, health_report_data, None, None)

#Path(os.path.join(user_input_path, "my_data.db").touch()



#read from csv file that created earlier and import the entire data into an sqlite table and use the headers in the csv file to become the headers in the sqlite table
df = pd.read_csv(os.path.join(csv_folder_path, "Health Report.csv"))

# strip whitespace from headers
df.columns = df.columns.str.strip()

db_path = os.path.join("C:\\", user_input_path,"Health__Report.sqlite" )

conn = sqlite3.connect(db_path)
cur = conn.cursor()

conn.commit()
# drop data into database
df.to_sql("HealthReportTable",conn,if_exists='replace')

#df_data_frame = px.data.iris() #!!!!!! hahahahah, it is soooo hilarious because this iris() is a a flower data set ..... sooooo funny!!!!!!!!

# schema in python
cur.execute("PRAGMA table_info('HealthReportTable')")
d =cur.execute("PRAGMA table_info('HealthReportTable')").fetchall()

# for row in d: 
#     print(row)

# find my target columns
mng_0_RSSI = df.iloc[:,df.columns.get_loc("HealthReport_SignalRssi_0_values_0"):(df.columns.get_loc("HealthReport_SignalRssi_0_values_15")+1)]
mng_1_RSSI = df.iloc[:,df.columns.get_loc("HealthReport_SignalRssi_1_values_0"):(df.columns.get_loc("HealthReport_SignalRssi_1_values_15")+1)]
mng_0_PathStability = df.iloc[:,df.columns.get_loc("HealthReport_PathStability_0_values_0"):(df.columns.get_loc("HealthReport_PathStability_0_values_15")+1)]
mng_1_PathStability = df.iloc[:,df.columns.get_loc("HealthReport_PathStability_1_values_0"):(df.columns.get_loc("HealthReport_PathStability_1_values_15")+1)]

#change a wide dataframe to a long dataframe
mng_0_RSSI_x = mng_0_RSSI.melt(var_name = "mng_0_RSSI_var", value_name = "mng_0_RSSI_value")
mng_1_RSSI_x= mng_1_RSSI.melt(var_name = "mng_1_RSSI_var", value_name = "mng_1_RSSI_value")
mng_0_PathStability_y = mng_0_PathStability.melt(var_name = "mng_0_PathStability_var",value_name = "mng_0_PathStability_value")
mng_1_PathStability_y = mng_1_PathStability.melt(var_name ="mng_1_PathStability_var", value_name = "mng_1_PathStability_value")

#define a series of color to represent the 16 channels: using 'Series.repeat(repeats, axis=None)'
channel = [i for i in range(0,16)] # create a list of integers using range()
color = pd.Series(channel, name="color").repeat(len(df["HealthReport_SignalRssi_0_values_0"])) # repeat() also repeat the 
# index to 00000, 11111... which later using pd.concat() require unique index

# Create the unique Index
index_ = [i for i in range(0, len(mng_0_RSSI_x))]
# set the index
color.index = index_


# concatenate the x, y color to one dataframe
mng_0_data = pd.concat([mng_0_RSSI_x, mng_0_PathStability_y, color], axis= 1) # axis =1 is to assembly by side, =0 (default) is to assembly vertical
mng_1_data = pd.concat([mng_1_RSSI_x, mng_1_PathStability_y, color], axis= 1)




#plot manager 0 RSSI vs Stability, subplot 1
fig1= px.scatter(mng_0_data,
    x="mng_0_RSSI_value", 
    y="mng_0_PathStability_value",
    color="color",
    labels ={
        "mng_0_RSSI_value": "Manager 0 RSSI (dBm)",
        "mng_0_PathStability_value": "Manager 0 Path Stability (%)",
        "color": "Channels"
    },
    title = "Manager 0 RSSI vs PathStability")
trace1 = fig1['data'][0]
#print(trace1)

# basic_layout = go.Layout(title="Manager 0 -All Channels: WaterFall Curve")
# fig = go.Figure(data=scatter_data, layout=basic_layout)


#plot manager 1 RSSI vs Stability, subplot 2
fig2= px.scatter(mng_1_data,
    x="mng_1_RSSI_value", 
    y="mng_1_PathStability_value",
    color="color",
    labels ={
        "mng_1_RSSI_value": "Manager 1 RSSI (dBm)",
        "mng_1_PathStability_value": "Manager 1 Path Stability (%)",
        "color": "Channels"
    },
    title = "Manager 1 RSSI vs PathStability")
trace2 = fig2['data'][0]


#define subplots layout: stack
fig = make_subplots(rows=2, cols=1, shared_xaxes=False,subplot_titles=("Manager 0 -All Channels: WaterFall Curve", "Manager 1 -All Channels: WaterFall Curve"))

# add traces
fig.add_trace(trace1, row=1, col=1)
fig.add_trace(trace2, row=2, col=1)


# Update xaxis properties
fig.update_xaxes(title_text = "Manager 0 RSSI (dBm)", row =1,col =1)
fig.update_xaxes(title_text = "Manager 1 RSSI (dBm)", row =2,col =1)

# Update yaxis properties
fig.update_yaxes(title_text = "Manager 0 PathStability (%)", row =1,col =1)
fig.update_yaxes(title_text = "Manager 1 PathStability (%)", row =2,col =1)

# Update title and height, width
fig.update_layout(height=2000, width=2000, title_text="Managers RSSI vs PathStability")


fig.write_html("Mng_All_Channels.html", auto_open=True)


#### pd.Series.append is also a way
'''
# mng_0_RSSI_x = pd.Series(data= None, dtype = "int64", name = "mng_0_RSSI")
# mng_0_PathStability_y = pd.Series(data= None, dtype = "int64", name = "mng_0_PathStability")
# mng_1_RSSI_x = pd.Series(data= None, dtype = "int64", name = "mng_1_RSSI")
# mng_1_PathStability_y = pd.Series(data= None, dtype = "int64", name = "mng_1_PathStability")

# #print(mng_0_RSSI_x.append(df["HealthReport_SignalRssi_0_values_14"]))

# #construct manager 0 RSSI and SignalStability list
# for c in df:
#     if (df.columns.get_loc(c) >= df.columns.get_loc("HealthReport_SignalRssi_0_values_0")) and (df.columns.get_loc(c) <= df.columns.get_loc("HealthReport_SignalRssi_0_values_15")):
#         #print(df[c])
#         mng_0_RSSI_x = mng_0_RSSI_x.append(df[c])
#     if (df.columns.get_loc(c) >= df.columns.get_loc("HealthReport_PathStability_0_values_0")) and (df.columns.get_loc(c) <= df.columns.get_loc("HealthReport_PathStability_0_values_15")):
#         mng_0_PathStability_y = mng_0_PathStability_y.append(df[c])


# #construct manager 1 RSSI and SignalStability list
# for c in df:
#     if (df.columns.get_loc(c) >= df.columns.get_loc("HealthReport_SignalRssi_1_values_0")) and (df.columns.get_loc(c) <= df.columns.get_loc("HealthReport_SignalRssi_1_values_15")):
#         mng_1_RSSI_x = mng_0_RSSI_x.append(df[c])
#     if (df.columns.get_loc(c) >= df.columns.get_loc("HealthReport_PathStability_1_values_0")) and (df.columns.get_loc(c) <= df.columns.get_loc("HealthReport_PathStability_1_values_15")):
#         mng_1_PathStability_y = mng_0_PathStability_y.append(df[c])
'''


# i = 1

# for c in df:

#     while i<3:
#         #print(df.iloc[:,df.columns.get_loc(c)])
#         if df.columns.get_loc(c) >= df.columns.get_loc("HealthReport_PathStability_0_values_0"):
#             fig.add_scatter(
#                 x = df.iloc[:,df.columns.get_loc("HealthReport_SignalRssi_0_values_0")+i] , 
#                 y = df.iloc[:,df.columns.get_loc("HealthReport_PathStability_0_values_0")+i],
#                 mode="markers",
#                 marker={'symbol':'circle-dot', 'size':10})
#                 #marker={'symbol':'circle-dot', 'size':10, 'color': 'green'})
#             i +=1
#         else: break

