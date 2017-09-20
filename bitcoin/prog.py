import argparse

parser = argparse.ArgumentParser(description='Read through numbers')

#parser.add_argument('-s', '--start', dest='start_block', type=int,
#                    help='What block to start indexing. If nothing is provided, the latest block indexed will be used.')

#parser.add_argument('-e', '--end', dest='end_block', type=int,
#                    help='What block to finish indexing. If nothing is provided, the latest one will be used.')

#parser.add_argument("-v", "--verbose", help="increase output verbosity",
#                    action="store_true")

parser.add_argument("-s", "--start", dest='start_block', help="display a square of a given number", action="store_true")

args = parser.parse_args()
print(args.start_block)
