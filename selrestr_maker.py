from parser import Parser
import argparse
import pprint

argparser = argparse.ArgumentParser(prog="python3 frodo.py", description="Selectional Restriction Maker for frame roles")
argparser.add_argument("-d","--directory_path", action="store",help="N-triples directory path to calculate selectional restrictions. The directory must contain files named SENTENCE_n.nt containing the n-th graph", required=True)

args = argparser.parse_args()
directory_path = args.directory_path

pp = pprint.PrettyPrinter()

parser = Parser(directory_path)

frequency_dict = parser.calculate_frequencies()
metrics_dict = parser.calculate_metrics(frequency_dict)

pp.pprint(metrics_dict)
