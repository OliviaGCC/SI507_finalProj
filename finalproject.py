#################################
##### Name: Chenchen Gao
##### Uniqname: gaochenc
#################################



import sys
import os
import os.path
from os import path
import ast
import numpy as np
import json
import pandas as pd
import time
#from tkinter import Tk
#from tkinter.filedialog import askdirectory, askopenfilename
import statistics
import csv
#import argparse
import nptdms
from pathlib import Path, PureWindowsPath
import sqlite3
#from sqlalchemy import create_engine
import plotly.graph_objects as go 
import plotly.express as px
from plotly.subplots import make_subplots
#import itertools
import newName  # a python file that convert DATA_DATA name to descriptive names like RSSI, PathStability
import twoscompliment_to_decimal  # a python file that convert a two's complement back to negative dBm value
pd.options.mode.chained_assignment = None



def export_data_to_csv(node_hr_data=None, node_Bhr_data=None, mng_hr_data=None, mng_Bhr_data=None, network_data=None, sheet_grouping="PACKET"):
    """    Exports all the panda data frames to seperate csvs in a directory
    :param hr_data: panda data from from the healtreport file
    :param exp_log_data: panda data from from the explorer log file
    :param sheet_grouping: either "SCRIPT", "PACKET", by default the files are imported by packet then can be sorted by
                            script with another function
    :return: No return but outputs a file
    """

    # Make a nice, timestamped directory for our csvs
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    csv_folder_name = "%s wbms_explorer_datastore" % current_time
    csv_folder = os.path.join( user_input_path, csv_folder_name)
    os.mkdir(csv_folder)

    # Convert everything! File names are either the packet numbers or the script names

    if node_hr_data is not None:
        node_hr_data.to_csv(os.path.join(csv_folder, "Node_Health_Report.csv"))
    
    if node_Bhr_data is not None:
        node_Bhr_data.to_csv(os.path.join(csv_folder, "Node_Background_Health_Report.csv"))

    if mng_hr_data is not None:
        mng_hr_data.to_csv(os.path.join(csv_folder, "Manager_Health_Report.csv"))

    if mng_Bhr_data is not None:
        mng_Bhr_data.to_csv(os.path.join(csv_folder, "Manager_Background_Health_Report.csv"))

    if network_data is not None:
        network_data.to_csv(os.path.join(csv_folder, "Network_Data.csv"))
    
    return csv_folder


