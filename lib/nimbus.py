#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import sys
import time
import urllib2

"""
        curl -X GET "http://nnovbus.rnc52.ru/api/depots" -H "accept: application/json" -H "Authorization: Token 5eb103d95c204a87a27c74e4b8f6bae0"
        curl -X GET "http://nnovbus.rnc52.ru/api/depot/{depot_id}/stops" -H "accept: application/json" -H "Authorization: Token 5eb103d95c204a87a27c74e4b8f6bae0"       # Остановка
        curl -X GET "http://nnovbus.rnc52.ru/api/depot/{depot_id}/routes" -H "accept: application/json" -H "Authorization: Token 5eb103d95c204a87a27c74e4b8f6bae0"      # Маршруты
        curl -X GET "http://nnovbus.rnc52.ru/api/depot/{depot_id}/rides" -H "accept: application/json" -H "Authorization: Token 5eb103d95c204a87a27c74e4b8f6bae0"       # Поездки
        curl -X GET "http://nnovbus.rnc52.ru/api/depot/{depot_id}/patterns" -H "accept: application/json" -H "Authorization: Token 5eb103d95c204a87a27c74e4b8f6bae0"    # Шаблоны
"""

HOST =	r'http://nnovbus.rnc52.ru/api/'
TOKEN =	'Token 30e04452062e435a9b48740f19d56f45'


def _get_panel (depot_id = 128, stop_id = 20422, token = TOKEN):
	print """ Читать Маршруты АвтоПарка (Депо)	"""
	cmnd = 'depot/%s/stop/%s/panel' % (depot_id, stop_id)
	res = api_nimbus (cmnd, token)
#	for k in res.keys():	print "\t%s:\t" % k, res[k]
	print "Название остановки: %s \t%s" % (res['n'].encode('utf-8'), time.strftime("%T %d.%m.%Y", time.localtime (time.time())))
	panel = res.get('r')
	for r in panel:
	#	print r
		if r['tt']:
			print r['id'], r['idx'], r['n'], "\t%s\t%s\t%s" % (r['fs'].encode('utf-8'), r['ls'].encode('utf-8'), r['d'].encode('utf-8'))
			print "\ttt:\t", r['tt'], time.strftime("%T %d.%m.%Y", time.localtime (r['tt'][0]['pt']))
	#	for k in r.keys():	print "\t%s:\t" % k, r[k]
	#	print	"\t%d\t" % r['id'], r['n'], '\t',  r['d'], r['u']
	#	for t in r['tt']:			print	"\t", t
	print "\tВсего %d Маршрутов" % len(panel)


def get_panel (depot_id = 89, stop_id = 16038, token = TOKEN):
	cmnd = 'depot/%s/stop/%s/panel' % (depot_id, stop_id)
	res = u8api_nimbus (cmnd, token)
	print res.keys(), "\td: %s,\tn: %s" % (res.get('d'), res.get('n'))
	for r in res['r']:
		print r.keys()
		print r.get('fs')
		break


def get_routes (depot_id = 89):
	print """ Читать Маршруты АвтоПарка (Депо)	"""
	cmnd = 'depot/%s/routes' % depot_id
	res = api_nimbus (cmnd)
#	for k in res.keys():	print "\t%s:\t" % k, res[k]
	routes = res.get('routes')
	for route in routes:
		# for k in route.keys():	print "\t%s:\t" % k, route[k]
		print	"\t%d\t" % route['id'], route['n'], '\t',  route['d'], route['u']
		for t in route['tt']:
			print	"\t", t
	print "\tВсего %d Маршрутов" % len(routes)


def	get_stops (depot_id = 89, token = TOKEN):
	print   """ Читать остановки АвтоПарка (Депо)	depot_id:""", depot_id
	cmnd = 'depot/%s/stops' % depot_id
	res = api_nimbus (cmnd, token)
