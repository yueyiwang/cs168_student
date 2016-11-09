import json
import sys

def most_number_AS(filename):
	data = []
	with open(filename) as fh:
		for line in fh:
			data.append(json.loads(line))
	host_to_AS = {}
	for results in data:
		for host in results:
			if host == "timestamp":
				continue
			if host not in host_to_AS:
				host_to_AS[host] = []
			for hop in results[host]:
				for ind in hop:
					asn = ind["ASN"]
					#print(asn)
					if asn != "None":
						host_to_AS[host] += [asn]

	most_AS = []
	num = 0
	for host in host_to_AS:
		#print(host)
		host_set = set(host_to_AS[host])
		print(host_set)
		if (len(host_set)) > num:
			most_AS = [host]
			num = len(host_set)
		elif len(host_set) == num:
			most_AS += [host]
	print(set(host_to_AS[host]))
	return most_AS

def load_balanced(filename):
	data = []
	with open(filename) as fh:
		for line in fh:
			data.append(json.loads(line))
	for results in data:
		host_to_hop = {}
		for host in results:
			if host  == "timestamp":
				continue
			if host not in host_to_hop:
				host_to_hop[host] = []
			for hop in results[host]:
				hop_set = []
				for ind in hop:
					ip = ind["ip"]
					hop_set += [ip]	
				host_to_hop[host] += [set(hop_set)]
		for host in host_to_hop:
			hops = host_to_hop[host]
			for h in hops:
				if len(h) > 1:
					print(host)
					print_hops(hops)
					break


def print_hops(hops):
	string = ""
	for h  in hops:
		string += "["
		for ip in h:
			string += ip + ", "
		string += "] -> "
	print(string)

	# for host in host_to_hop:
	# 	for asn in host_to_hop[host]:
	# 		host_to_hop[host][asn] = set(host_to_hop[host][asn])
	# for host in host_to_hop:
	# 	asns = host_to_hop[host].keys()
	# 	asns.sort()
	# 	print(host)
	# 	for asn in asns:
	# 		string = asn + " -> "
	# 		if len(host_to_hop[host][asn]) > 1:
	# 			string += "["
	# 			for ip in host_to_hop[host][asn]:
	# 				string += str(ip)
	# 				string+= ", "
	# 			string+= "]"
	# 			print(string)



def unique_routes(filename):
	data = []
	with open(filename) as fh:
		for line in fh:
			data.append(json.loads(line))
	host_to_hop = [0, 0, 0, 0, 0]
	hosts = []
	for i in range(5):
		results = data[i]
		host_to_hop[i] = {}
		for host in results:
			if host  == "timestamp":
				continue
			if host not in hosts:
				hosts += [host]
			if host not in host_to_hop[i]:
				host_to_hop[i][host] = []
			for hop in results[host]:
				hop_set = []
				for ind in hop:
					ip = ind["ip"]
					hop_set += [ip]	
				host_to_hop[i][host] += [set(hop_set)]	

	print(get_unique_num(host_to_hop, "facebook.com"))
def get_unique_num(host_to_hop, host):
	massive_set = []
	print(host_to_hop[0][host])
	for i in range(5):
		if  check_set_in(host_to_hop[i][host], massive_set):
			massive_set += [host_to_hop[i][host]]
	return len(massive_set)
def check_set_in(hops, massive_set):
	for i in range(len(hops)):
		h  = hops[i]
		for j in range(len(massive_set)):
			other_hops = massive_set[j]
			if i >= len(other_hops):
				return False
			if other_hops[i] != h:
				return False
	return True


		


unique_routes("tr_a.json")
