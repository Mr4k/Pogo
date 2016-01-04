import json
import argparse
import svgwrite
from svgwrite import cm, mm 
import math

def main():
	parser = argparse.ArgumentParser(description='render_graph writes a json result of a 2d graph to an svg')
	parser.add_argument(dest="fname", help="The name of the graph file (json)")
	parser.add_argument('--width', action="store", dest="svg_width", default = 800, type=int, help = "The width of the svg")
	parser.add_argument('--height', action="store", dest="svg_height", default = 600, type=int, help = "The height of the svg")
	results = parser.parse_args()

	with open(results.fname, 'r') as infile:
		soln = json.load(infile)

	#graph bubble properties
	bubble_rad = 0.35
	bubble_outline = 0.05
	line_width = 0.05

	#establish bounds
	bbox_left = None
	bbox_right = None
	bbox_top = None
	bbox_bottom = None

	for user in soln.values():
		if user["x"] < bbox_left or bbox_left == None:
			bbox_left = user["x"]
		if user["x"] > bbox_right or bbox_right == None:
			bbox_right = user["x"]
		if user["y"] < bbox_top or bbox_top == None:
			bbox_top = user["y"]
		if user["y"] > bbox_bottom or bbox_bottom == None:
			bbox_bottom = user["y"]

	dwg = svgwrite.Drawing('output.svg',size = (results.svg_width,results.svg_height), profile='tiny')

	dwg.viewbox(minx = bbox_left-bubble_rad-bubble_outline, miny=bbox_top-bubble_rad-bubble_outline,
	 width = bbox_right-bbox_left+2*bubble_rad+2*bubble_outline, height = bbox_bottom-bbox_top+2*bubble_rad+2*bubble_outline)

	for user in soln:
		usr = soln[user]
		for other in usr["follows"]:
			othr = soln[other]
			dwg.add(dwg.line(start=(usr["x"], usr["y"]), end = (othr["x"], othr["y"]), stroke='blue',
                          stroke_width=line_width))
	for user in soln:
		usr = soln[user]
		for other in usr["friends"]:
			othr = soln[other]
			dwg.add(dwg.line(start=(usr["x"], usr["y"]), end = (othr["x"], othr["y"]), stroke='red',
                          stroke_width=line_width))

	for user in soln:
		usr = soln[user]
		dwg.add(dwg.circle(center=(usr["x"], usr["y"]), r=str(bubble_rad),fill = "white", stroke='black',
                          stroke_width=bubble_outline))
		text = dwg.text(user,insert=(usr["x"],usr["y"]), font_size=str(bubble_rad/math.sqrt(2)/len(user)*4))
		text["text-anchor"] = "middle"
		dwg.add(text)
	dwg.save()

if __name__ == "__main__":
    main()