import numpy as np
import scipy.optimize as opt
from graph import Graph
from graph import Node
import re
from loading_bar import LoadingBar
import sys
import random 
from datetime import datetime 
import build_graph
import argparse
import json

import signal

def save_solution(graph, solution, name):
    i = 0
    soln = {}
    for user in graph.get_users():
        soln[user.name] = {
            "friends" : [usr.name for usr in user.get_friends()],
            "follows" : [usr.name for usr in user.get_follows() if usr not in user.get_friends()],
            "x" : solution[i*2],
            "y": solution[i*2+1]
        }
        i += 1
    with open(name+".json", 'w') as outfile:
        json.dump(soln, outfile)
        outfile.close()

def construct_spring_approximation(fname, verbose, run_tests, prune,load_dist, iterations_to_save = -1, solver = "BFGS", k = 1000, q = 500):
    #Create the Graph
    graph = build_graph.build_graph(fname,prune,verbose)

    i = 0
    j = 0
    #unit distance
    e = 1
    #replusion distance scaler
    scale = 1

    position_matrix = e*graph.get_num_users()*np.random.random((graph.get_num_users(), 2))
    length_matrix = np.zeros((graph.get_num_users(),graph.get_num_users()))
    un_length_matrix = np.zeros((graph.get_num_users(),graph.get_num_users()))

    if load_dist:
        length_matrix = np.load("directed_length_matrix")
        un_length_matrix = np.load("undirected_length_matrix")
    else:
        if verbose:
            print "About to construct all pair distance matrices. This could take a while."
        length_matrix = graph.compute_all_path_matrix(True)
        un_length_matrix = graph.compute_all_path_matrix(False)
        if verbose:
            print "Done computing distance matrices"
        print "Saving all pair distance matrices"
        np.save("directed_length_matrix",length_matrix)
        np.save("undirected_length_matrix",un_length_matrix)

    connectivity_matrix = np.min(length_matrix,1)
    connectivity_matrix[connectivity_matrix == 0] = 1
    connectivity_matrix[connectivity_matrix == -1] = 0
    repulsion_matrix = (1-connectivity_matrix)

    print connectivity_matrix
    print repulsion_matrix
    print length_matrix
    print un_length_matrix

    #a quick vectorized distance function
    dist = lambda P: np.sqrt((P[:,0]-P[:,0][:, np.newaxis])**2 + 
                             (P[:,1]-P[:,1][:, np.newaxis])**2)

    #general broadcasting function
    def build_matrix(func, args):
        return func(*args) 

    def diff(A,B):
        return A[:,np.newaxis] - B

    def energy(P):
        epsilon = 0.000001
        P = P.reshape((-1, 2))
        D = dist(P)
        # The potential energy is the sum of the elastic potential energies plus the repel energies.
        return (k * connectivity_matrix * (D - length_matrix)**2).sum() + (q*(un_length_matrix)*(repulsion_matrix)*(1/(D/scale+epsilon))).sum()

    def grad(P):
        epsilon = 0.000001
        P = P.reshape((-1, 2))
        # We compute the distance matrix.
        D = dist(P)
        x_diff = build_matrix(diff,(P[:,0],P[:,0]))
        y_diff = build_matrix(diff,(P[:,1],P[:,1]))
        num_users = P.shape[0]
        grad = np.zeros((num_users,2))
        #Sorry there has to be a little math involved
        grad[:,0]=((2*k*connectivity_matrix*(D-length_matrix)*(1/(D+epsilon)) - q*un_length_matrix*repulsion_matrix*1/((D/scale)**3+epsilon))*x_diff).sum(axis = 1)
        grad[:,0]+=((2*k*np.transpose(connectivity_matrix)*(D-np.transpose(length_matrix))*(1/(D+epsilon)) - q*np.transpose(un_length_matrix)*np.transpose(repulsion_matrix)*1/((D/scale)**3+epsilon))*x_diff).sum(axis = 1)
        grad[:,1]=((2*k*connectivity_matrix*(D-length_matrix)*(1/(D+epsilon)) - q*un_length_matrix*repulsion_matrix*1/((D/scale)**3+epsilon))*y_diff).sum(axis = 1)
        grad[:,1]+=((2*k*np.transpose(connectivity_matrix)*(D-np.transpose(length_matrix))*(1/(D+epsilon)) - q*np.transpose(un_length_matrix)*np.transpose(repulsion_matrix)*1/((D/scale)**3+epsilon))*y_diff).sum(axis = 1)
        return grad.ravel()

    #Q:Why are there arrays here?
    #A:Python's closures do not let you modify the variables outside of local scope but they do let you modify objects like arrays
    num_iterations = [0]
    best_soln = [None]
    last_time = datetime.now()

    def solver_callback(xk):
        num_iterations.append(num_iterations[0] + 1)
        num_iterations.pop(0)
        best_soln.append(xk)
        best_soln.pop(0)
        print str(num_iterations[0]) + " iterations with energy " + str(energy(xk))
        if num_iterations[0] % iterations_to_save == 0 and iterations_to_save > 0:
            print str(iterations_to_save) + " iterations in:" + str((datetime.now()-last_time).seconds) + "seconds"
            last_time = datetime.now()
            print "Saving Current Solution..."
            save_solution(graph,xk,"iteration_"+str(num_iterations[0]))
            print "Solution Saved as " + "iteration_"+str(num_iterations[0])+".js"

    def leave_handler(signal, frame):
        if best_soln[0] != None:
            print "Saving best solution on exit as exit_solution.js"
            save_solution(graph, "exit_solution", "exit_solution")

        return (solver_callback, leave_handler)

    signal.signal(signal.SIGINT, leave_handler)

    if run_tests:
        from scipy.optimize import check_grad
        from scipy.optimize import approx_fprime
        print "Checking Gradient:"
        print check_grad(energy, grad, position_matrix.ravel())

        print "Speed Tests:"
        print "Energy Function Speed:"
        print datetime.now()
        print energy(position_matrix.ravel())
        print datetime.now()
        print "Gradient Speed:"
        print datetime.now()
        print grad(position_matrix.ravel())
        print datetime.now()

    print "Minimizing with " + str(solver)

    solution = opt.minimize(energy, position_matrix.ravel(),
                      method=solver,jac = grad,callback = solver_callback)

    print "Solved to optimiality"
    if verbose:
        print energy(position_matrix.ravel())
        print energy(solution.x)

    save_solution(graph,solution.x,"results")

