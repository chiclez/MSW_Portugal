#Data libraries
import pandas as pd
import numpy as np

# Plotting libraries
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import geopandas as gp
from shapely.geometry import Point, Polygon, LineString

# Misc libraries
import os
from pyomo.environ import *

# Key takeaways

# Get yourself in the data directory
data_dir = os.path.join(os.getcwd(), "data")

# All municipalities in normal case
muns = ['Agueda', 'Albergaria-a-Velha', 'Anadia', 'Arouca', 'Aveiro', 
    'Estarreja', 'Ilhavo', 'Mealhada', 'Murtosa', 'Oliveira de Azemeis', 
    'Oliveira do Bairro', 'Ovar', 'Sao Joao da Madeira', 'Sever do Vouga', 
    'Vagos', 'Vale de Cambra', 'Arganil', 'Cantanhede', 'Coimbra', 
    'Condeixa-a-Nova', 'Figueira da Foz', 'Gois', 'Lousa', 'Mira', 
    'Miranda do Corvo', 'Montemor-o-Velho', 'Pampilhosa da Serra', 'Penacova', 
    'Penela', 'Soure', 'Vila Nova Poiares', 'Alvaiazere', 'Ansiao', 
    'Castanheira de Pera', 'Figueiro dos Vinhos', 'Pedrogao Grande']

# Functions

# Original function for Antunes et al (2001) model

def get_data(demax, dlmax):

    data_sheet = os.path.join(data_dir, 'data.xls')

    data_hace_mucho = pd.read_excel(data_sheet, sheet_name=0, header = 1)
    distance_jk_sheet = pd.read_excel(data_sheet, sheet_name=1, header = 2)
    distance_kl_sheet = pd.read_excel(data_sheet, sheet_name=2, header = 2)
    w_jk0_sheet = pd.read_excel(data_sheet, sheet_name=4, header = None)

    q_j_init = data_hace_mucho.copy()
    q_j_init = q_j_init[["Q_2001"]]

    distmatrix1 = distance_jk_sheet.copy()
    d_jk_d_jl_init = distmatrix1.drop(columns = ["Unnamed: 0"])
    d_jk_d_jl_init.columns = list(range(0, 36))

    distmatrix2 = distance_kl_sheet.copy()
    d_kl_init = distmatrix2.drop(columns = ["Unnamed: 0"])

    w_jk0_init = w_jk0_sheet.copy()

    # Create f_jk_f_jl matrices: 
    # If the distances between municipalities and transfer stations  
    # d_jk <= demax or w_jk =1, then 1. Else, 0.
    f_jk_f_jl_init = d_jk_d_jl_init.copy()
    w_jk0_init.sort_index(inplace=True) == d_jk_d_jl_init.sort_index(inplace = True)

    f_jk_f_jl_init[(f_jk_f_jl_init <= demax) | (w_jk0_init == 1)] = 1
    f_jk_f_jl_init[f_jk_f_jl_init != 1]= 0
    f_jk_f_jl_init = f_jk_f_jl_init.astype(int)

    # Take the transposed matrix. wjk0 and f_jk_f_jl are not symmetric 
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
    base_keys = [(i, j) for i in muns for j in muns]

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
    q_j_dict = dict(zip(muns, q_j_list))
    d_jk_d_jl_dict = dict(zip(base_keys, d_jk_d_jl_list))
    d_kl_dict = dict(zip(base_keys, d_kl_list))
    w_jk0_dict = dict(zip(base_keys, w_jk0_list))
    f_jk_f_jl_dict = dict(zip(base_keys, f_jk_f_jl_list))
    g_kl_dict = dict(zip(base_keys, g_kl_list))

    basura_hace_mucho = [q_j_dict, d_jk_d_jl_dict, d_kl_dict, w_jk0_dict, 
                f_jk_f_jl_dict, g_kl_dict]

    return basura_hace_mucho

