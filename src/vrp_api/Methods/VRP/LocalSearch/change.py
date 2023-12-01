# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 16:58:40 2023

@author: jose-
"""

import numpy as np
from ..._interfaces import SE as interfaceSE, FE as interfaceFE



class changeModule:
    def __init__(self, SE, FE, n: int,  tipo = "nx0", tipoComb = "default",
                   routingFunction = lambda route, idxs, cap: route):
        self.SE = SE
        self.FE = FE
        self.S = SE.S
        self.m_s = SE.m_s
        self.Q2_s = SE.Q2_s
        self.d_i = SE.d_i
        self.C_ij = SE.C_ij
        self.routingFunction = routingFunction
        self.n = n
        self.tipo = tipo
        self.tipoComb = tipoComb
        self.exec()
    def returnData(self):
        return self.SE.copy(), self.FE.copy()
        
    def _getNextNC(self, candidates, s1=0, s2=1, comb = [], n = 2, lastIdx = -1, MEMORIA = []):
        #retorna grupo de combinaçao de cliente para iteração
        Retornar = False
        #print(MEMORIA)
        for idx, c in enumerate(candidates):
            if idx <= lastIdx: 
                continue
            #print("teste do comb", comb + [c])
            comb.append(c)
            if (s1, s2, comb) in MEMORIA:
                comb.remove(c)
                continue
            
            if len(comb) == n:
                MEMORIA.append((s1, s2, comb.copy()))
                #print(comb, lastIdx)
                Retornar = True
                return Retornar, comb, lastIdx, MEMORIA
            else:
                newcandidates = candidates#[idx+1:]
                #newcandidates.remove(c)
                Retornar, comb, lastIdx, MEMORIA = self._getNextNC(newcandidates, s1=s1, s2=s2, comb = comb,  n = n, lastIdx = idx, MEMORIA = MEMORIA.copy())
                if Retornar: return Retornar, comb, lastIdx, MEMORIA
            del comb[-1]
        return Retornar, comb, lastIdx, MEMORIA
    
    def _getNextNC_Sequence(self, candidates, s1=0, s2=1, comb = [], n = 2, lastIdx = -1, MEMORIA = []):
        #retorna grupo de combinaçao de cliente para iteração
        Retornar = False
        
        while 1:
            lastIdx+=1
            if lastIdx+n > len(candidates):
                break
            comb = candidates[lastIdx:lastIdx+n]
            if (s1, s2, comb) not in MEMORIA:
                MEMORIA.append((s1, s2, comb.copy()))
                break
            
        return Retornar, comb, lastIdx, MEMORIA
    
    def _procedimento_nx0(self, s1, s2, c1 = list[int], c2 = None):
        
        improved = False
        
        SE = interfaceSE(
            S=self.S, 
            m_s=self.m_s, 
            Q2_s=self.Q2_s, 
            d_i=self.d_i, 
            C_ij=self.C_ij)
        
        for s in self.S:
            SE.routes[s].route = self.SE.routes[s].route.copy()
            SE.routes[s].getIndexEndRoute()
            SE.routes[s].getWeight(d_i = self.d_i)
            SE.routes[s].getCost(dist_matrix=self.C_ij)
        SE.getCost()
        SEtCost = SE.costSE
        
        FE = interfaceFE(s = 0, S=self.S, n_Trips=10, cap=self.FE.cap, C_ij=self.C_ij)
        FE.routes = self.FE.routes.copy()
        FE.W_s = self.FE.W_s.copy()
        #FE.weight = self.FE.weight
        FE.getIndexEndRoute()
        FE.getCost(dist_matrix=self.C_ij)
        rFE = FE.routes.copy()
        
        route1 = SE.routes[s1]
        route2 = SE.routes[s2]
        
        cost1 = route1.tCost
        cost2 = route2.tCost
        costFE = FE.tCost
        
        r1 = route1.route.copy()
        r2 = route2.route.copy()
        
        #print("Procedimento", c1, c2)
        #print("Costs", cost1, cost2, costFE, (cost1+cost2+costFE))
        #print("Costs", SEtCost, costFE, (SEtCost+costFE))
        ##print(r1)
        #print(r2)
        #print(rFE)
        
        
        route1.remove(c1 = c1, d_i=SE.d_i, dist_matrix=SE.C_ij)
        if c2!=None:
            route2.remove(c1 = c2, d_i=SE.d_i, dist_matrix=SE.C_ij)
        sucess = route2.add(c1 = c1, d_i=SE.d_i, dist_matrix=SE.C_ij, routingFunction = self.routingFunction)
        if sucess and c2!=None:
            sucess = route1.add(c1 = c2, d_i=SE.d_i, dist_matrix=SE.C_ij, routingFunction = self.routingFunction)
        
        SE.getCost()
        FE.W_s[s1] -= self.d_i[c1].sum()
        FE.W_s[s2] += self.d_i[c1].sum()
        FE.calcFE()
        FE.getIndexEndRoute()
        FE.getCost(dist_matrix=self.C_ij)
        
        #print("Costs", route1.tCost, route2.tCost, FE.tCost, (route1.tCost+route2.tCost+FE.tCost))
        #print("Costs", SE.costSE, FE.tCost, (SE.costSE+FE.tCost))
        
        #print(route1.route)
        #print(route2.route)
        #print(FE.routes)
        
        #print("Validacao: ", self.SE.validarRotas())
        #print("MELHORIA", sucess, (route1.tCost+route2.tCost+FE.tCost) - (cost1+cost2+costFE))
        #print((route1.tCost+route2.tCost+FE.tCost) - (cost1+cost2+costFE) < 0)
        #print((SE.costSE<SEtCost), SE.costSE, SEtCost)
        #(SE.costSE<SEtCost):#
        
        if sucess and (SE.costSE+FE.tCost<SEtCost+costFE):#(route1.tCost+route2.tCost+FE.tCost) - (cost1+cost2+costFE) < 0:
            
            #print("Procedimento", c1, c2)
            #print("Validacao: ", self.SE.validarRotas())
            #print("MELHORIA", sucess, (route1.tCost+route2.tCost+FE.tCost) - (cost1+cost2+costFE))
            
            ##print("Costs", cost1, cost2, costFE, (cost1+cost2+costFE))
            #print("Costs", SEtCost, costFE, (SEtCost+costFE))
            #print(r1)
            #print(r2)
            #print(rFE)
            
            ##print("Costs", route1.tCost, route2.tCost, FE.tCost, (route1.tCost+route2.tCost+FE.tCost))
            #print("Costs", SE.costSE, FE.tCost, (SE.costSE+FE.tCost))
            
            #print(route1.route)
            #print(route2.route)
            #print(FE.routes)
            
            improved = True
            for s in self.S:
                self.SE.routes[s].route = SE.routes[s].route.copy()
                self.SE.routes[s].getIndexEndRoute()
                self.SE.routes[s].getWeight(d_i = self.d_i)
                self.SE.routes[s].getCost(dist_matrix=self.C_ij)
            self.SE.getCost()
            
            self.FE.routes = FE.routes.copy()
            self.FE.W_s = FE.W_s.copy()
            self.FE.weight = FE.weight
            self.FE.getIndexEndRoute()
            self.FE.getCost(dist_matrix=self.C_ij)
            
        """     for s in self.S:
                self.SE.routes[s].route = SE.routes[s].route.copy()
                self.SE.routes[s].idxEndRoute = SE.routes[s].idxEndRoute.copy()
                self.SE.routes[s].cost = SE.routes[s].cost
                self.SE.routes[s].tCost = SE.routes[s].tCost
                self.SE.routes[s].weight = SE.routes[s].weight
            self.SE.costSE = SE.costSE
            
            self.FE.routes = FE.routes.copy()
            self.FE.idxEndRoute = FE.idxEndRoute
            self.FE.cost = FE.cost
            self.FE.tCost = FE.tCost
            self.FE.weight = FE.weight
            
        """
        return improved

    def exec(self):
        
        if self.tipoComb == "default":
            self.combFunction = self._getNextNC
        else:
            self.combFunction = self._getNextNC_Sequence
        
        if self.tipo=="nx0":
            self.change_nx0()
        elif self.tipo=="nxn":
            self.change_nxn()
        else:
            self.change_misto()
    def change_nx0(self):
        improved = True
        MEMORIA = list()
        
        while improved:
            improved = False
            
            for s1 in self.S:
                for s2 in self.S:
                    if s1 == s2: 
                        continue
                    
                    candidados = [i for i in self.SE.routes[s1].route if i != s1]
                    #print("candidados", candidados)
                    comb = []
                    lastIdx = -1
                    
                    while 1:
                        #Retornar, comb, lastIdx, MEMORIA = self._getNextNC(
                        #    candidates = candidados, s1=s1, s2=s2, comb = comb, 
                        #    n = self.n, lastIdx = lastIdx, MEMORIA = MEMORIA.copy())
                        Retornar, comb, lastIdx, MEMORIA = self.combFunction(
                            candidates = candidados, s1=s1, s2=s2, comb = comb, 
                            n = self.n, lastIdx = lastIdx, MEMORIA = MEMORIA.copy())
                        
                        # Sem Novas Possibilidades
                        if len(comb) < self.n or not Retornar:
                            break

                        # Procedimento , _SE, _FE
                        improved = self._procedimento_nx0(s1 = s1, s2 = s2, 
                            c1 = comb)
                        
                        #print("compara", self.SE.routes[s1] == _SE.routes[s1])
                        # Caso melhore:
                        if improved:
                            # Gerenciar Memoria
                            MEMORIA = [
                                M for M in MEMORIA
                                if all([c_ not in comb for c_ in M[2]])
                                ]
                            MEMORIA.append((s1, s2, comb.copy()))
                            break
            
                        # Fim das possibilidades
                        if comb == candidados[-self.n:]:
                            break
                        if comb[-1] == candidados[-1]: 
                            # Todas possibilidades testas
                            # Remove o último e ante penultimo
                            del comb[-1]
                            del comb[-1]
                        else:
                            # Elimina so o ultimo
                            del comb[-1]
        #return self.SE, FE                
    def change_nxn(self):
        improved = True
        MEMORIA = list()
        
        while improved:
            improved = False
            
            for s1 in self.S:
                for s2 in self.S:
                    if s1 == s2: 
                        continue
                    
                    candidados1 = [i for i in self.SE.routes[s1].route if i != s1]
                    candidados2 = [i for i in self.SE.routes[s2].route if i != s2]
                    #print("candidados", candidados1)
                    #print("candidados", candidados2)
                    comb1 = []
                    lastIdx1 = -1
                    comb2 = []
                    lastIdx2 = -1
                    
                    while 1:
                        #Retornar, comb1, lastIdx1, MEMORIA = self._getNextNC(
                        #    candidates = candidados1, s1=s1, s2=s2, comb = comb1, 
                        #    n = self.n, lastIdx = lastIdx1, MEMORIA = MEMORIA.copy())
                        Retornar, comb1, lastIdx1, MEMORIA = self.combFunction(
                            candidates = candidados1, s1=s1, s2=s2, comb = comb1, 
                            n = self.n, lastIdx = lastIdx1, MEMORIA = MEMORIA.copy())
                        
                        #print(MEMORIA)
                        # Sem Novas Possibilidades
                        if len(comb1) < self.n or not Retornar:
                            break
                        while 1:
                            #Retornar, comb2, lastIdx2, MEMORIA = self._getNextNC(
                            #    candidates = candidados2, s1=s1, s2=s2, comb = comb2, 
                            #    n = self.n, lastIdx = lastIdx2, MEMORIA = MEMORIA.copy())
                            Retornar, comb2, lastIdx2, MEMORIA = self.combFunction(
                                candidates = candidados2, s1=s1, s2=s2, comb = comb2, 
                                n = self.n, lastIdx = lastIdx2, MEMORIA = MEMORIA.copy())
                            
                            
                            # Sem Novas Possibilidades
                            if len(comb2) < self.n or not Retornar:
                                break

                            # Procedimento , _SE, _FE
                            # Procedimento , _SE, _FE
                            improved = self._procedimento_nx0(s1 = s1, s2 = s2, 
                                c1 = comb1, c2 = comb2)
                            #print("compara", self.SE.routes[s1] == _SE.routes[s1])
                            # Caso melhore:
                            if improved:
                                # Gerenciar Memoria
                                MEMORIA = [
                                    M for M in MEMORIA
                                    if all([c_ not in comb1+comb2 for c_ in M[2]])
                                    ]
                                MEMORIA.append((s1, s2, comb1.copy()))
                                MEMORIA.append((s1, s2, comb2.copy()))
                                break
                            
                            # Fim das possibilidades
                            if comb2 == candidados2[-self.n:]:
                                break
                            if comb2[-1] == candidados2[-1]: 
                                # Todas possibilidades testas
                                # Remove o último e ante penultimo
                                del comb2[-1]
                                del comb2[-1]
                            else:
                                # Elimina so o ultimo
                                del comb2[-1]
                            
                        if improved:
                            break
                        # Fim das possibilidades
                        if comb1 == candidados1[-self.n:]:
                            break
                        if comb1[-1] == candidados1[-1]: 
                            # Todas possibilidades testas
                            # Remove o último e ante penultimo
                            del comb1[-1]
                            del comb1[-1]
                        else:
                            # Elimina so o ultimo
                            del comb1[-1]
        
        
        #return self.SE, FE                
    def change_misto(self):
        improved = True
        MEMORIA = list()
        
        while improved:
            improved = False
            
            for s1 in self.S:
                for s2 in self.S:
                    if s1 == s2: 
                        continue
                    
                    candidados1 = [i for i in self.SE.routes[s1].route if i != s1]
                    candidados2 = [i for i in self.SE.routes[s2].route if i != s2]
                    #print("candidados", candidados1)
                    #print("candidados", candidados2)
                    comb1 = []
                    lastIdx1 = -1
                    comb2 = []
                    lastIdx2 = -1
                    
                    
                    while 1:
                        #Retornar, comb1, lastIdx1, MEMORIA = self._getNextNC(
                        #    candidates = candidados1, s1=s1, s2=s2, comb = comb1, 
                        #    n = self.n, lastIdx = lastIdx1, MEMORIA = MEMORIA.copy())
                        Retornar, comb1, lastIdx1, MEMORIA = self.combFunction(
                            candidates = candidados1, s1=s1, s2=s2, comb = comb1, 
                            n = self.n, lastIdx = lastIdx1, MEMORIA = MEMORIA.copy())
                        #print(MEMORIA)
                        # Sem Novas Possibilidades
                        if len(comb1) < self.n or not Retornar:
                            break
                        
                        improved = self._procedimento_nx0(s1 = s1, s2 = s2, 
                            c1 = comb1)
                        #print("compara", self.SE.routes[s1] == _SE.routes[s1])
                        # Caso melhore:
                        if improved:
                            # Gerenciar Memoria
                            MEMORIA = [
                                M for M in MEMORIA
                                if all([c_ not in comb1 for c_ in M[2]])
                                ]
                            MEMORIA.append((s1, s2, comb1.copy()))
                            break
                        
                        while 1:
                            #Retornar, comb2, lastIdx2, MEMORIA = self._getNextNC(
                            #    candidates = candidados2, s1=s1, s2=s2, comb = comb2, 
                            #    n = self.n, lastIdx = lastIdx2, MEMORIA = MEMORIA.copy())
                            Retornar, comb2, lastIdx2, MEMORIA = self.combFunction(
                                candidates = candidados2, s1=s1, s2=s2, comb = comb2, 
                                n = self.n, lastIdx = lastIdx2, MEMORIA = MEMORIA.copy())
                            #print(MEMORIA)
                            # Sem Novas Possibilidades
                            if len(comb2) < self.n or not Retornar:
                                break
                            
                            improved = self._procedimento_nx0(s1 = s2, s2 = s1, 
                                c1 = comb2)
                            if improved:
                                # Gerenciar Memoria
                                MEMORIA = [
                                    M for M in MEMORIA
                                    if all([c_ not in comb2 for c_ in M[2]])
                                    ]
                                MEMORIA.append((s2, s1, comb2.copy()))
                                break
                            
                            # Procedimento , _SE, _FE
                            # Procedimento , _SE, _FE
                            improved = self._procedimento_nx0(s1 = s1, s2 = s2, 
                                c1 = comb1, c2 = comb2)
                            #print("compara", self.SE.routes[s1] == _SE.routes[s1])
                            # Caso melhore:
                            if improved:
                                # Gerenciar Memoria
                                MEMORIA = [
                                    M for M in MEMORIA
                                    if all([c_ not in comb1+comb2 for c_ in M[2]])
                                    ]
                                MEMORIA.append((s1, s2, comb1.copy()))
                                MEMORIA.append((s1, s2, comb2.copy()))
                                break
                            
                            # Fim das possibilidades
                            if comb2 == candidados2[-self.n:]:
                                break
                            if comb2[-1] == candidados2[-1]: 
                                # Todas possibilidades testas
                                # Remove o último e ante penultimo
                                del comb2[-1]
                                del comb2[-1]
                            else:
                                # Elimina so o ultimo
                                del comb2[-1]
                            
                        if improved:
                            break
                        # Fim das possibilidades
                        if comb1 == candidados1[-self.n:]:
                            break
                        if comb1[-1] == candidados1[-1]: 
                            # Todas possibilidades testas
                            # Remove o último e ante penultimo
                            del comb1[-1]
                            del comb1[-1]
                        else:
                            # Elimina so o ultimo
                            del comb1[-1]
change = lambda SE, FE, n, tipo, tipoComb, routingFunction: changeModule(SE, FE, n, tipo = tipo, tipoComb=tipoComb, routingFunction=routingFunction).returnData()