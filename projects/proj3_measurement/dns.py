def run_dig(hostname_filename, output_filename, dns_query_server=None):
	with open(hostname_filename, 'r') as fp:
	hostnames = []
	line = fp.readline()
	while line != "":
		#print(line)
		hostnames += [line.split("\n")[0]]
		line = fp.readline()
	for host in hostnames:
		print(host)
		if dns_query_server == None:
			output = subprocess.check_output("dns +trace +tries=1 +nofail " + host + " 2>&1", shell=True)
		with open(output_filename, "a") as f:
			f.write(output)


def get_average_ttls(filename):


def get_average_times(filename):

def generate_time_cdfs(json_filename, output_filename):


def count_different_dns_responses(filename1, filename2):
