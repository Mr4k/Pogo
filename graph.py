import heapq
import collections
import numpy as np
from loading_bar import LoadingBar
import sys

class Node:
	def __init__(self, name, graph):
		self.name = name
		self.pruned_follows_table = {}
		self.follows_table = {}
		self.followers = {}
		self.friends = None
		self.depth = -1
		self.metadata = {}
		self.built = False
		self.graph = graph
		self.index = -1
	def compute_friends(self):
		self.friends = {}
		for user in self.get_follows():
			if user.name in self.followers:
				self.friends[user.name] = user
	def compute_pruned_follows(self):
		self.pruned_follows_table = [follow for follow in self.follows_table.values() if follow.built]
	def get_friends(self):
		if self.friends == None:
			self.compute_friends()
		return self.friends.values()
	def get_follows(self):
		if self.graph.use_prune:
			return self.pruned_follows_table
		else:
			return self.follows_table.values()
	def get_followers(self):
		return self.followers.values()
	def begin_following(self, follow):
		follow.followers[self.name] = self
		self.follows_table[follow.name] = follow
	def update_depth(self, directed):
		usr_list = []
		for user in self.get_follows():
			if user.depth == -1 or user.depth > self.depth + 1:
				user.depth = self.depth + 1
				usr_list.append(user)
		if not directed:
			for user in self.followers.values():
				if user.depth == -1 or user.depth > self.depth + 1:
					user.depth = self.depth + 1
					usr_list.append(user)
		return usr_list
	def get_depth(self):
		return self.depth
	def reset_depth(self):
		self.depth = np.inf

class Graph:
	def __init__(self):
		self.users = {}
		self.num_users = 0;
		self.users_by_links = collections.deque()
		self.users_by_friends = collections.deque()
		self.num_pruned_users = 0
		self.pruned_users = []
		self.avg_friends = 0
		self.use_prune = False
		self.edges = -1
	def user_exists(self, name):
		return name in self.users
	def add_user(self, name):
		usr = Node(name,self)
		self.users[name] = usr
		self.num_users += 1
		return usr
	def get_user(self, name):
		return self.users[name]
	def get_users(self):
		if self.use_prune:
			return self.pruned_users
		else:
			return self.users.values()
	def get_num_users(self):
		if self.use_prune:
			return self.num_pruned_users
		else:
			return self.num_users
	def get_user_linked(self,number):
		return self.users_by_links[number][1]
	def get_user_friends(self,number):
		return self.users_by_friends[number][1]
	def get_num_edges(self):
		if self.edges == -1:
			self.calculate_edges()
		return self.edges
	def calculate_edges(self):
		self.edges = 0
		for user in self.get_users():
			self.edges+=2*len(user.get_follows()) - len(user.get_friends())
		self.edges/=2
	def prune_text(self):
		if self.use_prune:
			return " (Pruned)"
		else:
			return ""
	def sort_by_links(self):
		usrs_queue = []
		loading_bar = LoadingBar(self.get_num_users(),"Calculating" + self.prune_text() + " Links:")
		for user in self.get_users():
			loading_bar.print_load(1)
			heapq.heappush(usrs_queue,[-len(user.get_followers()),user])
		loading_bar = LoadingBar(self.get_num_users(),"Pulling links out of queue:")
		while len(usrs_queue) > 0:
			loading_bar.print_load(1)
			self.users_by_links.append(heapq.heappop(usrs_queue))
	def calculate_friends(self):
		friends_queue = []
		total_friends = 0
		loading_bar = LoadingBar(self.get_num_users(),"Calculating" + self.prune_text() + " friends:")
		for user in self.get_users():
			loading_bar.print_load(1)
			total_friends += len(user.get_friends())
			heapq.heappush(friends_queue,[-len(user.get_friends()),user])
		self.avg_friends = float(total_friends)/self.get_num_users()
		loading_bar = LoadingBar(self.get_num_users(),"Pulling out of friends queue:")
		while len(friends_queue) > 0:
			loading_bar.print_load(1)
			self.users_by_friends.append(heapq.heappop(friends_queue))
	def get_adjacency_matrix(self, directed):
		adj_matrix = np.empty((self.get_num_users(),self.get_num_users()))
		adj_matrix.fill(0)
		np.fill_diagonal(adj_matrix, 1)
		index = 0
		for user in self.get_users():
			user.index = index
			index += 1
		for user in self.get_users():
			for other in user.get_follows():
				adj_matrix[user.index,other.index] = 1
			if not directed:
				for other in user.followers.values():
					adj_matrix[user.index,other.index] = 1
		return adj_matrix
	def compute_all_path_matrix(self, directed):
		#A little bit of anaylsis saves us a lot of time
		#Floyd Warshall is great for dense graphs (E < V^2)
		#Dijkstra is faster for sparse graphs
		if self.get_num_edges() < self.get_num_users()*self.get_num_users():
			return self.dijkstra_all_pair(directed)
		else:
			return self.floyd_warshall(directed)
	def floyd_warshall(self, directed):
		dist_matrix = self.get_adjacency_matrix(directed)
		dist_matrix[dist_matrix == 0] = np.inf
		np.fill_diagonal(dist_matrix, 0)
		for k in xrange(self.get_num_users()):
			dist_matrix = np.minimum(dist_matrix,dist_matrix[:,k,np.newaxis]+dist_matrix[np.newaxis,k,:])
		dist_matrix[dist_matrix == np.inf] = -1
		return dist_matrix
	def dijkstra_all_pair(self, directed):
		dist_matrix = np.zeros((self.get_num_users(),self.get_num_users()))
		i = 0
		j = 0
		for user in self.get_users():
			self.center_user(user, directed)
			j = 0
			for other in self.get_users():
				dist_matrix[i,j] = other.get_depth()
				j+=1
			i+=1
		dist_matrix[dist_matrix == np.inf] = -1
		return dist_matrix
	def center_user(self, cntr, directed):
		usr_queue = []
		for user in self.get_users():
			user.reset_depth()
			heapq.heappush(usr_queue,[sys.maxint,user])
		heapq.heappush(usr_queue,[0,cntr])
		cntr.depth = 0
		while usr_queue:
			usr = heapq.heappop(usr_queue)
			if usr[0] > usr[1].depth:
				continue
			for add_usr in usr[1].update_depth(directed):
				heapq.heappush(usr_queue,[add_usr.depth,add_usr])
	def prune(self, prune):
		self.use_prune = prune
	def prune_users(self):
		for user in self.users.values():
			user.compute_pruned_follows()
			if user.built:
				self.pruned_users.append(user)
		self.num_pruned_users = len(self.pruned_users)
	def distance_to_user(self, usr):
		return usr.get_depth()
	def un_distance_to_user(self, usr):
		return usr.get_un_depth()
