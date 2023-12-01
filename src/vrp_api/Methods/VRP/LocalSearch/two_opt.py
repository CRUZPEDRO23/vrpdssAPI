# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 18:51:14 2023

@author: jose-
"""
import numpy as np
#from time import time

def calculate_distance(route: list[int], dist_matrix: np.ndarray) -> float:
    return dist_matrix[np.roll(route, 1), route].sum()

def calculate_distance2(route: list[int], dist_matrix: np.ndarray) -> float:
    return dist_matrix[np.roll(route, 1), route]

"""
def two_opt_(route, idxs, cap, d_i, dist_matrix):
    best = route.copy()
    bestidxs = idxs.copy()
    improved = True
    
    while improved:
        
        improved = False
        idxi = 0
        
        for i in range(1, len(route) - 2):
            if i > idxs[idxi]:
                idxi += 1
            # Realiza interação com rota vizinha
            idxj = 0
            for j in range(i + 2, len(route)):
                if j - i == 1: continue  # changes nothing, skip then
                while j > idxs[idxj]:
                    idxj += 1
                
                new_route = route[:]    # Creates a copy of route
                new_route[i:j] = route[j - 1:i - 1:-1]  # this is the 2-optSwap since j >= i we use -1
                
                # Verificar se muda cliente de rotas:
                # Restricao de capacidade
                _l = idxs.copy()
                auxiliar = False
                if j >= idxs[idxi]:  # Trabalhando na rota diferente que i inicia
                    # Posicao do satélite após inversão:
                    _l[idxi:idxj] = i + (j - 1 - idxs[idxi:idxj])
                    _l = np.sort(_l)
                    for indxK in range(len(idxs)):
                        if indxK == 0:
                            r = new_route[:_l[indxK]+1]
                        else:
                            r = new_route[_l[indxK-1]:_l[indxK]+1]
                        if d_i[r].sum() > cap:
                            auxiliar = True
                            break
                            #continue
                                
                    if auxiliar: 
                        continue
                    # print(_l, idxs)
                    # Nao desobedeceu restricao de capacidade:
                    
                    
                if not auxiliar and calculate_distance(new_route, dist_matrix=dist_matrix) < calculate_distance(best, dist_matrix=dist_matrix):
                    
                    if list(_l) != list(idxs):
                        idxs = _l.copy()
                    
                    best = new_route.copy()
                    bestidxs = idxs.copy()
                    improved = True
                    route = best.copy()
                    break
                
            if improved: break
    return best



def two_opt__(route, idxs, cap, d_i, dist_matrix, ALL = False):
    best = route.copy()
    bestidxs = idxs.copy()
    anyBest = False
    improved = True
    melhoriaAcumulada = 0
    
    while improved:
        
        improved = False
        idxi = 0
        node_start_Route = 0
        node_end_Route = bestidxs[idxi]
        node_end_nestRoute = bestidxs[idxi+1] if idxi+1 < len(bestidxs) else node_end_Route
        
        for i in range(1, len(route) - 2):
            if i > node_end_Route:
                idxi += 1
                node_start_Route = node_end_Route
                node_end_Route = bestidxs[idxi]
                node_end_nestRoute = bestidxs[idxi+1] if idxi+1 < len(bestidxs) else node_end_Route
    
            # Realiza interação com rota vizinha
            for j in range(i + 1, node_end_nestRoute):
                if j - i == 1: continue  # changes nothing, skip then
                
                new_route = best[:]    # Creates a copy of route
                
                # Validar Melhoria de custo:
                if (dist_matrix[best[i-1], best[j-1]] + dist_matrix[best[i], best[j]]) - (dist_matrix[best[i-1], best[i]] + dist_matrix[best[j-1], best[j]]) >= 0 :
                    continue
                
                newReverseRoute = best[j - 1:i - 1:-1]
                new_route[i:j] = newReverseRoute  # this is the 2-optSwap since j >= i we use -1
                    
                # Verificar se muda cliente de rotas:
                # Restricao de capacidade
                _l = -1
                if j > node_end_Route:  # Trabalhando na rota diferente que i inicia
                    # Posicao do satélite após inversão:
                    #_l = (j-1) - (node_end_Route - i)
                    _l = i + (j - 1 - node_end_Route)
                    
                    if d_i[new_route[node_start_Route:_l+1]].sum() > cap:
                        continue
                    if d_i[new_route[_l:node_end_nestRoute+1]].sum() > cap:
                        continue
                MELHORIA = calculate_distance(new_route, dist_matrix=dist_matrix) - calculate_distance(best, dist_matrix=dist_matrix)
                if MELHORIA < 0:
                    
                    if _l != -1:
                        idxs[idxi] = _l
                        node_end_Route = _l
                    #print(_l, len(route))
                    improved = True
                    #idxs[0] = _l
                    #print("PASS HERE")
                    best = new_route.copy()
                    bestidxs = idxs.copy()
                    anyBest = MELHORIA < 0
                    melhoriaAcumulada += MELHORIA
                    
                    route = best.copy()
                    
                    #print(best)
                    #print(MELHORIA)
                    
                if improved: break 
            if improved: break 
        
    if ALL: 
        return best, bestidxs, melhoriaAcumulada, anyBest
    return best



