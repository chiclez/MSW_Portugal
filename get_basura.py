# Data libraries
import pandas as pd
import numpy as np

# Plotting libraries
import matplotlib.pyplot as plt
import seaborn as sns
import folium

# Misc libraries
import os

# Here are the script functions

# Original function

def get_data(demax, dlmax):

    currDir = os.getcwd()
    dataAntunes = os.path.join(currDir, 'data_antunes.xls')

    antunesSheet0 = pd.read_excel(dataAntunes, sheet_name=0, header = 1)
    antunesSheet1 = pd.read_excel(dataAntunes, sheet_name=1, header = 2)
    antunesSheet2 = pd.read_excel(dataAntunes, sheet_name=2, header = 2)
    antunesSheet4 = pd.read_excel(dataAntunes, sheet_name=4, header = None)

    municipalities = antunesSheet0.copy()
    municipalities = municipalities.drop(
        columns = ["ORD_COD", "Q (ton/dia)", "Q (ton/ano)", "Pop 2001", "ET exist.", "ET assign."])

    q_j_init = antunesSheet0.copy()
    q_j_init = q_j_init.drop(
        columns = ["ORD_COD", "Concelho", "Q (ton/dia)", "Pop 2001", "ET exist.", "ET assign."])

    distmatrix1 = antunesSheet1.copy()
    d_jk_d_jl_init = distmatrix1.drop(columns = ["Unnamed: 0"])
    d_jk_d_jl_init.columns = list(range(0, 36))

    distmatrix2 = antunesSheet2.copy()
    d_kl_init = distmatrix2.drop(columns = ["Unnamed: 0"])

    w_jk0_init = antunesSheet4.copy()

    # Create f_jk_f_jl matrices: 
    # If the distances between municipalities and transfer stations  
    # d_jk <= demax or w_jk =1, then 1. Else, 0.
    f_jk_f_jl_init = d_jk_d_jl_init.copy()
    w_jk0_init.sort_index(inplace=True) == d_jk_d_jl_init.sort_index(inplace = True)

    f_jk_f_jl_init[(f_jk_f_jl_init <= demax) | (w_jk0_init == 1)] = 1
    f_jk_f_jl_init[f_jk_f_jl_init != 1]= 0
    f_jk_f_jl_init = f_jk_f_jl_init.astype(int)

    # Take the transposed matrix instead as wjk0 an f_jk_f_jl are not symmetric 
    w_jk0_init = w_jk0_init.T
    f_jk_f_jl_init = f_jk_f_jl_init.T

    # Create g_kl matrix: 
    # If the distances between transfer stations to incinerator 
    # d_kl <= dlmax, then 1. Else, 0.
    g_kl_init = d_kl_init.copy()
   
    g_kl_init = g_kl_init.where(d_kl_init > dlmax, 1)
    g_kl_init[g_kl_init != 1] = 0
    g_kl_init = g_kl_init.astype(int)

    # Create temp dictionaries
    q_j_init_dict = q_j_init.to_dict(orient = "list")
    d_jk_d_jl_init_dict = d_jk_d_jl_init.to_dict(orient = "list")
    d_kl_init_dict = d_kl_init.to_dict(orient = "list")
    w_jk0_init_dict = w_jk0_init.to_dict(orient = "list")
    f_jk_f_jl_init_dict = f_jk_f_jl_init.to_dict(orient = "list")
    g_kl_init_dict = g_kl_init.to_dict(orient = "list")

    # Get the base_keys for the dictionaries
    mun_list = municipalities.squeeze().to_list()
    base_keys = [(i, j) for i in mun_list for j in mun_list]

    # Get the matrix values 
    q_j = [value for key, value in q_j_init_dict.items()]
    q_j_list = [j for i in q_j for j in i]

    d_jk_d_jl = [value for key, value in d_jk_d_jl_init_dict.items()]
    d_jk_d_jl_list = [j for i in d_jk_d_jl for j in i]

    d_kl = [value for key, value in d_kl_init_dict.items()]
    d_kl_list = [j for i in d_kl for j in i]

    w_jk0 = [value for key, value in w_jk0_init_dict.items()]
    w_jk0_list = [j for i in w_jk0 for j in i]

    f_jk_f_jl = [value for key, value in f_jk_f_jl_init_dict.items()]
    f_jk_f_jl_list = [j for i in f_jk_f_jl for j in i]

    g_kl = [value for key, value in g_kl_init_dict.items()]
    g_kl_list = [j for i in g_kl for j in i]

    # create final dictionaries
    q_j_dict = dict(zip(mun_list, q_j_list))
    d_jk_d_jl_dict = dict(zip(base_keys, d_jk_d_jl_list))
    d_kl_dict = dict(zip(base_keys, d_kl_list))
    w_jk0_dict = dict(zip(base_keys, w_jk0_list))
    f_jk_f_jl_dict = dict(zip(base_keys, f_jk_f_jl_list))
    g_kl_dict = dict(zip(base_keys, g_kl_list))

    return q_j_dict, d_jk_d_jl_dict, d_kl_dict, w_jk0_dict, f_jk_f_jl_dict, g_kl_dict

