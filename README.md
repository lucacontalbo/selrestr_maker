# Selectional Restrictions Extractor

These Python scripts empirically determine the types of frame roles based on the knowledge graphs given in input and create new domain-specific axioms in OWLStar.  
The pipeline can be described as a multi-step approach:  

1. **Roles identification**: obtain `<frame_type, role, object_type>` triples, where `frame_type` and `object_type` are the types of the frame and the class covering `role` respectively.  
2. **Type estimation**: empirically estimate the probability of having a certain class as the type of the argument of frame roles  
3. **Type generalization**: obtain general types through WordNet mappings​  
4. **Ontology creation**: mapping of triples to OWLStar  

This module has been developed specifically for dealing with MUSICBO ontologies for the Polifonia project.

### Prerequisites

The scripts have been developed and tested with the following packages and their respective versions:

- python3: 3.9.7
- rdflib: 6.2.0
- SPARQLWrapper: 2.0.0 

## Usage

Run the following command  

``python3 selrestr_maker.py -d [KG_DIR]``  

where `[KG_DIR]` is the directory where the `.nq` files are stored.  

It is also possible to run a OWLStar to OWL parser:

``python3 owlstar2owl.py -i [INPUT_TTL] -o [OUTPUT_TTL]``

As of now, the tool is only able to produce .ttl files