#	for k in res.keys():	print "\t%s:\t" % k, res[k]
	stops = res.get('stops')
	for stop in stops:
		print	"\t%d\t" % stop['id'], stop['n'].encode('utf-8'), '\t[ %s ]' % stop['d'].encode('utf-8'), '\t', stop['p']
	#	for k in stop.keys():	print "\t%s:\t" % k, stop[k]
	print	"\tВсего %d остановок" % len(stops)


def get_depots (token = TOKEN):
	print	""" Читать АвтоПарки (Депо)	"""
	res = u8api_nimbus ('depots', token)
	depots = res.get('depots')
	for depot in depots:
		print "%5d\t%s" % (depot['id'], depot['n']) # .encode('utf-8'))
		for k in depot.keys():
			if not depot[k]:	continue
			if k in ['n','id']:	continue
			if k == 'tp':
				# continue
				print "\t%s:\t[" % k
				for r in depot[k]:
					print '\t\t', r
				print	'\t\t]'
			else:
				if k in ['n','d']:
					print "\t%s:\t" % k, depot[k].encode('utf-8')
				else:	print "\t%s:\t" % k, depot[k]


def	api_nimbus (cmnd = 'user/token/check', token = 'Token 30e04452062e435a9b48740f19d56f45'):
	"""
	Выполнить запрос к NimBus
	:param cmnd:
	:param token:
	:return:   json
	boundary = '--apiNimBus' +str(int(random.random()*1e10))
	print	"api_nimbus", boundary
	print	url, token
	"""
	global res
	url = HOST + cmnd
	headers = {
		'Accept': 'application/json',
		'Authorization': token,
		'User-Agent': 'Mozilla 5.10'
	}
	try:
		req = urllib2.Request(url, headers=headers)
		res = urllib2.urlopen(req)
	except:
		pexcept ('api_nimbus URL: %s' % url)
	return	json.loads(res.read())


def	pexcept (mark = None, fexit = False):
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT:\t%s", mark, exc_type, exc_value
		if fexit:    sys.exit()

	
def pres (res):
	"""
	Конвертировать json из encode в UTF-8 (pdict (dict), plist (list))
	"""

	def pdict(d):
		dd = {}
		for k in d.keys():
			sk = k.encode('UTF-8')
			if type (d[k]) == dict:		dd[sk] = pdict (d[k])
			elif type (d[k]) == list:	dd[sk] = plist (d[k])
			elif isinstance(d[k], basestring):
				dd[sk] = d[k].encode('UTF-8')
			else:	dd[sk] = d[k]
		return dd

	def plist(l):
		ll = []
		for c in l:
			if type (c) == dict:	ll.append(pdict(c))
			elif type (c) == list:	ll.append(plist(c))
			elif isinstance(c, basestring):
				ll.append (c.encode('UTF-8'))
			else: ll.append(c)
		return ll
	
	if type (res) == dict:  	return	pdict (res)
	elif type (res) == list:	return	plist (res)
	###	pres	########################################################


def u8api_nimbus (cmnd = 'user/token/check', token = 'Token 30e04452062e435a9b48740f19d56f45'):
	return pres (api_nimbus (cmnd, token))


def get_stops (depot_id = 128):
	res = u8api_nimbus(cmnd = 'depot/%s/stops' % depot_id, token = 'Token 30e04452062e435a9b48740f19d56f45')
	print res.keys()
	print res['stops'][0].keys()
	for r in res['stops']:
		print "%s\t%s\t%s\t" % (r.get('id'), r.get('n'), r.get('d')), r.get('p')
		
		
def test ():
	res = api_nimbus ()
	for k in res.keys():
		print "\t%s:\t" % k, res[k]
	get_depots ()


if __name__ == "__main__":
	'''
	test ()
	get_stops ()
	get_routes ()
	get_depots ()
	_get_panel ()
	print get_panel(depot_id = 128, stop_id = 20422, token = TOKEN)
	print u8api_nimbus(cmnd = 'depot/128/stops', token = 'Token 30e04452062e435a9b48740f19d56f45')
	'''
	get_stops ()
	print pres(api_nimbus())
