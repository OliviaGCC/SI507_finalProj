"""
convert the ADI 2's compliment(in decimal) back to negative RSSI value
params N_to_MN_Y: any dataframe that all the columns need updates
params column_start: the index of column that starts conversion
params column_num: how many columns totally
return: the updated dataframe
"""


import pandas as pd
import numpy as np

def twoscompliment2dec(N_to_MN_Y, column_start, column_num):
    j = 0
    while j< column_num: 
        list_i = []   
        #N_to_MN_Y.iloc[:,0]  = N_to_MN_Y.iloc[:,0] -256
        for i in N_to_MN_Y.iloc[:,(column_start+j)]: 
            
            if i!= 0: 
                i = i-256
                list_i.append(i)
            else:
                list_i.append(0)
        pd_list_i = pd.Series(list_i)
        N_to_MN_Y.iloc[:,(column_start+j)] = pd_list_i
        j += 1
    return N_to_MN_Y