# Function for using data from 2019 and recycling data

def get_new_data(demax, dlmax, drmax):

    data_sheet = os.path.join(data_dir, "data.xls")

    distance_jk_sheet = pd.read_excel(data_sheet, sheet_name=1, header = 2)
    distance_kl_sheet = pd.read_excel(data_sheet, sheet_name=2, header = 2)
    w_jk0_sheet = pd.read_excel(data_sheet, sheet_name=4, header = None)
    data_2019 = pd.read_excel(data_sheet, sheet_name=7, header = 1)
    
    # Non-recyclable waste for 2019
    q_j_init = data_2019[["q_j_2019"]]

    # Total recyclable for 2019
    q_r_init = data_2019[["q_r"]]

    # Recycling materials
    # q_paper_init = data_2019[["Paper"]]
    # q_plastic_init = data_2019[["Plastic"]]
    # q_metals_init = data_2019[["Metals"]]
    # q_glass_init = data_2019[["Glass"]]
    # q_wood_init = data_2019[["Wood"]]

    recycling_mat = ["Paper", "Plastic", "Metals", "Glass", "Wood"]
    q_r_max_init = data_2019[recycling_mat].T

    # Distance matrices
    distmatrix1 = distance_jk_sheet.copy()
    d_jk_d_jl_init = distmatrix1.drop(columns = ["Unnamed: 0"])
    d_jk_d_jl_init.columns = list(range(0, 36))

    distmatrix2 = distance_kl_sheet.copy()
    d_kl_init = distmatrix2.drop(columns = ["Unnamed: 0"])

    # Existing transfer stations links
    w_jk0_init = w_jk0_sheet.copy()

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

    # Create g_jk matrix for the recycling centers and municipalities 
    # If the distances between centers to municipalities 
    # d_kl <= drmax, then 1. Else, 0.
    g_jk_init = d_jk_d_jl_init.copy()
   
    g_jk_init = g_jk_init.where(d_jk_d_jl_init > drmax, 1)
    g_jk_init[g_jk_init != 1] = 0
    g_jk_init = g_jk_init.astype(int)

    # Create dij matrix with only upper triangle, for linearizing the problem
    distance_upper_diag = np.triu(d_jk_d_jl_init)
    d_jk_upper = pd.DataFrame(data = distance_upper_diag, columns = list(range(0, 36)))

    d_jk_bin_array = np.where(distance_upper_diag !=0, 1, distance_upper_diag)
    d_jk_bin = pd.DataFrame(data = d_jk_bin_array, columns = list(range(0, 36)))

    # Create temp dictionaries
    q_j_init_dict = q_j_init.to_dict(orient = "list")
    q_r_init_dict = q_r_init.to_dict(orient = "list")
    # q_paper_init_dict = q_paper_init.to_dict(orient = "list")
    # q_plastic_init_dict = q_plastic_init.to_dict(orient = "list")
    # q_metals_init_dict = q_metals_init.to_dict(orient = "list")
    # q_glass_init_dict = q_glass_init.to_dict(orient = "list")    
    # q_wood_init_dict = q_wood_init.to_dict(orient = "list")

    q_r_max_init_dict = q_r_max_init.to_dict(orient = "list")

    d_jk_d_jl_init_dict = d_jk_d_jl_init.to_dict(orient = "list")
    d_kl_init_dict = d_kl_init.to_dict(orient = "list")
    w_jk0_init_dict = w_jk0_init.to_dict(orient = "list")
    f_jk_f_jl_init_dict = f_jk_f_jl_init.to_dict(orient = "list")
    g_kl_init_dict = g_kl_init.to_dict(orient = "list")
    g_jk_init_dict = g_jk_init.to_dict(orient = "list")

    d_jk_upper_init_dict = d_jk_upper.to_dict(orient = "list")
    d_jk_bin_init_dict = d_jk_bin.to_dict(orient = "list")

    # Get the base_keys for the dictionaries
    base_keys = [(i, j) for i in muns for j in muns]
    recycling_keys = [(i, r) for i in muns for r in recycling_mat]

    # Get the matrix values 
    q_j = [value for key, value in q_j_init_dict.items()]
    q_j_list = [j for i in q_j for j in i]

    q_r = [value for key, value in q_r_init_dict.items()]
    q_r_list = [j for i in q_r for j in i]

    # q_paper = [value for key, value in q_paper_init_dict.items()]
    # q_paper_list = [j for i in q_paper for j in i]

    #q_plastic = [value for key, value in q_plastic_init_dict.items()]
    # q_plastic_list = [j for i in q_plastic for j in i]

    # q_metals = [value for key, value in q_metals_init_dict.items()]
    # q_metals_list = [j for i in q_metals for j in i]

    # q_glass = [value for key, value in q_glass_init_dict.items()]
    # q_glass_list = [j for i in q_glass for j in i]

    # q_wood = [value for key, value in q_wood_init_dict.items()]
    # q_wood_list = [j for i in q_wood for j in i]

    q_r_max = [value for key, value in q_r_max_init_dict.items()]
    q_r_max_list = [j for i in q_r_max for j in i]

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

    g_jk = [value for key, value in g_jk_init_dict.items()]
    g_jk_list = [j for i in g_jk for j in i]

    d_jk_tri = [value for key, value in d_jk_upper_init_dict.items()]
    d_jk_tri_list = [j for i in d_jk_tri for j in i]

    d_jk_bin_split = [value for key, value in d_jk_bin_init_dict.items()]
    d_jk_bin_list = [j for i in d_jk_bin_split for j in i]

    # create final dictionaries

    # Waste
    q_j_dict = dict(zip(muns, q_j_list))
    q_r_dict = dict(zip(muns, q_r_list))

    #q_paper_dict = dict(zip(muns, q_paper_list))
    #q_plastic_dict = dict(zip(muns, q_plastic_list))
    #q_metals_dict = dict(zip(muns, q_metals_list))
    #q_glass_dict = dict(zip(muns, q_glass_list))
    #q_bio_dict = dict(zip(muns, q_bio_list))

    # q_jr
    q_r_max_dict = dict(zip(recycling_keys, q_r_max_list))

    # distances and existing links
    d_jk_d_jl_dict = dict(zip(base_keys, d_jk_d_jl_list))
    d_kl_dict = dict(zip(base_keys, d_kl_list))
    w_jk0_dict = dict(zip(base_keys, w_jk0_list))
    f_jk_f_jl_dict = dict(zip(base_keys, f_jk_f_jl_list))
    g_kl_dict = dict(zip(base_keys, g_kl_list))
    g_jk_dict = dict(zip(base_keys, g_jk_list))
    d_jk_tri_dict = dict(zip(base_keys, d_jk_tri_list))
    d_jk_bin_dict = dict(zip(base_keys, d_jk_bin_list))
    
    new_basura = [q_j_dict, q_r_dict, q_r_max_dict, d_jk_d_jl_dict, d_kl_dict, 
                    w_jk0_dict, f_jk_f_jl_dict, g_kl_dict, g_jk_dict, 
                    d_jk_tri_dict, d_jk_bin_dict]

    return new_basura

