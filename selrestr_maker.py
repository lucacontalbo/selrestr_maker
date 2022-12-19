from parser import Parser
import argparse


argparser = argparse.ArgumentParser(prog="python3 frodo.py", description="Selectional Restriction Maker for frame roles")
argparser.add_argument("-d","--directory_path", action="store",help="N-triples directory path to calculate selectional restrictions. The directory must contain files named SENTENCE_n.nt containing the n-th graph", required=True)

args = argparser.parse_args()
#competency_question, outtype, save, simplify, auto = args.competency_question, args.outtype, args.save, args.simplify, args.auto
directory_path = args.directory_path

parser = Parser(directory_path)
print(parser.calculate_probabilities())
