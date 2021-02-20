# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 22:13:16 2021

@author: franc
"""
import os
import pandas as pd
from pyomo.environ import *

path = 'C:\\Users\\franc\\Desktop\\moselfaker\\10feb\\data_antunes.xlsx'

xl_file = pd.ExcelFile("data_antunes.xlsx")

#dfs = pd.read_excel("data_antunes.xlsx", sheet_name=None)

dfs = {sheet_name: xl_file.parse(sheet_name) 
          for sheet_name in xl_file.sheet_names}

model = ConcreteModel()

data = DataPortal()
data.load(filename='output.csv')

J = ["Harlingen", "Memphis", "Ashland"]
L=K=J

model.w_jk = Var(J, K, within=Binary)
model.v_jl = Var(J, L, within=Binary)
model.y_k = Var(K, within=Binary)
model.z_l = Var(L, within=Binary)
model.x_kl = Var(K,L, domain = NonNegativeReals)

model.w_jk0 = Param(J,K)
model.f_jk = Param(J,K)
model.f_jl = Param(J,L)
model.g_kl = Param(K,L)

model.q_j = Param(J, domain = NonNegativeReals)
model.q = 
s_k...

def obj_rule(model):
    return sum( c_u * dist_jk[j,k] * q_j[j] * w_jk[j,k] for j in J for k in K)+\ 
           sum( c_u * dist_jl[j,l] * q_j[j] * v_jl[j,l] for j in J for l in L)+\
           sum( c_c * dist_kl[k,l] * x_kl[k,l] for k in K for l in L)+\
           sum( m*y_[k] for k in K)

model.obj = Objective(rule=obj_rule)

                     
def rule_1(model,j):
    return sum( model.w_jk[j,k] for k in model.K ) + \
           sum( model.v_jl[j,l] for l in model.L ) == 1 
    
def rule_2(model,k):
    return sum( model.q_j[j]*w_jk[j,k] for j in model.J ) == \
           sum( model.x_kl[k,l] for l in model.L )  
    
def rule_3(model,j,k):
    return w_jk[j,k] <= f_jk[j,k]*y_k[k]

def rule_4(model,j,l):
    return v_jl[j,l] <= f_jl[j,l]*z_l[l]
   
def rule_5(model,k,l):
    return x_kl[k,l] <= g_kl[k,l]*q*z_l[l]

def rule_6(model,k):
    return sum(q_j[j]*w_jk[j,k] for j in model.J)<=s_k*y_k[k]

def rule_7(model):
    return sum(z_l[l] for l in model.L)==1

model.C_1 = Constraint( model.J, rule=rule_1 )
model.C_2 = Constraint( model.K, rule=rule_2 )
model.C_3 = Constraint( model.J, model.K, rule=rule_3 )
model.C_4 = Constraint( model.J, model.L, rule=rule_4 )
model.C_5 = Constraint( model.K, model.L, rule = rule_5)
model.C_6 = Constraint( model.K, rule = rule_6 )
model.C_7 = Constraint( rule = rule_7)