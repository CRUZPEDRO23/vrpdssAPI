# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 16:40:24 2023

@author: jose-
"""

import numpy as np


def NearestNeiborhold2ECVRP(avaibleRoutes: list, S: list, C: list, d_i: np.ndarray, cost_Matrix: np.ndarray, Clurster_s = None):
    
    if Clurster_s == None:
        candidates = C.copy()
    else:
        candidates = Clurster_s[avaibleRoutes[0].s]
    idxr = 0
    #print(candidates)
    #print(avaibleRoutes)
    #print(avaibleRoutes[0])
    Matrix = cost_Matrix.copy()
    for i in range(len(Matrix)):
        if i not in candidates: 
            #Matrix[i, :] = np.inf
            Matrix[:, i] = np.inf
        
    #Matrix[[0]+S, :] = np.inf
    #Matrix[:, [0]+S] = np.inf
    
    while len(candidates) and idxr < len(avaibleRoutes):
        p = avaibleRoutes[idxr].length() - 2
        lastC = avaibleRoutes[idxr].route[p]
        nextC = np.argmin(Matrix[lastC, :])
        while nextC not in candidates:
            Matrix[lastC, nextC] = np.inf
            nextC = np.argmin(Matrix[lastC, :])
            #print("avaliar", lastC, nextC, p, Matrix[lastC, nextC], nextC in candidates)
            break
        #print("avaliar", lastC, nextC, p, Matrix[lastC, nextC], nextC in candidates)
        if nextC == 0:
            idxr += 1
            continue
        if Matrix[lastC, nextC] != np.inf and avaibleRoutes[idxr].weight + d_i[nextC] <= avaibleRoutes[idxr].cap:
            # Atualizar atributos
            avaibleRoutes[idxr].weight += d_i[nextC]
            avaibleRoutes[idxr].cost += cost_Matrix[avaibleRoutes[idxr].route[p], nextC]
            avaibleRoutes[idxr].cost += cost_Matrix[nextC, avaibleRoutes[idxr].route[p+1]]
            avaibleRoutes[idxr].cost -= cost_Matrix[avaibleRoutes[idxr].route[p], avaibleRoutes[idxr].route[p+1]]
            
            avaibleRoutes[idxr].addi(i = nextC, p = avaibleRoutes[idxr].length()-1)
            
            Matrix[:, nextC] = np.inf
            candidates.remove(nextC)
            #print("added")
        else:
            Matrix[lastC, nextC] = np.inf
        
        
    return avaibleRoutes, candidates