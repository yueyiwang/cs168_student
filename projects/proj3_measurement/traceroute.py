import subprocess
import sys

def run_traceroute(hostnames, num_packets, output_filename):
	for host in hostnames:
		output = subprocess.check_output("traceroute -a -q " + str(num_packets) + " " + host + " 2>&1", shell=True)
		with open(output_filename, "a") as f:
			f.write(output)

def parse_traceroute(raw_traceroute_filename, output_filename):
	

run_traceroute(["google.com"], 2, "raw_trace.out")

