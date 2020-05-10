import datetime

from peafowlterm import *
import UnitsConstants

def unitRecognize(type, v):
	if type == 'recur-unit':
		if v == 'year':
			return UnitsConstants.RUYear
		if v == 'month':
			return UnitsConstants.RUMonth
		if v == 'week':
			return UnitsConstants.RUWeek
		if v == 'day':
			return UnitsConstants.RUDay
	if type == 'date':
		dt = datetime.datetime.strptime(v, "%Y-%m-%d")
		return datetime.date(dt.year, dt.month, dt.day)
	if type == 'time':
		if len(v) != 4:
			return None
		try:
			v = datetime.time(int(v[:2]), int(v[2:]))
		except Exception:
			return None
		return v
	if type == 'days':
		daysExcluded = []
		for d in range(len(v)):
			if v[d] == 'm':
				daysExcluded.append(UnitsConstants.DMon)
			elif v[d] == 't':
				daysExcluded.append(UnitsConstants.DTue)
			elif v[d] == 'w':
				daysExcluded.append(UnitsConstants.DWed)
			elif v[d] == 'r':
				daysExcluded.append(UnitsConstants.DThu)
			elif v[d] == 'f':
				daysExcluded.append(UnitsConstants.DFri)
			elif v[d] == 's':
				daysExcluded.append(UnitsConstants.DSat)
			elif v[d] == 'u':
				daysExcluded.append(UnitsConstants.DSun)
		if set(['m', 't', 'w', 'r', 'f', 's', 'u']) in daysExcluded:
			raise Exception, "All days of the week are excluded."
		return set(daysExcluded)
	if type == 'BA':
		if v == 'b':
			return UnitsConstants.BABefore
		if v == 'a':
			return UnitsConstants.BAAfter
		return None
	if type == 'yn':
		if v == 'y':
			return True
		if v == 'n':
			return False
	if type == 'color':
		if v == 'yel':
			return ColorScheme(ColorYellow, ColorYellow)
		if v == 'red':
			return ColorScheme(ColorRed, ColorYellow)
		return None
	if type == 'opt-integer':
		if v == '-':
			return None
		else:
			return int(v)
	raise Exception, "unitRecognize() fell through on type %s!" % type

def fileReadNextLine(f):
	line = f.readline().strip()
	while len(line) > 0 and line[0] == '#':
		line = f.readline().strip()
	if len(line) == 0:
		return None
	return line

def eventsGetLastRecur(fn):
	f = open(fn, 'r')
	eventsLast = []
	line = fileReadNextLine(f)
	while line is not None:
		lineE = line.split('\t')
		event = {}
		event['date'] = unitRecognize('date', lineE[0])
		event['notify-thresh'] = unitRecognize('opt-integer', lineE[1])
		event['name'] = lineE[2]
		eventsLast.append(event)
		line = fileReadNextLine(f)
	f.close()
	return eventsLast

def eventsGetRecur(fn):
	f = open(fn, 'r')
	events = []
	line = fileReadNextLine(f)
	while line is not None:
		lineE = line.split('\t')
		event = {}
		event['date'] = unitRecognize('date', lineE[0])
		event['recur-unit'] = unitRecognize('recur-unit', lineE[1])
		event['recur-every'] = int(lineE[2])
		event['days-excluded'] = unitRecognize('days', lineE[3])
		event['occur-BAexcl'] = unitRecognize('BA', lineE[4])
		event['show-ON'] = unitRecognize('yn', lineE[5])
		event['time-start'] = unitRecognize('time', lineE[6])
		event['time-finish'] = unitRecognize('time', lineE[7])
		event['name'] = lineE[8]
		event['recurring'] = True
		events.append(event)
		line = fileReadNextLine(f)
	f.close()
	return events

def eventsGetNonrecur(fn):
	f = open(fn, 'r')
	events = []
	line = fileReadNextLine(f)
	while line is not None:
		lineE = line.split('\t')
		event = {}
		event['date'] = unitRecognize('date', lineE[0])
		event['time-start'] = unitRecognize('time', lineE[1])
		event['time-finish'] = unitRecognize('time', lineE[2])
		event['color'] = unitRecognize('color', lineE[3])
		event['name'] = lineE[4]
		event['recurring'] = False
		events.append(event)
		line = fileReadNextLine(f)
	f.close()
	return events
