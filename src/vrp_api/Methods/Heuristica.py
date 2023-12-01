# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 16:31:57 2023

@author: jose-
"""

from ._interfaces import interface

# default clurster method
from .Clusters.NearestNaiborhold import NearestNaiborhold
# VRP methods
from .VRP.NearestNeiborhold2ECVRP import NearestNeiborhold2ECVRP
from .VRP.savings import savings_init
from .VRP.insertion import insertion_init

from .VRP.LocalSearch.two_opt import two_opt
from .VRP.LocalSearch import LocalSearch

from .VRP.LocalSearch.change import change



class Heuristica(interface, LocalSearch):
    def exec(self):
        # Clursters:
        ClusterMethod = lambda C, S: NearestNaiborhold(S = S, C = C, d_i = self.d_i, cost_Matrix = self.d_ij, cv_s=self.cv_s, time_Matrix = self.ts_ij, cHr_s=self.cHr_s)
        Clurster_s = self.Clurster(ClusterMethod = ClusterMethod)
        
        # Inicial Solution
        
        VRPMethod = lambda C, s, cap, cv: insertion_init(
            Cost_Matrix = self.d_ij * cv, 
            d_i = self.d_i, 
            Q2 = cap, 
            C = C, 
            sat = s)
        
        def _ConstructMethod(Clurster_s):
            for s in self.S:
                routes = VRPMethod(C = Clurster_s[s], s=s, cap=self.routesSE.routes[s].cap, cv=self.cv_s[s])
                while len(routes) > self.routesSE.m_s[s] and [s, s] in routes:
                    routes.remove([s, s])
                if len(routes) > self.routesSE.m_s[s]:
                    print("Mais rotas que o comportado")
                lastIdx = 1
                for i in range(min([self.routesSE.m_s[s], len(routes)])):
                    self.routesSE.routes[s].route = self.routesSE.routes[s].route[:lastIdx] + routes[i][1:-1] + self.routesSE.routes[s].route[lastIdx:]
                    self.routesSE.routes[s].idxEndRoute[i] = lastIdx + len(routes[i][1:-1]) + 1
                    lastIdx += len(routes[i][1:-1]) + 1
                self.routesSE.routes[s].getIndexEndRoute()
                self.routesSE.routes[s].getWeight(d_i = self.d_i)
                self.routesSE.routes[s].getCost(dist_matrix = self.d_ij * self.cv_s[s])
            self.routesSE.getCost()
        self.ConstructMethod(Method = _ConstructMethod, Clurster_s = Clurster_s)
        
        two_optMethod = lambda route, idxs, cap, cv: two_opt(route, idxs, cap, d_i=self.d_i, dist_matrix = self.d_ij*cv)
        
        for s in self.S:
            r = two_optMethod(
                route = self.routesSE.routes[s].route,
                idxs = self.routesSE.routes[s].idxEndRoute,
                cap = self.routesSE.routes[s].cap,
                cv = self.cv_s[s]
                )
            #print(s, r)
            self.routesSE.routes[s].route = r
            self.routesSE.routes[s].getIndexEndRoute()
            self.routesSE.routes[s].getWeight(d_i = self.d_i)
            self.routesSE.routes[s].getCost(dist_matrix = self.d_ij * self.cv_s[s])
            
        self.routesSE.getCost()
        self.calcFE()
        
    
    def exec_(self):
        
        # Clursters:
        ClusterMethod = lambda C, S: NearestNaiborhold(S = S, C = C, d_i = self.d_i, cost_Matrix = self.C_ij)
        Clurster_s = self.Clurster(ClusterMethod = ClusterMethod)
        
        # Inicial Solution
        
        VRPMethod = lambda C, s, cap: savings_init(
            Cost_Matrix = self.C_ij, 
            d_i = self.d_i, 
            Q2 = cap, 
            C = C, 
            sat = s)
        
        def _ConstructMethod(Clurster_s):
            for s in self.S:
                routes = VRPMethod(C = Clurster_s[s], s=s, cap=self.routesSE.routes[s].cap)
                if len(routes) > self.routesSE.m_s[s]:
                    print("Mais rotas que o comportado")
                lastIdx = 1
                for i in range(min([self.routesSE.m_s[s], len(routes)])):
                    self.routesSE.routes[s].route = self.routesSE.routes[s].route[:lastIdx] + routes[i][1:-1] + self.routesSE.routes[s].route[lastIdx:]
                    self.routesSE.routes[s].idxEndRoute[i] = lastIdx + len(routes[i][1:-1]) + 1
                    lastIdx += len(routes[i][1:-1]) + 1
                self.routesSE.routes[s].getIndexEndRoute()
                self.routesSE.routes[s].getWeight(d_i = self.d_i)
                self.routesSE.routes[s].getCost(dist_matrix = self.C_ij)
            self.routesSE.getCost()
            
        self.ConstructMethod(Method = _ConstructMethod, Clurster_s = Clurster_s)
        
        
        two_optMethod = lambda route, idxs, cap: two_opt(route, idxs, cap, d_i=self.d_i, dist_matrix = self.C_ij)
        
        for s in self.S:
            r = two_optMethod(
                route = self.routesSE.routes[s].route,
                idxs = self.routesSE.routes[s].idxEndRoute,
                cap = self.routesSE.routes[s].cap
                )
            #print(s, r)
            self.routesSE.routes[s].route = r
            self.routesSE.routes[s].getIndexEndRoute()
            self.routesSE.routes[s].getWeight(d_i = self.d_i)
            self.routesSE.routes[s].getCost(dist_matrix = self.C_ij)
            
        self.routesSE.getCost()
        self.calcFE()
        
        SE_, FE_ = change(
            SE=self.routesSE.copy(), 
            FE=self.routesFE.copy(),
            n = 1, 
            tipo = "nx0",
            tipoComb = "default",
            routingFunction=two_optMethod)
        self.routesSE.getCost()
        self.calcFE()
        
        SE_, FE_ = change(
            SE=SE_.copy(), 
            FE=FE_.copy(),
            n = 1, 
            tipo = "misto",
            tipoComb = "default",
            routingFunction=two_optMethod)
        self.routesSE.getCost()
        self.calcFE()
        
        SE_, FE_ = change(
            SE=SE_.copy(), 
            FE=FE_.copy(),
            n = 1, 
            tipo = "nxn",
            tipoComb = "default",
            routingFunction=two_optMethod)
        self.routesSE.getCost()
        self.calcFE()
        
        SE_, FE_ = change(
            SE=SE_.copy(), 
            FE=FE_.copy(),
            n = 2, 
            tipo = "nx0",
            tipoComb = "default",
            routingFunction=two_optMethod)
        self.routesSE.getCost()
        self.calcFE()
        
        SE_, FE_ = change(
            SE=SE_.copy(), 
            FE=FE_.copy(),
            n = 2, 
            tipo = "nxn",
            tipoComb = "default",
            routingFunction=two_optMethod)
        self.routesSE.getCost()
        self.calcFE()
        
        
        ##########
        
        SE_, FE_ = change(
            SE=self.routesSE.copy(), 
            FE=self.routesFE.copy(),
            n = 1, 
            tipo = "nx0",
            tipoComb = "sequence",
            routingFunction=two_optMethod)
        self.routesSE.getCost()
        self.calcFE()
        
        
        SE_, FE_ = change(
            SE=SE_.copy(), 
            FE=FE_.copy(),
            n = 2, 
            tipo = "nx0",
            tipoComb = "sequence",
            routingFunction=two_optMethod)
        self.routesSE.getCost()
        self.calcFE()
        
        SE_, FE_ = change(
            SE=SE_.copy(), 
            FE=FE_.copy(),
            n = 2, 
            tipo = "nxn",
            tipoComb = "sequence",
            routingFunction=two_optMethod)
        self.routesSE.getCost()
        self.calcFE()
        
        
        SE_, FE_ = change(
            SE=SE_.copy(), 
            FE=FE_.copy(),
            n = 4, 
            tipo = "nx0",
            tipoComb = "sequence",
            routingFunction=two_optMethod)
        self.routesSE.getCost()
        self.calcFE()
        
        
        #SE_, FE_ = change(
        #    SE=self.routesSE.copy(), 
        #    FE=self.routesFE.copy(),
        #    n = 2, 
        #    routingFunction=two_optMethod)
        #print(FE_.routes)
        #self.routesSE.getCost()
        #self.calcFE()
        #print(self.routesSE.costSE)
        """self.LocalSearchMethod([
                lambda r: self.change_nx0(
                    routes = r,
                    n = 1
                    )
            ])
        lambda r: self.change_1x1(
            routes = r),
        lambda r: self.change_1x0(
            routes = r,
            needFEChange = self.FEchanged
            ),"""