def main():
    parser = argparse.ArgumentParser(description='spring_model generates a 2d projection of a directed graph')

    parser.add_argument(dest="fname", help="The name of the graph file")
    parser.add_argument('--solver', action="store", dest="solver", default = 'BFGS',type = str, help = "The solver with which to solve energy mimization problem. Use BFGS for small graphs and L-BFGS-B when you need more speed.")
    parser.add_argument('--prune', action="store_true", default=False, help = 'Do NOT include leaf nodes in the graph calculations')
    parser.add_argument('--test', action="store_true", default=False, help = 'Run speed and correctness tests on the gradient and energy functions')
    parser.add_argument('--preload', action="store_true", default=False, help = 'If true the program will try to load the all pairs distance matrices from the files directed_length_matrix.npy and undirected_length_matrix.npy. This is used to save time for large dense graphs.')
    parser.add_argument('--verbose', action="store_true", default=False, help = 'Enable verbose output')
    parser.add_argument('--nsave', action="store", dest="nsave", default = -1, type=int, help = "Saves the current best solution every n iterations. A negative value never save.")
    parser.add_argument('-k', action="store", dest="k", default = 1000, type=float, help = "The spring stiffness constant")
    parser.add_argument('-q', action="store", dest="q", default = 500, type=float, help = "The node replusion constant")

    results = parser.parse_args()

    construct_spring_approximation(results.fname,results.verbose,results.test,results.prune,results.preload,results.nsave,results.solver,results.k,results.q)

if __name__ == "__main__":
    main()