# import os
import rtts

with open('alexa_top_100', 'r') as fp:
	lines = []
	line = fp.readline()
	while line != "":
		#print(line)
		lines += [line.split("\n")[0]]
		line = fp.readline()
	rtts.run_ping(lines, 10, 'rtt_a_raw.json', 'rtt_a_agg.json')