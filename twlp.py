#!/usr/bin/python
# -*- coding: utf-8 -*-

import	os, sys, time
import	urllib
import	json
from	wtools import *
from	mobph_wlp import *
from	auto_wlp import *

def	send_post (sid, svc, spost):
	url = r"http://wialon.rnc52.ru/wialon/ajax.html"	# ?sid=%s&svc=%s" % (sid, svc)
	data =  {'sid': sid, 'svc': svc}
#	data['params'] = spost 
	data['params'] = mobph 
	enc_data = urllib.urlencode(data)
	print enc_data
	doc = urllib.urlopen(url, enc_data)
	print doc.info()
	print "getcode", doc.getcode()
	print doc.read()
	return
        res = json.load(urllib.urlopen(url, spost))
	ppp(res)

def	get_post (sid, svc, params = None):
	params = { "filterType":"type", "filterValue":["auto"], "includeType": True }
	url = r"http://wialon.rnc52.ru/wialon/ajax.html"
	data =  {'sid': sid, 'svc': svc}
	data['params'] = json.dumps(params)
	enc_data = urllib.urlencode(data)
#	doc = urllib.urlopen(url, enc_data)
	res = json.load(urllib.urlopen(url, enc_data))
	if type(res) == type([]):
		for r in res:
			ppp(r)
	else:
		ppp(res)


if __name__ == "__main__":
#	print auto_wlp
	auto_wlp['general']['n'] = "ГОС-123456"
	auto_wlp['afields'] = [{ 'id': 1, 'n': "inn", 'v': "520000000999" }]
#	print json.dumps(auto_wlp)
	sess = login()
	sid = sess['eid']
	get_post (sid, 'core/get_hw_types')
	send_post (sid, 'exchange/import_json', auto_wlp)	#json.dumps(auto_wlp))
	'''
	for root, dirs, files in os.walk(r'./wlp'):
		print root, dirs, files
		for fname in files:
			if fname[-4:] != '.wlp':	continue
			f = open(os.path.join(root, fname))
			st = f.readline()
			js = json.loads(st)
			ppp(js, fname)
	'''
