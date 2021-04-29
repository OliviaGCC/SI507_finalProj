def node_list_RSSI():
    Node_list = ["Node to Node_0_RSSI"]
    i =1
    while i<24:
        Node_list.append("Node to Node_0_RSSI".replace("0", str(i)))
        i += 1
    return Node_list

def mng_to_node_list_RSSI():
    MtoN_list = ["Mng to Node_0_RSSI"]
    i =1
    while i<24:
        MtoN_list.append("Mng to Node_0_RSSI".replace("0", str(i)))
        i += 1
    return MtoN_list

def signalStrengh_list():
    Signal_Strength_chl= ['Manager_0_Chl_0_SignalStrengh(%)']
    i =1
    while i<16:
        Signal_Strength_chl.append("Manager_0_Chl_"+"0_SignalStrengh(%)".replace("0", str(i)))
        i += 1
    j=0
    while j <16:
        Signal_Strength_chl.append("Manager_1_Chl_"+"0_SignalStrengh(%)".replace("0", str(j)))
        j += 1  
    return Signal_Strength_chl



def node_chl_bRSSI_list():
    inner = ["Node_BackgroundRSSI_chl_1_byte_1"]
    i = 2
    while i < 6:
        inner.append("Node_BackgroundRSSI_chl_1_" +"byte_1".replace("1", str(i)))
        i += 1
    node_chl_bRSSI = inner
    j = 2
    while j <16:
        inner2 = [sub.replace('chl_1', 'chl_'+str(j)) for sub in inner]
        j += 1
        node_chl_bRSSI =node_chl_bRSSI+ inner2

    return node_chl_bRSSI


def mng_chl_bRSSI_list():
    inner = ["Mng_BackgroundRSSI_chl_1_byte_1"]
    i = 2
    while i < 6:
        inner.append("Mng_BackgroundRSSI_chl_1_" +"byte_1".replace("1", str(i)))
        i += 1
    mng_chl_bRSSI = inner
    j = 2
    while j <16:
        inner2 = [sub.replace('chl_1', 'chl_'+str(j)) for sub in inner]
        j += 1
        mng_chl_bRSSI =mng_chl_bRSSI+ inner2

    return mng_chl_bRSSI



