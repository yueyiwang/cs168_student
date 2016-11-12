import subprocess
import json
import matplotlib.pyplot as plot
from matplotlib.backends import backend_pdf

def run_ping(hostnames, num_packets, raw_ping_output_filename, aggregated_ping_output_filename ):
	#print("pinging")
	host_to_raw = {}
	host_to_agg = {}
	for host in hostnames:
		#print(host)
		try: 
			output = subprocess.check_output("ping -c " + str(num_packets) + " " + host, shell=True)
			#output = subprocess.Popen("ping -c " + str(num_packets) + " " + host, shell=True)
			#print(output)
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




		

def plot_median_rtt_cdf(agg_ping_results_filesname, output_cdf_filename):
	with open(agg_ping_results_filesname) as fh:
		results = json.load(fh)
	x_values = []
	y_values = []
	median_to_num = {}
	num_hosts = 0
	for host in results:
		median_rtt = results[host]["median_rtt"]
		if median_rtt != -1:
			if median_rtt in median_to_num:
				median_to_num[median_rtt] += 1
			else:
				median_to_num[median_rtt] = 1
			num_hosts += 1

	plot_cdf(median_to_num, output_cdf_filename, num_hosts, "Median RTTS")

def plot_cdf(info, output_cdf_filename, num, host):
	keys = info.keys()
	x_values = []
	y_values = []
	keys.sort()
	started = False
	for i in range(len(keys)):
		if keys[i] != -1:
			x_values +=[keys[i]]
			if not started:
				#print(y_values[0])
				#print(median_to_num[keys[i]])
				#print(keys[i])
				y_values += [float(info[keys[i]])/float(num)]

				started = True
			else:
				y_values += [float(info[keys[i]])/float(num) + float(y_values[len(y_values) - 1])]
	#print(y_values)
	plot.plot(x_values, y_values, label= host)
	plot.legend() # This shows the legend on the plot.
	plot.grid() # Show grid lines, which makes the plot easier to read.
	plot.xlabel("Time (ms)") # Label the x-axis.
	plot.ylabel("CDF") # Label the y-axis.
	#plot.show()
	fig = plot.gcf()

	with backend_pdf.PdfPages(output_cdf_filename) as pdf:
		#pdf.savefig()
		pdf.savefig(fig)
	



def plot_ping_cdf(raw_ping_results_filename, output_cdf_filename):
	with open(raw_ping_results_filename) as fh:
		results = json.load(fh)
	#do one 
	for host in results:
		x_values = []
		y_values = []
		rtt_to_num = {}
		num_rtts = 0 
		rtt_list = results[host]
		for rtt in rtt_list:
			if rtt != -1:
				num_rtts += 1
				if rtt in rtt_to_num:
					rtt_to_num[rtt] += 1
				else:
					rtt_to_num[rtt] = 1
		plot_cdf(rtt_to_num, output_cdf_filename, num_rtts, host)

def percent_all_drop(agg_ping_results_filesname):
	with open(agg_ping_results_filesname) as fh:
		results = json.load(fh)
	num = 0
	num_hosts = 0
	for host in results:
		if results[host]["drop_rate"] == 100.0:
			num += 1
		num_hosts += 1
	return float(num) / float(num_hosts)

def percent_has_drop(agg_ping_results_filesname):
	with open(agg_ping_results_filesname) as fh:
		results = json.load(fh)
	num = 0
	num_hosts = 0
	for host in results:
		if results[host]["drop_rate"] != 0.0:
			num += 1
		num_hosts += 1
	return float(num) / float(num_hosts)


#print(percent_all_drop('rtt_a_agg.json'))
#print(percent_has_drop('rtt_a_agg.json'))
#plot_median_rtt_cdf("rtt_a_agg.json", "agg_rtt_cdf_a.pdf")
#plot_ping_cdf('rtt_b_raw.json', 'raw_rtt_cdf_b.pdf')
#run_ping(["google.com"], 100, "raw_google_output.json", "agg_google_output.json")
#plot_ping_cdf('raw_google_output.json', 'raw_rtt_cdf.pdf')
