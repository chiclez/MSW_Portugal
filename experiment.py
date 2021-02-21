# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
from pyomo.environ import *

def get_dict():

    currDir = os.getcwd()
    dataAntunes = os.path.join(currDir, 'data_antunes.xls')

    antunesSheet0 = pd.read_excel(dataAntunes, sheet_name=0, header = 1)
    antunesSheet1 = pd.read_excel(dataAntunes, sheet_name=1, header = 2)
    antunesSheet2 = pd.read_excel(dataAntunes, sheet_name=2, header = 2)
    antunesSheet4 = pd.read_excel(dataAntunes, sheet_name=4, header = None)
    antunesSheet5 = pd.read_excel(dataAntunes, sheet_name=5, header = 2)
    antunesSheet6 = pd.read_excel(dataAntunes, sheet_name=6, header = 2)

    municipalities = antunesSheet0.copy()
    municipalities = municipalities.drop(columns = ["ORD_COD", "Q (ton/dia)", "Q (ton/ano)", "Pop 2001", "ET exist.", "ET assign."])

    q_j_init = antunesSheet0.copy()
    q_j_init = q_j_init.drop(columns = ["ORD_COD", "Concelho", "Q (ton/dia)", "Pop 2001", "ET exist.", "ET assign."])

    distmatrix1 = antunesSheet1.copy()
    d_jk_d_jl_init = distmatrix1.drop(columns = ["Unnamed: 0"])

    distmatrix2 = antunesSheet2.copy()
    d_kl_init = distmatrix2.drop(columns = ["Unnamed: 0"])

    # Take the transposed matrix instead as wjk0 an f_jk_f_jl are not symmetric
    w_jk0_init = antunesSheet4.copy()
    w_jk0_init = w_jk0_init.T

    f_jk_f_jl_init = antunesSheet5.copy()
    f_jk_f_jl_init = f_jk_f_jl_init.drop(columns = ["Unnamed: 0"])
    f_jk_f_jl_init = f_jk_f_jl_init.T

    g_kl_init = antunesSheet6.copy()
    g_kl_init = g_kl_init.drop(columns = ["Unnamed: 0"])

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

def get_data(demax, dlmax):

    currDir = os.getcwd()
    dataAntunes = os.path.join(currDir, 'data_antunes.xls')

    antunesSheet0 = pd.read_excel(dataAntunes, sheet_name=0, header = 1)
    antunesSheet1 = pd.read_excel(dataAntunes, sheet_name=1, header = 2)
    antunesSheet2 = pd.read_excel(dataAntunes, sheet_name=2, header = 2)
    antunesSheet4 = pd.read_excel(dataAntunes, sheet_name=4, header = None)
    antunesSheet5 = pd.read_excel(dataAntunes, sheet_name=5, header = 2)
    antunesSheet6 = pd.read_excel(dataAntunes, sheet_name=6, header = 2)

    municipalities = antunesSheet0.copy()
    municipalities = municipalities.drop(columns = ["ORD_COD", "Q (ton/dia)", "Q (ton/ano)", "Pop 2001", "ET exist.", "ET assign."])

    q_j_init = antunesSheet0.copy()
    q_j_init = q_j_init.drop(columns = ["ORD_COD", "Concelho", "Q (ton/dia)", "Pop 2001", "ET exist.", "ET assign."])

    distmatrix1 = antunesSheet1.copy()
    d_jk_d_jl_init = distmatrix1.drop(columns = ["Unnamed: 0"])
    d_jk_d_jl_init.columns = list(range(0, 36))

    distmatrix2 = antunesSheet2.copy()
    d_kl_init = distmatrix2.drop(columns = ["Unnamed: 0"])

    w_jk0_init = antunesSheet4.copy()

    # Create f_jk_f_jl matrices: 
    # If the distances between municipalities and transfer stations  d_jk <= demax or w_jk =1, then 1. Else, 0.
    f_jk_f_jl_init = d_jk_d_jl_init.copy()

    w_jk0_init.sort_index(inplace=True) == d_jk_d_jl_init.sort_index(inplace = True)

    f_jk_f_jl_init[(f_jk_f_jl_init <= demax) | (w_jk0_init == 1)] = 1
    f_jk_f_jl_init[f_jk_f_jl_init != 1]= 0
    f_jk_f_jl_init = f_jk_f_jl_init.astype(int)

    f_jk_f_jl_init_orig = antunesSheet5.copy().drop(columns = ["Unnamed: 0"])
    f_jk_f_jl_init_orig.columns = list(range(0, 36))

    f_jk_f_jl_init_orig.to_csv("f_jk_orig.csv")
    f_jk_f_jl_init.to_csv("f_jk_test.csv")

    # Take the transposed matrix instead as wjk0 an f_jk_f_jl are not symmetric 
    w_jk0_init = w_jk0_init.T
    f_jk_f_jl_init = f_jk_f_jl_init.T

    # Create g_kl matrix: 
    # If the distances between transfer stations to incinerator d_kl <= dlmax, then 1. Else, 0.
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

    #coords = [(40.577888919067725, -8.446480749721951)]

    # create final dictionaries
    q_j_dict = dict(zip(mun_list, q_j_list))
    d_jk_d_jl_dict = dict(zip(base_keys, d_jk_d_jl_list))
    d_kl_dict = dict(zip(base_keys, d_kl_list))
    w_jk0_dict = dict(zip(base_keys, w_jk0_list))
    f_jk_f_jl_dict = dict(zip(base_keys, f_jk_f_jl_list))
    g_kl_dict = dict(zip(base_keys, g_kl_list))
    #coord_dict = dict(zip(mun_list, coords))

    return q_j_dict, d_jk_d_jl_dict, d_kl_dict, w_jk0_dict, f_jk_f_jl_dict, g_kl_dict

