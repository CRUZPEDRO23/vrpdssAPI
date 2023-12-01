# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 13:57:12 2023

@author: jose-
"""

###############################################################################
""" This file is a part of the Project of 2ECVRP of José Pedro and provides 
implementation of the Clarke and Wright (1964) savings functions for parallel 
(as in multiple route) savings heuristic. """
###############################################################################

import numpy as np


def find_ip(route: list, Cost_Matrix: np.ndarray, Candidates: list,  d_i, W, Q2):
    
    #addCost = lambda i, p: Cost_Matrix[route[p-1], i]+Cost_Matrix[i, route[p]]-Cost_Matrix[route[p-1], route[p]]
    addCostP = lambda i: Cost_Matrix[route[:-1], i]+Cost_Matrix[i, route[1:]]-Cost_Matrix[route[:-1], route[1:]]
    
    def permit(W, di, Q2):
        T = (W+di>Q2)
        return np.where(T==True, np.inf, 0) #List of routes impossivels
    
    bestI = -1
    bestP = -1
    bestCost = np.inf
    for i in Candidates:
        cost = addCostP(i)+permit(W, d_i[i], Q2)
        min_pos = cost.argmin()
        if cost[min_pos] < bestCost:
            bestCost = cost[min_pos]
            bestI = i
            bestP = min_pos+1
    
    return bestI, bestP


def insertion_init(Cost_Matrix: np.ndarray, d_i: np.ndarray, Q2, C: list, sat = 0, f_callback = find_ip):
    
    m_s = int(d_i.sum() / Q2)*2
    route = [sat] * (m_s+1)
    idxs = np.arange(1,m_s+1, 1)
    W = np.zeros(m_s)
    
    Candidates = C.copy()
    
    def idxP(p, idxs):
        for dx, i in enumerate(idxs):
            if p <= i:
                return dx
    while len(Candidates):
        W_ = np.array([W[idxP(p, idxs)] for p in range(1, len(route))])
        i, p = f_callback(route, Cost_Matrix, Candidates, d_i, W_, Q2)
        if i != -1:
            # Adicionar Cliente
            route.insert(p, i)
            #corrigir indxs e pesos
            idxp = idxP(p, idxs)
            idxs[idxp:]+=1
            W[idxp]+=d_i[i]
            Candidates.remove(i)
        else:
            # Adiciona mais um espaço para rotas
            route += [sat] * 3
            W = np.array(list(W)+[0]*3)
            idxs = np.array(list(idxs)+[i for i in range(idxs[-1]+1, idxs[-1]+1+3)])
        pass
    return [route[:i+1] if dx==0 else route[idxs[dx-1]:i+1] for dx, i in enumerate(idxs)]

def clarke_wright_savings_function(Cost_Matrix: np.ndarray, C:list, cd = 0):
    #print(C)
    N = len(C)
    #n = N-1
    n = N
    savings = [None]*int((n*n-n)/2)
    
    idx = 0
    for i_ in range(0,N):
        for j_ in range(i_+1,N):
            i = C[i_]
            j = C[j_]
            s = Cost_Matrix[i,cd]+Cost_Matrix[cd,j]-Cost_Matrix[i,j]
            savings[idx] = (s,-Cost_Matrix[i,j],i,j)
            idx+=1
    savings.sort(reverse=True)
    return savings 



def savings_init(Cost_Matrix: np.ndarray, d_i: np.ndarray, Q2, C: list, sat = 0, savings_callback=clarke_wright_savings_function):
    """
    Implementation of the basic savings algorithm / construction heuristic for
    capaciated vehicle routing problems with symmetric distances (see, e.g.
    Clarke-Wright (1964)). This is the parallel route version, aka. best
    feasible merge version, that builds all of the routes in the solution in
    parallel making always the best possible merge (according to varied savings
    criteria, see below).
    
    * Cost_Matrix is a numpy ndarray (or equvalent) of the full 2D distance matrix.
    * d_i         is a list of demands. d_i[0:n_sats] should be 0.0 as it is the depot and satellites.
    * Q2          is the capacity constraint limit for the identical vehicles.
    * C           is the customer list
    
    * optional savings_callback is a function of the signature:
        sorted([(s_11,x_11,i_1,j_1)...(s_ij,x_ij,i,j)...(s_nn,x_nn,n,n) ]) =
            savings_callback(D)
      where the returned (sorted!) list contains savings (that is, how much 
       solution cost approximately improves if a route merge with an edge
       (i,j) is made). This should be calculated for each i \in {1..n},
       j \\in {i+1..n}, where n is the number of customers. The x is a secondary
       sorting criterion but otherwise ignored by the savings heuristic.
      The default is to use the Clarke Wright savings criterion.
    
    Clarke, G. and Wright, J. (1964). Scheduling of vehicles from a central
     depot to a number of delivery points. Operations Research, 12, 568-81.
    """
    
    ignore_negative_savings = True
    
    ## 1. make route for each customer
    routes = [[i] for i in C]
    route_demands = d_i[C] if Q2 else [0]*len(C)
    
    try:
        ## 2. compute initial savings 
        savings = savings_callback(Cost_Matrix=Cost_Matrix, C=C, cd = sat)
        
        # zero based node indexing!
        #endnode_to_route = [0]+list(range(0,len(C)-1))
        endnode_to_route = list(range(len(C)))
        endnode_to_route = {i: endnode_to_route[idx] for idx, i in enumerate(C)}
        
        ## 3. merge
        # Get potential merges best savings first (second element is secondary
        #  sorting criterion, and it it ignored)
        #print("Clientes", C)
        #print(savings)
        for best_saving, _, i, j in savings:
            if ignore_negative_savings:
                cw_saving = Cost_Matrix[i,sat]+Cost_Matrix[sat,j]-Cost_Matrix[i,j]
                if cw_saving<0.0:
                    break
            
            left_route = endnode_to_route[i]
            right_route = endnode_to_route[j]
            #print("Inicio", routes, left_route, right_route, i, j)
            #print(endnode_to_route)
            #print(route_demands)
            # the node is already an internal part of a longer segment
            if ((left_route is None) or
                (right_route is None) or
                (left_route==right_route)):
                continue
            
            # check capacity constraint validity
            if Q2:
                merged_demand = route_demands[left_route]+route_demands[right_route]
                if merged_demand > Q2:
                    continue
            
            # update bookkeeping only on the recieving (left) route
            if Q2: 
                route_demands[left_route] = merged_demand
                route_demands[right_route] = None
            
            # merging is done based on the joined endpoints, reverse the 
            #  merged routes as necessary
            if routes[left_route][0]==i:
                routes[left_route].reverse()
            if routes[right_route][-1]==j:
                routes[right_route].reverse()
    
            # the nodes that become midroute points cannot be merged
            if len(routes[left_route])>1:
                endnode_to_route[ routes[left_route][-1] ] = None
            if len(routes[right_route])>1:
                endnode_to_route[ routes[right_route][0] ] = None
            
            # all future references to right_route are to merged route
            endnode_to_route[ routes[right_route][-1] ] = left_route
            
            # merge with list concatenation
            routes[left_route].extend( routes[right_route] )
            routes[right_route] = None
            
    except KeyboardInterrupt: # or SIGINT
        interrupted_sol = [[sat] + r + [sat] for r in routes if r != None]
        raise KeyboardInterrupt(interrupted_sol)
        
    return [[sat] + r + [sat] for r in routes if r != None]