"""


def two_opt(route, idxs, cap, d_i, dist_matrix, ALL = False):
    best = route.copy()
    bestidxs = idxs.copy()
    improved = True
    melhoriaAcumulada=0
    anyBest=False
    
    #print("inicial route", best)
    #print("inicial idxs", idxs)
    while improved:
        
        improved = False
        idxi = 0
        node_start_Route = 0
        node_end_Route = bestidxs[idxi]
        node_end_nestRoute = bestidxs[idxi+1] if idxi+1 < len(bestidxs) else node_end_Route
        
        for i in range(1, len(route) - 2):
            if i > node_end_Route:
                idxi += 1
                node_start_Route = node_end_Route
                node_end_Route = bestidxs[idxi]
                node_end_nestRoute = bestidxs[idxi+1] if idxi+1 < len(bestidxs) else node_end_Route
            #for j in range(i + 1, len(route)):
            # Realiza interação com rota vizinha
            for j in range(i + 1, node_end_nestRoute):
                if j - i == 1: continue  # changes nothing, skip then
                
                new_route = route[:]    # Creates a copy of route
                new_route[i:j] = route[j - 1:i - 1:-1]  # this is the 2-optSwap since j >= i we use -1
                
                # Verificar se muda cliente de rotas:
                    # Restricao de capacidade
                _l = -1
                if j > node_end_Route:  # Trabalhando na rota diferente que i inicia
                    # Posicao do satélite após inversão:
                    _l = (j-1) - (node_end_Route - i)
                    _l = i + (j - 1 - node_end_Route)
                    
                    if d_i[new_route[node_start_Route:_l+1]].sum() > cap:
                        continue
                    if d_i[new_route[_l:node_end_nestRoute+1]].sum() > cap:
                        continue
                    
                    # Nao desobedeceu restricao de capacidade:
                    
                #Melhoria = calculate_distance(new_route, dist_matrix=dist_matrix) - calculate_distance(best, dist_matrix=dist_matrix)
                
                M = calculate_distance2(new_route, dist_matrix=dist_matrix) - calculate_distance2(best, dist_matrix=dist_matrix)
                
                #if calculate_distance(new_route, dist_matrix=dist_matrix) < calculate_distance(best, dist_matrix=dist_matrix):
                if M.sum()<0:    
                    if _l != -1:
                        #print("iteracao", i, j, node_start_Route, node_end_Route, _l, node_end_nestRoute)
                        #print(new_route[i:j])
                        #print(new_route[node_start_Route:_l+1])
                        #print(new_route[_l:node_end_nestRoute+1])
                        #print(d_i[new_route[node_start_Route:_l]].sum(), d_i[new_route[_l:node_end_nestRoute]].sum())
                        #
                        #print("Valores aceitos:", cap)
                        #print("rota1", new_route[node_start_Route:_l+1], d_i[new_route[node_start_Route:_l+1]].sum())
                        #print("rota2", new_route[_l:node_end_nestRoute+1], d_i[new_route[_l:node_end_nestRoute+1]].sum())
                        
                        
                        idxs[idxi] = _l
                        node_end_Route = _l
                    
                    best = new_route.copy()
                    bestidxs = idxs.copy()
                    improved = True
                    route = best.copy()
                    anyBest = True
                    melhoriaAcumulada += M.sum()
                    #print("actual route", best)
                    #print("actual idxs", idxs)
                    
                    #if _l!=-1: print("rota", best)
                if improved: break
            if improved: break
    
    if ALL:
        return best, bestidxs, melhoriaAcumulada, anyBest
    return best

def two_opt_Extra(route, idxs, cap, d_i, dist_matrix, returnALL = False):
    #T = time()    
    MEMORIA = list()
    #print("r", route)
    #print("i", idxs)
    improved = True
    anyimproved = False
    #old__ = route.copy()
    
    bestImproved = 0
    
    while improved:
        improved = False
        for idx1 in range(len(idxs)):
            boolAnyEmpytRoute = idxs[idx1] - idxs[idx1-1] == 1
            if boolAnyEmpytRoute:
                continue
            for idx2 in range(idx1+1, len(idxs)):
                if (idx1, idx2) in MEMORIA:
                    continue
                r1 = route[:idxs[idx1]+1].copy() if idx1 == 0 else route[idxs[idx1-1]:idxs[idx1]+1].copy()
                r2 = route[idxs[idx2-1]:idxs[idx2]+1].copy()
                if boolAnyEmpytRoute or (len(r1)==2 and len(r2)==2):
                    continue
                if len(r1)==2 or len(r2)==2:
                    boolAnyEmpytRoute = True
                
                route_ = r1[:-1] + r2
                idxs_ = [len(r1)-1, len(r1)-1+len(r2)-1]
                #print("Teste", idx1, idx2, route_, idxs_)
                
                best, bestidxs, melhoriaAcumulada, anyBest = two_opt(route=route_.copy(), idxs=idxs_.copy(), cap=cap, d_i = d_i, dist_matrix = dist_matrix, ALL= True)
                
                #if calculate_distance(best, dist_matrix=dist_matrix) < calculate_distance(route_, dist_matrix=dist_matrix):
                if anyBest:#melhoriaAcumulada<0 and 
                    #print("Melhroria", calculate_distance(best, dist_matrix=dist_matrix),  calculate_distance(route_, dist_matrix=dist_matrix))
                    #print(calculate_distance(route_, dist_matrix=dist_matrix) - calculate_distance(best, dist_matrix=dist_matrix))
                    
                    # Verificar se NP nao ta tentando roubar
                    
                    
                    
                    #print("Validar Melhoria 2opt*")
                    #bestImproved += melhoriaAcumulada
                    #print("melhoriaAcumulada", melhoriaAcumulada)
                    
                    #print(best[:bestidxs[0]])
                    #print(route[idxs[idx1]:idxs[idx2-1]])
    
                    if idx1 == 0:
                        route = best[:bestidxs[0]].copy() + route[idxs[idx1]:idxs[idx2-1]] + best[bestidxs[0]:bestidxs[1]].copy() + route[idxs[idx2]:]
                        # Corrigir a diferença no idx1
                        dif = idxs[idx1] - bestidxs[0]
                        idxs[idx1:idx2] -= dif
                    else:
                        route = route[:idxs[idx1-1]] + best[:bestidxs[0]].copy() + route[idxs[idx1]:idxs[idx2-1]] + best[bestidxs[0]:bestidxs[1]].copy() + route[idxs[idx2]:]
                        # Corrigir a diferença no idx1
                        dif = idxs[idx1] - idxs[idx1-1] - bestidxs[0]
                        idxs[idx1:idx2] -= dif
                    #print("Validar")
                    #print(route)
                    #print(idxs)
                    improved = True
                    anyimproved = True     
                    
                    MEMORIA = [M for M in MEMORIA if (idx1 not in M and idx2 not in M)]
                    
                MEMORIA.append((idx1, idx2))
                if improved: break  
            if improved: break  
    #print("r_f", route)
    #print("i_f", idxs)
    #print(route)
    #print("Tempo 2opt", anyimproved, time() - T)
    
    #print("melhoriaAcumulada-", bestImproved)
    #melhoriaReal = calculate_distance(route, dist_matrix=dist_matrix) - calculate_distance(old__, dist_matrix=dist_matrix)
    #print("melhoriaReal-", melhoriaReal)
    
    if returnALL:
        return route, idxs, anyimproved, bestImproved, anyimproved
    return route