from rdflib import Graph, RDF, RDFS, URIRef, Namespace
import os
from copy import deepcopy
from SPARQLQuery import SPARQLQuery
from scipy.stats import entropy
from scipy.special import softmax
import numpy as np
from sklearn.preprocessing import normalize

class Parser:
	"""
	This class calculates the probability of each frame occurrence-predicate pair to have a particular type as range role
	input: directory_path: directory from where to load the files containing the different graphs
	"""

	def __init__(self,directory_path):
		self.rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
		self.rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
		self.fred = Namespace("http://www.ontologydesignpatterns.org/ont/fred/domain.owl#")
		self.dul = Namespace("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#")
		self.owl = Namespace("http://www.w3.org/2002/07/owl#")
		self.pb_role = Namespace("https://w3id.org/framester/pb/localrole/")
		self.pb_frame = Namespace("https://w3id.org/framester/pb/data/")
		self.fst_schema = Namespace("https://w3id.org/framester/schema/")
		self.vn_role = Namespace("http://www.ontologydesignpatterns.org/ont/vn/abox/role/")
		self.fn_frame = Namespace("https://w3id.org/framester/framenet/abox/frame/")
		self.quantifiers = Namespace("http://www.ontologydesignpatterns.org/ont/fred/quantifiers.owl#")
		self.wd = Namespace("https://www.wikidata.org/wiki/")
		self.db = Namespace("http://dbpedia.org/resource/")
		self.verbatlas = Namespace("http://verbatlas.org/")
		self.schema = Namespace("http://schema.org/")
		self.wn = Namespace("https://w3id.org/framester/wn/wn30/schema/")

		self.namespace2uri = {
			'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
			'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
			'dul': 'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#',
			'fred': 'http://www.ontologydesignpatterns.org/ont/fred/domain.owl#',
			'owl': 'http://www.w3.org/2002/07/owl#',
			'pb_role': 'https://w3id.org/framester/pb/localrole/',
			'pb_frame': 'https://w3id.org/framester/pb/data/',
			'fst_schema': 'https://w3id.org/framester/schema/',
			'vn_role': 'http://www.ontologydesignpatterns.org/ont/vn/abox/role/',
			'fn_frame': 'https://w3id.org/framester/framenet/abox/frame/',
			'quantifiers': 'http://www.ontologydesignpatterns.org/ont/fred/quantifiers.owl#',
			'wd': 'https://www.wikidata.org/wiki/',
			'db': 'http://dbpedia.org/resource/',
			'wn': 'https://w3id.org/framester/wn/wn30/schema/',
			'verbatlas': 'http://verbatlas.org/',
			'schema': 'http://schema.org/'
		}

		self.uri2namespace = {v:k for k,v in self.namespace2uri.items()}

		self.directory_path = directory_path

		self.sparql_query = SPARQLQuery()

		self.count_sparql_errors = 0

		self.metrics = ['subj_pred_obj_frequency','subj_pred_obj_probability','subj_pred_obj_total_probability',
			'subj_pred_frequency','subj_pred_probability','subj_pred_total_probability',
			'subj_frequency','subj_probability','subj_total_probability', 'frequency'
		]

	def graph_init(self,file_path):
		graph = Graph()
		graph.parse(file_path)

		graph.bind('rdf',URIRef(self.rdf),False)
		graph.bind('rdfs',URIRef(self.rdfs),False)
		graph.bind('dul',URIRef(self.dul),False)
		graph.bind('fred',URIRef(self.fred),False)
		graph.bind('owl',URIRef(self.owl),False)
		graph.bind('pb_role',URIRef(self.pb_role),False)
		graph.bind('pb_frame',URIRef(self.pb_frame),False)
		graph.bind('fst_schema',URIRef(self.fst_schema),False)
		graph.bind('vn_role',URIRef(self.vn_role),False)
		graph.bind('fn_frame',URIRef(self.fn_frame),False)
		graph.bind('quantifiers',URIRef(self.quantifiers),False)
		graph.bind('wd',URIRef(self.wd),False)
		graph.bind('db',URIRef(self.db),False)
		graph.bind('wn',URIRef(self.wn),False)
		graph.bind('verbatlas',URIRef(self.verbatlas),False)
		graph.bind('schema',URIRef(self.schema),False)

		return graph

	"""
	get_frame_occ_list: recursive function which finds the instances of frame occurrences.
	Input: object(optional) -> the input is a class, treated as an object when looking for triples. The parameter is ONLY used for the recursion
				   hence this function MUST be called without the parameter for its intended use.
	Output: list of frame occurrences
	"""

	def get_frame_occ_list(self,graph,object=None):
		list = []
		if object == None:
			for s,p,o in graph.triples((None,RDFS.subClassOf,self.dul.Event)):
				list.extend(self.get_frame_occ_list(graph,s))
		else:
			for s,p,o in graph.triples((None,RDFS.subClassOf,object)):
				list.extend(self.get_frame_occ_list(graph,s))
			for s,p,o in graph.triples((None,RDF.type,object)):
				list.append(s)
		return list

	def uriref2name(self,uriref):
		splitted = str(uriref).split('/')[-1].split('#')
		uri_base, name = '/'.join(splitted[:-1]), splitted[-1]

		if uri_base in self.uri2namespace.keys():
			return self.uri2namespace[uri_base]+':'+name
		else:
			return name

	def get_frequencies_dict(self):
		frequencies = {}
		frequencies['frequency'] = 0
		for file_path in os.listdir(self.directory_path):
			if file_path.split('.')[-1] != 'owl': continue
			graph = self.graph_init(os.path.join(self.directory_path,file_path))
			frame_occurrence_list = self.get_frame_occ_list(graph)
			for frame_occurrence in frame_occurrence_list:
				frame_occurrence_type = graph.value(frame_occurrence,self.rdf.type,None)
				frame_occurrence_str = self.uriref2name(frame_occurrence_type)
				if str(frame_occurrence_type) not in frequencies.keys():
					frequencies[str(frame_occurrence_type)] = {}
					frequencies[str(frame_occurrence_type)]['subj_frequency'] = 0
				for _,p,_ in graph.triples((frame_occurrence,None,None)):
					if p.startswith(self.pb_role):
						p_str = self.uriref2name(p)
						types = []
						if str(p) not in frequencies[str(frame_occurrence_type)].keys():
							frequencies[str(frame_occurrence_type)][str(p)] = {}
							frequencies[str(frame_occurrence_type)][str(p)]['subj_pred_frequency'] = 0
						for _,_,o in graph.triples((frame_occurrence,p,None)):
							o_type = str(graph.value(o,self.rdf.type,None))
							o_type_str = self.uriref2name(o_type)
							if o_type not in frequencies[str(frame_occurrence_type)][str(p)].keys():
								frequencies[str(frame_occurrence_type)][str(p)][o_type] = {}
								frequencies[str(frame_occurrence_type)][str(p)][o_type]['subj_pred_obj_frequency'] = 0
							frequencies[str(frame_occurrence_type)][str(p)][o_type]['subj_pred_obj_frequency']+=1
							frequencies[str(frame_occurrence_type)][str(p)]['subj_pred_frequency']+=1
							frequencies[str(frame_occurrence_type)]['subj_frequency']+=1
							frequencies['frequency']+=1
							types.append(o_type)
						common_ancestor_type, cardinality = self.generalize_common(graph,types)
						if common_ancestor_type not in frequencies[str(frame_occurrence_type)][str(p)].keys(): #TODO: add generalization info
							frequencies[str(frame_occurrence_type)][str(p)][str(common_ancestor_type)] = {}
							frequencies[str(frame_occurrence_type)][str(p)][str(common_ancestor_type)]['subj_pred_obj_frequency'] = cardinality
						#frequencies = self.generalize(frequencies,graph,frame_occurrence_str,p_str,o_type)
		return frequencies

	def calculate_metrics(self,frequency,total_frequency,frequency_previous):
		support = float(frequency)/float(total_frequency)
		confidence = float(frequency)/float(frequency_previous)
		return support, confidence

	def get_metrics_dict(self,frequency_dict):
		for k1,v1 in frequency_dict.items():
			if k1 in self.metrics: continue
			for k2,v2 in v1.items():
				if k2 in self.metrics: continue
				for k3,v3 in v2.items():
					if k3 in self.metrics: continue
					frequency_dict[k1][k2][k3]['subj_pred_obj_total_probability'], frequency_dict[k1][k2][k3]['subj_pred_obj_probability']= \
						self.calculate_metrics(frequency_dict[k1][k2][k3]['subj_pred_obj_frequency'], frequency_dict['frequency'], frequency_dict[k1][k2]['subj_pred_frequency'])
				frequency_dict[k1][k2]['subj_pred_total_probability'], frequency_dict[k1][k2]['subj_pred_probability']= \
					self.calculate_metrics(frequency_dict[k1][k2]['subj_pred_frequency'], frequency_dict['frequency'], frequency_dict[k1]['subj_frequency'])
			frequency_dict[k1]['subj_total_probability'], frequency_dict[k1]['subj_probability']= \
				self.calculate_metrics(frequency_dict[k1]['subj_frequency'], frequency_dict['frequency'], frequency_dict['frequency'])

		return frequency_dict

	def generalize_common(self,graph,types,k=1): #generalize up until most general type across WordNet taxonomy. Issue: highly computationally demanding due to high number
					   #of SPARQL queries. One possible fix would be to extract the Wordnet hypernim paths into a separate file and load it without using sparql queries.
					   #for reduced computational time, the parameter k puts a bound on the number of possible hypernim steps.
		wn_types = []
		for o in types: #extract wn alignments for each type
			o_wn = graph.value(URIRef(o),self.owl.equivalentClass,None)
			if o_wn == None: continue
			wn_types.append(o_wn)
		generalizations = []
		for type1 in wn_types: #extract wn hierarchy path for each type
			generalized_type = [type1]
			for i in range(k):
				query_text = 'SELECT ?o WHERE {{ <'+str(type1)+'> <'+str(self.wn.hyponymOf)+'> ?o .}}'
				try:
					result = self.sparql_query.query(query_text)
				except:
					break
				if isinstance(result,bytes) or result == None or len(result['results']['bindings']) == 0:
					break
				wn_generalized_type = result['results']['bindings'][0]['o']['value']
				generalized_type.append(wn_generalized_type)
				type1 = wn_generalized_type
			generalizations.append(generalized_type)

		common_ancestor_type = None
		if len(generalizations) == 0:
			return common_ancestor_type, 0

		for type in generalizations[0]:
			common_ancestor = True
			for i in range(1,len(generalizations)):
				if type not in generalizations[i]:
					common_ancestor = False
					break
			if common_ancestor:
				common_ancestor_type = type
				break

		return common_ancestor_type, len(generalizations)

	def generalize(self,frequency_dict,graph,s,p,o): #naive generalization function, visiting WordNet taxonomy by visiting 3 steps of the hierarchy.
							 #Each generalization found (even non common ones) are added inside the final result
							 #It is quicker than generalize_common due to the reduced amount of SPARQL queries
		def update_graph(self,frequency_dict,s,p,o,o_wn_generalized_str):
			if o_wn_generalized_str not in frequency_dict[s][p].keys():
				frequency_dict[s][p][o_wn_generalized_str] = {}
				frequency_dict[s][p][o_wn_generalized_str]['subj_pred_obj_frequency'] = 0
				frequency_dict[s][p][o_wn_generalized_str]['generalizes'] = []
			frequency_dict[s][p][o_wn_generalized_str]['subj_pred_obj_frequency'] += 1
			o_str = self.uriref2name(o)
			if o_str not in frequency_dict[s][p][o_wn_generalized_str]['generalizes']:
				frequency_dict[s][p][o_wn_generalized_str]['generalizes'].append(o_str)
			return frequency_dict

		o_wn = graph.value(o,self.owl.equivalentClass,None)
		if o_wn == None:
			return frequency_dict

		query_text = 'SELECT ?o ?o2 ?o3 WHERE {{ <'+str(o_wn)+'> <'+str(self.wn.hyponymOf)+'> ?o . ?o <'+str(self.wn.hyponymOf)+'> ?o2 . ?o2 <'+str(self.wn.hyponymOf)+'> ?o3}} LIMIT 10'
		try:
			result = self.sparql_query.query(query_text)
		except:
			self.count_sparql_errors += 1
			return frequency_dict

		if isinstance(result,bytes) or result == None or len(result['results']['bindings']) == 0:
			return frequency_dict

		o_wn_generalized = result['results']['bindings'][0]['o']['value']
		o_wn_generalized_str = str(o_wn_generalized)

		o_wn_generalized2 = result['results']['bindings'][0]['o2']['value']
		o_wn_generalized2_str = str(o_wn_generalized2)

		o_wn_generalized3 = result['results']['bindings'][0]['o3']['value']
		o_wn_generalized3_str = str(o_wn_generalized3)

		frequency_dict = update_graph(self,frequency_dict,s,p,o,o_wn_generalized_str)
		frequency_dict = update_graph(self,frequency_dict,s,p,o,o_wn_generalized2_str)
		frequency_dict = update_graph(self,frequency_dict,s,p,o,o_wn_generalized3_str)

		return frequency_dict

	def clean_dictionary(self,frequency_dict):
		copied_dict = deepcopy(frequency_dict)
		for k1,v1 in frequency_dict.items():
			if not isinstance(v1,dict): continue
			for k2,v2 in v1.items():
				if not isinstance(v2,dict): continue
				for k3,v3 in v2.items():
					if not isinstance(v3,dict): continue
					if 'generalizes' in v3.keys() and len(v3['generalizes']) == 1:
						del copied_dict[k1][k2][k3]

		return copied_dict

	def print_statistics(self,frequency_dict): #used for calculating statistics about most frequent groupings or most frequent types
		most_frequent_types = {}
		for k1,v1 in frequency_dict.items():
			if not isinstance(v1,dict): continue
			for k2,v2 in v1.items():
				if not isinstance(v2,dict): continue
				for k3,v3 in v2.items():
					if not isinstance(v3,dict): continue
					if k3 not in most_frequent_types.keys():
						most_frequent_types[k3] = 0
					print("{} --- {}".format(k3,type(k3)))
					most_frequent_types[k3] += 1
		most_frequent_groupings = {}
		most_frequent_groupings_count = {}
		for k1,v1 in frequency_dict.items():
			if not isinstance(v1,dict): continue
			for k2,v2 in v1.items():
				if not isinstance(v2,dict): continue
				for k3,v3 in v2.items():
					if not isinstance(v3,dict): continue
					if 'generalizes' in v3.keys():
						if k3 not in most_frequent_groupings.keys():
							most_frequent_groupings[k3] = set()
							most_frequent_groupings_count[k3] = 0
						for el in v3['generalizes']:
							most_frequent_groupings[k3].add(el)

						most_frequent_groupings_count[k3] += 1

		sorted_keys = sorted(most_frequent_types, key=most_frequent_types.get, reverse=True)
		for r in sorted_keys:
    			print("{} --- {}".format(r, most_frequent_types[r]))

		print("-----------------------")

		sorted_keys = sorted(most_frequent_groupings_count, key=most_frequent_groupings_count.get, reverse=True)
		for r in sorted_keys:
			print("{} --- {} --- {}".format(r, most_frequent_groupings_count[r], most_frequent_groupings[r]))


	def get_types(self,frequency_dict,zero=False):
		types = {}
		for k1,v1 in frequency_dict.items():
			if not isinstance(v1,dict): continue
			for k2,v2 in v1.items():
				if not isinstance(v2,dict): continue
				for k3,v3 in v2.items():
					if not isinstance(v3,dict): continue
					if zero:
						types[k3] = 0.0001
					elif k3 not in types.keys():
						types[k3] = v3['subj_pred_obj_frequency']
					else:
						types[k3] += v3['subj_pred_obj_frequency']
		return types

	def get_preference(self,frequency_dict,frame):
		types = self.get_types(frequency_dict)
		types_given_frame = self.get_types(frequency_dict,zero=True)
		for k,v1 in frequency_dict[frame].items():
			if not isinstance(v1,dict): continue
			for k2,v2 in v1.items():
				if not isinstance(v2,dict): continue
				types_given_frame[k2] += v2['subj_pred_obj_frequency']
		types_list = normalize(np.array([v for k,v in types.items()])[:,np.newaxis], axis=0).reshape(-1)
		types_names = [k for k,v in types.items()]
		types_given_frame_list = normalize(np.array([v for k,v in types_given_frame.items()])[:,np.newaxis], axis=0).reshape(-1)
		return frame, entropy(types_given_frame_list,types_list)
