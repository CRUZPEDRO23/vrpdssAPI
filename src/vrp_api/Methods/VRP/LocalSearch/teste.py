# -*- coding: utf-8 -*-
"""
Created on Sat Jul 22 16:39:36 2023

@author: jose-
"""
import numpy as np
from .two_opt import two_opt_Extra, two_opt


def calculate_distance(route: list[int], dist_matrix: np.ndarray) -> float:
    return dist_matrix[np.roll(route, 1), route].sum()




def two_opt_2routes_Extra(route1, idxs1, route2, idxs2, cap1, cap2, d_i, dist_matrix):
    
    #MEMORIA = list()
    improved = True
    MelhoriaAcumulada = 0
    
    tCost = calculate_distance(route1, dist_matrix)+calculate_distance(route2, dist_matrix)
    bestCost = tCost
    
    bestroute1, bestIndx1, _, _, _ = two_opt_Extra(route1.copy(), idxs1, cap1, d_i, dist_matrix, returnALL = True)
    bestroute2, bestIndx2, _, _, _ = two_opt_Extra(route2.copy(), idxs2, cap2, d_i, dist_matrix, returnALL = True)
    
    print("bestroute1", bestroute1)
    print("bestIndx1", bestIndx1)
    print("bestroute2", bestroute2)
    print("bestIndx2", bestIndx2)
    
    print("Iniciando While")
    while improved:
        improved = False
        
        route1 = bestroute1.copy()
        route2 = bestroute2.copy()
        idxs1 = bestIndx1.copy()
        idxs2 = bestIndx2.copy()
        
        for idx1 in range(len(bestIndx1)):
            for idx2 in range(len(bestIndx2)):
                """
                    Fazer 2opt-estrela em uma rota de cada satelite
                    depois 2optestrela nas rotas resultantes de cada satelite
                """
                if ((idx1==0 and bestIndx1[idx1]==2) or \
                    bestIndx1[idx1] - bestIndx1[idx1-1] == 1) and \
                    ((idx2==0 and bestIndx2[idx2]==2) or bestIndx2[idx2] - bestIndx2[idx2-1] == 1):
                    continue
                start1 = bestIndx1[idx1-1] if idx1 > 0 else 0
                start2 = bestIndx2[idx2-1] if idx2 > 0 else 0
                
                end1 = bestIndx1[idx1]
                end2 = bestIndx2[idx2]
                
                for i in range(start1+1, end1):
                    for j in range(start2+1, end2-1):
                        
                        # Validar Capacidade
                        if d_i[bestroute1[start1:i]+bestroute2[j-1:start2:-1]+[bestroute1[0]]].sum() > cap1:
                            continue
                        
                        if d_i[[bestroute2[0]] + bestroute1[end1-1:i-1:-1] + bestroute2[j:end2]].sum() > cap2:
                            continue
                        
                        newroute1 = bestroute1[:i].copy()
                        newroute1+= bestroute2[j-1:start2:-1].copy()
                        newroute1+= bestroute1[end1:].copy()
                        
                        idxs1 = bestIndx1.copy()
                        idxs2 = bestIndx2.copy()

                        idxs1[idx1:]+= ((j - start2 - 1) - (end1 - i))
                        
                        newroute2 = bestroute2[:start2+1].copy()
                        newroute2+= bestroute1[end1-1:i-1:-1].copy()
                        newroute2+= bestroute2[j:].copy()
                        
                        idxs2[idx2:]+= ((end1 - i)-(j - start2 - 1))
                        
                        newroute1[start1:idxs1[idx1]+1] = two_opt(route=newroute1[start1:idxs1[idx1]+1], idxs=[len(newroute1[start1:idxs1[idx1]+1])], cap=cap1, d_i=d_i, dist_matrix=dist_matrix)
                        newroute2[start2:idxs2[idx2]+1] = two_opt(route=newroute2[start2:idxs2[idx2]+1], idxs=[len(newroute2[start2:idxs2[idx2]+1])], cap=cap2, d_i=d_i, dist_matrix=dist_matrix)
                        
                        print("")
                        #print(bestroute1)
                        #print(bestroute2)
                        #print(bestIndx1)
                        #print(bestIndx2)
                        #print(idx1, idx2, i, j, start1, end1, start2, end2)
                        
                        if (15 in newroute1[start1:idxs1[idx1]+1] and 10 in newroute1[start1:idxs1[idx1]+1] and 13  in newroute1[start1:idxs1[idx1]+1] and 5  in newroute1[start1:idxs1[idx1]+1] and 6 in newroute1[start1:idxs1[idx1]+1]) or \
                            (15 in newroute2[start2:idxs2[idx2]+1] and 10 in newroute2[start2:idxs2[idx2]+1] and 13  in newroute2[start2:idxs2[idx2]+1] and 5  in newroute2[start2:idxs2[idx2]+1] and 6 in newroute2[start2:idxs2[idx2]+1]):
                            print("newroute1", newroute1)
                            print("idxs1", idxs1)
                            print("newroute2", newroute2)
                            print("idxs2", idxs2)
                        
                        newroute1, idxs1, _, bestImproved1, anyimproved1 = two_opt_Extra(newroute1.copy(), idxs1.copy(), cap1, d_i, dist_matrix, returnALL = True)
                        newroute2, idxs2, _, bestImproved2, anyimproved2 = two_opt_Extra(newroute2.copy(), idxs2.copy(), cap2, d_i, dist_matrix, returnALL = True)
                        
                        if (15 in newroute1[start1:idxs1[idx1]+1] and 10 in newroute1[start1:idxs1[idx1]+1] and 13  in newroute1[start1:idxs1[idx1]+1] and 5  in newroute1[start1:idxs1[idx1]+1] and 6 in newroute1[start1:idxs1[idx1]+1]) or \
                            (15 in newroute2[start2:idxs2[idx2]+1] and 10 in newroute2[start2:idxs2[idx2]+1] and 13  in newroute2[start2:idxs2[idx2]+1] and 5  in newroute2[start2:idxs2[idx2]+1] and 6 in newroute2[start2:idxs2[idx2]+1]):
                            print("newroute1", newroute1)
                            print("idxs1", idxs1)
                            print("newroute2", newroute2)
                            print("idxs2", idxs2)
                            
                        newtCost = calculate_distance(newroute1, dist_matrix)+calculate_distance(newroute2, dist_matrix)
                        #print(newtCost, tCost, newtCost - tCost)
                        #print(anyimproved1, anyimproved2, newtCost < bestCost)
                        #bestImproved1+bestImproved2<0 and
                        if  (anyimproved1 or anyimproved2) and newtCost < bestCost:
                            print("Melhoria encontrada")
                            print("newroute1", newroute1)
                            print("idxs1", idxs1)
                            print("newroute2", newroute2)
                            print("idxs2", idxs2)
                            a = input()
                            #MelhoriaAcumulada += bestImproved1 + bestImproved2
                            bestroute1 = newroute1.copy()
                            bestroute2 = newroute2.copy()
                            bestIndx1 = idxs1.copy()
                            bestIndx2 = idxs2.copy()
                            bestCost = newtCost
                            improved=True
                        if improved: break  
                    if improved: break
                if improved: break  
            if improved: break  
    
    MelhoriaAcumulada = calculate_distance(bestroute1, dist_matrix)+calculate_distance(bestroute2, dist_matrix) - tCost
    return bestroute1, bestIndx1, bestroute2, bestIndx2, MelhoriaAcumulada


"""
route1 = [2, 14, 17, 20, 22, 19, 2, 16, 18, 2, 15, 21, 23, 2, 2]
idx1 = np.array([6, 9, 13, 14])
route2 = [1, 8, 3, 4, 7, 9, 11, 1, 13, 6, 5, 10, 12, 1, 1, 1]
idx2 = np.array([7, 13, 14, 15])
d_i = np.zeros(25)
d_i[3:] += 1

dist_matrix = np.random.rand(25, 25)
cap1 = 20
cap2 = 20

LS = lambda  route1, idxs1, route2, idxs2: two_opt_2routes_Extra(route1, idxs1, route2, idxs2, cap1, cap2, d_i, dist_matrix)
print(LS(route1, idx1, route2, idx2))
"""