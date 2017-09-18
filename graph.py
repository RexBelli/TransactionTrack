#!/usr/bin/env python3

# Author: Rex Belli
# Date: 9/13/2017

# Read in information about expenses, and graph running totals

import pprint
pp = pprint.PrettyPrinter(indent=4)

from yaml import load
import sys
import argparse
import datetime
from dateutil import parser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
#initial = d['initial']
#monthly = d['monthly']
#once = d['once']

account_names = [i for i in d['initial']]

# delta will contain the change in value each day for each account
delta = {}
# transactions will contain all transactions
transactions = {}
# get first and last dates as specified in the config file
first_date = start
last_date = end
temp_dates = []
# pull all date fields from yaml and set first_date, last_date
for a in account_names:
	date = parser.parse(d['initial'][a]['date']).date()
	if date < first_date: first_date = date
	if date > last_date: last_date = date
for o in d['once']:
	date = parser.parse(d['once'][o]['date']).date()
	if date < first_date: first_date = date
	if date > last_date: last_date = date
for t in d['transfers']:
	date = parser.parse(d['transfers'][t]['date']).date()
	if date < first_date: first_date = date
	if date > last_date: last_date = date
#---------------------------------------------------------------------
#run through transactions to build running total

# zero out the delta dict
for i in d['initial']:
	day = first_date
	while day < last_date:
		if i not in delta: delta[i] = {}
		delta[i][str(day)] = 0
		day = day + datetime.timedelta(days=1)

#---
# generate list of all transactions
day = first_date
while day < last_date:
	for m in d['monthly']:
		account_name = d['monthly'][m]['account']
		trans_day = d['monthly'][m]['day']
		default = d['monthly'][m]['default']
		if day.day == trans_day:
			if account_name not in transactions: transactions[account_name] = {}
			if m not in transactions[account_name]: transactions[account_name][m] = {}
			transactions[account_name][m][str(day)] = default
	day = day + datetime.timedelta(days=1)
#pp.pprint(transactions)
#---
# put transfers into transactions
for t in d['transfers']:
	account_from = d['transfers'][t]['from']
	account_to = d['transfers'][t]['to']
	date = parser.parse(d['transfers'][t]['date']).date()
	amount = d['transfers'][t]['amount']
	
	transactions[account_from][t] = {}
	transactions[account_to][t] = {}
	
	transactions[account_from][t][str(date)] = amount * -1
	transactions[account_to][t][str(date)] = amount
#pp.pprint(transactions)


#pp.pprint(d['monthly_overrides']) 
#---
# change defaults to overridden valuies
for m in d['monthly_overrides']:
	for o in d['monthly_overrides'][m]:
		date = parser.parse(m).replace(day=d['monthly'][o]['day']).date()
		if date < first_date or date > last_date: continue
		amount = d['monthly_overrides'][m][o]
		account_name = d['monthly'][o]['account']
		transactions[account_name][o][str(date)] = amount
#pp.pprint(transactions)

#---
# populate delta for each day

#pp.pprint(delta)
for account_name in transactions:
	for t in transactions[account_name]:
		for date in transactions[account_name][t]:
			delta[account_name][date] += transactions[account_name][t][date]
#pp.pprint(delta)

#---
# calculate running total
day = first_date
amounts = {}
while day < last_date:
	for account_name in d['initial']:
		if account_name not in amounts: amounts[account_name] = {}
		if day == first_date: amounts[account_name][str(day-datetime.timedelta(days=1))] = 0
		amounts[account_name][str(day)] = amounts[account_name][str(day-datetime.timedelta(days=1))] + delta[account_name][str(day)]
	day = day + datetime.timedelta(days=1)
#pp.pprint(amounts)


#--- 
# use initial amount in each account to calculate difference, and fix the running total
offset = {}
for account_name in d['initial']:
	date = str(parser.parse(d['initial'][account_name]['date']).date())
	amount = d['initial'][account_name]['amount']

	offset[account_name] = amount - amounts[account_name][date]

for account_name in amounts:
	for date in amounts[account_name]:
		amounts[account_name][date] += offset[account_name]
#pp.pprint(amounts)

#---
# run through amounts, check for any with below zero value
day = start
while day < end:
	prev_day = day - datetime.timedelta(days=1)
	for account_name in amounts:
		if amounts[account_name][str(day)] < 0:
			if amounts[account_name][str(prev_day)] >= 0:
				print("Warning: "+account_name+" goes negative on "+str(day)+".")
	day = day + datetime.timedelta(days=1)


#---
# create temporary variable to hold array of tuples (date, amount) and sort them based on date
data = {}
for account_name in amounts:
	data[account_name] = []
	for date in amounts[account_name]:
		data[account_name].append((date,amounts[account_name][date]))
for account_name in data:
	data[account_name] = sorted(data[account_name], key=lambda x: x[0])

#---
# remove valies from data that don't fall within start and end (our graphable range)

#---
# create arrays that will be graphed: dates vs values
dates = []
values = {}
dates_full = False
for account_name in data:
	values[account_name] = []
	for t in data[account_name]:
		if not dates_full: dates.append(parser.parse(t[0]))
		values[account_name].append(t[1])
	dates_full = True
values['total'] = []
for i in range(len(dates)):
	temp_total = 0
	for account_name in data:
		temp_total += values[account_name][i]
	values['total'].append(temp_total)

#---
# Graph each account and total
fig, ax = plt.subplots()

for account_name in values: ax.plot(dates,values[account_name], label=account_name)

plt.legend(loc=1)#bbox_to_anchor=(1.05,1), loc=2, borderaxespad=0)
plt.axhline(0, color='black')

fig.autofmt_xdate()
myFmt = mdates.DateFormatter('%Y-%m-%d')
ax.xaxis.set_major_formatter(myFmt)
plt.show()