# Common functions

def get_coord(y, z, j_ts, l_inc, exist_ts, x_k = None, j_rec = None):

    # Read the coordinates list
    coordinates = pd.read_csv(os.path.join(data_dir, "coordinates.csv"))

    # Transfer stations coordinates
    df_y = pd.DataFrame(y, columns =['mun'])
    ts_all_coord = pd.merge(coordinates, df_y, how="inner", on=["mun"])

    # Incinerator coordinates
    df_z = pd.DataFrame(z, columns =['mun']) 
    inc_coord = pd.merge(coordinates, df_z, how="inner", on=["mun"])

    # All facilities
    all_fac = pd.merge(df_y, df_z, how = "outer", on = ["mun"])

    # Add recycling centres
    if x_k:
        df_x_k = pd.DataFrame(x_k, columns=["mun"])
        rec_coord = pd.merge(coordinates, df_x_k, how="inner", on=["mun"])
        all_fac = all_fac.append(df_x_k)

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
        columns = {"mun_x": "ts", "lat_x": "lat_ts", "long_x": "long_ts", 
        "mun_y": "mun", "lat_y": "lat_mun", "long_y": "long_mun"})

    # Incinerator links dataframe
    v_jl = pd.DataFrame(l_inc, columns =['inc', 'mun'])
    v_jl_coord = pd.merge(coordinates, v_jl, how="inner", on=["mun"])
    links_inc_coord = pd.merge(
        coordinates, v_jl_coord, how="inner", left_on=["mun"], right_on = ["inc"])
    links_inc_coord = links_inc_coord.sort_values(by=["inc"], ascending=True)
    links_inc_coord = links_inc_coord.drop(columns = "inc")    
    links_inc_coord = links_inc_coord.rename(
        columns = {"mun_x": "inc", "lat_x": "lat_inc", "long_x": "long_inc", 
        "mun_y": "mun", "lat_y": "lat_mun", "long_y": "long_mun"})

    # Recycling centre links dataframe
    if j_rec:

        u_jk = pd.DataFrame(j_rec, columns =['rec', 'mun'])
        u_jk_coord = pd.merge(coordinates, u_jk, how="inner", on=["mun"])
        links_rec_coord = pd.merge(coordinates, u_jk_coord, how="inner", 
                                    left_on=["mun"], right_on = ["rec"])
        links_rec_coord = links_rec_coord.sort_values(by=["rec"], ascending=True)
        links_rec_coord = links_rec_coord.drop(columns = "rec")    
        links_rec_coord = links_rec_coord.rename(
        columns = {"mun_x": "rec", "lat_x": "lat_rec", "long_x": "long_rec", 
        "mun_y": "mun", "lat_y": "lat_mun", "long_y": "long_mun"})

    # Indicate type of facility
    ts_new_coord["type"] = "ts_new"
    ts_exist_coord["type"] = "ts_existing"
    inc_coord["type"] = "incinerator"

    if x_k:
        rec_coord["type"] = "rec"
        coordinates_results = [ts_new_coord, ts_exist_coord, inc_coord, rec_coord,
                                rest_mun, links_ts_coord, links_inc_coord, 
                                links_rec_coord]
    else:
        coordinates_results = [ts_new_coord, ts_exist_coord, inc_coord, rest_mun, 
                            links_ts_coord, links_inc_coord]

    return coordinates_results