# New function for bringing recent data and recycling data

def get_new_data(demax, dlmax, year):

    currDir = os.getcwd()
    dataAntunes = os.path.join(currDir, 'data_antunes.xls')
    new_data = os.path.join(currDir, "data_antunes_new.xls")

    antunesSheet0 = pd.read_excel(dataAntunes, sheet_name=0, header = 1)
    antunesSheet1 = pd.read_excel(dataAntunes, sheet_name=1, header = 2)
    antunesSheet2 = pd.read_excel(dataAntunes, sheet_name=2, header = 2)
    antunesSheet4 = pd.read_excel(dataAntunes, sheet_name=4, header = None)

    municipalities = antunesSheet0.copy()
    municipalities = municipalities.drop(
        columns = ["ORD_COD", "Q (ton/dia)", "Q (ton/ano)", "Pop 2001", "ET exist.", "ET assign."])
    
    # New data
    waste_df = pd.read_excel(new_data, sheet_name=0, header = 1)
    q_j_init = waste_df.drop(
        columns = ["ORD_COD", "Concelho", "Q (ton/dia)", "Q_2001", "Pop 2001", "Q_2015", "Pop_2015", "ET exist.", "ET assign."])

    distmatrix1 = antunesSheet1.copy()
    d_jk_d_jl_init = distmatrix1.drop(columns = ["Unnamed: 0"])
    d_jk_d_jl_init.columns = list(range(0, 36))

    distmatrix2 = antunesSheet2.copy()
    d_kl_init = distmatrix2.drop(columns = ["Unnamed: 0"])

    w_jk0_init = antunesSheet4.copy()

    # Create f_jk_f_jl matrices: 
    # If the distances between municipalities and transfer stations 
    # d_jk <= demax or w_jk =1, then 1. Else, 0.
    f_jk_f_jl_init = d_jk_d_jl_init.copy()
    w_jk0_init.sort_index(inplace=True) == d_jk_d_jl_init.sort_index(inplace = True)

    f_jk_f_jl_init[(f_jk_f_jl_init <= demax) | (w_jk0_init == 1)] = 1
    f_jk_f_jl_init[f_jk_f_jl_init != 1]= 0
    f_jk_f_jl_init = f_jk_f_jl_init.astype(int)

    # Take the transposed matrix instead as wjk0 an f_jk_f_jl are not symmetric 
    w_jk0_init = w_jk0_init.T
    f_jk_f_jl_init = f_jk_f_jl_init.T

    # Create g_kl matrix: 
    # If the distances between transfer stations to incinerator 
    # d_kl <= dlmax, then 1. Else, 0.
    g_kl_init = d_kl_init.copy()
   
    g_kl_init = g_kl_init.where(d_kl_init > dlmax, 1)
    g_kl_init[g_kl_init != 1] = 0
    g_kl_init = g_kl_init.astype(int)

    # Create temp dictionaries
    q_j_init_dict = q_j_init.to_dict(orient = "list")
    d_jk_d_jl_init_dict = d_jk_d_jl_init.to_dict(orient = "list")
    d_kl_init_dict = d_kl_init.to_dict(orient = "list")
    w_jk0_init_dict = w_jk0_init.to_dict(orient = "list")
    f_jk_f_jl_init_dict = f_jk_f_jl_init.to_dict(orient = "list")
    g_kl_init_dict = g_kl_init.to_dict(orient = "list")

    # Get the base_keys for the dictionaries
    mun_list = municipalities.squeeze().to_list()
    base_keys = [(i, j) for i in mun_list for j in mun_list]

    # Get the matrix values 
    q_j = [value for key, value in q_j_init_dict.items()]
    q_j_list = [j for i in q_j for j in i]

    d_jk_d_jl = [value for key, value in d_jk_d_jl_init_dict.items()]
    d_jk_d_jl_list = [j for i in d_jk_d_jl for j in i]

    d_kl = [value for key, value in d_kl_init_dict.items()]
    d_kl_list = [j for i in d_kl for j in i]

    w_jk0 = [value for key, value in w_jk0_init_dict.items()]
    w_jk0_list = [j for i in w_jk0 for j in i]

    f_jk_f_jl = [value for key, value in f_jk_f_jl_init_dict.items()]
    f_jk_f_jl_list = [j for i in f_jk_f_jl for j in i]

    g_kl = [value for key, value in g_kl_init_dict.items()]
    g_kl_list = [j for i in g_kl for j in i]

    # create final dictionaries
    q_j_dict = dict(zip(mun_list, q_j_list))
    d_jk_d_jl_dict = dict(zip(base_keys, d_jk_d_jl_list))
    d_kl_dict = dict(zip(base_keys, d_kl_list))
    w_jk0_dict = dict(zip(base_keys, w_jk0_list))
    f_jk_f_jl_dict = dict(zip(base_keys, f_jk_f_jl_list))
    g_kl_dict = dict(zip(base_keys, g_kl_list))

    return q_j_dict, d_jk_d_jl_dict, d_kl_dict, w_jk0_dict, f_jk_f_jl_dict, g_kl_dict

