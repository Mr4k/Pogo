from graph import Graph
from graph import Node
import re
from loading_bar import LoadingBar
import sys

def build_graph(fname, prune, verbose = False):
    #construct the graph
    num_lines = 1
    if verbose:
        print "Constructing the Graph"
        num_lines = sum(1 for line in open(fname))
        bar = LoadingBar(num_lines, "Lines Analysed")

    graph = Graph()
    try:
        f = open(fname,"r")
    except:
        if verbose:
            print "Could not open file " + fname
        exit(1)

    for line in f:
        people = line.split()
        if len(people) < 3:
            #print "hmm... "+ line
            continue
        people[0] = people[0].lstrip("@")
        people[2] = people[2].lstrip("@")
        if not graph.user_exists(people[0]):
            person_a = graph.add_user(people[0])
        else:
            person_a = graph.get_user(people[0])

        person_a.built = True

        if not graph.user_exists(people[2]):
            person_b = graph.add_user(people[2])
        else:
            person_b = graph.get_user(people[2])
        
        person_a.begin_following(person_b)

        if verbose:
            bar.print_load(1)

    f.close()
    graph.prune_users()
    graph.prune(prune)

    if verbose:
        print "Graph Completed!"

    return graph