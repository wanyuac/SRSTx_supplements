"""
This script assigns identifiers to allele variants in the compiled result of SRST2 (https://github.com/katholt/srst2) in accordance with consensus sequences clustered by cd-hit-est. Results are printed to STDOUT.

Usage: python clustering_allele_variants.py -t <compiledResults.txt> -c <nucl.clstr> > compiledResults_clusterd.txt

Input:
	1. A compiled tab-deliminated file generated by SRST2 using the command: python srst2.py --prev_output *__genes*results.txt --output <prefix>
	2. A cluster file created by cd-hit-est.
	
Output: A new file of compiled results, where each allele variant are assigned a unique cluster identifier.

Author: Yu Wan (wanyuac@gmail.com, GitHub: https://github.com/wanyuac)
First edition: 29 July 2015
Last edition: 29 July 2015

License: GNU GPL 2.1
"""

import collections, re
from argparse import ArgumentParser

def parse_arguments():
	# read arguments from the command line
	parser = ArgumentParser(description = "Read arguments: -t and -c")
	parser.add_argument("-t", type = str, required = True, help = "Allele table compiled by SRST2", default = "")
	parser.add_argument("-c", type = str, required = True, help = "List of clusters produced by cd-hit-est")
	return parser.parse_args()
	
def get_alleleID(id):
	"""
	This function changes sequence names in the cluster file into allele names used in SRST2. For example, 
	if isAllele == True:
		input = "66__FloR_Phe__FloR__1212", output = "FloR_1212"
	"""
	fields = id.split("__")[-2:]  # only take the last two elements: allele name and sequence identifier
	return "_".join(fields)

def read_clusters(file):
	"""
	This function reads a cluster file produced by cd-hit-est, and returns a dictionary of clusters following the structure:
	{allele_name: {cluster_id : [sample1, sample2, ...]}}, where two keys are applied hierarchically.
	"""
	clusters = collections.defaultdict(dict)
	with open(file, "rU") as f:
		for line in f:
			line = line.strip("\n")
			if line.startswith(">"):
				cluster_id = line.split(" ")[-1]  # read a new cluster ID: "0", "1", "2", ...
			else:  # the last line in the file, which is empty, will not be read
				allele = get_alleleID(re.findall(">(.+?)\.consensus", line)[0])  # extract the sequence ID, such as 52__TetA_Tet__TetA__1545, with a regular expression; then convert it into an allele name
				sample = re.findall("\|(.+?)\.\.\.", line)[0]  # extract the sample ID from the line with a regular expression
				clusters[sample][allele] = cluster_id  # save this cluster_id in the dictionary {sample : {allele : cluster_id}}
	return clusters
	
def assign_clusterIDs(table, clusters):
	"""
	This function assigns allele identifiers, which are cluster IDs, to every allele variant.
	Currently, the question marks following the allele names are simply removed, regardless of their coverages.
	For example, "Aac6-Iaa_760*?" becomes "aac6-Iaa_760.140" in the new compiled results, where 140 is the cluster ID of this allele in the cd-hit-est outputs.
	"""
	f = open(table, "rU").readlines()
	print f[0].strip("\n")  # print the header line
	for line in f[1:]:  # for other lines in this file
		fields = (line.rstrip("\n")).split("\t")
		sample = fields[0]
		new_line = [sample]
		for allele in fields[1:]:
			allele = allele.rstrip("?")  # arbitrarily ignore the question mark from allele calls
			if allele[-1] == "*":  # This is a variant
				allele = allele[:-1] + "." + clusters[sample][allele[:-1]]  # join the cluster ID to the allele name
			new_line.append(allele)
		print "\t".join(new_line)  # print a new line to STDOUT
	return

def main():
	args = parse_arguments()
	assign_clusterIDs(table = args.t, clusters = read_clusters(args.c))
	
# The main program
if __name__ == "__main__":
    main()