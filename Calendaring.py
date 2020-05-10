import calendar
import datetime

import UnitsConstants

def eventCompare(e1, e2):
	# difference in hours
	diff = (e1['date'] - e2['date']).days * 24 * 60
	if e1.has_key('time-start') and e1['time-start'] is not None and e2.has_key('time-start') and e2['time-start'] is not None:
		# add difference between start times, in minutes
		diff += (e1['time-start'].hour*60 + e1['time-start'].minute) - (e2['time-start'].hour*60 + e2['time-start'].minute)
	elif e1.has_key('time-finish') and e1['time-finish'] is not None and e2.has_key('time-finish') and e2['time-finish'] is not None:
		# add difference between finish times, in minutes
		diff += (e1['time-finish'].hour*60 + e1['time-finish'].minute) - (e2['time-finish'].hour*60 + e2['time-finish'].minute)
	return diff

def eventsMerge(elist1, elist2):
	ptr1 = 0
	ptr2 = 0
	elistmerged = []
	while ptr1 < len(elist1) or ptr2 < len(elist2):
		if ptr1 == len(elist1):
			# elist1 is exhausted
			elistmerged += elist2[ptr2:]
			return elistmerged
		if ptr2 == len(elist2):
			# elist2 is exhausted
			elistmerged += elist1[ptr1:]
			return elistmerged
		if elist1[ptr1]['date'] <= elist2[ptr2]['date']:
			elistmerged.append(elist1[ptr1])
			ptr1 += 1
		else:
			elistmerged.append(elist2[ptr2])
			ptr2 += 1
	return elistmerged

def dateAdjust(event, date):
	wkday = calendar.weekday(date.year, date.month, date.day)
	offset = 0
	if event['occur-BAexcl'] == UnitsConstants.BABefore:
		delta = -1
	else:
		delta = 1
	while wkday in event['days-excluded']:
		date += datetime.timedelta(delta)
		offset += delta
		wkday = calendar.weekday(date.year, date.month, date.day)
	return date, offset

def dateNormalize(year, month, day):
	while month > 12:
		year += 1
		month -= 12
	daysInMonth = calendar.monthrange(year, month)[1]
	if daysInMonth is not None:
		if day < 1:
			month -= 1
			daysInMonth = calendar.monthrange(year, month)[1]
			day = daysInMonth + day
		elif day > daysInMonth:
			day -= daysInMonth
			month += 1
			daysInMonth = calendar.monthrange(year, month)[1]
	while month > 12:
		year += 1
		month -= 12
	return (year, month, day)

def occurrenceFindNext(event):
	datelcv = event['date']
	dateFrom = event['last_occur']
	current = False
	occurrenceCount = 0
	while not current:
		if datelcv > dateFrom:
			current = True
			continue
		#print("datelcv is %s and there are %s days in it." % (datelcv, calendar.monthrange(datelcv.year, datelcv.month)))
		daysInMonth = None
		yearNext = datelcv.year
		monthNext = datelcv.month
		dayNext = datelcv.day
		if event['recur-unit'] == UnitsConstants.RUYear:
			yearNext = datelcv.year + event['recur-every']
		elif event['recur-unit'] == UnitsConstants.RUMonth:
			monthNext = datelcv.month + event['recur-every']
		elif event['recur-unit'] == UnitsConstants.RUWeek or event['recur-unit'] == UnitsConstants.RUDay:
			if event['recur-unit'] == UnitsConstants.RUWeek:
				dayNext = event['recur-every'] * (datelcv.day+7)
			elif event['recur-unit'] == UnitsConstants.RUDay:
				dayNext = datelcv.day + event['recur-every']
		(yearNext, monthNext, dayNext) = dateNormalize(yearNext, monthNext, dayNext)
		datelcv = datetime.date(yearNext, monthNext, dayNext)
		occurrenceCount += 1
	return dateAdjust(event, datelcv), occurrenceCount
