import subprocess

def run_traceroute(hostnames, num_packets, output_filename):
	for host in hostnames:
		output = subprocess.check_output("traceroute -a -q " + str(num_packets) + " " + host, shell=True)
		with open(output_filename, "a") as f:
			f.write(output)

run_traceroute(["google.com"], 2, "raw_trace.out")

