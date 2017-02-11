#!/usr/bin/python
# -*- coding: utf-8 -*-

import	os, sys, time
import	urllib
import	json
from	wtools import *

def	request (sid, svc, params = None):
	if not params:	params = ''
	url = r"http://wialon.rnc52.ru/wialon/ajax.html?sid=%s&svc=%s&params={%s}" % (sid, svc, params)
#	try:
	res = json.load(urllib.urlopen(url))
	if not res:	print url
#	elif type(res) == list:
#		print res
	elif type(res) == dict and res.has_key('error'):
		print url
		perror (res['error'])
	return res
#	except:
#		print "except: request", url

def	rPOST():
	params = urllib.url_encode({'spam': 1, 'eggs': 2, 'text': "ТЕКСТ TEXT"})
	f = urllib.urlopen(url, params)
	print f.read()

def	get_autos (sid):
	""" найти все машины	"""
#	res = request (sid, svss['search_items'], "'spec':{'itemsType':'avl_unit','propName':'*','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':1033,'from':0,'to':0")
	res = request (sid, svss['search_items'], "'spec':{'itemsType':'avl_unit','propName':'*','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':-1,'from':0,'to':0")
	if res:
	#	ppp(res)
	#	return
		if res.has_key('error'):
			print "error:", res['error']
		elif res.has_key('items') and res['items']:
	#		ppp(res['items'])
	#		return
			print "Len res['items']", len(res['items'])
			j = 0
			for item in  res['items']:
				j += 1
				print "%6d" % item['id'],
				print item['nm'].encode('UTF-8'), ppos(item['pos']),
				if item['pos']:
					tpos = item['pos']['t']
				else:	tpos = None
				if item.has_key('lmsg'):
					print plmsg(item['lmsg'], tpos),
				if item.has_key('aflds') and item['aflds']:
					print "\taflds[",
					for k in item['aflds'].keys():
					#	print item['aflds'][k] ,
						print "%s: '%s'" % (item['aflds'][k]['n'], item['aflds'][k]['v']) ,
					print "]",
				#	ppp(item['aflds'], 'aflds')
				print ""
		#		ppp (item, "%3d" %j)
		elif res.has_key('afields') and res['afields']:
				print res['afields']
		else:
			ppp(res)
	else:	print res

def	ppos (pos):
	if not pos:	return "\tpos None"
	if pos.has_key('t'):
		return	"\tX:%10.6f, Y:%10.6f %s" % (pos['x'], pos['y'], time.strftime("%Y-%m-%d %T", time.localtime(pos['t'])))
	else:	return  "\tX:%10.6f, Y:%10.6f" % (pos['x'], pos['y'])

def	plmsg (lmsg, tpos):
	if not lmsg:		return "\tlmsg None"
	if tpos == lmsg['t']:	return ""
	if lmsg.has_key('pos'):
		return  "\tlmsg %s %s" % (time.strftime("%Y-%m-%d %T", time.localtime(lmsg['t'])), ppos(lmsg['pos']))
	else:	return  "\tlmsg %s" % time.strftime("%Y-%m-%d %T", time.localtime(lmsg['t']))
	ppp (lmsg)

def	create_unit (sid, name = 'ZZZ_1234', creatorId = 31, hwTypeId = 14):
	# https://sdk.wialon.com/wiki/ru/local/remoteapi1604/codesamples/update_item#udalenie_obekta
	params={
		"creatorId": creatorId,
		"name": name,
		"hwTypeId": "%d" % 9,	#hwTypeId,
		"dataFlags":257
	}
#	help (json)
#	http://wialon.rnc52.ru/wialon/ajax.html?svc=core/create_unit&params={%22creatorId%22:31,%22name%22:%22test_sdk%22,%22hwTypeId%22:%229%22,%22dataFlags%22:257}&sid=002b3269fd1e9468b8c47f0c6443fdb2
	sprm = json.dumps(params)
	print type(sprm), urllib.quote(sprm[1:-1].replace(' ', ''), ':,')
	print "[%s]" % json.dumps(params)
#	res = request (sid, svss['create_unit'], urllib.quote(sprm[1:-1].replace(' ', ''), ':,'))	#urllib.urlencode(sprm[1:-1]))
	res = request (sid, svss['create_unit'], "%22creatorId%22:31,%22name%22:%22test_QQQ%22,%22hwTypeId%22:%229%22,%22dataFlags%22:257")
	ppp(res)
	
svss = {
	'curr_account': 'core/get_account_data',	# Информация о текущей учетной записи type {1|2} ( минимальная | детальная )
	'get_hw_types':	'core/get_hw_types',		# можно получить все доступные типы оборудования
	'search_items': 'core/search_items',		# Поиск объектов (элементов) по критериям
	'create_unit':	'core/create_unit',		# Создать объект (элемент)
	'delete_item':	'item/delete_item',		# Удалить объект (элемент)
	'export_wlp':	'exchange/export_json',
	'import_wlp':	'exchange/import_json',
	'token_list':	'token/list',
	}

