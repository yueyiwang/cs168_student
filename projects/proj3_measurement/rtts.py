import subprocess
import json

def run_ping(hostnames, num_packets, raw_ping_output_filename, aggregated_ping_output_filename ):
	#print("pinging")
	host_to_raw = {}
	host_to_agg = {}
	for host in hostnames:
		#print(host)
		try: 
			output = subprocess.check_output("ping -O -c " + str(num_packets) + " " + host, shell=True)
			#output = subprocess.Popen("ping -c " + str(num_packets) + " " + host, shell=True)
			print(output)
			lines = output.split('\n')
			for i in range(1, len(lines)-5):
				parse = lines[i].split('=')
				rtt = parse[-1].split(' ')[0]
				if rtt == "Request" or rtt == "no":
					rtt = -1.0
				#print(rtt)
				if host in host_to_raw:
					rtt_list = host_to_raw[host]
					rtt_list += [float(rtt)]
				else:
					host_to_raw[host] = [float(rtt)]
			agg_data = lines[-2]
			data = agg_data.split("/")
			#print(data)
			drop_rate = float(lines[-3].split("%")[0].split(" ")[-1])
			if drop_rate == 100.0:
				max_rtt = -1.0
				median_rtt = -1.0
			else:
				max_rtt = float(data[-2])
				median_rtt = float(data[-3])
			# account for time out?
			if host in host_to_agg:
				#host_to_agg[host]['max']
				print("here")
			else:
				host_to_agg[host] = {}
				host_to_agg[host]['max_rtt'] = max_rtt
				host_to_agg[host]['median_rtt'] = median_rtt
				host_to_agg[host]['drop_rate'] = drop_rate

		except subprocess.CalledProcessError:
			host_to_raw[host] = [-1.0] * num_packets
			host_to_agg[host] = {}
			host_to_agg[host]['max_rtt'] = -1.0
			host_to_agg[host]['median_rtt'] = -1.0
			host_to_agg[host]['drop_rate'] = 100.0


	with open(raw_ping_output_filename, 'w') as fp:
		json.dump(host_to_raw, fp)
	with open(aggregated_ping_output_filename, 'w') as fp:
		json.dump(host_to_agg, fp)

	# print str(host_to_raw)
	# print str(host_to_agg)




		

# def plot_median_rtt_cdf(agg_ping_results_filesname, output_cdf_filename):


# def plot_ping_cdf(raw_ping_results_filename, output_cdf_filename):


# run_ping(["google.com"], 5)
