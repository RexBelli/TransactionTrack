#!/usr/bin/env python3

# Author: Rex Belli
# Date: 9/13/2017

# Read in information about expenses, and graph running totals

from yaml import load
import sys
import argparse
import datetime
from dateutil import parser

ap = argparse.ArgumentParser()
ap.add_argument("--start")
ap.add_argument("--end")
ap.add_argument("--length")
ap.add_argument("file_in")
args = ap.parse_args()

start = datetime.datetime.now().date()
if args.start: start = parser.parse(args.start).date()
length = 180
if args.length: length = int(args.length)
end = start + datetime.timedelta(days=length)
if args.end: end = parser.parse(args.end).date()
if not args.file_in:
	print('Please specify input file')
	sys.exit()
#print(start)
#print(end)

#import trasactions from file
d = {}
with open(args.file_in,'r') as s:
	d = load(s)
initial = d['initial']
monthly = d['monthly']
once = d['once']

accounts = {}
for i in initial:
	accounts[i] = {}
print(accounts)
print(initial)
#run through transactions to build running total

#graph
