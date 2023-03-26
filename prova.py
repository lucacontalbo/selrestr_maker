import pickle
from pprint import PrettyPrinter

pp = PrettyPrinter()

with open('frequency_dict.pkl','rb') as reader:
	d = pickle.load(reader)

pp.pprint(d)