def	get_hw_types(sid):
	# type – значения: auto, tracker, mobile, soft 
	# "filterType":<text>,"filterValue":[<text>|<uint>], "includeType":<bool>}
	params = { "filterType":"type", "filterValue":["auto"], "includeType": True }
	for vtype in ["auto", "mobile", "soft"]:	# "tracker"]:
		params["filterValue"] = [vtype]
		print ">>><%s>" % json.dumps(params)
		res = request (sid, svss['get_hw_types'], json.dumps(params)[1:-1])
		print "filterValue:", params["filterValue"]
		for r in res:
			print "\t%4d\t%s" % (r['id'], r['name'])
#		ppp(res)


sppp = '{"afields":[{"id":1,"n":"inn","v":"520000000123"}],"fields":[],"general":{"hw":"WiaTag","n":"TestPhone","ph":"","ph2":"","psw":"","uid":"864359028299999","uid2":""},"hwConfig":{"fullData":1,"hw":"WiaTag","params":{}},"icon":{"lib":"3","url":"Z_11.png"},"imgRot":"0","mu":0,"type":"avl_unit","version":"b4"}'
def	send_post (sid, svc):
	url = r"http://wialon.rnc52.ru/wialon/ajax.html?sid=%s&svc=%s" % (sid, svc)
        res = json.load(urllib.urlopen(url, sppp))
	ppp(res)

def	get_user (sid, flags = 1 | 0x0040 | 0x0080 | 0x0100):
	print "#"*33, "get_user"
	res = request (sid, svss['search_items'], "'spec':{'itemsType':'user','propName':'sys_name','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':%s,'from':0,'to':0" % flags)
	ppp(res)
	
if __name__ == "__main__":
#	sess = {}
#	sess = login(usr2token['wialon'])
	sess = login(usr2token['V.Smirnov'])
	sid = sess['eid']
	get_autos (sid)
#	get_hw_types(sid)
#	get_user (sid)
	print "#"*33, '"user_namt": "%s"' % sess["user"]["nm"]
	for u in sess["user"]["prp"].keys():
		if u == "monugv":
			print sess["user"]["prp"][u]
		if u == "monugr":
#			print sess["user"]["prp"][u]
			monugr = json.loads(sess["user"]["prp"][u])
#			print monugr
			for g in monugr.keys():
				print g, ">\t", monugr[g]
				if int(g) == 0:	continue
				res = request (sid, 'core/search_item', '"id":%s,"flags":1025' % g)
				if res.has_key('item'):
				#	ppp(res['item'], g)
					print "%s >\t nm:'%s', id: %d" % (g, res['item']['nm'], res['item']['id'])
				else:	ppp(res, g)

	'''
	UUU = 'http://wialon.rnc52.ru/wialon/ajax.html?svc=core/create_unit&params={"creatorId":31,"name":"test_LLL","hwTypeId":"9","dataFlags":257}&sid=' + sid
	print "SID", UUU
	res = json.load(urllib.urlopen(UUU))
	ppp(res, "RES")
	create_unit (sid) ### ???
	send_post (sid, svss['import_wlp'])
#	request (sid, svss['import_wlp'], params = sppp[1:-1])
	try:
		for uname in usr2token.keys():
			print "#"*33, uname
			sess = login()
			sid = sess['eid']
			break
		#	get_autos (sid)
			get_user (sid)
			logout(sid)
		get_hw_types(sid)
		res = create_unit (sid, 'ZZZ', 17)
		ppp(res)
	except:
		print 'except:'
		if sess.has_key('error'):
			perror(sess['error'])
		else:	print sess
	'''	
	'''
	if sess and sess.has_key('eid'):
		sid = sess['eid']
#		ppp(sess)
		print "sid:", sid
		print "sess['user']['id']", sess['user']['id']
	#	res = request (sid, svss['token_list'], "'userId': 17")
		# найти всех пользователей 
		flags = 1 | 0x0040 | 0x0080 | 0x0100	# | 0x0200 # уведомления пользователя
	#	res = request (sid, svss['search_items'], "'spec':{'itemsType':'user','propName':'sys_name','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':%s,'from':0,'to':0" % flags)
		res = request (sid, svss['search_items'], "'spec':{'itemsType':'user','propName':'sys_name','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':%s,'from':0,'to':0" % flags)
		ppp(res)
		# найти все машины
	#	get_autos ()
		res = request (sid, svss['search_items'], "'spec':{'itemsType':'avl_unit','propName':'*','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':1025,'from':0,'to':0")
	#	print res
		ppp(res['items'], 'items')
		
		if sess['user']['prp']['monu']:
		#	print sess['user']['prp']['monu']
			smonu = json.loads(sess['user']['prp']['monu'])
			monu = []
			for s in smonu:
				monu.append(int(s))
				print s,
			print "<", monu, len (monu)
		if sess['user']['prp']['monugr']:
			o = json.loads(sess['user']['prp']['monugr'])
			for k in o.keys():
				print k, len (o[k]), ":\t",
				if o[k]:
					for s in o[k]:
						print s,
						if s in monu:
							print "t,",
						else:	print "f,",
				print ""
#		account = request (sid, svss['curr_account'], "'type': 2")
		logout(sid)
	else:
		ppp(sess)
	'''
