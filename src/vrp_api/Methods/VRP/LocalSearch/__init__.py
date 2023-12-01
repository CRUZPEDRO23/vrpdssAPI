# -*- coding: utf-8 -*-
"""
Created on Sat Jul  8 09:29:40 2023

@author: jose-
"""

import copy

from .change_1x1 import change_1x1, change_1x0, change_nx0
from .two_opt import two_opt
from .tree_opt import tree_opt
#from ..._interfaces import interface

class LocalSearch(object):
    def two_opt(self, route):
        return two_opt(route, dist_matrix = self.C_ij)
    
    def tree_opt(self, route):
        return tree_opt(route, dist_matrix = self.C_ij)
    def change_1x1(self, routes):
        return change_1x1(
            routes, 
            d_i = self.d_i, 
            dist_matrix = self.C_ij, 
            routingFunction = lambda r: self.two_opt(r)
            )
    def change_1x0(self, routes, needFEChange):
        return change_1x0(
            routes, 
            d_i = self.d_i, 
            dist_matrix = self.C_ij, 
            needFEChange = needFEChange,
            routingFunction = lambda r: self.two_opt(r)
            )
    
    def change_nx0(self, routes, n):
        def routingFunction(r):
            r = self.two_opt(r)
            cost = self.calculate_distance(r, self.C_ij)
            return (r, cost)
        return change_nx0(
            routes, 
            n = n, 
            d_i = self.d_i, 
            FE = copy.copy(self.routesFE),
            dist_matrix = self.C_ij, 
            routingFunction = lambda r: routingFunction(r), 
            needFEChange = lambda r1, r2, i, j: False
            )