# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 15:42:31 2023

@author: jose-
"""

import numpy as np
from copy import copy

def NearestNaiborhold(S: list, C: list, d_i: np.ndarray, cost_Matrix: np.ndarray, cv_s: dict, time_Matrix: np.ndarray, cHr_s: dict, CAPs = None):
    """
    Algoritmo se baseia em alocar os clientes com menor custo de delocamento (seja de ida seja de volta) aos satelites

    Parameters
    ----------
    S : list
        DESCRIPTION.
    C : list
        DESCRIPTION.
    d_i : np.ndarray
        DESCRIPTION.
    cost_Matrix : np.ndarray -> distances
        DESCRIPTION.
    CAPs : TYPE, optional list: [0, cap1, cap2, ....]: 0 cause central depot 0
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    """
    Matrix = copy(cost_Matrix)
    timeMatrix = copy(time_Matrix)
    
    # Distancias entre clientes são irrelevantes:
    for c in C:
        Matrix[c,C] = np.inf

    # Distancia do CD para qualquer lugar tb é irrelevante aq
    Matrix[0,:] = np.inf
    Matrix[:,0] = np.inf
    #for s in S:
        #timeMatrix[s][0,:] = np.inf
        #timeMatrix[s][:,0] = np.inf

    # Distancia entre satélites é irrelevante:
    for s in S:
        Matrix[s,S] = np.inf
        #timeMatrix[s][s,S] = np.inf

    # Calculo de custos:
    for s in S:
        Matrix[s, C] = Matrix[s, C] * cv_s[s]  +  timeMatrix[s][s, C] * cHr_s[s]
        Matrix[C, s] = Matrix[C, s] * cv_s[s]  +  timeMatrix[s][C, s] * cHr_s[s]
        
        #timeMatrix

    # Iniciar conjunto de retorno:
    Cluster_s = dict()
    for s in S:
        Cluster_s[s] = list()
    
    candidates = C.copy()
    
    while len(candidates):
        # Identificação de menor custo
        indexs = np.where(Matrix == np.amin(Matrix))
        idx1 = indexs[0][0] # Indice do minimo dentre linhas 
        idx2 = indexs[1][0] # Indice do minimo dentre colunas

        if idx1 in S: # Indice 1 é satelite -> Menor custo na ida
            s = idx1
            c = idx2
        else: # Indice 1 é cliente -> Menor custo na volta
            c = idx1
            s = idx2
        
        # Impossibilitar reavaliação da coordenada / indexs
        Matrix[c, :] = np.inf
        Matrix[:, c] = np.inf

        if CAPs == None:
            Cluster_s[s].append(c)
            candidates.remove(c)
        elif CAPs[s] - d_i[c] >= 0:    
            CAPs[s] -= d_i[c]
            Cluster_s[s].append(c)
            candidates.remove(c)


    return Cluster_s


#S = [1, 2]
#C = [i for i in range(len(S)+1,len(S)+7)]
#d_i = np.array([1 if i in C else 0 for i in [0]+S+C])
#cost_Matrix = np.random.rand(len(S+C)+1, len(S+C)+1)

#CAPs = [d_i.sum() / (len(S)*0.8)  if s in S else 0 for s in [0] + S]

#print(NearestNaiborhold(S, C, d_i, cost_Matrix, CAPs=CAPs))
def NearestNaiborhold_old(S: list, C: list, d_i: np.ndarray, cost_Matrix: np.ndarray, CAPs = None):
    """
    

    Parameters
    ----------
    S : list
        DESCRIPTION.
    C : list
        DESCRIPTION.
    d_i : np.ndarray
        DESCRIPTION.
    cost_Matrix : np.ndarray -> distances
        DESCRIPTION.
    CAPs : TYPE, optional list: [0, cap1, cap2, ....]: 0 cause central depot 0
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    """
    


    Cluster_s = dict()
    for s in S:
        Cluster_s[s] = list()
    
    if CAPs == None:
        for c in C:
            Matrix = cost_Matrix[c, S]
            s = np.argmin(Matrix) + 1 # +1 cause centrak depot
            Cluster_s[s].append(c)
    
        return Cluster_s
    else:
        
        candidates = C.copy()
        cost_Matrix[:, [0]+C] = np.inf
        cost_Matrix[[0]+S, :] = np.inf
        Matrix = cost_Matrix
        while len(candidates):
            c = np.argmin(Matrix, axis=1)# return candidate nearest
            costs = np.min(Matrix, axis=1)
            c = np.argmin(costs)
            s = np.argmin(Matrix[c, :])
            
            #s = np.argmin(Matrix[c, :])
            while CAPs[s] - d_i[c] < 0:
                Matrix[c, s] = np.inf
                c = np.argmin(Matrix, axis=1)# return candidate nearest
                costs = np.min(Matrix, axis=1)
                c = np.argmin(costs)
                s = np.argmin(Matrix[c, :])
            CAPs[s] -= d_i[c]
            Cluster_s[s].append(c)
            candidates.remove(c)
            Matrix[c][:] = np.inf
            
        return Cluster_s

#S = [1, 2]
#C = [i for i in range(len(S)+1,len(S)+7)]
#d_i = np.array([1 if i in C else 0 for i in [0]+S+C])
#cost_Matrix = np.random.rand(len(S+C)+1, len(S+C)+1)

#CAPs = [d_i.sum() / (len(S)*0.8)  if s in S else 0 for s in [0] + S]

#print(NearestNaiborhold(S, C, d_i, cost_Matrix, CAPs=CAPs))