# Common functions

def get_coord(y, z, j_ts, l_inc, exist_ts):

    # Read the coordinates list
    coordinates = pd.read_csv("coordinates.csv")

    # Transfer stations coordinates
    df_y = pd.DataFrame(y, columns =['mun'])
    ts_all_coord = pd.merge(coordinates, df_y, how="inner", on=["mun"])

    # Incinerator coordinates
    df_z = pd.DataFrame(z, columns =['mun']) 
    inc_coord = pd.merge(coordinates, df_z, how="inner", on=["mun"])

    # All facilities
    all_fac = pd.merge(df_y, df_z, how = "outer", on = ["mun"])

    # Existing ts
    df_exist_ts = pd.DataFrame(exist_ts, columns =['mun'])
    ts_exist_coord = pd.merge(coordinates, df_exist_ts, how="inner", on=["mun"])

    # New ts
    ts_new_coord = pd.merge(
        ts_all_coord, ts_exist_coord, how="left", on=["mun"], indicator= True)
    ts_new_coord = ts_new_coord.loc[ts_new_coord["_merge"] == "left_only"]
    ts_new_coord = ts_new_coord.rename(
        columns = {"lat_x": "lat", "long_x": "long"})
    ts_new_coord = ts_new_coord.drop(columns = ["lat_y", "long_y", "_merge"])

    # Rest of municipalities: Not TS, not inc
    centro = pd.merge(
        coordinates, all_fac, on=['mun'], how='left', indicator=True)
    rest_mun = centro.loc[centro["_merge"] == "left_only"]

    # Transfer station links dataframe
    w_jk = pd.DataFrame(j_ts, columns =['ts', 'mun']) 
    w_jk_coord = pd.merge(coordinates, w_jk, how="inner", on=["mun"])
    links_ts_coord = pd.merge(
        coordinates, w_jk_coord, how="inner", left_on=["mun"], right_on = ["ts"])
    links_ts_coord = links_ts_coord.sort_values(by=["ts"], ascending=True)
    links_ts_coord = links_ts_coord.drop(columns = "ts")    
    links_ts_coord = links_ts_coord.rename(
        columns = {"mun_x": "ts", "lat_x": "lat_ts", "long_x": "long_ts", "mun_y": "mun", "lat_y": "lat_mun", "long_y": "long_mun"})

    # Incinerator links dataframe
    v_jl = pd.DataFrame(l_inc, columns =['inc', 'mun'])
    v_jl_coord = pd.merge(coordinates, v_jl, how="inner", on=["mun"])
    links_inc_coord = pd.merge(
        coordinates, v_jl_coord, how="inner", left_on=["mun"], right_on = ["inc"])
    links_inc_coord = links_inc_coord.sort_values(by=["inc"], ascending=True)
    links_inc_coord = links_inc_coord.drop(columns = "inc")    
    links_inc_coord = links_inc_coord.rename(
        columns = {"mun_x": "inc", "lat_x": "lat_inc", "long_x": "long_inc", "mun_y": "mun", "lat_y": "lat_mun", "long_y": "long_mun"})

    # Indicate type of facility
    ts_new_coord["type"] = "ts_new"
    ts_exist_coord["type"] = "ts_existing"
    inc_coord["type"] = "incinerator"

    return ts_new_coord, ts_exist_coord, inc_coord, rest_mun, links_ts_coord, links_inc_coord

