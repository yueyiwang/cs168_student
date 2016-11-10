import subprocess
import json
import matplotlib.pyplot as plot
from matplotlib.backends import backend_pdf

def run_dig(hostname_filename, output_filename, dns_query_server=None):
	with open(hostname_filename, 'r') as fp:
		hostnames = []
		line = fp.readline()
		while line != "":
			#print(line)
			hostnames += [line.split("\n")[0]]
			line = fp.readline()
	# hostnames = hostname_filename
	hostnames *= 5
	all_digs = []
	for host in hostnames:
		print(host)
		if dns_query_server == None:
			output = subprocess.check_output("dig +trace +tries=1 +nofail " + host + " 2>&1", shell=True)
			dig_dict = parse_no_dns_server(host, output)
			#print(output)
			all_digs += [dig_dict]
		else:
			output = subprocess.check_output("dig " + host + "@" + dns_query_server + " 2>&1", shell=True)
			dig_dict = parse_with_dns_server(host, output)
			all_digs += [dig_dict]

		#print(all_digs)

	with open(output_filename, 'w') as fp:
		json.dump(all_digs, fp)


def parse_no_dns_server(host, output):
	lines = output.split("\n")
	dig_dict = {}
	dig_dict["Name"] = host
	queries = []
	success = False
	current_dict = {}
	for i in range(2, len(lines)):
		tokens = lines[i].split()
		if len(tokens) <= 1:
			continue
		if tokens[1] == "Received":
			current_dict["Time"] = tokens[-2]
			queries += [current_dict]
			current_dict = {}
			continue
		elif tokens[0] == ";" or tokens[0] == ";;":
			continue
		current_answer = {}
		current_answer["Queried name"] = tokens[0]
		current_answer["Data"] = tokens[4]
		current_answer["Type"] = tokens[3]
		if tokens[3] == "A":
			success = True
		current_answer["TTL"] = tokens[1]
		if "Answers" not in current_dict:
			current_dict["Answers"] = []
		current_dict["Answers"] += [current_answer]
	if success:
		dig_dict["Success"] = True
		dig_dict["Queries"] = queries
	else:
		dig_dict["Success"] = False
		
	return dig_dict

def parse_with_dns_server(host, output):
	data = output.split("SECTION:")
	name_parts = data[1].split(';')[1].split('.')
	name = name_parts[0] + "." + name_parts[1]
	host_to_queries = {}
	host_to_queries['Name'] = name
	success = True
	answers = data[2].split(';;')[0]
	info = data[2].split(';;')[1:]
	for a in answers.split('\n'):
		if a == "":
			continue
		tokens = a.split()
		ans = tokens[0]
		ttl = tokens[1]
		typ = tokens[2]
		if tokens[3] != 'A':
			success = False
			break
		data = tokens[4]
		if 'Queries' not in host_to_queries:
			host_to_queries['Queries'] = [{}]
			host_to_queries['Queries'][0]['Answers'] = [{'Queried name': ans, 'Data': data, 'Type': typ, 'TTL': ttl}]
		else:
			i = len(host_to_queries['Queries'])
			host_to_queries['Queries'][0]['Answers'] += [{'Queried name': ans, 'Data': data, 'Type': typ, 'TTL': ttl}]
	if success:
		time = info[0].split()[2]
		host_to_queries['Success'] = success
		host_to_queries['Queries'][0]['Time'] = time
	else:
		host_to_queries['Name'] = host_to_queries['Name'].split('\\')[0]
		host_to_queries['Success'] = success
	return host_to_queries

# print(run_dig(["google.com"], "dig_ouput_test.json"))
# run_dig("part3_test_host_filename.txt", "dig_ouput_test.json")
#run_dig('alexa_top_100', 'first_run.json')

def get_average_ttls(filename):
	with open(filename) as fh:
		results = json.load(fh)
	root_servers = {}
	tld_servers = {}
	other_servers = {}
	answer_servers = {}
	for host_info in results:
		if not host_info["Success"]:
			continue
		for query in host_info["Queries"]:
			for answer in query["Answers"]:
				ttl = int(answer["TTL"])
				server = answer["Data"]
				if "root-servers.net" in server:
					if server not in root_servers:
						root_servers[server] = (1, [ttl])
					else:
						num, lst = root_servers[server]
						root_servers[server] = (num + 1, lst + [ttl])
				elif "gtld-servers.net" in server:
					if server not in tld_servers:
						tld_servers[server] = (1, [ttl])
					else:
						num, lst = tld_servers[server]
						tld_servers[server] = (num + 1, lst + [ttl])
				elif answer["Type"] == "A":
					if server not in answer_servers:
						answer_servers[server] = (1, [ttl])
					else:
						num, lst = answer_servers[server]
						answer_servers[server] = (num + 1, lst + [ttl])
				else:
					if server not in other_servers:
						other_servers[server] = (1, [ttl])
					else:
						num, lst = other_servers[server]
						other_servers[server] = (num + 1, lst + [ttl])
	answer = []
	print(root_servers)
	for root in root_servers:
		root_servers[root] = float(sum(root_servers[root][1])) / root_servers[root][0]
	for tld in tld_servers:
		tld_servers[tld] = float(sum(tld_servers[tld][1])) / tld_servers[tld][0]
	for other in other_servers:
		other_servers[other] = float(sum(other_servers[other][1])) / other_servers[other][0]
	for answer in answer_servers:
		answer_servers[answer] = float(sum(answer_servers[answer][1])) / answer_servers[answer][0]
	root_TTL = 0 
	roots = 0
	for root in root_servers:
		roots += 1
		root_TTL += root_servers[root]
	tld_TTL = 0 
	tlds = 0
	for tld in tld_servers:
		tlds += 1
		tld_TTL += tld_servers[tld]
	other_TTL = 0 
	others = 0
	for server in other_servers:
		others += 1
		other_TTL += other_servers[server]
	a_TTL = 0 
	answers = 0

	for server in answer_servers:
		answers += 1
		a_TTL += answer_servers[server]

	return [float(root_TTL)/roots, float(tld_TTL)/ tlds, float(other_TTL)/ others, float(a_TTL)/ answers]


