#!/bin/env python

import datetime
import sys

import peafowltermutil.metadata
from peafowlterm import *

import Calendaring
import FileReader

def stringifyEventName(name, ON=None):
	if ON is None:
		return name
	else:
		return "%s #%d" % (name, ON)

def getDaysFromNow(date):
	return (date - datetime.date.today()).days

def stringifyDaysFromNow(numdays):
	if numdays == 0:
		s = "today"
	elif numdays == 1:
		s = "tomorrow"
	elif numdays == -1:
		s = "yesterday"
	elif numdays < -1:
		s = "%2d days ago" % (numdays*(-1))
	else:
		s = "in %3d days" % numdays
	return s

def stringifyEventTime(event):
	format = "%H:%M"
	if event['time-start'] is None and event['time-finish'] is None:
		return ""
	str = " "
	if event['time-start'] is not None:
		if event['time-finish'] is not None:
			str += "%s-%s" % (event['time-start'].strftime(format), event['time-finish'].strftime(format))
		else:
			str += "@ %s" % event['time-start'].strftime(format)
	else:
		str += "until %s" % event['time-finish'].strftime(format)
	return str

def stringifyOffset(offset):
	if offset == 0:
		return ""
	if offset < 0:
		return " (-%dd)" % offset
	return " (+%dd)" % offset

def checkNotifyThresh(events):
	proximate = []
	for e in events:
		if not e.has_key('notify-thresh') or e['notify-thresh'] is None:
			continue
		daysfromnow = getDaysFromNow(e['date'])
		if daysfromnow >= 0 and e['notify-thresh'] >= daysfromnow:
			proximate.append((daysfromnow, e))
	if len(proximate) == 0:
		return
	print("== Proximity Warnings ==")
	counter = 0
	for (daysfromnow, e) in proximate:
		counter += 1
		print("%2d) %s occurs %s" % (counter, e['name'], stringifyDaysFromNow(daysfromnow)))
	print("")

# start here

if peafowltermutil.metadata.version.minor != 1:
	sys.stderr.write("Dependency problem: This program requires PeafowlTerm major version 1.\n")
	sys.exit(1)

if len(sys.argv) < 4 or len(sys.argv) > 5:
	sys.stderr.write("Syntax: %s <input-recur> <input-nonrecur> [<days-span>]\n" % sys.argv[0])
	sys.exit(2)

input_recur_fn = sys.argv[1]
input_recurlast_fn = sys.argv[2]
input_nonrecur_fn = sys.argv[3]
if len(sys.argv) == 5:
	days_span = int(sys.argv[4])
	deadline = datetime.date.today() + datetime.timedelta(days_span)
else:
	deadline = None

events_recur = FileReader.eventsGetRecur(input_recur_fn)
events_last_recur = FileReader.eventsGetLastRecur(input_recurlast_fn)
# Check if all events_last_recur are accounted for, and assign last_occur dates to events_recur
for e1 in events_last_recur:
	name = e1['name']
	found = False
	for e2 in events_recur:
		if name == e2['name']:
			e2['last_occur'] = e1['date']
			e2['notify-thresh'] = e1['notify-thresh']
			found = True
	if not found:
		sys.stderr.write("Error: Could not find a recurrent event for '%s'.\n" % name)

for e in events_recur:
	if not e.has_key('last_occur'):
		e['last_occur'] = datetime.date.today()

for e in events_recur:
	((e['date'], e['occur-offset']), e['ON']) = Calendaring.occurrenceFindNext(e)

events_nonrecur = FileReader.eventsGetNonrecur(input_nonrecur_fn)

events = Calendaring.eventsMerge(events_recur, events_nonrecur)

events.sort(Calendaring.eventCompare)

checkNotifyThresh(events)

print("== Upcoming Events ==")
for e in events:
	if deadline is not None and e['date'] > deadline:
		continue
	if e['recurring']:
		line = ColoredText(ColoredString("%s, %-12s%-12s  %s\n" % (
			e['date'].strftime("%a %b %d"),
			("%s," % stringifyDaysFromNow(getDaysFromNow(e['date']))),
			stringifyEventTime(e),
			#stringifyOffset(e['occur-offset']),
			stringifyEventName(e['name'], e['ON'] if e['show-ON'] else None)
		)))
	else:
		line = ColoredText(ColoredString("%s, %-12s%-12s  " % (
				e['date'].strftime("%a %b %d"),
				("%s," % stringifyDaysFromNow(getDaysFromNow(e['date']))),
				stringifyEventTime(e))
			))
		line.append(ColoredString(stringifyEventName(e['name']+"\n"), e['color'] if e.has_key('color') and e['color'] is not None else None))
	line.display()