def create_map(ts_new, ts_exist, inc, mun, w_jk, v_jl):

    # Create a map of the Centro region of Portugal
    centro_coord = [40.784142221076074, -8.12884084353569]

    # Instantiate feature groups for the transfer stations, incinerator 
    # and municipalities
    ts_group = folium.map.FeatureGroup(name = "New transfer stations")
    ts_e_group = folium.map.FeatureGroup(name = "Existing transfer stations")
    inc_group = folium.map.FeatureGroup(name = "Incinerator")
    mun_group = folium.map.FeatureGroup(name = "Municipalities")

    # Add each ts, municipalities and the incinerator to the feature groups
    for lat, lng, in zip(ts_new.lat, ts_new.long):
        ts_group.add_child(
            folium.CircleMarker([lat, lng], radius=5, color='green', fill=True, 
            fill_color='green', fill_opacity=0.7))
    for lat, lng, in zip(ts_exist.lat, ts_exist.long):
        ts_e_group.add_child(
            folium.CircleMarker([lat, lng], radius=5, color='blue', fill=True, 
            fill_color='blue', fill_opacity=0.7))
    for lat, lng, in zip(mun.lat, mun.long):
        mun_group.add_child(
            folium.CircleMarker([lat, lng], radius=2, color='black', fill=True, 
            fill_color='black', fill_opacity=0.7))
    for lat, lng, in zip(inc.lat, inc.long):
        inc_group.add_child(
            folium.CircleMarker([lat, lng], radius=6, color='red', fill=True, 
            fill_color='red', fill_opacity=0.7))

    # Add the feature groups to the map
    portugal_map = folium.Map(location=centro_coord, zoom_start=8)
    portugal_map.add_child(ts_group)
    portugal_map.add_child(ts_e_group)
    portugal_map.add_child(mun_group)
    portugal_map.add_child(inc_group)

    # Add a layer control to the map and other tile layer options
    folium.TileLayer('cartodbpositron').add_to(portugal_map)
    folium.TileLayer('stamentoner').add_to(portugal_map)
    folium.map.LayerControl('topright', collapsed=False).add_to(portugal_map)

    # Add the graph lines for the links
    w_jk_link = list(
        zip(zip(w_jk.lat_ts, w_jk.long_ts), zip(w_jk.lat_mun, w_jk.long_mun)))
    v_jl_link = list(
        zip(zip(v_jl.lat_inc, v_jl.long_inc), zip(v_jl.lat_mun, v_jl.long_mun)))

    folium.PolyLine(
        w_jk_link, color="darkred", weight=1.5, opacity=1).add_to(portugal_map)
    folium.PolyLine(
        v_jl_link, color="darkred", weight=1.5, opacity=1).add_to(portugal_map)

    # Return the map
    return portugal_map