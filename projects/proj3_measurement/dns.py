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
		try:
			#print(host)
			if dns_query_server == None:
				output = subprocess.check_output("dig +trace +tries=1 +nofail " + host + " 2>&1", shell=True)
				dig_dict = parse_no_dns_server(host, output)
				#print(output)
				all_digs += [dig_dict]
			else:
				output = subprocess.check_output("dig " + host + " @" + dns_query_server + " 2>&1", shell=True)
				dig_dict = parse_with_dns_server(host, output)
				all_digs += [dig_dict]
		except subprocess.CalledProcessError:
			dig_dict = {}
			dig_dict[utils.NAME_KEY] = host
			dig_dict[utils.SUCCESS_KEY] = False

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
		if tokens[3] == "A" or tokens[3] == "CNAME":
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
		typ = tokens[3]
		if tokens[3] != 'A':
			if tokens[3] != 'CNAME':
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

# Korean 202.68.250.174
#run_dig('alexa_top_100', 'q3/from_korea.json', '202.68.250.174')


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
				ttl = answer[utils.TTL_KEY]
				server = answer[utils.QUERIED_NAME_KEY]
				if answer[utils.TYPE_KEY] == "A" or answer[utils.TYPE_KEY] == "CNAME":
					if name not in answer_servers:
						answer_servers[name] = [ttl]
					else:
						lst = answer_servers[name]
						answer_servers[name] = lst + [ttl]

				elif server == ".":
					if name not in root_servers:
						root_servers[name] = [ttl]
					else:
						lst = root_servers[name]
						root_servers[name] = lst + [ttl]
				elif server.count(".") == 1:
					if name not in tld_servers:
						tld_servers[name] = [ttl]
					else:
						lst = tld_servers[name]
						tld_servers[name] = lst + [ttl]
				else:
					if name not in other_servers:
						other_servers[name] = [ttl]
					else:
						lst = other_servers[name]
						other_servers[name] = lst + [ttl]
	answer = []
	a_TTL = []
	other_TTL = []
	tld_TTL = []
	root_TTL = []
	for root in root_servers:
		root_TTL += [np.mean(root_servers[root])]
	for tld in tld_servers:
		tld_TTL += [np.mean(tld_servers[tld])]
	for other in other_servers:
		other_TTL += [np.mean(other_servers[other])]
	for answer in answer_servers:
		a_TTL += [np.mean(answer_servers[answer])]
	return [np.mean(root_TTL), np.mean(tld_TTL), np.mean(other_TTL), np.mean(a_TTL)]


#print(get_average_ttls("q3/first_run.json"))

def get_average_times(filename):
	with open(filename) as fh:
		results = json.load(fh)
	total_time = []
	final_time = []
	for host_info in results:
		if not host_info[utils.SUCCESS_KEY]:
			continue
		queries = host_info[utils.QUERIES_KEY]
		tmp_final = []
		for query in queries:
			time = query[utils.TIME_KEY]
			total_time += [time]
			for answer in query[utils.ANSWERS_KEY]:
				if answer[utils.TYPE_KEY] == "A" or answer[utils.TYPE_KEY] == "CNAME":
					tmp_final += [time]
		final_time += [np.mean(tmp_final)]
	return [np.mean(total_time), np.mean(final_time)]

#print(get_average_times("q3/from_korea.json"))

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
				if a[utils.TYPE_KEY] == "A" or a[utils.TYPE_KEY] == "CNAME":
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
		#print("total time: ")
		#print(total_time)

	#print("num hosts: ")
	#print(num_hosts)


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

#generate_time_cdfs("q3/updated_first_run.json", "q3/updated_part3_time_cdfs.pdf")
#print(get_average_ttls("q3a_500.json"))


def count_different_dns_responses(filename1, filename2):
	with open(filename1) as fh:
		results = json.load(fh)
	host_to_ip = {}
	first_value = 0
	for host_info in results:
		if not host_info[utils.SUCCESS_KEY]:
			continue
		for query in host_info[utils.QUERIES_KEY]:
			host_set = []
			for a in query[utils.ANSWERS_KEY]:
				if a[utils.TYPE_KEY] == "A" or a[utils.TYPE_KEY] == "CNAME":
					host_set += [a[utils.ANSWER_DATA_KEY]]
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
				if a[utils.TYPE_KEY] == "A" or a[utils.TYPE_KEY] == "CNAME":
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
			#print(host + " : first_value")
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
							#print(host + ": second_value")
							second_value += 1
							break

	return [first_value, second_value + first_value]

#print(count_different_dns_responses("q3/dns_output_1.json", "q3/dns_output_other_server.json"))
