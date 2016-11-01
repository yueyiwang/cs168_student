import subprocess
def run_ping(hostnames, num_packets, raw_ping_output_filename, aggregated_ping_output_filename ):
	for host in hostnames:
		output = subprocess.check_output("ping -c " + num_packets + " " + host, shell=True)

		

# def plot_median_rtt_cdf(agg_ping_results_filesname, output_cdf_filename):


# def plot_ping_cdf(raw_ping_results_filename, output_cdf_filename):


run_ping(["google.com"], 5)