def create_folium(ts_new, ts_exist, inc, mun, w_jk, v_jl, r_centre = None, u_jk = None):

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

    # Create Portugal map instance
    portugal_map = folium.Map(location=centro_coord, zoom_start=8)

    # Add the feature groups to the map
    portugal_map.add_child(ts_group)
    portugal_map.add_child(ts_e_group)
    portugal_map.add_child(mun_group)
    portugal_map.add_child(inc_group)

    # Add recycling centres to the feature groups
    if isinstance(r_centre, pd.DataFrame):
        rec_group = folium.map.FeatureGroup(name = "Recycling centres")
        
        for lat, lng, in zip(r_centre.lat, r_centre.long):
            rec_group.add_child(
                folium.CircleMarker([lat, lng], radius=5, color='purple', 
                fill=True, fill_color='purple', fill_opacity=0.7))

        portugal_map.add_child(rec_group)

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

    if isinstance(u_jk, pd.DataFrame):
        u_jk_link = list(
        zip(zip(u_jk.lat_rec, u_jk.long_rec), zip(u_jk.lat_mun, u_jk.long_mun)))
        
        folium.PolyLine(
        u_jk_link, color="darkred", weight=1.5, opacity=1).add_to(portugal_map)

    # Return the map
    return portugal_map

def create_gis(ts_new, ts_exist, inc, w_jk, v_jl, r_centre = None, u_jk = None):

    # Load results data into a single dataframe
    if isinstance(r_centre, pd.DataFrame):
        results_df = pd.concat([ts_new, ts_exist, inc, r_centre], axis = 0)
    else:    
        results_df = pd.concat([ts_new, ts_exist, inc], axis = 0)
    
    w_jk = w_jk.rename(columns= {"ts": "fac", "lat_ts": "lat_fac", 
    "long_ts": "long_fac"})
    w_jk["type"] = "ts"
    v_jl = v_jl.rename(columns= {"inc": "fac", "lat_inc": "lat_fac", 
    "long_inc": "long_fac"})
    v_jl["type"] = "incinerator"
    links_df = w_jk.append(v_jl)

    # Get the Recycling centres and links information
    if isinstance(u_jk, pd.DataFrame):
        u_jk = u_jk.rename(columns= {"rec": "fac", "lat_rec": "lat_fac", 
                            "long_rec": "long_fac"})
        u_jk["type"] = "rec"
        links_df = links_df.append(u_jk)

    # Geopandas visualization
    shape_files = os.path.join(os.getcwd(), "Shapefiles")

    # Municipalities shapefiles
    mun = gp.read_file(os.path.join(shape_files, "ersucconc.shp"))
    topo = gp.read_file(os.path.join(shape_files, "ersucconc_topo.shp"))
    topo = topo.sort_values(by = "ORD_COD")
    topo["municipality"] = muns

    # Get all facilities geometries from shapefiles and convert to GeoDataFrame
    all_facs = pd.merge(results_df, topo, left_on="mun", 
    right_on = "municipality", how = "inner")
    all_facs = gp.GeoDataFrame(all_facs)

    # Get all links points
    links_tmp2 = pd.merge(links_df, topo, left_on="mun", 
    right_on="municipality")
    links_tmp2 = pd.merge(links_tmp2, topo, left_on="fac", 
    right_on = "municipality")

    # Create a list that contains the linestrings for all link ends
    links_list = []

    for i in range(0, links_tmp2.shape[0]):
        links_list.append(
            LineString(
                [Point(links_tmp2.X_COORD_x[i], links_tmp2.Y_COORD_x[i]), 
                Point(links_tmp2.X_COORD_y[i], links_tmp2.Y_COORD_y[i])]))

    n = w_jk.shape[0] + v_jl.shape[0]

    if isinstance(u_jk, pd.DataFrame):
        n += u_jk.shape[0]
    else:
        n = n

    links_gp = gp.GeoDataFrame(list(range(0, n)), geometry = links_list)

    render_issues = ["Vale de Cambra", "Arganil", "Pedrogao Grande"]
    topo_issues = topo[topo.municipality.isin(render_issues)]
    topo_no_issues = topo[~topo.municipality.isin(render_issues)]

    # Display geopandas plot
    fig, ax = plt.subplots(figsize = (10,10))
    mun.plot(ax =ax, alpha=0.35, edgecolor='k')
    topo.plot(ax = ax, markersize=10, color = "black", marker = "o", 
    label = "Municipalities")

    all_facs[all_facs["type"] == "incinerator"].plot(ax = ax, markersize=35, 
    color = "red", marker = "*", label = "Incinerator")

    all_facs[all_facs["type"] == "ts_new"].plot(ax = ax, markersize=35, 
    color = "blue", marker = "^", label = "New transfer station")

    all_facs[all_facs["type"] == "ts_existing"].plot(ax = ax, markersize=35, 
    color = "purple", marker = "^", label = "Existing transfer station")

    if isinstance(r_centre, pd.DataFrame):
        all_facs[all_facs["type"] == "rec"].plot(ax = ax, markersize=35, 
        color = "green", marker = "s", label = "Recycling centre")
    
    links_gp.plot(ax =ax, alpha = 0.5, color='brown', linestyle = "--")

    for x, y, label in zip(topo_no_issues.geometry.x, topo_no_issues.geometry.y, topo_no_issues.municipality):
        ax.annotate(label, xy=(x, y), xytext=(6, -7), textcoords="offset points", fontsize=7.5)

    for x, y, label in zip(topo_issues.geometry.x, topo_issues.geometry.y, topo_issues.municipality):
        ax.annotate(label, xy=(x, y), xytext=(6, -1), textcoords="offset points", fontsize=7.5)

    plt.legend(prop = {'size': 10}, loc = "lower right")

    return None

