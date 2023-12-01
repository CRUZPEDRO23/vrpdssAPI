# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 15:42:31 2023

@author: jose-
"""

import numpy as np

def NearestNaiborholdFull(S: list, C: list, d_i: np.ndarray, cost_Matrix: np.ndarray, CAPs = None):
    """
    

    Parameters
    ----------
    S : list
        DESCRIPTION.
    C : list
        DESCRIPTION.
    d_i : np.ndarray
        DESCRIPTION.
    cost_Matrix : np.ndarray
        DESCRIPTION.
    CAPs : TYPE, optional list: [0, cap1, cap2, ....]: 0 cause central depot 0
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    """
    
    
    _cost_Matrix = 0.5 * (
        cost_Matrix[S[0]:S[-1]+1, C[0]:C[-1]+1] + np.transpose(cost_Matrix[C[0]:C[-1]+1, S[0]:S[-1]+1]))
    
    _cost_Matrix += np.array([[i] * len(C) for i in 0.5 * ( 
        cost_Matrix[S[0]:S[-1]+1, 0] + np.transpose(cost_Matrix[0, S[0]:S[-1]+1]))])
    #print(len(S), len(C), np.shape(_cost_Matrix))
    
    Cluster_s = dict()
    for s in S:
        Cluster_s[s] = list()
    
    if CAPs == None:
        for c in C:
            Matrix = cost_Matrix[c-1-len(S), S]
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
