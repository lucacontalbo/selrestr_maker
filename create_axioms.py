import pandas as pd
import re as re
import argparse
import os

def create_axioms_owlstar(dictionary,output_folder): #properties_input_tsv, triplets_input_tsv, output_folder, topic, date_wikidata_dump, thresholds):

	output_ttls = os.path.join(output_folder,"probabilistic_pattern_owlstar.ttl")

	with open(output_ttls, "w") as ttls:
		ttls.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ." + "\n")
		ttls.write("@prefix os: <http://w3id.org/owlstar/> ." + "\n")
		ttls.write("@prefix pbdata: <https://w3id.org/framester/pb/data/> ." + "\n")
		ttls.write("@prefix pbrole: <https://w3id.org/framester/pb/localrole/> ." + "\n")

		ttls.write("\n")

		#add ontology metadata

		for subj,value1 in dictionary.items():
			if not isinstance(value1,dict): continue
			for pred,value2 in value1.items():
				if not isinstance(value2,dict): continue
				for obj,value3 in value2.items():
					if not isinstance(value3,dict): continue
					ttls.write('<< << pbdata:' + subj + ' pbrole:' + pred + ' pbdata:' + obj + ' >> os:interpretation os:AllSomeInterpretation . >> os:probability ' \
						+ '"' + str(value3['subj_pred_obj_probability']*100) + '%" .' + '\n\n') #+ "\" ; mb " + prob_pattern + " ." + "\n" + "\n")


def create_axioms(dictionary,output_folder):

	output_ttls = os.path.join(output_folder,'probabilistic_pattern.ttl')

	with open(output_ttls, 'w') as ttls:
		ttls.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ." + "\n")
		ttls.write("@prefix os: <http://w3id.org/owlstar/> ." + "\n")
		ttls.write("@prefix pbdata: <https://w3id.org/framester/pb/data/> ." + "\n")
		ttls.write("@prefix pbrole: <https://w3id.org/framester/pb/localrole/> ." + "\n")

		ttls.write("\n")

		#add ontology metadata

		for subj,value1 in dictionary.items():
			if not isinstance(value1,dict): continue
			for pred,value2 in value1.items():
				if not isinstance(value2,dict): continue
				for obj,value3 in value2.items():
					if not isinstance(value3,dict): continue
					#add universal and existential restrictions
