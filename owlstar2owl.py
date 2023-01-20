import re
import argparse
from copy import deepcopy
import sys

class OWLStar2OWLConverter:
	def __init__(self):
		self.triple2id = {}

		self.owlstar2owl = {
			'os:AllSomeInterpretation': '{} rdfs:subClassOf [a owl:Restriction ;\n\t\t owl:onProperty {} ;\n\t\t owl:someValuesFrom {}] .',
			'os:AllOnlyInterpretation': '{} rdfs:subClassOf [a owl:Restriction ;\n\t\t owl:onProperty {} ;\n\t\t owl:allValuesFrom {}] .',
			'os:SomeSomeInterpretation': '[a {}] {} [a {}] .'
			#TODO: 'os:AllSomeAllTimesInterpretation':
			#TODO: 'os:AllNumberInterpretation':
		}

		self.owl = 'http://www.w3.org/2002/07/owl#'
		self.rdf = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
		self.rdfs = 'http://www.w3.org/2000/01/rdf-schema#'
		self.xsd = 'http://www.w3.org/2001/XMLSchema#'

	def update_mapping(self,rdfstar_triple):
		if rdfstar_triple not in self.triple2id.keys():
			self.triple2id[rdfstar_triple] = ':_{}'.format(len(self.triple2id.keys()))

	def reify(self,rdfstar_triple):
		try:
			reification_text = ''

			id_statement = self.triple2id[rdfstar_triple]
			reification_text += '{} rdf:type rdf:Statement;\n'.format(id_statement)

			for el in zip(['subject','predicate','object'],rdfstar_triple.split()):
				if el[0] == 'object':
					reification_text += '\trdf:{} {} .\n'.format(el[0],el[1])
				else:
					reification_text += '\trdf:{} {};\n'.format(el[0],el[1])

			return reification_text+'\n'

		except e:
			print(e)
			raise e

	def get_rdfstar_triples(self,line):
		def get_rdfstar_triples_recursive(line,triples=[]):
			r = re.compile('''
				<<
					(?:
						[^<>]*
						|
						<<[^<>]*>>
					)*
				>>
			''', flags=re.X)

			rdfstar_triples = re.findall(r,line)
			if len(rdfstar_triples) == 0:
				return []

			for el in rdfstar_triples:
				triple = ' '.join(el.split()[1:-1])
				get_rdfstar_triples_recursive(triple,triples)
				triples.append(triple)

			return triples

		return get_rdfstar_triples_recursive(line)

	def add_initial_information(self,new_text):
		owl = False
		rdf = False
		rdfs = False
		xsd = False

		end_prefix = 0

		probability_text = ':probability a owl:DatatypeProperty ; rdfs:range xsd:string .\n'
		for i in range(len(new_text)):
			if new_text[i].startswith('@prefix') or new_text[i].startswith('@PREFIX') or new_text[i].startswith(' ') or new_text[i].startswith('\n'):
				if self.owl in new_text[i]:
					owl = True
				if self.rdf in new_text[i]:
					rdf = True
				if self.rdfs in new_text[i]:
					rdfs = True
				if self.xsd in new_text[i]:
					xsd = True

			else:
				end_prefix = i
				break

		new_text.insert(end_prefix,probability_text)

		if not owl: new_text.insert(end_prefix,'@prefix owl: <{}>'.format(self.owl))
		if not rdf: new_text.insert(end_prefix,'@prefix rdf: <{}>'.format(self.rdf))
		if not rdfs: new_text.insert(end_prefix,'@prefix rdfs: <{}>'.format(self.rdfs))
		if not xsd: new_text.insert(end_prefix,'@prefix xsd: <{}>'.format(self.xsd))

		return new_text

	def map(self,input_file_path,output_file_path):
		def map2rdf(self,line):
			rdfstar_triples = self.get_rdfstar_triples(line)
			if len(rdfstar_triples) == 0:
				return line

			reification_line = ''
			rdfstar_triples = deepcopy(sorted(rdfstar_triples,key=len))
			for i in range(len(rdfstar_triples)):
				splitted_rdfstar = rdfstar_triples[i].split()
				if len(splitted_rdfstar) == 4 and splitted_rdfstar[-1] == '.':
					rdfstar_triples[i] = ' '.join(splitted_rdfstar[:-1])
				elif len(splitted_rdfstar) == 4:
					print("error")
					sys.exit(0) #TODO: rewrite this
				self.update_mapping(rdfstar_triples[i])
				reification_text = self.reify(rdfstar_triples[i])

				end_dot = ' .' if len(splitted_rdfstar) == 4 else ''

				if splitted_rdfstar[1] == 'os:interpretation':
					splits = rdfstar_triples[i-1].split()
					restriction_line = self.owlstar2owl[splitted_rdfstar[2]].format(*splits[:3])+'\n\n'
					reification_line += restriction_line
					line = line.replace('<< {}{} >>'.format(rdfstar_triples[i],end_dot),splitted_rdfstar[0])
				else:
					reification_line += reification_text
					line = line.replace('<< {}{} >>'.format(rdfstar_triples[i],end_dot),self.triple2id[rdfstar_triples[i]])

				for j in range(len(rdfstar_triples[i+1:])):
					rdfstar_triples[i+j+1] = rdfstar_triples[i+j+1].replace('<< '+rdfstar_triples[i]+' >>',self.triple2id[rdfstar_triples[i]])

				line_splits = line.split()
				if line_splits[1] == 'os:probability':
					line_splits[1] = ':probability'
					line = ' '.join(line_splits)

			reification_line += line
			return reification_line

		with open(input_file_path,'r') as reader:
			text = reader.readlines()

		new_text = [map2rdf(self,line) for line in text]

		new_text = '\n'.join(self.add_initial_information(new_text))

		with open(output_file_path,'w') as writer:
			writer.write(new_text)


def inputs_checker(input_file_path,output_file_path):
	input_file_path_split = input_file_path.split('.') #used for checking file extension
	output_file_path_split = output_file_path.split('.')

	assert input_file_path_split[-1] == 'ttl', 'Input file must have .ttl extension'
	assert output_file_path_split[-1] == 'ttl', 'Output file must have .ttl extension'


if __name__ == '__main__':
	argparser = argparse.ArgumentParser(prog='python3 owlstar2owl.py', description='OWLStar to OWL python converter')
	argparser.add_argument('-i','--input_path',action='store',help='Turtle* input file path', required=True)
	argparser.add_argument('-o','--output_path',action='store',help='Output file path',required=True)

	args = argparser.parse_args()
	input_file_path = args.input_path
	output_file_path = args.output_path

	inputs_checker(input_file_path,output_file_path)

	converter = OWLStar2OWLConverter()
	converter.map(input_file_path,output_file_path)
