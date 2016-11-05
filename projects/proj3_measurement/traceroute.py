import subprocess
import sys

def run_traceroute(hostnames, num_packets, output_filename):
	for host in hostnames:
		output = subprocess.check_output("traceroute -a -q " + str(num_packets) + " " + host + " 2>&1", shell=True)
		with open(output_filename, "a") as f:
			f.write(output)

def parse_traceroute(raw_traceroute_filename, output_filename):
	f = open(raw_traceroute_filename, 'r')
	#readline returns blank string if at the end of string
	host_to_trace = {}
	firstLine = f.readline()
	firstHost = firstLine.split(" ")[2]
	host_to_trace.add[firstHost]

	currHost = firstHost
	currHop = 1
	line = f.readLine()
	while (line != ""):
		if line.split(" ")[0] == "traceroute":
			currHost = line.split(" ")[2]
			currHop = 0
		else:
			elements = f.split(" ")
			if elements[0].isdigit():
				currHop = elements[0]
			if currHost not in host_to_trace:
				host_to_trace[currHost] = [[{info here}]]

		line = f.readLine()



run_traceroute(["google.com"], 2, "raw_trace.out")

