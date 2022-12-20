from rdflib import Graph, RDF, RDFS, URIRef, Namespace
import os

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

		self.directory_path = directory_path

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
		graph.bind('verbatlas',URIRef(self.verbatlas),False)
		graph.bind('schema',URIRef(self.schema),False)

		return graph

	"""
	get_frame_occ_list: recursive function which finds the instances of frame occurrences. Read Frodo's paper for the definition of frame occurrence
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
		return str(uriref).split('/')[-1].split('#')[-1]

	def calculate_frequencies(self):
		probabilities = {}
		for file_path in os.listdir(self.directory_path):
			graph = self.graph_init(self.directory_path+file_path)
			frame_occurrence_list = self.get_frame_occ_list(graph)
			for frame_occurrence in frame_occurrence_list:
				frame_occurrence_type = graph.value(frame_occurrence,self.rdf.type,None)
				frame_occurrence_str = self.uriref2name(frame_occurrence_type)
				if frame_occurrence_str not in probabilities.keys():
					probabilities[frame_occurrence_str] = {}
				for _,p,_ in graph.triples((frame_occurrence,None,None)):
					if p.startswith(self.pb_role):
						p_str = self.uriref2name(p)
						if p_str not in probabilities[frame_occurrence_str].keys():
							probabilities[frame_occurrence_str][p_str] = {}
						for _,_,o in graph.triples((frame_occurrence,p,None)):
							o_type = graph.value(o,self.rdf.type,None)
							o_type_str = self.uriref2name(o_type)
							if o_type_str not in probabilities[frame_occurrence_str][p_str].keys():
								probabilities[frame_occurrence_str][p_str][o_type_str] = 0
							probabilities[frame_occurrence_str][p_str][o_type_str]+=1
		return probabilities

	def calculate_metrics(self):
		pass
