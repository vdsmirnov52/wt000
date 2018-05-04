#!/usr/bin/python
# -*- coding: utf-8 -*-

import	os, sys, time
import	urllib
import	json

LIBRARY_DIR = r"/home/smirnov/Wialon/lib/"
sys.path.insert(0, LIBRARY_DIR)
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
	res = request (sid, svss['search_items'], "'spec':{'itemsType':'avl_unit','propName':'*','propValueMask':'*','sortType':''},'force':1,'flags':-1,'from':0,'to':0")
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
				print '\t', item['uid'],
				'''
				if item.has_key('aflds') and item['aflds']:
					print "\taflds[",
					for k in item['aflds'].keys():
						sn = item['aflds'][k]['n'].encode('UTF-8')
						sv = item['aflds'][k]['v'].encode('UTF-8')
						print "'%s': '%s'," % (sn, sv) ,
					print "]",
				'''
				if item.has_key('flds') and item['flds']:
					prn_filds (item['flds'], 'flds')
				#	ppp(item['aflds'], 'aflds')
				if item.has_key('aflds') and item['aflds']:
					prn_filds (item['aflds'], 'aflds')
				if item.has_key('pflds') and item['pflds']:
					prn_filds (item['pflds'], 'pflds')
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

def	get_hw_types(sid, dbid = None):
	# type – значения: auto, tracker, mobile, soft 
	# "filterType":<text>,"filterValue":[<text>|<uint>], "includeType":<bool>}
	params = { "filterType":"type", "filterValue":["auto"], "includeType": True }
	for vtype in ["auto", "mobile", "soft"]:	#, "tracker"]:
		params["filterValue"] = [vtype]
		print ">>><%s>" % json.dumps(params)
		res = request (sid, svss['get_hw_types'], json.dumps(params)[1:-1])
		print "filterValue:", params["filterValue"]
		for r in res:
			if dbid:
				insert_into (dbid, 'hw_types', {'code': r['id'], 'class': vtype, 'tname': r['name']})
			else:
				print "\t%4d\t%s" % (r['id'], r['name'])
#		ppp(res)


sppp = '{"afields":[{"id":1,"n":"inn","v":"520000000123"}],"fields":[],"general":{"hw":"WiaTag","n":"TestPhone","ph":"","ph2":"","psw":"","uid":"864359028299999","uid2":""},"hwConfig":{"fullData":1,"hw":"WiaTag","params":{}},"icon":{"lib":"3","url":"Z_11.png"},"imgRot":"0","mu":0,"type":"avl_unit","version":"b4"}'
def	send_post (sid, svc):
	url = r"http://wialon.rnc52.ru/wialon/ajax.html?sid=%s&svc=%s" % (sid, svc)
        res = json.load(urllib.urlopen(url, sppp))
	ppp(res)

def	get_zones (sid, flags = 1 | 0x0040 | 0x0080 | 0x0100):	# zones_library
	print "#"*33, "zones_library"
	res = request (sid, svss['search_items'], "'spec':{'itemsType':'avl_resource','propName':'zones_library','propValueMask':'*','sortType':''},'force':1,'flags':%s,'from':0,'to':0" % flags)
	ppp(res)

def	get_user (sid, flags = 1 | 0x0040 | 0x0080 | 0x0100):
	print "#"*33, "get_user"
	res = request (sid, svss['search_items'], "'spec':{'itemsType':'user','propName':'sys_name','propValueMask':'*','sortType':'sys_user_creator'},'force':1,'flags':%s,'from':0,'to':0" % flags)
#	ppp(res)
	for r in res['items']:
#		if not r.has_key('pop'):
		if r['prp'].has_key('znsvlist'):
			znsvlist = json.loads(r['prp']['znsvlist'])
			if not znsvlist.has_key('e'):	continue
			print r['id'], r['nm'], r['crt']
			print '\tznsvlist',	znsvlist['e'].keys()	# r['prp']['znsvlist']
			for u in r['prp'].keys():
				if u[:4] == 'monu':
					ju = json.loads(r['prp'][u])
					if not ju:	continue
				#	print '\t', u, ju, len(ju)
					print '\t', u, r['prp'][u], len(ju)
		#	ppp (r['prp'], 'prp znsvlist')
		if r['flds']:	# r.has_key('flds'):
			prn_filds(r['flds'])
		if r.has_key('aflds') and  r['aflds']:
			prn_filds(r['aflds'])
		if r.has_key('pflds') and  r['pflds']:
			prn_filds(r['pflds'])
	print "="*33, "get_user"
	
def	prn_filds(flds, label = None, frmt = '\t%22s:\t%s'):
	if not flds:	return
	if label:
		print '\t%s' % label
	for j in  xrange(len(flds)):
		sj = str(1+j)
	#	print '\t\t', sj, flds[sj]['n'], flds[sj]['v']
		if not flds[sj]['v']:	continue
		print frmt % (flds[sj]['n'].encode('UTF-8'), flds[sj]['v'].encode('UTF-8'))
	
def	puser_prp (sess):
	sid = sess['eid']
	print "#"*33, '"user_namt": "%s"' % sess["user"]["nm"]
	print sess["user"]["prp"].keys()
	for u in sess["user"]["prp"].keys():
		if u == "monugv":
			print sess["user"]["prp"][u]
		if u == "monugr":
#			print sess["user"]["prp"][u]
			monugr = json.loads(sess["user"]["prp"][u])