def log_health_report_datastore_to_data_frame(file_path,is_hr):
    """
    convert one json single file healthReport to 4 panda dataframe: node_health_report, node_background_health_report, Manager_health_report and Manager_background_health_report
    healthReport above v110 has manager healthreport data and background data, the new format changed the previous key names from discriptive names to all the same DATA_DATA_
    based on ADI EE_NWK_015{Diagnosing Netwrok Performance Using the wBMS Interface Library}, converted the key names(column names) back to discriptive names, e.g. SignalStability
    :param file_path: the file path where the json healthReport stored
    :param is_hr: bool: if it's the healthreport file, true, false otherwise
    :return: return a list of panda dataframes which can be converted to csv file using export_data_to_csv funciton
    """
    
    line_counter = 0
    master_node_hr_dict = {}
    master_node_Bhr_dict = {}
    master_mng_hr_dict = {}
    master_mng_Bhr_dict = {}
    node_hr_dict = {}
    node_Bhr_dict = {}
    mng_hr_dict = {}
    mng_Bhr_dict = {}
   
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
                    if line_as_dict["Data_Data_0"] == 0:
                        node_hr_dict.update(line_as_dict)

                    if line_as_dict["Data_Data_0"] == 1:
                        node_Bhr_dict.update(line_as_dict)
                    if line_as_dict["Data_Data_0"] == 17:
                        mng_hr_dict.update(line_as_dict)
                    if line_as_dict["Data_Data_0"] == 18:
                        mng_Bhr_dict.update(line_as_dict)

                #data_dict.update(line_as_dict)
                line_counter += 1

            if line_counter == 3:
                # Once we have a set of 3, add it to our dictionary of values
                line_counter = 0

                #data_dict.update(line_as_dict)
                if line_as_dict["Data_Data_0"] == 18:
                    mng_Bhr_dict.update(line_as_dict)
                if line_as_dict["Data_Data_0"] == 17:
                    mng_hr_dict.update(line_as_dict)
                if line_as_dict["Data_Data_0"] == 1:
                    node_Bhr_dict.update(line_as_dict)
                if line_as_dict["Data_Data_0"] == 0:
                    node_hr_dict.update(line_as_dict)


                for key, data in mng_Bhr_dict.items():
                    try:
                        master_mng_Bhr_dict[key].append(data)
                    except KeyError:
                        master_mng_Bhr_dict[key] = [data]

                for key, data in mng_hr_dict.items():
                    try:
                        master_mng_hr_dict[key].append(data)
                    except KeyError:
                        master_mng_hr_dict[key] = [data]

                for key, data in node_Bhr_dict.items():
                    try:
                        master_node_Bhr_dict[key].append(data)
                    except KeyError:
                        master_node_Bhr_dict[key] = [data]

                for key, data in node_hr_dict.items():
                    try:
                        master_node_hr_dict[key].append(data)
                    except KeyError:
                        master_node_hr_dict[key] = [data]

                node_hr_dict = {}
                node_Bhr_dict = {}
                mng_hr_dict = {}
                mng_Bhr_dict = {}


    data_frame_node_hr = pd.DataFrame(master_node_hr_dict)
    data_frame_node_Bhr = pd.DataFrame(master_node_Bhr_dict)
    data_frame_mng_hr = pd.DataFrame(master_mng_hr_dict)
    data_frame_mng_Bhr = pd.DataFrame(master_mng_Bhr_dict)

    
    #in Node Health Report,update the column name from Data_Data to Node_to_Mng/Node
    #call function from n.py to get the name list
    a =newName.signalStrengh_list()
    b =newName.node_list_RSSI()
    c = a +["Node to Manager_0","Node to Manager_1"] + b # this is the new name will replace Data_Data_15-72 in node_health_report

    rename = {}
    column = data_frame_node_hr.columns[21:79].to_list()
    for i, j in zip(column,c):
        rename[i] = j
    data_frame_node_hr.rename(columns = rename, inplace = True)
   

    #in Mng Health Report,update the column name from Data_Data to Mng_to_Node
    d =newName.mng_to_node_list_RSSI()
    rename1 = {}
    column1 = data_frame_mng_hr.columns[62:(62+24)].to_list()
    for i, j in zip(column1,d):
        rename1[i] = j
    data_frame_mng_hr.rename(columns = rename1, inplace = True)
   

    #in Node background Health Report,update the column name from Data_Data to Mng_to_Node
    e =newName.node_chl_bRSSI_list()
    rename2 = {}
    column2 = data_frame_node_Bhr.columns[7:(7+75)].to_list()
    for i, j in zip(column2,e):
        rename2[i] = j
    data_frame_node_Bhr.rename(columns = rename2, inplace = True)

    #in Mng background Health Report,update the column name from Data_Data to Mng_to_Node
    f =newName.mng_chl_bRSSI_list()
    rename3 = {}
    column3 = data_frame_mng_Bhr.columns[7:(7+75)].to_list()
    for i, j in zip(column3,f):
        rename3[i] = j
    data_frame_mng_Bhr.rename(columns = rename3, inplace = True)

    #call function twos compliment to decimal to convert RSSI to negative dBm
    data_frame_node_hr = twoscompliment_to_decimal.twoscompliment2dec(data_frame_node_hr,53,26)
    data_frame_node_Bhr = twoscompliment_to_decimal.twoscompliment2dec(data_frame_node_Bhr,7,75)
    data_frame_mng_hr = twoscompliment_to_decimal.twoscompliment2dec(data_frame_mng_hr,62,24)
    data_frame_mng_Bhr = twoscompliment_to_decimal.twoscompliment2dec(data_frame_mng_Bhr,7,75)

    return [data_frame_node_hr, data_frame_node_Bhr, data_frame_mng_hr, data_frame_mng_Bhr]


