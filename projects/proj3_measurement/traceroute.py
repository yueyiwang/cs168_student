import subprocess
import sys
import re
import json

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

	currHost = firstHost
	currHop = 0
	line = f.readline()
	while (line != ""):
		if line.split(" ")[0] == "*":
			continue
		if line.split(" ")[0] == "traceroute":
			currHost = line.split(" ")[2]
			currHop = 0
		else:
			data = line.split(" ")
			# example data:
			# ['', '6', '', '[AS15169]', '108.170.242.241', '(108.170.242.241)', '', '3.641', 'ms\n']
			if data[1].isdigit():
				currHop = int(data[1])
			ASN = data[3].replace('[', '').replace(']', '').replace('A', '').replace('S', '')
			name = data[4]
			ip = data[5].replace('(', '').replace(')', '')
			if currHost not in host_to_trace:
				host_to_trace[currHost] = [[{'ip': ip, 'name': name, 'ASN': ASN}]]
			else:
				if len(host_to_trace[currHost]) == currHop:
					host_to_trace[currHost][currHop-1] += [{'ip': ip, 'name': name, 'ASN': ASN}]
				else:
					host_to_trace[currHost] += [[{'ip': ip, 'name': name, 'ASN': ASN}]]

		line = f.readline()

	with open(output_filename, 'w') as fp:
		json.dump(host_to_trace, fp)
	# print(host_to_trace)


parse_traceroute('raw_trace.out', 'traceroute.json')
#run_traceroute(["google.com"], 2, "raw_trace.out")

