import subprocess
import json
def run_dig(hostname_filename, output_filename, dns_query_server=None):
	# with open(hostname_filename, 'r') as fp:
	# 	hostnames = []
	# 	line = fp.readline()
	# 	while line != "":
	# 		#print(line)
	# 		hostnames += [line.split("\n")[0]]
	# 		line = fp.readline()
	hostnames = hostname_filename
	all_digs = []
	for host in hostnames:
		print(host)
		if dns_query_server == None:
			output = subprocess.check_output("dig +trace +tries=1 +nofail " + host + " 2>&1", shell=True)
			dig_dict = parse_no_dns_server(host, output)
			print(output)
			all_digs += [dig_dict]
		else:
			output = subprocess.check_output("dig " + host + "@" + dns_query_server + " 2>&1", shell=True)

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
			current_dict["Time in millis"] = tokens[-2]
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
	return dig_dict

print(run_dig(["google.com"], "dig_ouput_test.json"))
# def get_average_ttls(filename):


# def get_average_times(filename):

# def generate_time_cdfs(json_filename, output_filename):


# def count_different_dns_responses(filename1, filename2):
