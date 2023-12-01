# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 16:40:39 2023

@author: jose-


Realiza leitura das instancias
"""

import numpy as np
import copy

from typing import Type, List, Tuple

# default clurster method
from .Clusters.NearestNaiborhold import NearestNaiborhold
# default VRP method
from .VRP.NearestNeiborhold2ECVRP import NearestNeiborhold2ECVRP
from .VRP.savings import savings_init


class _generalFunctions(object):
    def calculate_distance_matrix(self, locations: List[Tuple[float, float]]) -> np.ndarray:
        n = len(locations)
        dist_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(i+1, n):
                dist_matrix[i][j] = dist_matrix[j][i] = np.linalg.norm(np.array(locations[i]) - np.array(locations[j]))
        return dist_matrix

    def calculate_total_distance(self, solution: List[List[int]], dist_matrix: np.ndarray) -> float:
        total_distance = 0
        for route in solution:
            if len(route)>0:
                r = np.array(route)
                total_distance += dist_matrix[np.roll(r, 1), r].sum()
        return total_distance
    def calculate_distance(self, route: List[int], dist_matrix: np.ndarray) -> float:
        return dist_matrix[np.roll(route, 1), route].sum()

class _instancia(_generalFunctions):
    def __init__(self, **kwargs):
        """
        
        **kwargs["file"]: Object Opened as readding:: file = Open(filename, "r")

        """

        # DADOS GERAIS DA INSTANCIA
        self.n_cds = 0
        self.n_sats = 0
        self.n_customers = 0

        self.CD = None#np.arange(n_cds)
        self.S = None#np.arange(start = n_cds, stop=n_cds+n_sats)
        self.C = None#np.arange(start = n_cds+n_sats, stop=n_cds+n_sats+n_customers)
        
        self.locations = list()# Localizaçoes [(x, y)] -> Primeiro CDS, depois SATS depois Clientes.
        
        self.d_i = None #Demanda por cliente i
        
        # Dados para a First Echelong FE
        self.Q1 = None
        self.K1 = None     # Qnt truck on depot
        self._cost_per_km_from_CD = None
        self._fixedCostPerTruck = None
        
        # Dados para a Second Echelong SE
        self.Q2_s = None    #Cap per Satellite
        self.m_s = None     # Qnt city freighter per sat
        self.K2 = None      # Total city freighter on SE
        
        self._CAPACITY_Q2 = None # Instancias consideram capacidade igual em todos os veículos
        self._cost_per_km_from_SAT = None
        self._fixedCostPercity_freighter = None
        self._city_freighterPerSat = None
        
        self.cv_s = None # Custo variavel dos veículos no satelite s
        self.cv_cd = None # Custo variavel dos veiculos do CD
        self.cHr_s = None # Custo Hora dos veículos no satelite s
        self.cHr_cd = None # Custo Hora dos veiculos do CD
        
        # Dados de Custo:
        self.d_ij = None #calculate_distance_matrix(locations)
        self.C_ij = None #d_ij
        self.t_ij = None #time_ij
        self.ts_ij= None # time_ij from s
        self.h_s = None # Custo de manutençao de estoque no satelite
        
        #Arcos
        self.A1 = list() # list[(i, j)] arcos da FE i, j in CD unicao S
        self.A2 = list() # list[(i, j)] # list[(i, j)] arcos da SE i, j in S unicao C exceto onde i, j pertencem a S        

        ## CONTROLER __ READED WITH SUCESS
        self.sucessReaded = False
        
        self._from_JSON_request(request_data = kwargs["request_data"])
    def _from_JSON_request_OLD(self, request_data):
        
    
        nodes = []
        sats = []
        vehicle = "car"
        if request_data:
            for inp in request_data:
                if inp == "d_ij":
                    self.d_ij = request_data[inp]
                if inp == "t_ij":
                    self.t_ij = request_data[inp]
                if inp == "d_i":
                    d_i = request_data[inp]
                    self.d_i = np.array(d_i, dtype=float)
                if inp == "Q1":
                    self.Q1 = request_data[inp]
                if inp == "K1":
                    self.K1 = request_data[inp]
                if inp == "Q2_s":
                    Q2_s = request_data[inp]
                    Q2_s = {int(s): Q2_s[s] for s in Q2_s}
                    self.Q2_s = Q2_s #request_data[inp]
                if inp == "m_s":
                    self.m_s = request_data[inp]
                if inp == "h_s":
                    self.h_s = request_data[inp]
                    
                if inp == "nodes":
                    nodes = request_data[inp]
                #if inp == "vehicle":
                #    vehicle = request_data[inp]
                if inp == "sats":
                    sats = request_data[inp]
            if self.d_ij==None or self.t_ij==None:
                print("ERRO 1")
                return -1
        else:
            print("ERRO 2")
            return -1
        
        try:
            nodes = np.arange(len(self.d_ij))
            self.d_ij = np.array(self.d_ij)
            self.t_ij = np.array(self.t_ij)
            
        except:
            print("ERRO 3")
            return -1

        ## DADOS GERAIS (nodes)
        self.n_cds = 1
        self.n_sats = len(sats)
        self.n_customers = len(nodes) - self.n_cds - self.n_sats
        
        self.CD = np.arange(self.n_cds)
        self.S = np.arange(start = self.n_cds, stop=self.n_cds+self.n_sats)
        self.C = np.arange(start = self.n_cds+self.n_sats, stop=self.n_cds+self.n_sats+self.n_customers)

        if type(self.d_i) != np.ndarray:
            self.d_i = np.zeros(len(nodes))
            self.d_i[self.n_cds+self.n_sats:] = 1
        

        # Dados para a First Echelong FE
        if self.Q1 == None: self.Q1 = 100
        if self.K1 == None: self.K1 = 100     # Qnt truck on depot

        self._cost_per_km_from_CD = 1
        self._fixedCostPerTruck = 1
        
        # Dados para a Second Echelong SE
        if self.Q2_s == None: self.Q2_s = {s: 10 for s in self.S}    #Cap per Satellite
        if self.m_s == None: self.m_s = {s: int(self.n_customers/10)*10 for s in self.S}     # Qnt city freighter per sat
        if self.K2 == None: self.K2 = sum(self.m_s.values())      # Total city freighter on SE
        
        self._CAPACITY_Q2 = None # Instancias consideram capacidade igual em todos os veículos
        self._cost_per_km_from_SAT = 1
        self._fixedCostPercity_freighter = None
        self._city_freighterPerSat = None
        
        
        # Dados de Custo:
        #self.d_ij = None #calculate_distance_matrix(locations)
        #self.C_ij = None #d_ij
        if self.h_s == None: self.h_s = np.zeros(self.n_cds+self.n_sats) # Custo de manutençao de estoque no satelite
        
        # Arcos
        self.A1 = [(i, j) for i in list(self.CD)+list(self.S) for j in list(self.CD)+list(self.S) if i!=j]
        self.A2 = [(i, j) for i in list(self.S)+list(self.C) for j in list(self.S)+list(self.C) if (i!=j and (i not in self.S or j not in self.S))]
        
        self.C_ij = self.d_ij
        self.C_ij[0:self.n_cds, :] *= self._cost_per_km_from_CD
        self.C_ij[:, 0:self.n_cds] *= self._cost_per_km_from_CD
        self.C_ij[self.n_cds:, self.n_cds:] *= self._cost_per_km_from_SAT
        
        
        
        self.sucessReaded = True
    
    def _from_JSON_request(self, request_data):
        
        nodes = []
        sats = []
        vehicle = "car"
        if request_data:
            for inp in request_data:
                if inp == "d_ij":
                    self.d_ij = request_data[inp]
                if inp == "t_ij":
                    self.t_ij = request_data[inp]
                if inp == "ts_ij":
                    self.ts_ij = request_data[inp]
                if inp == "d_i":
                    d_i = request_data[inp]
                    self.d_i = np.array(d_i, dtype=float)
                if inp == "Q1":
                    self.Q1 = request_data[inp]
                if inp == "K1":
                    self.K1 = request_data[inp]
                if inp == "Q2_s":
                    Q2_s = request_data[inp]
                    Q2_s = {int(s): Q2_s[s] for s in Q2_s}
                    self.Q2_s = Q2_s #request_data[inp]
                if inp == "m_s":
                    self.m_s = request_data[inp]
                if inp == "h_s":
                    self.h_s = request_data[inp]
                    
                if inp == "nodes":
                    nodes = request_data[inp]
                #if inp == "vehicle":
                #    vehicle = request_data[inp]
                if inp == "sats":
                    sats = request_data[inp]
                
                # INPUTS Custos variaveis
                if inp == "cv_s":
                    self.cv_s = request_data[inp]
                if inp == "cv_cd":
                    self.cv_cd = request_data[inp]
                if inp == "cHr_s":
                    self.cHr_s = request_data[inp]
                if inp == "cHr_cd":
                    self.cHr_cd = request_data[inp]


            if self.d_ij==None or self.t_ij==None:
                print("ERRO 1")
                return -1
        else:
            print("ERRO 2")
            return -1
        
        try:
            nodes = np.arange(len(self.d_ij))
            self.d_ij = np.array(self.d_ij)
            self.t_ij = np.array(self.t_ij)
            
        except:
            print("ERRO 3")
            return -1
            
        
        ## DADOS GERAIS (nodes)
        self.n_cds = 1
        self.n_sats = len(sats)
        self.n_customers = len(nodes) - self.n_cds - self.n_sats
        
        self.CD = np.arange(self.n_cds)
        self.S = np.arange(start = self.n_cds, stop=self.n_cds+self.n_sats)
        self.C = np.arange(start = self.n_cds+self.n_sats, stop=self.n_cds+self.n_sats+self.n_customers)
        
        try:
            ts_ij = dict()
            for idx_s, t_ij in enumerate(self.ts_ij):
                s = self.S[idx_s]
                ts_ij[s] = np.array(list(self.ts_ij[idx_s]))
                #self.t_ij = np.array(self.t_ij)
            self.ts_ij = ts_ij
        except:
            print("ERRO 4")
            return -1
        
        # -- Demanda
        if type(self.d_i) != np.ndarray:
            self.d_i = np.zeros(len(nodes))
            self.d_i[self.n_cds+self.n_sats:] = 1
        

        # Dados para a First Echelong FE
        if self.Q1 == None: self.Q1 = 100
        if self.K1 == None: self.K1 = 100     # Qnt truck on depot

        # Custos variaveis
        self._cost_per_km_from_CD = 1
        self._fixedCostPerTruck = 1
        if self.cv_s == None: 
            self.cv_s = {s: 1 for s in self.S}
        else:
            self.cv_s = {s: self.cv_s[idx_s] for idx_s, s in enumerate(self.S)}
        if self.cv_cd == None: 
            self.cv_cd = {cd: 1 for cd in self.CD}
        else:
            self.cv_cd = {cd: self.cv_cd[idx_cd] for idx_cd, cd in enumerate(self.CD)}

        if self.cHr_s == None: 
            self.cHr_s = {s: 1 for s in self.S}
        else:
            self.cHr_s = {s: self.cHr_s[idx_s] for idx_s, s in enumerate(self.S)}
        if self.cHr_cd == None: 
            self.cHr_cd = {cd: 1 for cd in self.CD}
        else:
            self.cHr_cd = {cd: self.cHr_cd[idx_cd] for idx_cd, cd in enumerate(self.CD)}


        #print(self.cv_s)

        # Dados para a Second Echelong SE
        if self.Q2_s == None: self.Q2_s = {s: 10 for s in self.S}    #Cap per Satellite
        if self.m_s == None: self.m_s = {s: int(self.n_customers/10)*10 for s in self.S}     # Qnt city freighter per sat
        if self.K2 == None: self.K2 = sum(self.m_s.values())      # Total city freighter on SE
        
        self._CAPACITY_Q2 = None # Instancias consideram capacidade igual em todos os veículos
        self._cost_per_km_from_SAT = 1
        self._fixedCostPercity_freighter = None
        self._city_freighterPerSat = None
        
        
        # Dados de Custo:
        #self.d_ij = None #calculate_distance_matrix(locations)
        #self.C_ij = None #d_ij
        if self.h_s == None: self.h_s = np.zeros(self.n_cds+self.n_sats) # Custo de manutençao de estoque no satelite
        
        # Arcos
        self.A1 = [(i, j) for i in list(self.CD)+list(self.S) for j in list(self.CD)+list(self.S) if i!=j]
        self.A2 = [(i, j) for i in list(self.S)+list(self.C) for j in list(self.S)+list(self.C) if (i!=j and (i not in self.S or j not in self.S))]
        
        self.C_ij = self.d_ij
        self.C_ij[0:self.n_cds, :] *= self._cost_per_km_from_CD
        self.C_ij[:, 0:self.n_cds] *= self._cost_per_km_from_CD
        self.C_ij[self.n_cds:, self.n_cds:] *= self._cost_per_km_from_SAT
        
        
        
        self.sucessReaded = True

    def _read(self, file):
        #dados = dict()
        contador = 1 # auxilia a saber qual dado é
        """
        contador = 1 Trucks: (total #, capacity, cost per distance, fixcost)
        contador = 2 CityFreighters: (max cf/sat, total #, cap, cost/dist, fixcost)
        contador = 3 Stores: (first: depot x,y; then: satellites x,y)
        contador = 4 Customers: (x,y,demand)
        
        """
        
        
        with file:
            linhas = file.readlines()
            for l in linhas:
                if l[0] == "!":continue
                
                if contador == 1:
                    self.K1, self.Q1, self._cost_per_km_from_CD, self._fixedCostPerTruck = [float(d.strip()) for d in l.split(",")]
                    self.K1 = np.arange(self.K1)
                    #print(self.Q1, self.CD_CAPACITY, self.cost_per_km_from_CD, self.fixedCostPerTruck)
                elif contador == 2:
                    self._city_freighterPerSat, total, self._CAPACITY_Q2, self._cost_per_km_from_SAT, self._fixedCostPercity_freighter = [float(d.strip()) for d in l.split(",")]
                    
                elif contador == 3:
                    data = l.split("   ")
                    
                    # Para cada coordenada:
                    
                    for idx, d in enumerate(data):
                        if len(d)==0: continue # só sugeira da leitura
                        
                        if len(self.locations) == 0: 
                            self.n_cds += 1 # Primeira localização
                        else:
                            self.n_sats += 1
                        # pegar coordenadas e inserir como tuple
                        x, y = d.strip().split(",")
                        self.locations.append((float(x.strip()), float(y.strip())))
                        
                    # Agora como temos número de satélites, podemos preencher seus dados corretamente:
                    # O [0 for d in range(self.n_cds)] é apenas para corrigir indices quando usar o modelo não ter problemas
                    
                    self.Q2_s = np.array([0 for d in range(self.n_cds)]+[self._CAPACITY_Q2 for s in range(self.n_sats)])
                    self.m_s = np.array([0 for d in range(self.n_cds)]+[self._city_freighterPerSat for s in range(self.n_sats)], dtype=np.int)
                    self.K2 = self.m_s.sum()
                    self.K2_s = self.m_s
                    
                    del data
                elif contador == 4:
                    data = l.split("   ")
                    # Istanciar demanda iniciando com 0 para depot e sats -> Feito para faciliar uso de indices no modelo
                    d_i = [0 for i in range(self.n_cds+self.n_sats)]
                    
                    for idx, d in enumerate(data):
                        #x, y, demand
                        if len(d)==0: continue # só sugeira da leitura
                        x, y, demand = d.strip().split(",")
                        self.locations.append((float(x.strip()), float(y.strip())))
                        d_i.append(float(demand))
                        self.n_customers+=1
                    
                    self.d_i = np.array(d_i)
                    
                    # Criar conjuntos:
                    self.CD = np.arange(self.n_cds)
                    self.S = np.arange(start = self.n_cds, stop=self.n_cds+self.n_sats)
                    self.C = np.arange(start = self.n_cds+self.n_sats, stop=self.n_cds+self.n_sats+self.n_customers)
                    
                    del data
                    
                contador += 1
            
            
        # Calculo de Custos:
        # como instancias consideram h_s = 0
        self.h_s = np.zeros(self.n_cds+self.n_sats)
        
        # Distancias Euclidianas
    
        self.d_ij = self.calculate_distance_matrix(self.locations)
        
        self.C_ij = self.d_ij
        self.C_ij[0:self.n_cds, :] *= self._cost_per_km_from_CD
        self.C_ij[:, 0:self.n_cds] *= self._cost_per_km_from_CD
        self.C_ij[self.n_cds:, self.n_cds:] *= self._cost_per_km_from_SAT
        
        # Arcos
        self.A1 = [(i, j) for i in list(self.CD)+list(self.S) for j in list(self.CD)+list(self.S) if i!=j]
        self.A2 = [(i, j) for i in list(self.S)+list(self.C) for j in list(self.S)+list(self.C) if (i!=j and (i not in self.S or j not in self.S))]
        
        file.close()
        
    def costs(self):
        """
        
        Realiza avaliação de custos 

        Returns
        -------
        None.

        """
        if not hasattr(self, "rotas") or not hasattr(self, "rotasFE"):
            print("Sem variáveis de rotas definidas")
        else:
            self.rotasSE = [[int(i) for i in r] for r in self.rotas]
            self.rotasFE = [[int(i) for i in r] for r in self.rotasFE]
            
            self.costSE = self.calculate_total_distance(self.rotasSE, self.C_ij)
            self.costWs = sum([self.W_s[s] * self.h_s[s] for idxs, s in enumerate(self.S)])
            self.costFE = self.calculate_total_distance(self.rotasFE, self.C_ij)
    
            self.totalCost = self.costSE+self.costWs+self.costFE
            
            print("Insetion custo FE", self.costFE)
            print("Insetion custo SE", self.costSE)
            print("Insetion custo Ws", self.costWs)
            print("Insetion Custo Total", self.totalCost) 
            
    


    def CalcWs(self):
        return {s: sum([self.d_i[i] for rota in self.rotas for i in rota[1:-1] if rota[0] == s]) for s in self.S}
    

#I = instancia("./2/Set2a_E-n22-k4-s6-17.dat")

class route(object):
    def __init__(self, **kwargs):#s, m_s, cap, d_i, C_ij
        self.route = [kwargs["s"]] * (kwargs["m_s"]+1) # Big turn
        self.idxEndRoute = np.array(list(range(1, kwargs["m_s"]+1)))
        self.s = kwargs["s"]
        self.cost = np.array([0.0] * kwargs["m_s"])
        self.tCost = 0.0
        self.time = np.array([0.0] * kwargs["m_s"])
        self.tTime = 0.0
        self.weight = np.array([0.0] * kwargs["m_s"])
        self.cap = kwargs["cap"]
        self.nC = 0
        self.m_s = kwargs["m_s"]
        #self.id = kwargs["id"]
    def getIndexEndRoute(self):
        self.idxEndRoute = np.array(list(range(1, self.m_s+1)))
        idx = 0
        for i in range(1, len(self.route)):
            if self.route[i] == self.s:
                self.idxEndRoute[idx] = i
                idx+=1
        
    def getWeight(self, d_i):
        lastIdx = 0
        for i, idx in enumerate(self.idxEndRoute):
            self.weight[i] = d_i[self.route[lastIdx:idx]].sum()
            lastIdx = idx
    def CalcCost(self, route, dist_matrix):
        return _generalFunctions().calculate_distance(route=route, 
                                                      dist_matrix = dist_matrix)
    def getCost(self, dist_matrix):
        lastIdx = 0
        for i, idx in enumerate(self.idxEndRoute):
            if len(self.route[lastIdx:idx])==0:
                self.cost[i] = 0
            else:
                self.cost[i] = self.CalcCost(route=self.route[lastIdx:idx], dist_matrix = dist_matrix)
            lastIdx = idx
        self.tCost = self.cost.sum()
    
    #--- Rotinas
    def remove(self, c1: list[int], d_i, dist_matrix):

        self.route = [i for i in self.route if i not in c1]
        self.getIndexEndRoute()
        self.getWeight(d_i = d_i)
        self.getCost(dist_matrix=dist_matrix)
    
    def add(self, c1: list[int], d_i, dist_matrix,routingFunction = lambda route, idxs, cap: route):
        # Adiciona nas rotas menos ociosas primeiro
        sucess = True
        for c in c1:
            ociosidade = self.cap - self.weight
            
            for i in range(self.m_s):
                #if all(list(ociosidade==np.inf)):
                #    sucess = False
                #    break
                idx = np.argmin(ociosidade)
                #print("ociosidade", ociosidade, idx)
                if ociosidade[idx]==np.inf:
                    sucess = False
                    return sucess
                if ociosidade[idx] - d_i[c] < 0:
                    ociosidade[idx] = np.inf
                    continue
                
                end = self.idxEndRoute[idx]
                #print("idx", end)
                self.route.insert(end, c)
                #self.route = self.route[:end+1] + [c] + self.route[end+1:]
                self.idxEndRoute[idx:]+=1
                self.weight[idx]+=d_i[c]
                break
        
        self.route = routingFunction(route=self.route.copy(), idxs=self.idxEndRoute.copy(), cap=self.cap)
        self.getIndexEndRoute()
        self.getWeight(d_i = d_i)
        self.getCost(dist_matrix=dist_matrix)
        return sucess
    def copy(self):
        return copy.copy(self)

class SE(object):
    def __init__(self, **kwargs):#S, m_s, Q2_s, d_i, C_ij, cv_s
        self.routes = {s: route(s = s, m_s = kwargs["m_s"][s], cap = kwargs["Q2_s"][s]) for s in kwargs["S"]}
        self.S = kwargs["S"]
        self.costSE = 0
        self.d_i = kwargs["d_i"]
        self.d_ij = kwargs["d_ij"]
        self.m_s = kwargs["m_s"]
        self.Q2_s = kwargs["Q2_s"]
        self.cv_s = kwargs["cv_s"]
    def getCost(self):
        self.costSE = 0
        for r in self.routes.values():
            s = r.route[0]
            r.getCost(dist_matrix = self.d_ij*self.cv_s[s])
            #print(r.tCost)
            self.costSE += r.tCost
    def validarRotas(self):        
        
        # Validar capacidade:
        for s in self.S:
            r = self.routes[s].route
            idx_ = 0
            idx_r = 0
            for i in range(1, len(r)):
                if r[i] == s:
                    # Validar capacidade:
                    if self.d_i[r[idx_:i]].sum()>self.routes[s].cap:
                        print("Capacidade Inválida em ", s)
                        return False
                    # Validar Weight:
                    if self.d_i[r[idx_:i]].sum()!=self.routes[s].weight[idx_r]:
                        print("Carga Incorreta em ", s)
                        return False
                    # Validar Indexs:
                    if self.routes[s].idxEndRoute[idx_r]!=i:
                        print(self.routes[s].idxEndRoute)
                        print(self.routes[s].route)
                        print("Indices Incorretos em ", s)
                        return False
                    # Validar Costs:
                    if self.routes[s].CalcCost(route=r[idx_:i], dist_matrix=self.d_ij*self.cv_s[s])!=self.routes[s].cost[idx_r]:
                        #print("rota", r[idx_:i], r)
                        #print("cost", self.routes[s].cost, idx_r)
                        #print(self.routes[s].CalcCost(route=r[idx_:i], dist_matrix=self.C_ij), self.routes[s].cost[idx_r])
                        print("Custo Incorreto em ", s)
                        return False
                    
                    idx_ = i
                    idx_r += 1
            
            
        return True
    def copy(self):
        return copy.copy(self)
class FE(object):
    def __init__(self, **kwargs):
        self.routes = [kwargs["s"]] * (kwargs["n_Trips"]+1) # Big turn
        self.idxEndRoute = np.array(list(range(1, kwargs["n_Trips"]+1)))
        self.n_Trips = kwargs["n_Trips"]
        self.s = kwargs["s"]
        self.S = kwargs["S"]
        self.cost = np.array([0] * kwargs["n_Trips"])
        self.tCost = 0
        self.weight = np.array([0] * kwargs["n_Trips"])
        self.cap = kwargs["cap"]
        self.nC = [0] * kwargs["n_Trips"]
        self.d_i = None     
        self.C_ij = kwargs["C_ij"]
        self.W_s = {s: 0 for s in kwargs["S"]}
    def CalcCost(self, route, dist_matrix):
        return _generalFunctions().calculate_distance(route=route, 
                                                      dist_matrix = dist_matrix)
    def calcFE(self):
        self.routes = [self.s] * (self.n_Trips+1) # Big turn
        self.idxEndRoute = np.array(list(range(1, self.n_Trips+1)))
        self.cost = np.array([0] * self.n_Trips)
        self.tCost = 0
        self.weight = [0] * self.n_Trips
        # Criar Rotas Diretas:
        idxr = 0
        startRota = 0
        p = 1
        d_s = np.array([self.W_s[s] if s in self.S else 0 for s in [0] + list(self.S)])
        #print(self.S)    
        for s in self.S:
            while d_s[s] >= self.cap:
                if idxr>0:
                    startRota = p
                p = self.idxEndRoute[idxr]
                self.routes.insert(p, s)
                self.weight[idxr] += self.cap
                #print("C",self.C_ij[0, s])
                #print(self.C_ij[s, 0])
                #print(self.cost)
                self.cost[idxr] += self.C_ij[0, s] + self.C_ij[s, 0]
                self.idxEndRoute[idxr:]+=1
                d_s[s] -= self.cap
                idxr+=1
        #print(d_s, self.cap)
        routes = savings_init(
            Cost_Matrix=self.C_ij, 
            d_i = d_s, 
            Q2=self.cap, 
            C=self.S)
        for r in routes:
            if len(r)==2: continue
            if idxr>0:
                startRota = self.idxEndRoute[idxr-1]
            else:  
                startRota = 0
            p = self.idxEndRoute[idxr]
            self.routes = self.routes[:startRota+1] + r[1:-1] + self.routes[p:]
            self.weight[idxr] = d_s[r].sum()
            self.cost[idxr] = self.CalcCost(route=r, dist_matrix=self.C_ij)
            self.idxEndRoute[idxr:]+=len(r[1:-1])
            idxr+=1
        self.getIndexEndRoute()
        self.getCost(dist_matrix = self.C_ij)
        
    def getIndexEndRoute(self):
        idx = 0
        for i in range(1, len(self.routes)):
            if self.routes[i] == self.s:
                self.idxEndRoute[idx] = i
                idx+=1
    def getWeight(self, d_i):
        lastIdx = 0
        for i, idx in enumerate(self.idxEndRoute):
            self.weight[i] = d_i[self.routes[lastIdx:idx]].sum()
            lastIdx = idx
    
    def getCost(self, dist_matrix):
        #if dist_matrix == None: dist_matrix = self.C_ij
        
        lastIdx = 0
        for i, idx in enumerate(self.idxEndRoute):
            if len(self.routes[lastIdx:idx])==0:
                self.cost[i] = 0
            else:
                self.cost[i] = self.CalcCost(route=self.routes[lastIdx:idx], dist_matrix = dist_matrix)
            lastIdx = idx
        self.tCost = self.cost.sum()

    def copy(self):
        return copy.copy(self)
    
    def showRoutes(self):
        self.getCost(dist_matrix = self.C_ij)
        lastidx = 0
        #print(self.routes)
        for i, idx in enumerate(self.idxEndRoute):
            if idx < len(self.routes):
                r = self.routes[lastidx: idx+1]# + [self.s]
            else:
                r = self.routes[lastidx:]# + [self.s]
            if len(r)>2: 
                print(r, self.weight[i], self.cost[i])
            lastidx = idx
class interface(_instancia):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.routesSE = SE(S=self.S, m_s=self.m_s, Q2_s=self.Q2_s, d_i=self.d_i, C_ij=self.C_ij, d_ij=self.d_ij, cv_s = self.cv_s)
        self.routesFE = FE(s = 0, S=self.S, n_Trips=10, cap=self.Q1, C_ij=self.d_ij * self.cv_cd[0])
        self.costSE = 0
        self.costFE = 0
        self.totalCost = 0
        
    ## --------- Rotinas
    def calcFE(self):
        W_s = {s: self.d_i[self.routesSE.routes[s].route].sum() for s in self.S}
        self.routesFE.W_s = W_s
        self.routesFE.calcFE()
        self.routesFE.getCost(dist_matrix=self.d_ij * self.cv_cd[0])
    
    
    ## --------- Methods
    
    
    def Clurster(self, ClusterMethod = None):
        if ClusterMethod == None: ClusterMethod = lambda C, S: NearestNaiborhold(S = S, C = C, d_i = self.d_i, cost_Matrix=self.C_ij)
        return ClusterMethod(S = list(self.S), C = list(self.C))
    def ConstructMethod(self, Method =  None, Clurster_s = None):
        if Method == None:
            Method = lambda avaibleRoutes, S, C, d_i, cost_Matrix, Clurster_s: NearestNeiborhold2ECVRP(avaibleRoutes = avaibleRoutes, S = S, C = C, Clurster_s = Clurster_s, d_i = d_i, cost_Matrix=cost_Matrix)
            for s in self.S:
                changeR, idxs = list(zip(*[(r, ir) for ir, r in enumerate(self.routesSE) if r.s == s]))
                #print(idxs)
                changeR, nonroutedcandidates = Method(avaibleRoutes = list(changeR), S = list(self.S), C = list(self.C), d_i = self.d_i, cost_Matrix=self.C_ij, Clurster_s = Clurster_s)
                
                for i, idx in enumerate(idxs):
                    self.routesSE[idx] = changeR[i]
                if len(nonroutedcandidates):
                    print("Rerouting", nonroutedcandidates, Clurster_s[s])
        else:
            Method(Clurster_s)
            
        self.routesSE.getCost()
        self.calcFE()
        self.Method_VRP = Method
        
        
        #self._calcFE(Method = Method)
        #self.CalcCosts()
        
    """def LocalSearchMethod(self, Melhorias):
        
        for Melhoria in Melhorias:
            self.routesSE = Melhoria(self.routesSE)
        
        self._calcFE(Method = self.Method_VRP)
        self.CalcCosts()
        
    """        
    def showRoutes(self):
        self.routesSE.getCost()
        self.costSE = self.routesSE.costSE
        self.costFE = self.routesFE.tCost
        self.totalCost = self.costSE + self.costFE
        print("###############################")
        print("###############################")
        print(f"Routes SE - total: {len(self.routesSE.routes.values())} - Costs: {self.costSE}", self.routesSE.validarRotas())
        for r in self.routesSE.routes.values():
            if len(r.route)>2: 
                print(r.route)#, r.weight, r.cap)
        print("-------------------------------")
        print(f"Routes FE - total: {len(self.routesFE.routes)} - Costs: {self.costFE}")
        self.routesFE.showRoutes()
        
        print(f"Total Cost: {self.totalCost}")
        print("###############################")
        print("###############################")
    
