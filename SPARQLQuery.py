from SPARQLWrapper import SPARQLWrapper, JSON

class SPARQLQuery():
	def __init__(self):
		self.PREFIX = """PREFIX bn: <http://babelnet.org/rdf/>
PREFIX ds: <http://www.ontologydesignpatterns.org/cp/owl/descriptionandsituation.owl>
PREFIX sem: <http://www.ontologydesignpatterns.org/cp/owl/semiotics.owl>
PREFIX spec: <http://www.ontologydesignpatterns.org/cp/owl/specialization.owl>
PREFIX own2dul: <http://www.ontologydesignpatterns.org/ont/own3/own2dul.owl>
PREFIX skos: <http://www.w3.org/2004/02/skos/core>
PREFIX fn: <https://w3id.org/framester/framenet/tbox/>
PREFIX pb: <https://w3id.org/framester/pb/pbschema/>
PREFIX prep: <https://w3id.org/framester/prep/prepont/>
PREFIX vn: <https://w3id.org/framester/vn/schema/>
PREFIX wn: <https://w3id.org/framester/wn/wn30/schema/>
PREFIX framestercore: <https://w3id.org/framester/data/framestercore/> 
PREFIX fschema: <https://w3id.org/framester/schema/> 
PREFIX owl: <http://www.w3.org/2002/07/owl#>

		"""

		self.endpoint = 'http://etna.istc.cnr.it/framester2/sparql'

	def query(self,query_text):
		sparql = SPARQLWrapper(self.endpoint)
		sparql.setReturnFormat(JSON)

		sparql.setQuery(query_text)
		result = sparql.queryAndConvert()

		#print(result)
		#print(a)
		return result
