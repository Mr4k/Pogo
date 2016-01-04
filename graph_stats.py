from graph import Graph
from graph import Node
import re
from loading_bar import LoadingBar
import sys
import build_graph
import argparse

def main():
	parser = argparse.ArgumentParser(description='graph_stats provides some basic statistics about directed graphs')

	parser.add_argument(dest="fname", help="the name of the graph file")
	parser.add_argument('-n', action="store", dest="num_display", default = 10, type=int, help = "Number of users to display in the statistics")
	parser.add_argument('--prune', action="store_true", default=False, help = 'Do NOT include leaf nodes in the graph calculations')
	parser.add_argument('--verbose', action="store_true", default=False, help = 'Enable verbose output')

	results = parser.parse_args()

	graph = build_graph.build_graph(results.fname, results.prune, results.verbose)

	print "Graph Statistics:"
	print "Total Nodes " + str(graph.get_num_users())
	print "Total Edges " + str(graph.get_num_edges())
	graph.sort_by_links()
	for i in xrange(0,min(results.num_display,graph.get_num_users())):
		most_linked = graph.get_user_linked(i)
		print str(i + 1) + "th most linked " + most_linked.name + " with " + str(len(most_linked.followers))
	graph.calculate_friends()
	for i in xrange(0,min(results.num_display,graph.get_num_users())):
		most_friends = graph.get_user_friends(i)
		print str(i + 1) + "th most friends " + most_friends.name + " with " + str(len(most_friends.friends))
	print "Average Friends " + str(graph.avg_friends)


if __name__ == "__main__":
    main()