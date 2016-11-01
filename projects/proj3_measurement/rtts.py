import subprocess
def run_ping(hostnames, num_packets): #, raw_ping_output_filename, aggregated_ping_output_filename ):
	host_to_raw = {}
	host_to_agg = {}
	for host in hostnames:
		output = subprocess.check_output("ping -c " + str(num_packets) + " " + host, shell=True)
		lines = output.split('\n')
		for i in range(1, len(lines)-5):
			rtt = lines[i].split('=')[-1].split(' ')[0]
			print(rtt)
			if host in host_to_raw:
				rtt_list = host_to_raw[host]
				rtt_list += [float(rtt)]
			else:
				host_to_raw[host] = [float(rtt)]
		agg_data = lines[-2]
		data = agg_data.split("/")
		print(data)
		max_rtt = float(data[-2])
		median_rtt = float(data[-3])
		drop_rate = float(lines[-3].split("%")[0].split(" ")[-1])
		if host in host_to_agg:
			#host_to_agg[host]['max']
			print("here")
		else:
			host_to_agg[host] = {}
			host_to_agg[host]['max_rtt'] = max_rtt
			host_to_agg[host]['median_rtt'] = median_rtt
			host_to_agg[host]['drop_rate'] = drop_rate

	print str(host_to_raw)
	print str(host_to_agg)




		

# def plot_median_rtt_cdf(agg_ping_results_filesname, output_cdf_filename):


# def plot_ping_cdf(raw_ping_results_filename, output_cdf_filename):


run_ping(["google.com"], 5)
