# Pogo 

# Basics

Pogo is a small set of tools which provides a way to generate 2d projections of directed graphs using a spring energy model. It was build orginally to graph user relations scraped from Tumblr but can be used with any directed graph.
Pogo contains three main tools:
 - `spring_model.py` is the main tool in Pogo. It takes a directed graph in the form of a text file and transforms it into a .json file which contains the x,y coordinates for each node in the graph
 - `render_graph.py` is a quick scipt which turns the .json output of spring_model.py into an .svg file
 - `graph_stats.py` is a tool which gives you basic information about the graph file.    

Pogo also includes three more python files which support the first three tools:
 - `graph.py` implements a directed graph model via a Graph object and a Node object
 - `build_graph.py` builds a Graph from a text file
 - `loading_bar.py` provides a small loading animation in the console   
  
# Dependancies
To run the scipts in Pogo, you must install svgwrite. You can do this via `pip install svgwrite`. Pogo also requires `scipy` and `numpy`. You can install both of them by installing [Anaconda](https://www.continuum.io/downloads).

# Example
We can take example.txt which describes a very simple directed graph:
```
@SherlockFan7 -> @DankMemes
@Peter -> @DankMemes
@3spooky5me -> @Peter
@3spooky5me -> @SherlockFan7
@Peter -> @3spooky5me
```
To make a graph of this we would first call `python spring_model.py example.txt` which would construct the graph then save it to results.json. Then we can convert that file into an svg by calling `python render_graph.py results.json`. The resulting svg would be stored as `output.svg`.