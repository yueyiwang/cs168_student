import subprocess
import json
import matplotlib.pyplot as plot
from matplotlib.backends import backend_pdf
import utils

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
	dig_dict[utils.NAME_KEY] = host
	queries = []
	success = False
	current_dict = {}
	for i in range(2, len(lines)):
		tokens = lines[i].split()
		if len(tokens) <= 1:
			continue
		if tokens[1] == "Received":
			current_dict[utils.TIME_KEY] = tokens[-2]
			queries += [current_dict]
			current_dict = {}
			continue
		elif tokens[0] == ";" or tokens[0] == ";;":
			continue
		current_answer = {}
		current_answer[utils.QUERIED_NAME_KEY] = tokens[0]
		current_answer[utils.ANSWER_DATA_KEY] = tokens[4]
		current_answer[utils.TYPE_KEY] = tokens[3]
		if tokens[3] == "A":
			success = True
		current_answer[utils.TTL_KEY] = tokens[1]
		if utils.ANSWERS_KEY not in current_dict:
			current_dict[utils.ANSWERS_KEY] = []
		current_dict[utils.ANSWERS_KEY] += [current_answer]
	if success:
		dig_dict[utils.SUCCESS_KEY] = True
		dig_dict[utils.QUERIES_KEY] = queries
	else:
		dig_dict[utils.SUCCESS_KEY] = False

	return dig_dict

def parse_with_dns_server(host, output):
	data = output.split("SECTION:")
	name_parts = data[1].split(';')[1].split('.')
	name = name_parts[0] + "." + name_parts[1]
	host_to_queries = {}
	host_to_queries[utils.NAME_KEY] = name
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
		if utils.QUERIES_KEY not in host_to_queries:
			host_to_queries[utils.QUERIES_KEY] = [{}]
			host_to_queries[utils.QUERIES_KEY][0][utils.ANSWERS_KEY] = [{utils.QUERIED_NAME_KEY: ans, utils.ANSWER_DATA_KEY: data, utils.TYPE_KEY: typ, utils.TTL_KEY: ttl}]
		else:
			i = len(host_to_queries[utils.QUERIES_KEY])
			host_to_queries[utils.QUERIES_KEY][0][utils.ANSWERS_KEY] += [{utils.QUERIED_NAME_KEY: ans, utils.ANSWER_DATA_KEY: data, utils.TYPE_KEY: typ, utils.TTL_KEY: ttl}]
	if success:
		time = info[0].split()[2]
		host_to_queries[utils.SUCCESS_KEY] = success
		host_to_queries[utils.QUERIES_KEY][0][utils.TIME_KEY] = time
	else:
		host_to_queries[utils.NAME_KEY] = host_to_queries[utils.NAME_KEY].split('\\')[0]
		host_to_queries[utils.SUCCESS_KEY] = success
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
		if not host_info[utils.SUCCESS_KEY]:
			continue
		for query in host_info[utils.QUERIES_KEY]:
			name = host_info[utils.NAME_KEY]
			for answer in query[utils.ANSWERS_KEY]:
				ttl = int(answer[utils.TTL_KEY])
				server = answer[utils.QUERIED_NAME_KEY]
				if answer[utils.TYPE_KEY] == "A":
					if name not in answer_servers:
						answer_servers[name] = (1, [ttl])
					else:
						num, lst = answer_servers[name]
						answer_servers[name] = (num + 1, lst + [ttl])

				elif server == ".":
					if int(ttl) > 400000:
						print(ttl)
					if name not in root_servers:
						root_servers[name] = (1, [ttl])
					else:
						num, lst = root_servers[name]
						root_servers[name] = (num + 1, lst + [ttl])
				elif server.count(".") == 1:
					if name not in tld_servers:
						tld_servers[name] = (1, [ttl])
					else:
						num, lst = tld_servers[name]
						tld_servers[name] = (num + 1, lst + [ttl])
				else:
					if name not in other_servers:
						other_servers[name] = (1, [ttl])
					else:
						num, lst = other_servers[name]
						other_servers[name] = (num + 1, lst + [ttl])
	answer = []

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
	#print(root_servers)
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
	print(roots)

	return [float(root_TTL)/roots, float(tld_TTL)/ tlds, float(other_TTL)/ others, float(a_TTL)/ answers]


print(get_average_ttls("eric_dns_b.json"))

def get_average_times(filename):
	with open(filename) as fh:
		results = json.load(fh)
	total_time = 0
	final_time = 0
	num_hosts = 0
	for host_info in results:
		if not host_info[utils.SUCCESS_KEY]:
			continue
		num_hosts += 1
		queries = host_info[utils.QUERIES_KEY]
		for query in queries:
			time = int(query[utils.TIME_KEY])
			total_time += time
			for answer in query[utils.ANSWERS_KEY]:
				if answer[utils.TYPE_KEY] == "A":
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
		if not host_info[utils.SUCCESS_KEY]:
			continue
		num_hosts += 1
		queries = host_info[utils.QUERIES_KEY]
		total_time = 0
		final_time = 0
		for q in queries:
			time = int(q[utils.TIME_KEY])
			total_time += time
			for a in q[utils.ANSWERS_KEY]:
				if a[utils.TYPE_KEY] == "A":
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
		if not host_info[util.SUCCESS_KEY]:
			continue
		for query in host_info[util.QUERIES_KEY]:
			host_set = []
			for a in query[util.ANSWERS_KEY]:
				if a[util.TYPE_KEY] == "A":
					host_set += [a[util.ANSWER_DATA_KEY]]
		name = host_info[utils.NAME_KEY]
		if name not in host_to_ip:
			host_to_ip[name] = []
		host_to_ip[name] += [set(host_set)]
	with open(filename2) as fh:
		results2 = json.load(fh)
	host_to_ip_2 = {}
	for host_info in results2:

		if not host_info[utils.SUCCESS_KEY]:
			continue
		for query in host_info[utils.QUERIES_KEY]:
			host_set = []
			for a in query[utils.ANSWERS_KEY]:
				if a[utils.TYPE_KEY] == "A":
					host_set += [a[utils.ANSWER_DATA_KEY]]
		name = host_info[utils.NAME_KEY]
		if name not in host_to_ip_2:
			host_to_ip_2[name] = []
		host_to_ip_2[name] += [set(host_set)]
	second_value = 0
	#print(host_to_ip)
	for host in host_to_ip:
		sets = host_to_ip[host]
		if sets[0] != sets[1] or sets[2] != sets[1] or sets[2] != sets[3] or sets[3] != sets[4]:
			first_value += 1
			print(host + " : first_value")
		else:
			if host not in host_to_ip_2:
				continue
			sets2 = host_to_ip_2[host]
			if sets2[0] != sets2[1] or sets2[2] != sets2[1] or sets2[2] != sets2[3] or sets2[3] != sets2[4]:
				second_value += 1 
			else:
				#print(sets)
				sets1 = sets
				if host in host_to_ip_2:
					sets2 = host_to_ip_2[host]
					#print(sets2)
					for s in sets2:
						if s not in sets1:
							print(host + ": second_value")
							second_value += 1
							break

	return [first_value, second_value + first_value]

#print(count_different_dns_responses("q3/first_run.json", "q3/from_italy.json"))