def get_coord(y, z, j_ts, l_inc):

    # Read the coordinates list
    coordinates = pd.read_csv("coordinates.csv")

    # Transfer stations coordinates
    df_y = pd.DataFrame(y, columns =['mun'])
    ts_coord = pd.merge(coordinates, df_y, how="inner", on=["mun"])

    # Incinerator coordinates
    df_z = pd.DataFrame(z, columns =['mun']) 
    inc_coord = pd.merge(coordinates, df_z, how="inner", on=["mun"])

    # Rest of municipalities: Not TS, not inc
    all_fac = pd.merge(df_y, df_z, how = "outer", on = ["mun"])
    centro = pd.merge(coordinates, all_fac, on=['mun'], how='left', indicator=True)
    rest_mun = centro.loc[centro["_merge"] == "left_only"]

    # Transfer station links dataframe
    w_jk = pd.DataFrame(j_ts, columns =['ts', 'mun']) 

    w_jk_coord = pd.merge(coordinates, w_jk, how="inner", on=["mun"])
    links_ts_coord = pd.merge(coordinates, w_jk_coord, how="inner", left_on=["mun"], right_on = ["ts"])
    links_ts_coord = links_ts_coord.sort_values(by=["ts"], ascending=True)
    links_ts_coord = links_ts_coord.drop(columns = "ts")    
    links_ts_coord = links_ts_coord.rename(columns = {"mun_x": "ts", "lat_x": "lat_ts", "long_x": "long_ts", "mun_y": "mun", "lat_y": "lat_mun", "long_y": "long_mun"})

    # Incinerator links dataframe
    v_jl = pd.DataFrame(l_inc, columns =['inc', 'mun'])
    v_jl_coord = pd.merge(coordinates, v_jl, how="inner", on=["mun"])
    links_inc_coord = pd.merge(coordinates, v_jl_coord, how="inner", left_on=["mun"], right_on = ["inc"])
    links_inc_coord = links_inc_coord.sort_values(by=["inc"], ascending=True)
    links_inc_coord = links_inc_coord.drop(columns = "inc")    
    links_inc_coord = links_inc_coord.rename(columns = {"mun_x": "inc", "lat_x": "lat_inc", "long_x": "long_inc", "mun_y": "mun", "lat_y": "lat_mun", "long_y": "long_mun"})

    return ts_coord, inc_coord, rest_mun, links_ts_coord, links_inc_coord

