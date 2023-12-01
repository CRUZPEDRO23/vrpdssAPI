# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 11:14:14 2023

@author: jose-
"""

import copy

import numpy as np
from ..._interfaces import route
from typing import Type

def calculate_distance(route: list[int], dist_matrix: np.ndarray) -> float:
    return dist_matrix[np.roll(route, 1), route].sum()


def _change_1x1(route1: Type[route], route2: Type[route], d_i: np.ndarray, dist_matrix: np.ndarray, routingFunction: lambda r: r):
    
    improved = True
    anyimproved = False
    bestr1 = route1.copy()
    bestr2 = route2.copy()
    
    #print("Rota Inicial 1", bestr1.route)
    #print("Rota Inicial 2", bestr2.route)
    
    
    while improved:
        improved = False
        for i in range(1, len(route1.route)-1):
            for j in range(1, len(route2.route)-1):
                if route1.s != route2.s and d_i[i]!=d_i[j]:
                    #DELTAFE_COST = DELTAFE_COST_callback(i, j)
                    continue
                else:
                    DELTAFE_COST = 0
                c1 = route1.route[i]
                c2 = route2.route[j]
                if route1.weight - d_i[c1] + d_i[c2] > route1.cap or \
                   route2.weight - d_i[c2] + d_i[c1] > route2.cap:
                        continue
                
                route1.removei(i = c1, idx = i)
                route1.addi(i = c2)
                route1.route = routingFunction(route1.route)
                route1.cost = calculate_distance(route1.route, dist_matrix)
                route2.removei(i = c2, idx = j)
                route2.addi(i = c1)
                route2.route = routingFunction(route2.route)
                route2.cost = calculate_distance(route2.route, dist_matrix)
                
                if route1.cost + route2.cost + DELTAFE_COST < bestr1.cost + bestr2.cost:
                    route1.weight += (d_i[c2]-d_i[c1])
                    route2.weight += (d_i[c1]-d_i[c2])
                    bestr1 = route1.copy()
                    bestr2 = route2.copy()
                    improved = True
                    anyimproved = True
                    break
                else:
                    #print(i, j, route1 == bestr1)
                    route1 = bestr1.copy()
                    route2 = bestr2.copy()
            if improved: break
    #print("Rota Final 1", bestr1.route)
    #print("Rota Final 2", bestr2.route)
    #print("Melhoria: ", anyimproved)
    return anyimproved, bestr1, bestr2



def _change_1x0(route1: Type[route], route2: Type[route], d_i: np.ndarray, dist_matrix: np.ndarray, routingFunction: lambda r: r, needFEChangeCost = lambda r1, r2, i, j: False):
    
    improved = True
    anyimproved = False
    
    bestr1 = route1.copy()
    bestr2 = route2.copy()
    
    #print("Rota Inicial 1", bestr1.route)
    #print("Rota Inicial 2", bestr2.route)
    

    
    while improved:
        improved = False
        for i in range(1, len(route1.route)-1):
            c1 = route1.route[i]
            
            #route1.s != route2.s or 
            if needFEChangeCost(r1 = route1, r2 = route2, c1 = [c1], c2 = []):
                
                # Calc delta cost:
                #DELTAFE_COST = DELTAFE_COST_callback(i, j)
                continue
            else:
                DELTAFE_COST = 0
            
            if route2.weight + d_i[c1] > route2.cap:
                continue
            
            route1.removei(i = c1, idx = i)
            route1.route = routingFunction(route1.route)
            route1.cost = calculate_distance(route1.route, dist_matrix)
            route2.addi(i = c1)
            route2.route = routingFunction(route2.route)
            route2.cost = calculate_distance(route2.route, dist_matrix)
            
            if route1.cost + route2.cost + DELTAFE_COST < bestr1.cost + bestr2.cost:
                route1.weight -= d_i[c1]
                route2.weight += d_i[c1]
                bestr1 = route1.copy()
                bestr2 = route2.copy()
                improved = True
                anyimproved = True
                break
            else:
                #print(i, j, route1 == bestr1)
                route1 = bestr1.copy()
                route2 = bestr2.copy()
        
    #print("Rota Final 1", bestr1.route)
    #print("Rota Final 2", bestr2.route)
    #print("Melhoria: ", anyimproved)
    return anyimproved, bestr1, bestr2


def change_1x1(routes: list[Type[route]], d_i: np.ndarray, dist_matrix: np.ndarray, routingFunction: lambda r: r):
    
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)-1):
            for j in range(i+1, len(routes)):
                improved, routes[i], routes[j] = _change_1x1(routes[i], routes[j], d_i, dist_matrix, routingFunction)
                if improved: break
            if improved: break
    return routes

def change_1x0(routes: list[Type[route]], d_i: np.ndarray, dist_matrix: np.ndarray, routingFunction: lambda r: r, needFEChange = lambda r1, r2, i, j: False):
    
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)-1):
            for j in range(i+1, len(routes)):
                improved, routes[i], routes[j] = _change_1x0(routes[i], routes[j], d_i, dist_matrix, routingFunction, needFEChangeCost = needFEChange)
                improved, routes[j], routes[i] = _change_1x0(routes[j], routes[i], d_i, dist_matrix, routingFunction, needFEChangeCost = needFEChange)
                if improved: break
            if improved: break
    return routes




def _Procedimentochange_nx0(
        routes: list[Type[route]], 
        idxr1: int, 
        idxr2: int, 
        d_i,
        FE,
        c1: list[int],
        avaliarFEFunction,
        routingFunction):
    
    improved = False
    
    if routes[idxr2].weight + d_i[c1].sum() <= routes[idxr2].cap:
        
        R1, cost1 = routingFunction(
            [i for i in routes[idxr1].route.copy() if i not in c1])
        R2, cost2 = routingFunction(
            routes[idxr2].route[:-1].copy() + c1 + [routes[idxr2].route[-1]])
        
        # Verificar variacao de custo FE
        if routes[idxr1].s == routes[idxr2].s:
            DeltaCost = 0
        else:
            print("WS")
            #print(FE.W_s)
            D_s = {s: 0 for s in FE.W_s}
            
            D_s[routes[idxr1].s] = -1 * d_i[c1].sum()
            D_s[routes[idxr2].s] = +1 * d_i[c1].sum()
            
            
            r1 = route(s=routes[idxr1].s, id = routes[idxr1].id, cap = routes[idxr1].cap)
            r1.route = R1.copy()
            r1.cost = cost1
            
            r2 = route(s=routes[idxr2].s, id = routes[idxr2].id, cap = routes[idxr2].cap)
            r2.route = R2.copy()
            r2.cost = cost2
            
            NECESSITARECALCULO, newroutesFE, newW_s, return_idxRotasDoSatélites, return_totalCost = avaliarFEFunction(
                D_s, copy.copy(r1), copy.copy(r2), idxr1, idxr2)
            if not NECESSITARECALCULO:
                DeltaCost = 0
            else:
                #DeltaCost = return_totalCost - FE.totalCost # calcular
                DeltaCost = np.inf
                print("AVALIAR TOTAL COST", return_totalCost - FE.totalCost)
                for r in newroutesFE:
                    print(r.route)
        
        
        #print("Relatorio de iteração", idxr1, idxr2, c1)
        #print("R1", routes[idxr1].route, routes[idxr1].cost)
        #print("newR1", R1, cost1)
        #print("R2", routes[idxr2].route, routes[idxr2].cost)
        #print("newR2", R2, cost2)
        #print("Delta", DeltaCost, (cost1+cost2), (routes[idxr1].cost+routes[idxr2].cost))
        DeltaCost += (cost1+cost2) - (routes[idxr1].cost+routes[idxr2].cost)
        #print(DeltaCost)
        
        if DeltaCost < 0: # Melhorou
            improved = True
            routes[idxr1].route = R1.copy()
            routes[idxr2].route = R2.copy()
            routes[idxr1].nC -= len(c1)
            routes[idxr2].nC += len(c1)
            routes[idxr1].cost = cost1
            routes[idxr2].cost = cost2
            routes[idxr1].weight -= d_i[c1].sum()
            routes[idxr2].weight += d_i[c1].sum()
            
            try:
                FE.routes = newroutesFE.copy()
                FE.W_s = newW_s.copy()
                FE.CalcCosts()
            except:
                pass
            
        # Verificar variação de custo SE
    
    return improved, routes, FE
    


def change_nx0(routes: list[Type[route]], FE, n: int, d_i: np.ndarray, dist_matrix: np.ndarray, routingFunction: lambda r: (r, np.inf), needFEChange = lambda r1, r2, i, j: False):
    
    improved = True
    MEMORIA = list()
    
    def routesSE(r1, r2, i1, i2):
        rs = copy.copy(routes)
        rs[i1] = copy.copy(r1)
        rs[i2] = copy.copy(r2)
        return rs
    avaliarFEFunction = lambda D_s, r1, r2, i1, i2: FE.recalcFE(D_s,d_i, cost_Matrix=dist_matrix, routesSE=routesSE(r1, r2, i1, i2))
    
    
    def getNextNC(candidates, comb = [], i=0, j=1, n = 2, lastIdx = -1, MEMORIA = []):
        Retornar = False
        for idx, c in enumerate(candidates):
            if idx <= lastIdx: 
                continue
            #print("teste do comb", comb + [c])
            comb.append(c)
            if (i, j, comb) in MEMORIA:
                comb.remove(c)
                continue
            
            if len(comb) == n:
                MEMORIA.append((i, j, comb.copy()))
                #print(comb, lastIdx)
                Retornar = True
                return Retornar, comb, lastIdx, MEMORIA
            else:
                newcandidates = candidates#[idx+1:]
                #newcandidates.remove(c)
                Retornar, comb, lastIdx, MEMORIA = getNextNC(newcandidates, comb = comb,  i=i, j=j,n = n, lastIdx = idx, MEMORIA = MEMORIA.copy())
                if Retornar: return Retornar, comb, lastIdx, MEMORIA
            del comb[-1]
        return Retornar, comb, lastIdx, MEMORIA
    
    def loop(routes, i, j, FE, MEMORIA = []):
        improved = False
        candidates = routes[i].route[1:-1]
        comb = []
        #n = n
        lastIdx = -1
        #print("start search", candidates, routes[i].s == routes[j].s)
        while 1:
            #print("STR", comb, lastIdx)
            _, comb, lastIdx, MEMORIA = getNextNC(
                candidates, 
                comb = comb, 
                i = i,
                j = j,
                n = n, 
                lastIdx = lastIdx, 
                MEMORIA = MEMORIA.copy())
            
            # Sem Novas Possibilidades
            
            if len(comb) < n or not _:
                break
            # Procedimento
            
            improved, routes, FE = _Procedimentochange_nx0(
                routes.copy(), 
                idxr1=i, 
                idxr2=j, 
                d_i = d_i,
                FE = copy.copy(FE),
                c1 = comb, 
                avaliarFEFunction = avaliarFEFunction,
                routingFunction=routingFunction
            )
            
            # Caso melhore:
            if improved:
                
                MEMORIA = [
                    M for M in MEMORIA
                    if all([c_ not in comb for c_ in M[2]])
                    ]
                MEMORIA.append((i, j, comb.copy()))
                break
            
            #print("ava", comb, lastIdx, _, MEMORIA)
            
            # Fim das possibilidades
            if comb == candidates[-n:]:
                break
            if comb[-1] == candidates[-1]: 
                # Todas possibilidades testas
                # Remove o último e ante penultimo
                del comb[-1]
                del comb[-1]
            else:
                # Elimina so o ultimo
                del comb[-1]
                
        return improved, routes, FE, MEMORIA
    
    while improved:
        improved = False
        rotasRepetidas = [
            1 if (len(routes)==2 and routes[i].route == routes[i-1].route) else 0 
            for i in range(len(routes))
        ]
  
        for i in range(len(routes)-1):
            for j in range(i+1, len(routes)):
                
                if routes[i].nC < n or rotasRepetidas[i] or rotasRepetidas[j]:
                    continue
                
                improved, routes, FE, MEMORIA = loop(routes.copy(), i, j, FE, MEMORIA = MEMORIA.copy())
                #improved, routes[i], routes[j] = _change_1x0(routes[i], routes[j], d_i, dist_matrix, routingFunction, needFEChangeCost = needFEChange)
                #improved, routes[j], routes[i] = _change_1x0(routes[j], routes[i], d_i, dist_matrix, routingFunction, needFEChangeCost = needFEChange)
                
                if improved: break
            if improved: break
    return routes