def network_data_to_data_frame(file_path, is_nd):
    """
    convert one json single file networkData to a dataframe: Network Dataframe
    :param file_path: the file path where the json healthData stored
    :param is_nd: bool: if it's the networkData file, true, false otherwise
    :return: return a list of panda dataframes which can be converted to csv file using export_data_to_csv funciton

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

                data_dict.update(line_as_dict)
                line_counter += 1

            if line_counter == 3:
                # Once we have a set of 3, add it to our dictionary of values
                line_counter = 0

                for key, data in data_dict.items():
                    try:
                        master_dict[key].append(data)
                    except KeyError:
                        master_dict[key] = [data]
                data_dict = {}



    sort_columns = ["Data_iPacketGenerationTime_high","Data_iPacketGenerationTime_low", "Data_iSequenceNumber"]

    data_frame = pd.DataFrame(master_dict).sort_values(by=sort_columns,ignore_index=True)

    # EPIC CONCATENATION then sort by time and sequence just to help
    #master_packet_frame = pd.concat([packet[append_columns] for packet in data_frame.values()]).sort_values(by=sort_columns,ignore_index=True)
                                                                    
    return data_frame
                                                               


def network_statistics(csv_file, explorer_log= False ):
    """
    created a list of statistics caculated from network data file that created
    params csv_file: the networkData csv file that was generated earlier
    return: a list of statistics for each node
    """
    f = open(r'{}'.format(csv_file))
    sheet = csv.reader(f)
    next(sheet)

    rssi = []
    seq = []
    port = []

    count = 0

    for row in sheet:
        if explorer_log == False:
            rssi.append(row[18])
            seq.append(row[16])
            port.append(row[11])
        else:
            rssi.append(row[8])
            seq.append(row[6])
            port.append(row[91])


    rssi = list(map(int, rssi))
    seq = list(map(int, seq))
    port = list(map(int, port))

    disconnect = False
    count_disc = 0
    disc_ind = []

    max_consec_loss = 0
    consec_loss = []
    for i in range(len(seq)):
        if i > 0:
            if seq[i] == 1:
                disconnect = True
                count_disc += 1
                disc_ind.append(i)
            if int(seq[i]) > (int(seq[i - 1]) + 1) and not disconnect:
                if (max_consec_loss < ((seq[i] - seq[i - 1]) - 1)):
                    max_consec_loss = (seq[i] - seq[i - 1]) - 1
                consec_loss.append((seq[i] - seq[i - 1]) - 1)
                count += (seq[i] - seq[i - 1]) - 1

        disconnect = False

    loss_over_4sec = 0
    for j in consec_loss:
        if j > 80:
            loss_over_4sec += 1

    total_seq = 0

    if count_disc == 1:
        total_seq = (seq[disc_ind[0] - 1] - seq[0]) + (seq[len(seq) - 1] - seq[disc_ind[0]])
    elif count_disc > 1:
        total_seq += seq[disc_ind[0] - 1] - seq[0]
        for i in range(1, len(disc_ind)):
            total_seq += seq[disc_ind[i] - 1] - seq[disc_ind[i - 1]]
        total_seq += seq[len(seq) - 1] - seq[disc_ind[len(disc_ind) - 1]]
    if total_seq > 0:
        disc_packet_loss = (count / total_seq) * 100
    if count_disc > 0:
        perc = disc_packet_loss
    else:
        perc = (count / (seq[len(seq) - 1] - seq[0])) * 100


    split_rssi = {240: [], 241: []}

    for rssi_val, port_id in zip(rssi, port):
        split_rssi[port_id].append(rssi_val)

    median_port0 = statistics.median(split_rssi[240])
    if len(split_rssi[241]) > 0:
        median_port1 = statistics.median(split_rssi[241])
    else:
        median_port1 = -99

    return [median_port0, median_port1, perc, count_disc, max_consec_loss / 20, loss_over_4sec]



def summarize_packet_data (network_dataframe, export_csv=False, explorer_data=False):
    """
    This takes all of the packet level information (ie RSSI, latency) and combines them into one DataFrame
    :param network_dataframe: the NetworkData dataframe which is panda dataframe type
    :param export_csv: bool: if true the DataFrames will be exported into a folder as csvs, incluing a netwrok summary
    :return: a list = [Dataframe, csv_folder]
            DataFrame of all the packet header data with MAC as the category to split things up if needed,
            csv_folder is the folder where all those network data csv are generated

    """


    # Make sure the node is a category type (the concat seems to drop this)
    network_dataframe["Data_eSrcDeviceId"] = network_dataframe["Data_eSrcDeviceId"].astype(dtype="category")

    #Dump the DataFrames into their own folder
    if export_csv:
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        csv_folder = os.path.join(user_input_path,("%s wbms_explorer_Network_data" % current_time))
        os.mkdir(csv_folder)
        with open(os.path.join(csv_folder, "Network_Statistics_Data.csv"), "w", newline="") as nwk_sum:
            nwk_sum.write("Node,Median RSSI Port 240,Median RSSI Port 241,Packet Loss,Disconnects,Max Consecutive Packet Loss (s),Packet Loss over 4 Second\r\n")
            for node in network_dataframe["Data_eSrcDeviceId"].cat.categories:
                csv_file = os.path.join(csv_folder, "%s_network_data.csv" % node)
                network_dataframe.loc[network_dataframe["Data_eSrcDeviceId"] == node].to_csv(csv_file)
                stats_str = [str(node)] # first column is the node id
                stats = network_statistics(csv_file, explorer_data)
                stats_str.extend(["%2.3f" % value for value in stats]) #append the statistics on the right
                stats_str[-1] += "\r\n" #next line
                nwk_sum.write(",".join(stats_str))


    return [network_dataframe, csv_folder]


#############################################################################################################################

################################################################################
###################################  PLOT ######################################
################################################################################

#plot node to mng/node rssi dataframe
def plot_n_to_M_N_RSSI(df_n_hr):
    """
    plot nodes to managers/nodes RSSI
    params df_n_hr: the dataframe of node health report
    return None
    """
    N_to_MN_Y = df_n_hr.iloc[:,df_n_hr.columns.get_loc("Node to Manager_0"):(df_n_hr.columns.get_loc("Node to Node_23_RSSI")+1)]
    N_to_MN = pd.concat([df_n_hr["Data_eDeviceId"],N_to_MN_Y], axis = 1).sort_values(by =["Data_eDeviceId"])


    #plot node to mng/node RSSI 
    fig1= px.scatter(N_to_MN,
        x="Data_eDeviceId",
        y =N_to_MN.columns[1:],
        labels = dict(x = "Node#",y="RSSI(dBm)"),
        title="Node to Mng_node RSSI")

    #basic_layout = go.Layout(title="node to mng/node RSSI")
    fig = go.Figure(data=fig1)
    fig.update_xaxes(dtick=1)
    fig.write_html("Node to Mng_node RSSI.html", auto_open=True)


# plot each node signal strength on channel 0-15
def plot_n_SignalStrength (df_n_hr):
    """
    plot each node signal strength on channel 0-15
    params df_n_hr: the dataframe of node health report
    return None
    """
    
    chl_SigStrgh_Y = df_n_hr.iloc[:,df_n_hr.columns.get_loc("Manager_0_Chl_0_SignalStrengh(%)"):(df_n_hr.columns.get_loc("Manager_0_Chl_15_SignalStrengh(%)")+1)]
    chl_SigStrgh = pd.concat([df_n_hr["Data_eDeviceId"],chl_SigStrgh_Y], axis = 1).sort_values(by =["Data_eDeviceId"])

    fig2= px.scatter(chl_SigStrgh,
        x="Data_eDeviceId",
        y =chl_SigStrgh_Y,
        title="Node SignalStrengh on different channel")

    #basic_layout = go.Layout(title="Node")
    fig2 = go.Figure(data=fig2)
    fig.update_xaxes(dtick=1)
    fig2.write_html("Node SignalStrengh on different channel.html", auto_open=True)


#Plot manager to nodes RSSI using manager health report data
def plot_M_to_N_RSSI(df_m_hr):
    """
    plot managers to nodes RSSI
    params df_m_hr: the dtaframe of manager health report
    return None
    """

    M_to_N_Y = df_m_hr.iloc[:,df_m_hr.columns.get_loc("Mng to Node_0_RSSI"):(df_m_hr.columns.get_loc("Mng to Node_23_RSSI")+1)]

    M_to_N_Y_long = M_to_N_Y.melt(var_name = "mng_to_nodes_RSSI_var", value_name = "mng_to_nodes_RSSI_value(dBm)" )

    node_lst = [i for i in range(0,24)] # create a list of node# using range()
    pd_node_lst = pd.Series(node_lst, name="Node#").repeat(len(M_to_N_Y["Mng to Node_0_RSSI"])) 
    #pd_node_lst_long = pd_node_lst.melt(var_name = "Node#_var", value_name = "Node#" )
    pd_color = ["mng_0","mng_1"]*24

    #plot node to mng/node RSSI 
    fig1= px.line(M_to_N_Y_long, x = pd_node_lst,y = "mng_to_nodes_RSSI_value(dBm)",color= pd_color , labels = dict(x = "Node#",color ="Mng#"),
    title="MNG to NODEs RSSI")

    fig = go.Figure(data=fig1)
    fig.update_xaxes(dtick=1)
    fig.write_html("MNG to NODEs RSSI.html", auto_open=True)


#Ploting the overall network data of all 24 nodes
def Plot_network_statistics (networkStatistics_dataframe):
    """
    plot network summary statistics
    params netwrokStatistics_csv: the csv of summary of network statistics created before
    return None
    """
    statistics_Y = networkStatistics_dataframe.iloc[1:]
    #plot node to mng/node RSSI 
    fig1= px.line(networkStatistics_dataframe, x = "Node",y= ["Median RSSI Port 240", "Median RSSI Port 241" ], labels = dict( Node = "Node#", y="Managers Median RSSI"),title="Network Statistics - Managers median RSSI")
    trace0 = fig1["data"][0]
    trace1 = fig1["data"][1]

    fig2= px.line(networkStatistics_dataframe, x = "Node",y= "Packet Loss", labels = dict( x = "Node#", y= "Packet Loss"),title="Network Statistics - Packet Loss")
    trace2 = fig2["data"][0]

    fig3= px.line(networkStatistics_dataframe, x = "Node",y= "Disconnects", labels = dict( x = "Node#", y= "Disconnects"),title="Network Statistics - Disconnects")
    trace3 = fig3["data"][0]

    fig4= px.line(networkStatistics_dataframe, x = "Node",y= "Max Consecutive Packet Loss (s)", labels = dict( x = "Node#", y= "Max Consecutive Packet Loss (s)"),title="Network Statistics - Max Consecutive Packet Loss (s)")
    trace4 = fig4["data"][0]

    fig5= px.line(networkStatistics_dataframe, x = "Node",y= "Packet Loss over 4 Second", labels = dict( x = "Node#", y= "Packet Loss over 4 Second"),title="Network Statistics - Packet Loss over 4 Second")
    trace5 = fig5["data"][0]

    #define subplots layout: stack
    fig = make_subplots(rows=5, cols=1, shared_xaxes=False,subplot_titles=("Manager Median RSSI","Packet Loss", "Disconnects", "Max Consecutive Packet Loss (s)", "Packet Loss over 4 Second"))
    # add traces
    fig.add_trace(trace0, row=1, col=1)
    fig.add_trace(trace1, row=1, col=1)
    fig.add_trace(trace2, row=2, col=1)
    fig.add_trace(trace3, row=3, col=1)
    fig.add_trace(trace3, row=4, col=1)
    fig.add_trace(trace3, row=5, col=1)

    
    # Update xaxis properties
    fig.update_xaxes(dtick=1,title_text = "Node#", row=5,col =1)
    fig.update_xaxes(dtick=1,col =1)

    # Update yaxis properties
    fig.update_yaxes(title_text = "Managers Median Stability", row =1,col =1)
    fig.update_yaxes(title_text = "Packet Loss", row =2,col =1)
    fig.update_yaxes(title_text = "Disconnects", row =3,col =1)
    fig.update_yaxes(title_text = "Max Consecutive Packet Loss (s)", row =4,col =1)
    fig.update_yaxes(title_text = "Packet Loss over 4 Second", row =5,col =1)

    fig.update_layout(height=1500, width=1500)

    # fig = go.Figure(data=fig1)
    fig.write_html("Network Statistics.html", auto_open=True)

#Plot Data RSSI on node of each channel
def plot_RSSI_on_node(network_data):
    """
    plot Data RSSI on node of each channel
    params df_m_hr: network data panda dataframe
    return None
    """

    fig1= px.scatter(network_data, x = "Data_eSrcDeviceId",y = "Data_iRSSI", color = "Data_eSrcDeviceId" ,labels = dict(Data_eSrcDeviceId = "Node#", Data_iRSSI = "RSSI(dBm)"),
    title="Data_RSSI at node")

    fig = go.Figure(data=fig1)
    fig.update_xaxes(dtick=1)
    #fig.show()
    fig.write_html("Data RSSI on node of each channel.html", auto_open=True)


#plot Data RSSI on channel of each node
def plot_RSSI_on_chl(network_data):
    """
    plot Data RSSI on channel of each node
    params df_m_hr: network data panda dataframe
    return None
    """

    fig1= px.scatter(network_data, x = "Data_iChannel",y = "Data_iRSSI", color = "Data_iChannel" ,labels = dict(Data_iChannel = "Channel#", Data_iRSSI = "RSSI(dBm)"),
    title="Data_RSSI at channel")

    fig = go.Figure(data=fig1)
    fig.update_xaxes(dtick=1)
    #fig.show()
    fig.write_html("Data RSSI on channel of each node.html", auto_open=True)


# plot a 3d of Data RSSI on channel and node
def plot_RSSI_on_chl_node(network_data):
    """
    plot a 3d of Data RSSI on channel and node
    params df_m_hr: network data panda dataframe
    return None
    """

    fig1= px.scatter_3d(network_data, x = "Data_iChannel",y = "Data_iRSSI", z = "Data_eSrcDeviceId", color = "Data_iChannel" ,labels = dict(Data_eSrcDeviceId = "Node#", Data_iRSSI = "RSSI(dBm)", Data_iChannel = "Channel#"),
    title="Data_RSSI at channel and node")

    fig = go.Figure(data=fig1)
    fig.update_traces(marker=dict(size=12,
                              line=dict(width=2,
                                        color='DarkSlateGrey')),
                  selector=dict(mode='markers'))
    #fig.show()
    fig.write_html("3d of RSSI on channel and node.html", auto_open=True)


################################################## sql  ##########################################################
# db_path_n_hr = os.path.join(user_input_path,"Node_Health_Report.sqlite" )
# db_path_n_Bhr = os.path.join(user_input_path,"Node_Background_Health_Report.sqlite" )
# db_path_m_hr = os.path.join(user_input_path,"Manager_Health_Report.sqlite" )
# db_path_m_Bhr = os.path.join(user_input_path,"Manager_Background_Health_Report.sqlite" )


# conn_n_hr = sqlite3.connect(db_path_n_hr) #open a connection to a database for node hr
# cur_n_hr = conn_n_hr.cursor() # create an instance of the curser class to invoke methods that execute SQLITE statement
# conn_n_hr.commit()
# # drop data into database
# df_n_hr.to_sql("HealthReport_Node_Table",conn_n_hr, if_exists='replace')

# conn_n_Bhr = sqlite3.connect(db_path_n_Bhr) #open a connection to a database for node background hr
# cur_n_Bhr = conn_n_Bhr.cursor()
# conn_n_Bhr.commit()
# # drop data into database
# df_n_Bhr.to_sql("HealthReport_Node__B_Table",conn_n_Bhr,if_exists='replace')

# conn_m_hr = sqlite3.connect(db_path_m_hr) #open a connection to a database for mng hr
# cur_m_hr = conn_m_hr.cursor()
# conn_m_hr.commit()
# # drop data into database
# df_m_hr.to_sql("HealthReport_Manager_Table",conn_m_hr,if_exists='replace')

# conn_m_Bhr = sqlite3.connect(db_path_m_Bhr)#open a connection to a database for mng Bhr
# cur_m_Bhr = conn_m_Bhr.cursor()
# conn_m_Bhr.commit()
# # drop data into database
# df_m_Bhr.to_sql("HealthReport_Manager_B_Table",conn_m_Bhr,if_exists='replace')

#df_data_frame = px.data.iris() #!!!!!! hahahahah, it is soooo hilarious because this iris() is a a flower data set ..... sooooo funny!!!!!!!!

# node health report schema in python
# cur.execute("PRAGMA table_info('HealthReportTable')")
# d =cur.execute("PRAGMA table_info('HealthReportTable')").fetchall()
# for row in d: 
#     print(row)

################################################################################################################## 



if __name__ == "__main__":


    user_input_path = input("please copy project folder <fp_subm> path here or exit: ")

    
    
    while True: 
        if user_input_path.lower()== "exit" : 
            print("BYE")
            break
        
        # elif FileNotFoundError:
        #     print("No such file or directory, please try again!")
        #     user_input_path = input("please copy project folder path here or exit: ")
        
        if path.isfile(os.path.join(user_input_path, "healthReport")) or path.isfile(os.path.join(user_input_path, "networkData")) == True: 
            user_input_path2 = input("Do you wanna convert BMS logging json data to csv files? Yes or No :")
            if user_input_path2.lower()== "exit" : 
                print("BYE")
                break

            if user_input_path2.lower().find("yes") != -1: 

                print("generating.....\n")
                node_hr_dataframe = log_health_report_datastore_to_data_frame(os.path.join(user_input_path, "healthReport"), True)[0]
                node_Bhr_dataframe = log_health_report_datastore_to_data_frame(os.path.join(user_input_path, "healthReport"), True)[1]
                mng_hr_dataframe = log_health_report_datastore_to_data_frame(os.path.join(user_input_path, "healthReport"), True)[2]
                mng_Bhr_dataframe = log_health_report_datastore_to_data_frame(os.path.join(user_input_path, "healthReport"), True)[3]
                network_dataframe = network_data_to_data_frame(os.path.join(user_input_path, "networkData"), True)
                
                hr_csv = export_data_to_csv(node_hr_dataframe, node_Bhr_dataframe, mng_hr_dataframe, mng_Bhr_dataframe, network_dataframe, None)

                #Network statistics will extracted from Network_Data.csv, as well as each of the node network info
                networkData_dataframe = pd.read_csv(os.path.join(hr_csv, "Network_Data.csv"))
                networkData_dataframe.columns = networkData_dataframe.columns.str.strip()
                nw_csv = summarize_packet_data(networkData_dataframe,export_csv=True, explorer_data=False)[1]

                network_data = pd.read_csv(os.path.join(nw_csv, "Network_Statistics_Data.csv"))
                
                print("\n")
                print("cvs files have been created in the same folder")
                print("\n")


                #read from csv file that created earlier to panda dataframes
                df_n_hr = pd.read_csv(os.path.join(hr_csv, "Node_Health_Report.csv"))
                df_n_Bhr = pd.read_csv(os.path.join(hr_csv, "Node_Background_Health_Report.csv"))
                df_m_hr = pd.read_csv(os.path.join(hr_csv, "Manager_Health_Report.csv"))
                df_m_Bhr = pd.read_csv(os.path.join(hr_csv, "Manager_Background_Health_Report.csv"))
                network_data = pd.read_csv(os.path.join(hr_csv, "Network_Data.csv"))

                # strip whitespace from headers
                df_n_hr.columns = df_n_hr.columns.str.strip()
                df_n_Bhr.columns = df_n_Bhr.columns.str.strip()
                df_m_hr.columns = df_m_hr.columns.str.strip()
                df_m_Bhr.columns = df_m_Bhr.columns.str.strip()
                network_data.columns = network_data.columns.str.strip()

                #read from csv file that created earlier and import the entire data into an sqlite table and use the headers in the csv file to become the headers in the sqlite table
                db_path_n_hr = os.path.join(user_input_path,"Node_Health_Report.sqlite" )
                db_path_n_Bhr = os.path.join(user_input_path,"Node_Background_Health_Report.sqlite" )
                db_path_m_hr = os.path.join(user_input_path,"Manager_Health_Report.sqlite" )
                db_path_m_Bhr = os.path.join(user_input_path,"Manager_Background_Health_Report.sqlite" )

                conn1 = sqlite3.connect(db_path_n_hr)
                conn2 = sqlite3.connect(db_path_n_Bhr)
                conn3 = sqlite3.connect(db_path_m_hr)
                conn4 = sqlite3.connect(db_path_m_Bhr)
                cur1 = conn1.cursor()
                cur2 = conn2.cursor()
                cur3 = conn3.cursor()
                cur4 = conn4.cursor()
                
                conn_n_hr = sqlite3.connect(db_path_n_hr) #open a connection to a database for node hr
                cur_n_hr = conn_n_hr.cursor() # create an instance of the curser class to invoke methods that execute SQLITE statement
                conn_n_hr.commit()
                # drop data into database
                df_n_hr.to_sql("HealthReport_Node_Table",conn_n_hr, if_exists='replace')

                conn_n_Bhr = sqlite3.connect(db_path_n_Bhr) #open a connection to a database for node background hr
                cur_n_Bhr = conn_n_Bhr.cursor()
                conn_n_Bhr.commit()
                # drop data into database
                df_n_Bhr.to_sql("HealthReport_Node__B_Table",conn_n_Bhr,if_exists='replace')

                conn_m_hr = sqlite3.connect(db_path_m_hr) #open a connection to a database for mng hr
                cur_m_hr = conn_m_hr.cursor()
                conn_m_hr.commit()
                # drop data into database
                df_m_hr.to_sql("HealthReport_Manager_Table",conn_m_hr,if_exists='replace')

                conn_m_Bhr = sqlite3.connect(db_path_m_Bhr)#open a connection to a database for mng Bhr
                cur_m_Bhr = conn_m_Bhr.cursor()
                conn_m_Bhr.commit()
                # drop data into database
                df_m_Bhr.to_sql("HealthReport_Manager_B_Table",conn_m_Bhr,if_exists='replace')

                #  ###node health report schema in python
                # cur1.execute("PRAGMA table_info('Node_Health_Table')")
                # d =cur1.execute("PRAGMA table_info('Node_Health_Table')").fetchall()
                # for row in d: 
                #     print(row)


                print("In the following plots: \n"
                    "1. Plot Node_x to Managers and Nodes RSSI(from Node Health Report) \n"
                    "2. Plot Managers to Nodes RSSI (from Manager Health Report) \n"
                    "3. Plot RSSI 3D based on nodes and channels (from Network Data) \n"
                    "4. Plot RSSI @ all nodes for each channel (from Network Data) \n"
                    "5. Plot Rssi @ all channels for each node (from Network Data) \n"
                    "6. Plot the network statistics summary of all nodes \n")
                
                while True: 
                    user_input3 = input(" please input a number which plot you wanna see? \n")

                    if user_input3.isnumeric() is True:
                        if  int(user_input3) > 0 and int(user_input3) <= 6:
                            
                            if user_input3 == "1": 
                                df_n_hr = pd.read_csv(os.path.join(hr_csv, "Node_Health_Report.csv"))
                                df_n_hr.columns = df_n_hr.columns.str.strip()
                                plot_n_to_M_N_RSSI(df_n_hr)

                            if user_input3 == "2":
                                df_m_hr = pd.read_csv(os.path.join(hr_csv, "Manager_Health_Report.csv"))     
                                df_m_hr.columns = df_m_hr.columns.str.strip()                           
                                plot_M_to_N_RSSI(df_m_hr)

                            if user_input3 == "3":
                                network_data = pd.read_csv(os.path.join(hr_csv, "Network_Data.csv"))    
                                network_data.columns = network_data.columns.str.strip()                          
                                plot_RSSI_on_chl_node(network_dataframe)

                            if user_input3 == "4":
                                network_data = pd.read_csv(os.path.join(hr_csv, "Network_Data.csv"))    
                                network_data.columns = network_data.columns.str.strip()                          
                                plot_RSSI_on_node(network_dataframe)

                            if user_input3 == "5":
                                network_data = pd.read_csv(os.path.join(hr_csv, "Network_Data.csv"))    
                                network_data.columns = network_data.columns.str.strip()                          
                                plot_RSSI_on_chl(network_dataframe)

                            if user_input3 == "6":
                                networkStatistics_dataframe = pd.read_csv(os.path.join(nw_csv, "Network_Statistics_Data.csv"))
                                networkStatistics_dataframe.columns = networkStatistics_dataframe.columns.str.strip()
                                Plot_network_statistics (networkStatistics_dataframe)

                        else:
                            print("Please enter a number within the range of the plots list.")

                    else:
                        try:  #validate the userinput is interger
                            float(user_input3)
                            print ("Please enter an INTEGER within the range of the list.")
                        except ValueError:
                            if user_input3.lower()== "exit" : 
                                user_input_path = "exit"
                                break
                            else:
                                print(" please enter an INTEGER")

            else:
                print("could not find the json files")          
    
                
        else: 
            print("No such file or directory, please try again!")
            user_input_path = input("please copy project folder path here or exit: ")
            