def get_coord2(y, z, j_ts, l_inc, exist_ts):

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
    all_fac_coord = pd.merge(all_fac, coordinates, how = "inner", on = ["mun"])

    # Existing ts
    df_exist_ts = pd.DataFrame(exist_ts, columns =['mun'])
    ts_exist_coord = pd.merge(coordinates, df_exist_ts, how="inner", on=["mun"])

    ts_new_coord = pd.merge(ts_all_coord, ts_exist_coord, how="left", on=["mun"], indicator= True)
    ts_coord = ts_new_coord.loc[ts_new_coord["_merge"] == "left_only"]
    ts_coord = ts_coord.rename(columns = {"lat_x": "lat", "long_x": "long"})
    ts_coord = ts_coord.drop(columns = ["lat_y", "long_y", "_merge"])

    print(ts_coord)

    # Rest of municipalities: Not TS, not inc
    centro = pd.merge(coordinates, all_fac, on=['mun'], how='left', indicator=True)
    rest_mun = centro.loc[centro["_merge"] == "left_only"]

    # Transfer station links dataframe
    w_jk = pd.DataFrame(j_ts, columns =['ts', 'mun']) 

    w_jk_coord = pd.merge(coordinates, w_jk, how="inner", on=["mun"])
    links_ts_coord = pd.merge(coordinates, w_jk_coord, how="inner", left_on=["mun"], right_on = ["ts"])
    links_ts_coord = links_ts_coord.sort_values(by=["ts"], ascending=True)
    links_ts_coord = links_ts_coord.drop(columns = "ts")    
    links_ts_coord = links_ts_coord.rename(columns = {"mun_x": "ts", "lat_x": "lat_ts", "long_x": "long_ts", "mun_y": "mun", "lat_y": "lat_mun", "long_y": "long_mun"})

    # Incinerator links dataframe
    v_jl = pd.DataFrame(l_inc, columns =['inc', 'mun'])
    v_jl_coord = pd.merge(coordinates, v_jl, how="inner", on=["mun"])
    links_inc_coord = pd.merge(coordinates, v_jl_coord, how="inner", left_on=["mun"], right_on = ["inc"])
    links_inc_coord = links_inc_coord.sort_values(by=["inc"], ascending=True)
    links_inc_coord = links_inc_coord.drop(columns = "inc")    
    links_inc_coord = links_inc_coord.rename(columns = {"mun_x": "inc", "lat_x": "lat_inc", "long_x": "long_inc", "mun_y": "mun", "lat_y": "lat_mun", "long_y": "long_mun"})

    return ts_coord, ts_exist_coord, inc_coord, rest_mun, links_ts_coord, links_inc_coord

"""
Created on Wed Feb 10 22:13:16 2021
Modified on Mon Feb 15 15:52:00 2021
@author: franc, mariel
"""

# Max distances
demax = 25
dlmax = 125

# Bring the data as dictionaries
q_j, dist_jk_dist_jl, dist_kl, w_jk0, f_jk_f_jl, g_kl = get_data(demax, dlmax)

# q_j, dist_jk_dist_jl, dist_kl, w_jk0, f_jk_f_jl, g_kl = get_dict() # "Hard-coded" f_jk_f_jl and g_kl from Excel

# Parameters
c_c = 0.045
c_u = 0.128571

q = 493534.8

s_k = 204400
m = 1E6

# Step 0: Instantiate a model object
model = ConcreteModel()
model.dual = Suffix(direction=Suffix.IMPORT)

# Step 1: Define index sets
J = list(q_j.keys())
K = list(q_j.keys())
L = list(q_j.keys())
J1 = ["Arouca", "Estarreja", "Oliveira de Azemeis", "Sao Joao da Madeira", "Sever do Vouga", "Gois", "Lousa", "Pampilhosa da Serra", "Penela", "Vila Nova Poiares", "Ansiao", "Castanheira de Pera", "Pedrogao Grande"]
K1 = ["Estarreja", "Oliveira de Azemeis", "Sever do Vouga", "Gois", "Pampilhosa da Serra", "Ansiao"]

# Step 2: Define the decision variables
model.w_jk = Var(J, K, within= Binary)
model.v_jl = Var(J, L, within=Binary)
model.y_k = Var(K, within=Binary)
model.z_l = Var(L, within=Binary)
model.x_kl = Var(K,L, domain = NonNegativeReals)

