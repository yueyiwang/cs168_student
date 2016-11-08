import subprocess
import sys
import re
import json
import time

def run_traceroute(hostnames, num_packets, output_filename):
	print("running trace route")
	with open(output_filename, "w") as f:
		t = str(time.time())
		print(t)
		f.write(t + '\n')
	for host in hostnames:
		print(host)
		output = subprocess.check_output("traceroute -a -q " + str(num_packets) + " " + host + " 2>&1", shell=True)
		with open(output_filename, "a") as f:
			f.write(output)

def parse_traceroute(raw_traceroute_filename, output_filename):
	print("parsing trace route")
	f = open(raw_traceroute_filename, 'r')
	#readline returns blank string if at the end of string
	host_to_trace = {}
	time = f.readline().split(" ")[0]
	print(time)
	host_to_trace["timestamp"] = time
	firstLine = f.readline()
	print(firstLine)
	firstHost = firstLine.split(" ")[2]
	currHost = firstHost
	currHop = 0
	line = f.readline()
	print(currHost)
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

	with open(output_filename, 'a') as fp:
		json.dump(host_to_trace, fp)
		fp.write('\n')
	# print(host_to_trace)


#parse_traceroute('raw_trace.out', 'traceroute.json')
#run_traceroute(["google.com", "facebook.com", "www.berkeley.edu", "allspice.lcs.mit.edu", "todayhumor.co.kr", "www.city.kobe.lg.jp","www.vutbr.cz", "zanvarsity.ac.tz"], 5, "raw_tr_a.out")
parse_traceroute('raw_tr_a.out', 'trace_a.json')