def create_gis_rec(r_centre, u_jk):

    # Load results data into a single dataframe
    results_df = r_centre

    # Get the Recycling centres and links information
    u_jk = u_jk.rename(columns= {"rec": "fac", "lat_rec": "lat_fac", 
                                "long_rec": "long_fac"})
    u_jk["type"] = "rec"
    links_df = u_jk

    # Geopandas visualization
    shape_files = os.path.join(os.getcwd(), "Shapefiles")

    # Municipalities shapefiles
    mun = gp.read_file(os.path.join(shape_files, "ersucconc.shp"))
    topo = gp.read_file(os.path.join(shape_files, "ersucconc_topo.shp"))
    topo = topo.sort_values(by = "ORD_COD")
    topo["municipality"] = muns

    # Get all facilities geometries from shapefiles and convert to GeoDataFrame
    all_facs = pd.merge(results_df, topo, left_on="mun", 
    right_on = "municipality", how = "inner")
    all_facs = gp.GeoDataFrame(all_facs)

    # Get all links points
    links_tmp2 = pd.merge(links_df, topo, left_on="mun", 
    right_on="municipality")
    links_tmp2 = pd.merge(links_tmp2, topo, left_on="fac", 
    right_on = "municipality")

    # Create a list that contains the linestrings for all link ends
    links_list = []

    for i in range(0, links_tmp2.shape[0]):
        links_list.append(
            LineString(
                [Point(links_tmp2.X_COORD_x[i], links_tmp2.Y_COORD_x[i]), 
                Point(links_tmp2.X_COORD_y[i], links_tmp2.Y_COORD_y[i])]))

    n = u_jk.shape[0]

    links_gp = gp.GeoDataFrame(list(range(0, n)), geometry = links_list)

    render_issues = ["Vale de Cambra", "Arganil", "Pedrogao Grande"]
    topo_issues = topo[topo.municipality.isin(render_issues)]
    topo_no_issues = topo[~topo.municipality.isin(render_issues)]

    # Display geopandas plot
    fig, ax = plt.subplots(figsize = (10,10))
    mun.plot(ax =ax, alpha=0.35, edgecolor='k')
    topo.plot(ax = ax, markersize=10, color = "black", marker = "o", 
    label = "Municipalities")

    all_facs[all_facs["type"] == "rec"].plot(ax = ax, markersize=35, 
            color = "green", marker = "s", label = "Recycling centre")
    
    links_gp.plot(ax =ax, alpha = 0.5, color='brown', linestyle = "--")

    for x, y, label in zip(topo_no_issues.geometry.x, topo_no_issues.geometry.y, topo_no_issues.municipality):
        ax.annotate(label, xy=(x, y), xytext=(6, -7), textcoords="offset points", fontsize=7.5)

    for x, y, label in zip(topo_issues.geometry.x, topo_issues.geometry.y, topo_issues.municipality):
        ax.annotate(label, xy=(x, y), xytext=(6, -1), textcoords="offset points", fontsize=7.5)

    plt.legend(prop = {'size': 10}, loc = "lower right")

    return None
