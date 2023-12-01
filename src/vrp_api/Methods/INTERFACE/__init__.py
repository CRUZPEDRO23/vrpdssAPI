

import numpy as np

from ._instancia import _instancia
from ..VRP.savings import savings_init

class Problema(_instancia):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.SE = {s: {"rota": [s for i in range(self.m_s[s]+1)],
                       "idxs": np.array(list(range(1, self.m_s[s]+1))),
                       "cost": np.zeros(self.m_s[s]),
                       "weight": np.zeros(self.m_s[s])}
                   for s in self.S}
        
        nTrips = int(self.d_i.sum() / self.Q1)*len(self.S)
        self.FE = {
            "rota": [0 for i in range(nTrips+1)],
            "weightInrota": [0 for i in range(nTrips+1)],
            "idxs": np.array(list(range(1, nTrips+1))),
            "cost": np.zeros(nTrips),
            "weight": np.zeros(nTrips)}
    
        self.W_s = {s: 0 for s in self.S}
    def CalcWs(self):
        return {s: self.d_i[self.SE[s]["rota"]].sum() for s in self.S}
    
    def removeri(self, s, C:list):
        #obj = self.SE[s].copy()
        obj = dict()
        for key in self.SE[s]:
            obj[key] = self.SE[s][key].copy()
        
        
        p = 1
        idx = 0
        while p < len(obj["rota"])-1 and len(C):
            if p > obj["idxs"][idx]:
                idx+=1
            if obj["rota"][p] in C:
                C.remove(obj["rota"][p])
                # Remover Peso e custo
                obj["weight"][idx] -= self.d_i[obj["rota"][p]]
                obj["cost"][idx] += self.C_ij[obj["rota"][p-1], obj["rota"][p+1]] - self.C_ij[obj["rota"][p-1], obj["rota"][p]] - self.C_ij[obj["rota"][p], obj["rota"][p+1]]
                # remover cliente
                obj["rota"] = obj["rota"][:p] + obj["rota"][p+1:]
                obj["idxs"][idx:] -= 1
            else:
                p+=1
        if len(C):
            return obj.copy(), False
        #print("validar indices remove", all(np.array(obj["rota"])[obj["idxs"]]==s))
        return obj.copy(), True
    def addi(self, s, C:list, Obj = None):
        #obj = self.SE[s].copy()
        obj = dict()
        if Obj==None:
            for key in self.SE[s]:
                obj[key] = self.SE[s][key].copy()
        else:
            for key in Obj:
                obj[key] = Obj[key].copy()
        #if s == 3: print("I", s, obj["weight"])        
        for c in C:
            bestP = -1
            bestCost = np.inf
            bestIdx = -1
            idx = 0
            for p in range(1, len(obj["rota"])):
                if p > obj["idxs"][idx]:
                    idx+=1
                i = obj["rota"][p-1]
                j = obj["rota"][p]
                cost = self.C_ij[i, c] + self.C_ij[c, j] - self.C_ij[i, j]
                if cost < bestCost and obj["weight"][idx] + self.d_i[c] <= self.Q2_s[s]:
                    bestCost = cost
                    bestP = p
                    bestIdx = idx
            if bestP == -1:
                return obj, False# Sem sucesso
            obj["rota"] = obj["rota"][:bestP] + [c] + obj["rota"][bestP:]
            obj["idxs"][bestIdx:] += 1
            obj["cost"][bestIdx] += bestCost
            obj["weight"][bestIdx] += self.d_i[c]
        #if s == 3: print(s, obj["weight"])
        validar = all(np.array(obj["rota"])[obj["idxs"]]==s)
        if not validar: print("validar indices add", validar)
        #print(obj)
        return obj, True # Sucesso
    def calcAttrbs(self, r):
        s = r[0]
        obj = {
            "rota": [s for i in range(self.m_s[s]+1)],
            "idxs": np.array(list(range(1, self.m_s[s]+1))),
            "cost": np.zeros(self.m_s[s]),
            "weight": np.zeros(self.m_s[s])}
        obj["rota"] = r
        idx = 0
        p = 0
        for i in range(1, len(r)):
            #print(i, "i")
            if r[i] == s:
                obj["idxs"][idx] = i
                obj["weight"][idx] = self.d_i[r[p:i]].sum()
                obj["cost"][idx] = self.calculate_distance(route=r[p:i+1], dist_matrix=self.C_ij) 
                p = i
                idx+=1
        #print("rota", obj["rota"])
        #print("idxs", obj["idxs"])
        return obj
    def calcFE(self, W_s):
        # Iniciar rota
        nTrips = int(self.d_i.sum() / self.Q1)*len(self.S)
        
        FE = {"rota": [0 for i in range(nTrips+1)],
              "weightInrota": [0 for i in range(nTrips+1)],
              "idxs": np.array(list(range(1, nTrips+1))),
              "cost": np.zeros(nTrips),
              "weight": np.zeros(nTrips)}

        # Criar rotas Diretas
        idxr = 0
        d_s = np.array([W_s[s] if s in self.S else 0 for s in [0] + list(self.S)])
        #print(d_s)
        for s in self.S:
            while d_s[s] >= self.Q1:
                p = FE["idxs"][idxr]
                FE["rota"] = FE["rota"][:p] + [s] + FE["rota"][p:]
                FE["weightInrota"] = FE["weightInrota"][:p] + [self.Q1] + FE["weightInrota"][p:]
                FE["weight"][idxr] = self.Q1
                FE["cost"][idxr] = self.C_ij[0, s] + self.C_ij[s, 0]
                #self.weight[idxr] += self.cap
                #self.cost += self.C_ij[0, s] + self.C_ij[s, 0]
                #self.idxEndRoute[idxr:]+=1
                FE["idxs"][idxr:]+=1
                d_s[s] -= self.Q1
                idxr+=1
                
        C = [s for s in self.S if d_s[s]>0]
        #print(d_s)
        routes = savings_init(
            Cost_Matrix=self.C_ij, 
            d_i = d_s, 
            Q2=self.Q1, 
            C=C)
        #print(routes)
        for r in routes:
            p = FE["idxs"][idxr]
            FE["rota"] = FE["rota"][:p] + r[1:-1] + FE["rota"][p:]
            FE["weightInrota"] = FE["weightInrota"][:p] + list(d_s[r[1:-1]]) + FE["weightInrota"][p:]
            FE["weight"][idxr] = d_s[r].sum()
            FE["cost"][idxr] = self.calculate_distance(r, self.C_ij)
            FE["idxs"][idxr:]+=len(r[1:-1])
            idxr+=1
            
        #print("FE", routes)
        #print("FE", FE["rota"])
        return FE
    def validar(self):
        
        for s in self.S:
            start = 0
            for idx, p in enumerate(self.SE[s]["idxs"]):
                if len(self.SE[s]["rota"][start:p+1])>2: 
                    if self.SE[s]['cost'][idx] != self.calculate_distance(self.SE[s]["rota"][start:p+1], self.C_ij):
                        print("Erro de custo", self.SE[s]['cost'][idx], self.calculate_distance(self.SE[s]["rota"][start:p+1], self.C_ij))
                    if self.d_i[self.SE[s]["rota"][start:p+1]].sum() != self.SE[s]['weight'][idx]:
                        print("Erro de peso")
                    
                start = p
        
        start = 0
        for idx, p in enumerate(self.FE["idxs"]):
            r = self.FE["rota"][start:p+1]
            if self.FE['cost'][idx] != self.calculate_distance(r, self.C_ij):
                print("Erro de custo FE")
            start = p
        
    def showRoutes(self):
        costSE = sum([self.SE[s]['cost'].sum() for s in self.S])
        costFE = self.FE['cost'].sum()
        
        print("###############################")
        print("###############################")
        print(f"Routes SE - Costs: {costSE}")
        for s in self.S:
            start = 0
            for idx, p in enumerate(self.SE[s]["idxs"]):
                if len(self.SE[s]["rota"][start:p+1])>2: 
                    print(
                        self.SE[s]["rota"][start:p+1], 
                        round(self.SE[s]['cost'][idx],1), 
                        round(self.SE[s]['weight'][idx],1), 
                        self.Q2_s[s],
                        self.d_i[self.SE[s]["rota"][start:p+1]].sum())
                start = p
        print("-------------------------------")
        print(f"Routes FE - Costs: {costFE}")
        start = 0
        for idx, p in enumerate(self.FE["idxs"]):
            r = self.FE["rota"][start:p+1]
            #print(r)
            if len(r)>2: 
                print(r, round(self.FE['cost'][idx],1), round(self.FE['weight'][idx],1), self.Q1)
            start = p
    
        print(f"Total Cost: {costSE+costFE}")
        print("###############################")
        print("###############################")
    
    ### DEV FUNCTIONS
    def routes(self):
        for s in self.S:
            print(self.SE[s]["rota"])
            
    def desloc(self, s1, s2, C):
        OBJ1, SUCESS1 = self.removeri(s1, C.copy())
        OBJ2, SUCESS2 = self.addi(s2, C.copy())
        if SUCESS1 and SUCESS2:
            self.SE[s1] = OBJ1
            self.SE[s2] = OBJ2
        else:
            print("Falha")
        