# Step 3: Objective function
def obj_rule(model):
    return sum( c_u * dist_jk_dist_jl[j,k] * q_j[j] * model.w_jk[j,k] for j in J for k in K)+\
        sum( c_u * dist_jk_dist_jl[j,l] * q_j[j] * model.v_jl[j,l] for j in J for l in L)+\
        sum( c_c * dist_kl[k,l] * model.x_kl[k,l] for k in K for l in L)+ sum( m*model.y_k[k] for k in K)

model.Cost = Objective(rule=obj_rule, sense = minimize)

# Step 4: Constraints              
def rule_1(model,J):
    return sum( model.w_jk[J,k] for k in K ) + \
           sum( model.v_jl[J,l] for l in L ) == 1 
    
def rule_2(model,K):
    return sum( q_j[j]*model.w_jk[j, K] for j in J ) == sum( model.x_kl[K,l] for l in L )  
    
def rule_3(model,J,K):
    return model.w_jk[J,K] <= f_jk_f_jl[J,K]*model.y_k[K]

def rule_4(model,J,L):
    return model.v_jl[J,L] <= f_jk_f_jl[J,L]*model.z_l[L]
   
def rule_5(model,K,L):
    return model.x_kl[K,L] <= g_kl[K,L]*q*model.z_l[L]

def rule_6(model,K):
    return sum(q_j[j]*model.w_jk[j,K] for j in J)<=s_k*model.y_k[K]

def rule_7(model):
    return sum(model.z_l[l] for l in L)==1

def rule_8(model, J1, K1):
    return model.w_jk[J1,K1] == w_jk0[J1, K1]

def rule_9(model): #experiment, incinerator not in Agueda
    return (model.z_l["Agueda"] == 0)

def rule_10(model): #experiment, incinerator not in Mealheada
    return (model.z_l["Mealhada"] == 0)

def rule_11(model): #experiment, incinerator not in Anadia
    return (model.z_l["Anadia"] == 0)

model.C_1 = Constraint( J, rule=rule_1 )
model.C_2 = Constraint( K, rule=rule_2 )
model.C_3 = Constraint( J, K, rule=rule_3 )
model.C_4 = Constraint( J, L, rule=rule_4 )
model.C_5 = Constraint( K, L, rule = rule_5)
model.C_6 = Constraint( K, rule = rule_6 )
model.C_7 = Constraint( rule = rule_7)
model.C_8 = Constraint(J1, K1, rule = rule_8) 
#model.C_9 = Constraint( rule = rule_9) # experiment, incinerator not in Agueda
#model.C_10 = Constraint( rule = rule_10) # experiment, incinerator not in Mealhada
#model.C_11 = Constraint( rule = rule_11) # experiment, incinerator not in Anadia

results = SolverFactory('amplxpress').solve(model)
#results.write()

# Solution
header = "Transfer stations"
print(f"\n{header}")
print(f"="*len(header))

for k in K:
    if(model.y_k[k]() == 1):
        print(k, model.y_k[k]())

for l in L:
    if(model.z_l[l]() == 1):
        print("Incinerator is in: ", l, model.z_l[l]())
        
if 'ok' == str(results.Solver.status):
    t_cost = round(model.Cost() - m*sum(model.y_k[k]() for k in K), 2)
    print("Optimal value = €", round(model.Cost(), 2))
    print("Transportation costs = €", t_cost)
else:
    print("No Valid Solution Found")

# Sensitivity analysis

#Map
y = []
z = []
links_ts = []
links_inc = []

for k in K:
    if(model.y_k[k]() == 1):
        y.append(k)

for l in L:
    if(model.z_l[l]() == 1):
        z.append(l)

for k in K:
    for j in J:
        if(model.w_jk[j, k]() == 1):
            links_ts.append((k, j))

for l in L:
    for j in J:
        if(model.v_jl[j, l]() == 1):
            links_inc.append((l, j))

ts_new, ts_exist, inc, mun, w_jk, v_jl = get_coord2(y, z, links_ts, links_inc, K1)