#print(get_average_ttls("dig_ouput_test.json"))

def get_average_times(filename):
	with open(filename) as fh:
		results = json.load(fh)
	total_time = 0
	final_time = 0
	num_hosts = 0
	for host_info in results:
		if not host_info["Success"]:
			continue
		num_hosts += 1
		queries = host_info["Queries"]
		for query in queries:
			time = int(query["Time"])
			total_time += time
			for answer in query["Answers"]:
				if answer["Type"] == "A":
					final_time += time
	return [float(total_time) / num_hosts, float(final_time)/num_hosts]

#print(get_average_times("dig_ouput_test.json"))

def generate_time_cdfs(json_filename, output_filename):
	with open(json_filename) as fh:
		results = json.load(fh)
	num_hosts = 0
	total_to_num = {}
	final_to_num = {}
	for host_info in results:
		if not host_info["Success"]:
			continue
		num_hosts += 1
		queries = host_info["Queries"]
		total_time = 0
		final_time = 0
		for q in queries:
			time = int(q["Time"])
			total_time += time
			for a in q["Answers"]:
				if a["Type"] == "A":
					final_time = time
					#final_to_num[time] = 1
		if final_time != 0:
			if final_time in final_to_num:
				final_to_num[final_time] += 1
			else:
				final_to_num[final_time] = 1
		if total_time in total_to_num:
			total_to_num[total_time] += 1
		else:
			total_to_num[total_time] = 1
		print("total time: ")
		print(total_time)

	print("num hosts: ")
	print(num_hosts)


	totalx, totaly = plot_cdf(total_to_num, num_hosts)
	finalx, finaly = plot_cdf(final_to_num, num_hosts)

	#print(totalx, totaly)
	#print(finalx, finaly)

	plot.plot(totalx, totaly, label= "Total time to resolve site")
	plot.plot(finalx, finaly, label= "Time to resolve final request")
	plot.legend() # This shows the legend on the plot.
	plot.grid() # Show grid lines, which makes the plot easier to read.
	plot.xlabel("Time (ms)") # Label the x-axis.
	plot.ylabel("CDF") # Label the y-axis.
	#plot.show()
	fig = plot.gcf()

	with backend_pdf.PdfPages(output_filename) as pdf:
		#pdf.savefig()
		pdf.savefig(fig)


def plot_cdf(info, num):
	keys = info.keys()
	x_values = []
	y_values = []
	keys.sort()
	started = False
	#print(num)
	prev = 0
	for i in range(len(keys)):
		if keys[i] != -1:
			x_values +=[keys[i]]
			if not started:
				# print("first info value: ")
				# print(info[keys[i]])
				# print("num: ")
				# print(num)
				y_values += [float(info[keys[i]])/float(num)]
				prev = info[keys[i]]
				started = True
			else:
				prev += info[keys[i]]
				y_values += [float(prev)/float(num)]
	#print(y_values)
	return x_values, y_values

#generate_time_cdfs("q3a_500.json", "part3_time_cdfs.pdf")
#print(get_average_ttls("q3a_500.json"))


def count_different_dns_responses(filename1, filename2):
	with open(filename1) as fh:
		results = json.load(fh)
	host_to_ip = {}
	first_value = 0
	for host_info in results:
		if not host_info["Success"]:
			continue
		for query in host_info["Queries"]:
			host_set = []
			for a in query["Answers"]:
				if a["Type"] == "A":
					host_set += [a["Data"]]
		name = host_info["Name"]
		if name not in host_to_ip:
			host_to_ip[name] = []
		host_to_ip[name] += [set(host_set)]
	with open(filename2) as fh:
		results2 = json.load(fh)
	host_to_ip_2 = {}
	for host_info in results2:
		if not host_info["Success"]:
			continue
		for query in host_info["Queries"]:
			host_set = []
			for a in query["Answers"]:
				if a["Type"] == "A":
					host_set += [a["Data"]]
		name = host_info["Name"]
		if name not in host_to_ip_2:
			host_to_ip_2[name] = []
		host_info[name] += [set(host_set)]
	second_value = 0
	for host in host_to_ip:
		sets = host_to_ip[host]
		if sets[0] != sets[1] or sets[2] != sets[1] or sets[2] != sets[3] or sets[3] != sets[4]:
			first_value += 1
		else:
			sets2 = host_to_ip_2[host]
			if sets2[0] != sets2[1] or sets2[2] != sets2[1] or sets2[2] != sets2[3] or sets2[3] != sets2[4]:
				second_value += 1 
			else:
				sets1 = set(sets)
				if host in host_to_ip_2:
					sets2 = set(host_to_ip_2[host])
					if sets2 != sets1:
						second_value += 1
	return [first_value, second_value + first_value]

print(count_different_dns_responses("q3/first_run.json", "q3/second_run.json"))