#			print monugr
			for g in monugr.keys():
				if int(g) == 0:	continue
				print g ,">\t" ,
				res = request (sid, 'core/search_item', '"id":%s,"flags":1025' % g)
				if res.has_key('item'):
					snm = res['item']['nm'].encode('UTF-8')
					print "'%s'\tid: %d\t" % (snm, res['item']['id']) ,
					print monugr[g]
				else:	ppp(res, g)

auto_keys =	['rtd', 'cfl', 'uid', 'pfldsmax', 'uacl', 'cml_max', 'pos', 'bact', 'gd', 'prp', 'prms', 'ph2', 'ct', 'rfc', 'uid2', 'pflds', 'sens_max', 'sens', 'ph', 
		'lmsg', 'cls', 'afldsmax', 'flds', 'hw', 'cmds', 'aflds', 'cml', 'cnkb', 'psw', 'ugi', 'cnm', 'crt', 'uri', 'm', 'si', 'fldsmax', 'simax', 'cneh'],
prps = {
	'auto':	['solid_colors', 'track_speed', 'idrive', 'track_solid', 'label_color'],
	'user': ['show_log', 'fpnl', 'umap', 'ursstp', 'vsplit', 'used_hw',
	#	'city', 'radd', 'email', 
		'tz', 'dst', 'tracks_player_show_sensors', 'monuei', 'monugr', 'muf', 'monugv', 'tracks_player_show_params', 'us_addr_ordr', 
		'lastmsgl', 'mtya', 'us_addr_fmt', 'hpnl', 'usuei', 'mu_location', 'mu_loc_mode', 'mu_sens', 'cfmt', 'mf_use_sensors', 'monuv', 
		'hbacit', 'evt_flags', 'znsvlist', 'minimap_zoom_level', 'access_templates', 'language', 'monuexpg', 
	#	'umsp', 'autocomplete', 'mont', 'mon', 
		'mu_fast_report_tmpl', 'route_provider', 'mu_fast_track_ival']
	}

def	get_factory (sid, usrid, item_type = 'user', parid = None):
	if not (sid or usrid):	return

	hw_list = []
	columns = {}
	flags = -1
	res = request (sid, 'core/search_item', '"id":%d,"flags":%d' % (usrid, flags))
	if res.has_key('item'):
		ir = res['item']
	#	print  ir.keys()
		snm = res['item']['nm'].encode('UTF-8')
		wid = res['item']['id']
		print "'%s'\tid: %d\t" % (snm, res['item']['id']) ,
		if item_type == 'auto':
			columns['idts'] = wid
			columns['idus'] = parid
			columns['gosnum'] = snm 
			columns['idd'] = ir.get('uid')
			columns['devtype'] = ir.get('hw')
		#	columns[''] = 
			pos = ir.get('pos')
			idd = ir.get('uid')	#.encode('UTF-8')
			devtype =  ir.get('hw')
		#	print ir['prp'].keys()
			if pos:
				print "\t%s %s %s %s" % (pos['x'], pos['y'], pos['z'], time.strftime("%Y-%m-%d %T", time.localtime(pos['t'])))
			insert_into (DBID, 'wtsdesc', columns)	#cols, vals)
		if item_type != 'user':			return
		prp_ignore_keys = prps['user']
		print
		prp = ir.get('prp')
		if prp:
			columns['idus'] = wid 
			columns['uname'] = snm 
		#	columns[''] = 
		#	print '	prp:', prp.keys()
			for k in prp.keys():
				if k in prp_ignore_keys:	continue
				v =  prp.get(k)
				if v:
					print '\t%s\t' %k, prp.get(k)
				if k == 'email' and v:	columns['email'] = v
				if k == 'monu'and len(v) > 4:
					autos = v[2:-2].split('","')
					for sa in autos:
						if sa and not sa.isdigit():	continue
						print int(sa), '>\t', 
						get_factory (sid, int(sa), 'auto', wid)
					sv = v.encode('UTF-8')
					columns['monu'] = sv.replace('"', '')
			insert_into (DBID, 'wuser', columns)
	#	print 'hm	', ir.get('hm')
	#	print 'mapps	', ir.get('mapps')
	else:	ppp(res, usrid)

import	dbtools
#	INSERT INTO wusert (wid, uname, email, muou) VALUES (357, 'Агрофирма РУСЬ', 'siluyan71@mail.ru', '[359,360,361,362,365,367,368,369,370]');

def	insert_into (dbid, tab, columns):
	cols = []
	vals = []
	for k in columns:
	#	print k, columns[k], type(columns[k])
		if not columns[k]:	continue
		cols.append(k)
		if type(columns[k]) == unicode:
			vals.append("%s" % columns[k].encode('UTF-8'))
		elif type(columns[k]) == int:
			vals.append("%d" % columns[k])
		else:	vals.append("%s" % str(columns[k]))
	query = "INSERT INTO %s (%s) VALUES('%s')" % (tab, ', '.join(cols), "', '".join(vals))
	print query
#	return
	if dbid:	dbid.qexecute(query)

if __name__ == "__main__":
	usr2token = init_conf ()
	print ''
#	sess = {}
	sess = login(usr2token['wialon'])
#	sess = login(usr2token['V.Smirnov'])
#	puser_prp (sess)

	sid = sess['eid']
	DBID = dbtools.dbtools('host=127.0.0.1 dbname=test port=5432 user=smirnov')
	for usrid in [357, 373, 436]:	print	get_factory (sid, usrid)
	'''
	get_hw_types(sid, DBID)
#	get_factory (sid, 357)
	'''
#	for usrid in [357, 373, 436, 166, 71, 617, 453]:	print	get_factory (sid, usrid)
#	get_autos (sid)
#	get_user (sid, -1)
#	get_zones (sid)

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
