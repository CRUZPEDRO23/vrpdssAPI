# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 18:51:58 2023

@author: jose-
"""

def tree_opt(self, route, dist_matrix):# REF https://en.wikipedia.org/wiki/3-opt
    best = route.copy()
    improved = True
    
    def aceptadedMoves(route, i, j, k):
        MOVES = list()
        
        tour = route.copy()
        tour[i:j] = reversed(tour[i:j])
        MOVES.append(tour)
        
        tour = route.copy()
        tour[j:k] = reversed(tour[j:k])
        MOVES.append(tour)
        
        tour = route.copy()
        tour[i:k] = reversed(tour[i:k])
        MOVES.append(tour)
        
        tour = route.copy()
        tmp = tour[j:k] + tour[i:j]
        tour[i:k] = tmp
        MOVES.append(tour)
        
    
        return MOVES
    
    def all_segments(n: int):
        """Generate all segments combinations"""
        return ((i, j, k)
            for i in range(n)
            for j in range(i + 2, n)
            for k in range(j + 2, n + (i > 0)))
            
    while improved:
        improved = False
        
        for i, j, k in all_segments(len(route)):
            if j - i == 1 or k - j == 1: continue  # changes nothing, skip then
            print(i, j, k)
            #for new_route in aceptadedMoves(route.copy(), i, j, k)                        
            ##    if self._cost(new_route) < self._cost(best):
            #        best = new_route
            #        improved = True
            #        route = best
    return best