#!/usr/bin/env python3

import os
import sys
import json
import argparse

try:
  from jsonDiffGui import App
  cli = False
except ImportError:
  cli = True

from jsonComparison import Comparison

def main(args):
  comparison = Comparison()
  try:
    fn = args.jsonFile1
    print('Reading: {}'.format(fn))
    comparison.jsonData['1'] = json.load(open(fn))
  except FileNotFoundError:
    print('Can not find: {}'.format(sys.arg[v]))
    sys.exit(1)
  except json.decoder.JSONDecodeError as e:
    print('Invalid JSON: {}'.format(e))
    sys.exit(1)

  try:
    fn = args.jsonFile2
    print('Reading: {}'.format(fn))
    comparison.jsonData['2'] = json.load(open(fn))
  except FileNotFoundError:
    print('Can not find: {}'.format(sys.arg[v]))
    sys.exit(1)
  except json.decoder.JSONDecodeError as e:
    print('Invalid JSON: {}'.format(e))
    sys.exit(1)

  comparison.compare()
  for path in comparison.mismatch:
    print(comparison.mismatch[path]['error'])
  

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Show differences between 2 JSON files with GUI when available')
  parser.add_argument('jsonFile1', nargs='?', action='store', default=None, help='JSON input file 1')
  parser.add_argument('jsonFile2', nargs='?', action='store', default=None, help='JSON input file 2')
  parser.add_argument('--cli', action='store_true', help='force cli handling')  
  args = parser.parse_args()    
  print(cli, args)                
  if cli or args.cli:
    if args.jsonFile1 is None or args.jsonFile2 is None:
      parser.print_usage()
      sys.exit(1)
    main(args)
  else:
    app = App(args, Comparison)
    app.run()

