# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 13:13:52 2023

@author: jose-
"""

import numpy as np
from typing import Type, List, Tuple
import copy


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
    
    def Copy(self, Obj):
        return copy.copy(Obj)

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
        
        
        # Dados de Custo:
        self.d_ij = None #calculate_distance_matrix(locations)
        self.C_ij = None #d_ij
        self.h_s = None # Custo de manutençao de estoque no satelite
        
        #Arcos
        self.A1 = list() # list[(i, j)] arcos da FE i, j in CD unicao S
        self.A2 = list() # list[(i, j)] # list[(i, j)] arcos da SE i, j in S unicao C exceto onde i, j pertencem a S


        ## CONTROLER __ READED WITH SUCESS
        self.sucessReaded = False
        
        self._from_JSON_request(request_data = kwargs["request_data"])


        
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
                if inp == "d_i":
                    self.d_i = request_data[inp]
                if inp == "Q1":
                    self.Q1 = request_data[inp]
                if inp == "K1":
                    self.K1 = request_data[inp]
                if inp == "Q2_s":
                    self.Q2_s = request_data[inp]
                if inp == "m_s":
                    self.m_s = request_data[inp]
                if inp == "h_s":
                    self.h_s = request_data[inp]
                    
                if inp == "nodes":
                    nodes = request_data[inp]
                if inp == "vehicle":
                    vehicle = request_data[inp]
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

        if self.d_i==None:
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
            
    


    
    
