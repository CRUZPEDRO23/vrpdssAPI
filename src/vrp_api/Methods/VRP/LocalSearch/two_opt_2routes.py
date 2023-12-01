# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 09:01:46 2023

@author: jose-
"""

import numpy as np

from .two_opt import two_opt

def calculate_distance(route: list[int], dist_matrix: np.ndarray) -> float:
    return dist_matrix[np.roll(route, 1), route].sum()

def two_opt_2routes(route, idxs, caps1, caps2, d_i, dist_matrix, ALL = False):
    
    # Algoritmo de 2opt usando duas rotas que podem partir de depot diferentes
    # idxs contem a posicao dos depositos (2 idxs - 1º fim rota 1 e 2º fim rota 2)
    # Routes EX: 1 e 2 são depositos: [1, 4, 5, 6, 1, 2, 9, 3, 2]
    # EX idxs: [4, 8]
    
    best = route.copy()
    bestidxs = idxs.copy()
    anyBest = False
    improved = True
    #print("inicial route", best)
    #print("inicial idxs", idxs)
    while improved:
        
        improved = False
        idxi = 0
        node_start_Route = 0 # inicio da rota que o ponto i pertence
        node_end_Route = bestidxs[idxi]# Fim da rota que o ponto i pertence
        node_end_nestRoute = bestidxs[idxi+1] if idxi+1 < len(bestidxs) else node_end_Route#Indice fim da proxima rota
        
        capRoute = caps1
        capNextRoute = caps2
        
        for i in range(1, len(route) - 1):# Tava -2 aqui
            # Atualizar posicao dos nos de inicio e fim
            if i == bestidxs[0]+1:
                continue
            if i > node_end_Route:
                idxi += 1
                node_start_Route = node_end_Route+1# Inicio da segunda rota
                node_end_Route = bestidxs[idxi]
                node_end_nestRoute = bestidxs[idxi+1] if idxi+1 < len(bestidxs) else node_end_Route
                
                capRoute = caps2
                
            #for j in range(i + 1, len(route)):
            # Realiza interação com rota vizinha
            for j in range(i + 1, node_end_nestRoute):
                if j - i == 1: continue  # changes nothing, skip then
                if j == node_end_Route+1: continue # depósito da proxima rota - evita criação de 3ª rota
                
                new_route = best[:]    # Creates a copy of route
                
                if j > node_end_Route: 
                    # inverte depósitos para desenverter em seguida
                    new_route[node_end_Route:node_end_Route+1+1] = new_route[node_end_Route + 1:node_end_Route-1:-1]
                    
                    # Variação de custo pois: --- 4 2 1 5 --- rota-se --- 5 2 1 4 (Exemplo) 
                    if (dist_matrix[best[node_end_Route], best[node_end_Route+2]] + \
                        dist_matrix[best[node_end_Route+1], best[node_end_Route-1]]) - (dist_matrix[best[node_end_Route-1], best[node_end_Route]]+ dist_matrix[best[node_end_Route+1], best[node_end_Route+2]]) + \
                        (dist_matrix[best[i-1], best[j-1]] + dist_matrix[best[i], best[j]]) - \
                        (dist_matrix[best[i-1], best[i]] + dist_matrix[best[j-1], best[j]]) >= 0 :
                        continue
                else:    
                    if (dist_matrix[best[i-1], best[j-1]] + dist_matrix[best[i], best[j]]) - (dist_matrix[best[i-1], best[i]] + dist_matrix[best[j-1], best[j]]) >= 0 :
                        continue
                
                # Validar Melhoria de custo:
                newReverseRoute = new_route[j - 1:i - 1:-1]
                
                #print("")
                #print("")
                #print(route)
                #print(i, j)
                #print(dist_matrix[route[i-1], route[j-1]], dist_matrix[route[i], route[j]], dist_matrix[route[i-1], route[i]], dist_matrix[route[j-1], route[j]])
                #print(Var_Cost)
                #print("")
                #print(dist_matrix[i-1, j-1] + dist_matrix[i, j], dist_matrix[i-1, i] + dist_matrix[j-1, j])
                #print(calculate_distance(new_route[i:j], dist_matrix=dist_matrix))
                #print(calculate_distance(route[j - 1:i - 1:-1], dist_matrix=dist_matrix))
                
                #new_route[i:j] = route[j - 1:i - 1:-1]  # this is the 2-optSwap since j >= i we use -1
                new_route[i:j] = newReverseRoute  # this is the 2-optSwap since j >= i we use -1
                #print("NEW", new_route)
                    
                # Verificar se muda cliente de rotas:
                    # Restricao de capacidade
                _l = -1
                if j > node_end_Route:  # Trabalhando na rota diferente que i inicia
                    # Posicao do satélite após inversão:
                    _l = (j-1) - (node_end_Route - i)
                    _l = i + (j - 1 - (node_end_Route+1)) # O Satelite que inicia rota 2 para ser fim da rota 1 - por isso inverti no início
                    
                    _1_new_route, _, anyBest1 = two_opt(route=new_route[:_l+1], idxs=[_l], cap=capRoute, d_i=d_i, dist_matrix=dist_matrix, ALL = True)
                    _2_new_route, _, anyBest2 = two_opt(route=new_route[_l+1:], idxs=[len(new_route[_l+1:])-1], cap=capNextRoute, d_i=d_i, dist_matrix=dist_matrix, ALL = True)
                    if 15 in new_route: print("new_route", new_route)
                    new_route = _1_new_route + _2_new_route
                    if 15 in new_route: print("new_route - ", new_route)
                    #print(_l)
                    #print(new_route[node_start_Route:_l+1])
                    #print(d_i[new_route[node_start_Route:_l+1]].sum(), capRoute)
                    
                    #print(new_route[_l+1:node_end_nestRoute+1])
                    #print(d_i[new_route[_l+1:node_end_nestRoute+1]].sum(), capNextRoute)
                    if d_i[new_route[node_start_Route:_l+1]].sum() > capRoute:
                        continue
                    if d_i[new_route[_l+1:node_end_nestRoute+1]].sum() > capNextRoute:
                        continue
                
                old_Cost = np.round(calculate_distance(best, dist_matrix=dist_matrix), decimals = 8)
                new_Cost = np.round(calculate_distance(new_route, dist_matrix=dist_matrix), decimals = 8)
                MELHORIA = new_Cost < old_Cost
                #print(MELHORIA)
                if MELHORIA:
                    print(best)
                    print(dist_matrix[np.roll(best, 1), best])
                    print(dist_matrix[np.roll(best, 1), best].sum())
                    print(new_route)
                    print(dist_matrix[np.roll(new_route, 1), new_route])
                    print(dist_matrix[np.roll(new_route, 1), new_route].sum())
                    
                    print(MELHORIA, new_Cost, old_Cost)
                    
                    if _l != -1:
                        idxs[idxi] = _l
                        node_end_Route = _l
                    
                    best = new_route.copy()
                    bestidxs = idxs.copy()
                    anyBest = MELHORIA
                    improved = True
                    route = best.copy()
                    break
            if improved: break   
    if ALL: 
        return best, bestidxs, anyBest
    return best

def two_opt_2routes_Extra(route, idxs, cap_s, d_i, dist_matrix):
    #print(route)
    #print(idxs)
    MEMORIA = list()
    improved = True
    anyimproved = False
    while improved:
        improved = False
        for idx1 in range(len(idxs)):
            #boolAnyEmpytRoute = idxs[idx1] - idxs[idx1-1] == 1
            #if boolAnyEmpytRoute:
            #    continue
            boolAnyEmpytRoute = False
            for idx2 in range(idx1+1, len(idxs)):
                if (idx1, idx2) in MEMORIA:
                    continue
                
                r1 = route[:idxs[idx1]+1].copy() if idx1 == 0 else route[idxs[idx1-1]:idxs[idx1]+1].copy()
                r2 = route[idxs[idx2-1]:idxs[idx2]+1].copy()
                #print(r1, r2)
                capr1 = cap_s[r1[0]]
                capr2 = cap_s[r2[0]]
                
                if len(r2)!=2:
                    boolAnyEmpytRoute = False
                    
                if (len(r1)==2 and r1[0]!=r1[1]) or (len(r2)==2 and r2[0]!=r2[1]):
                   continue 
                
                if boolAnyEmpytRoute or (len(r1)==2 and len(r2)==2):
                    #if (len(r1)==2 and len(r2)==2):
                    continue
                if len(r2)==2:
                    boolAnyEmpytRoute = True

                #print(r1, r2)
                route_ = r1 + r2#r1[:-1] + r2
                print("route_", route_)
                idxs_ = [len(r1)-1, len(route_)-1]
                #print(idxs_)
                #print("Teste", idx1, idx2, route_, idxs_)
                best, bestidxs, anyBest = two_opt_2routes(route=route_.copy(), idxs=idxs_.copy(), caps1=capr1, caps2=capr2, d_i = d_i, dist_matrix = dist_matrix, ALL= True)
                
                #if calculate_distance(best, dist_matrix=dist_matrix) < calculate_distance(route_, dist_matrix=dist_matrix):
                if anyBest:
                    #print("Melhroria", calculate_distance(best, dist_matrix=dist_matrix),  calculate_distance(route_, dist_matrix=dist_matrix))
                    #print(calculate_distance(route_, dist_matrix=dist_matrix) - calculate_distance(best, dist_matrix=dist_matrix))
                    
                    # Verificar se NP nao ta tentando roubar
                    anyimproved = True     
                    if idx1 == 0:
                        route = best[:bestidxs[0]].copy() + route[idxs[idx1]:idxs[idx2-1]] + best[bestidxs[0]+1:bestidxs[1]].copy() + route[idxs[idx2]:]
                        # Corrigir a diferença no idx1
                        dif = idxs[idx1] - bestidxs[0]
                        idxs[idx1:idx2] -= dif
                    else:
                        route = route[:idxs[idx1-1]] + best[:bestidxs[0]].copy() + route[idxs[idx1]:idxs[idx2-1]] + best[bestidxs[0]+1:bestidxs[1]].copy() + route[idxs[idx2]:]
                        # Corrigir a diferença no idx1
                        dif = idxs[idx1] - idxs[idx1-1] - bestidxs[0]
                        idxs[idx1:idx2] -= dif
                    print("Validar")
                    print(route_)
                    print(idxs_)
                    print(best)
                    print(bestidxs)
                    #print(route)
                    #print(idxs)
                    improved = True
                    
                    MEMORIA = [M for M in MEMORIA if (idx1 not in M and idx2 not in M)]
                    
                    break
                MEMORIA.append((idx1, idx2))
            if improved: break  
        
    #print(route)
    #print("Tempo 2opt", anyimproved, time() - T)
    return route