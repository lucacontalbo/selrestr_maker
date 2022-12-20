import os
import validators
from rdflib import URIRef

data_path = './musicbo_rdf_wikidata_specid/'

for file in os.listdir(data_path):
	if file.split('.')[-1] == 'py':
		continue
	with open(data_path+file,'r') as f:
		text = f.readlines()

	new_text = []
	for line in text:
		line_original = []
		line_parsed = []
		tmp = line.split('>')
		for i in range(len(tmp)):
			tmp2 = tmp[i].split('<')[-1]
			if i == 2 and '"' in tmp2:
				line_original.append(' '.join(tmp2.strip().split()[:-1]))
				line_original.append(' .\n')
			else:
				line_original.append(tmp2)

		for i in range(len(line_original)-1):
			if not validators.url(line_original[i]):
				print("{} --- {}".format(file,line_original[i]))
				line_parsed.append(line_original[i])
			else:
				line_parsed.append('<'+''.join(line_original[i].split())+'>')
		new_line_str = ' '.join(line_parsed)+' .'
		new_text.append(new_line_str)
	new_text_str = '\n'.join(new_text)

	with open(data_path+file,'w') as f:
		f.write(new_text_str)
