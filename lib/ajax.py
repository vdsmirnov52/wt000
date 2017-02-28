#!/usr/bin/python
# -*- coding: utf-8 -*-

import  cgi, os, sys
import	psycopg2, psycopg2.extensions
import	time
import	json

#print "Content-Type: text/html; charset=utf-8\n"

LIBRARY_DIR = r"/home/smirnov/Wialon/lib/"		# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

WHOST =	r"http://wialon.rnc52.ru/wialon/"

def	out_json(obj, **keywords):
	if keywords and keywords.has_key('iddom'):
		print "~%s|" % keywords['iddom']
	else:	print "~log|"
	if type(obj) == list:
		print "<pre>List:"
		for l in obj:		print l
		print "</pre>"
	elif type(obj) == dict:
		print "<pre>Dict:"
		for k in obj.keys():	print k, "=>\t", obj[k]
		print "</pre>"
	else:
		print "Type", type(obj)

def	select_hw_types (obj, sname = 'hwTypeId', iddom = '_hwTypeId'):
	print "~%s|" % iddom
	print "<select id='%s' class='ssel' name='%s' ><option value=''>  </option>" % (sname, sname)
	for dl in obj:
		if dl.has_key('hw_category'):
			name = "%s (%s)" % (dl['name'], dl['hw_category'])
		else:	name = dl['name']
		print "<option value='%s'> %s </option>" % (dl['id'], name)
	print "</select>"

def	get_hw_types (request):
	if request.has_key('wsid') and request['wsid']:
		sid = request['wsid']
		import	twlp
		vtype = ["auto", "mobile", "soft", "tracker"]
		data ={'sid': sid, 'svc': 'core/get_hw_types', 'params': { "filterType":"type", "filterValue":["auto", "mobile", "soft", "tracker"], "includeType": True}}
		fres, sres = twlp.requesr(data)		# sres = twlp.send_post(data)
		if fres:	select_hw_types(sres)
		else:	print "~error|", sres
	else:	print "~error|", request

def	select_users (obj, **keywords):
	""" Вывод <select id nm on... ... в iddom
		keywords [ iddom ='DOM', sid='Id', snm='Name', on='onchange="..."' ]
	"""
	print "~log| select_users", keywords
	out_json (obj)
	if keywords.has_key('iddom'):
		print "~%s|" % keywords['iddom']
	else:	print "~log|"
	sid = snm = son =''
	if keywords.has_key('sid'):	sid = keywords['sid']
	if keywords.has_key('snm'):	snm = keywords['snm']
	if not snm:	snm = sid
	print "<select id='%s' class='ssel' name='%s' %s ><option value=''>  </option>" % (sid, snm, son)
	for dl in obj:
		if dl.has_key(keywords['key']) and dl.has_key(keywords['val']):
			print "<option value='%s'> %s </option>" % (dl[keywords['key']], dl[keywords['val']].encode("UTF-8"))
	print "</select>"

def	get_items (request, itype, func = out_json, **keywords):
	itemsType = ['user', 'avl_unit', 'avl_unit_group', 'avl_resource', 'avl_retranslator']
	if itype not in itemsType:
		print "~error| get_items. Неизвестный itemsType: '%s'" % itype
		return
	if request.has_key('wsid') and request['wsid']:
		sid = request['wsid']
		import	twlp
		# svss['search_items'], "'spec':{'itemsType':'avl_unit','propName':'*','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':1025,'from':0,'to':0")
		data = {'sid': sid, 'svc': 'core/search_items', 'params':{'spec':{'itemsType':itype,'propName':'*','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':1025,'from':0,'to':0}}
		fres, sres = twlp.requesr(data)
		if fres:
			if itype == 'user':
				select_users(sres['items'], key = 'id', val = 'nm', iddom = '_creatorId', sid = 'creatorId')	#, keywords)
			else:	func(sres)
		else:	print "~error|", sres
	#	out_json(sres)
	else:	print "~error|", request
"""
step == 1
item =>	{'uacl': 880265986047, 'uid2': '', 'uid': '', 'hw': 29, 'psw': '', 'm': 0, 'ph2': '', 'ph': '', 'cls': 2, 'id': 250, 'nm': 'EGTS-27085418'}
flags =>	257
step == 2	###	"svc":"core/update_data_flags"
[{'i': 250, 'd': {
	'rtd': {'minTripTime': 60, 'minSat': 2, 'minStayTime': 300, 'maxMessagesDistance': 10000, 'gpsCorrection': 1, 'minMovingSpeed': 1, 'minTripDistance': 100, 'type': 1}, 
	'cfl': 0, 'uid': '', 'pfldsmax': 0, 'uacl': 880265986047, 'cml_max': -1, 'pos': None, 'bact': 18, 'gd': 'f9f1f499d74ed31ebda610ba40dc1568', 
	'prp': {}, 
	'prms': None, 'ph2': '', 'id': 250, 'ct': 1488271082, 
	'rfc': {'fuelConsRates': {'consSummer': 10, 'winterMonthFrom': 11, 'consWinter': 12, 'winterDayFrom': 1, 'winterDayTo': 30, 'winterMonthTo': 1}, 
		'fuelLevelParams': {'fillingsJoinInterval': 300, 'minFillingVolume': 20, 'filterQuality': 0, 'theftsJoinInterval': 300, 'minTheftTimeout': 0, 'minTheftVolume': 10, 'flags': 1, 'ignoreStayTimeout': 20, 'extraFillingTimeout': 0}, 
		'fuelConsMath': {'idling': 2, 'suburban': 7, 'loadCoef': 1.3, 'urban': 10}, 
		'fuelConsImpulse': {'maxImpulses': 0, 'skipZero': 0}, '
		calcTypes': 0}, 'uid2': '', 'nm': 'EGTS-27085418', 
		'pflds': {}, 
		'sens_max': -1, 'sens': {}, 
		'ph': '', 'lmsg': None, 'cls': 2, 'afldsmax': 0, 
		'flds': {}, 
		'hw': 29, 'cmds': [], 'aflds': {}, 'cml': {}, 
		'cnkb': 0, 'psw': '', 'ugi': 0, 'cnm': 0, 'crt': 17, 'uri': '/avl_library_image/3/0/library/unit/default.png', 'm': 0, 
		'si': {}, 
		'fldsmax': 0, 'simax': 0, 'cneh': 0}, 
	'f': 9007199254740991}] 
[{u'hwd': 0, u'uid': u'863591027085418', u'hw': 29}, {u'ph': u'+777777777'}, [1, {u'v': u'520123456789', u'id': 1, u'n': u'inn'}], {}
"""
def	create_unit(request, step = 2):
	import	twlp
	sid = usid = un_name = hwid = None
	if not (request.has_key('wsid') and request['wsid']):
		print """~eval| msg("<span style='color: #a00; font-weight: bold;'>Птеряно соединение с сервером!</span>")"""
		return
	sid = request['wsid']
	print "~clog|"
	if step == 1:
		'''
		'''
		if request.has_key('wusid') and request['wusid']:	usid = request['wusid']
		if request.has_key('name') and request['name']:	un_name = request['name']
		if request.has_key('hwTypeId') and request['hwTypeId']:	hwid = request['hwTypeId']
		if request.has_key('creatorId') and request['creatorId']:
			crid = request['creatorId']
		else:	crid = usid
		if sid and usid and un_name and hwid:
			data = {'sid': sid, 'svc': 'core/create_unit', 'params': {"creatorId": crid, "name": un_name,"hwTypeId": hwid,"dataFlags":"257"}}
			fres, sres = twlp.requesr(data)
			if fres:
				out_json(sres, iddom = 'clog')
		else:	out_json(data, iddom = 'clog')
	elif step == 2:
		sres1 = {'item': {'uacl': 880265986047, 'uid2': '', 'uid': '', 'hw': 29, 'psw': '', 'm': 0, 'ph2': '', 'ph': '', 'cls': 2, 'id': 250, 'nm': 'EGTS-27085418'}, 'flags': 257}
		itemId = sres1['item']['id']
		hwTypeId = sres1['item']['hw']
	#	data = {'sid': sid, 'svc': 'core/update_data_flags', "params":{"spec":[{"type":"id","data": itemId,"flags":9007199254740991,"mode":1}]}}
		data = {'sid': sid, 'svc': 'core/batch', "params":[{'svc': 'core/update_data_flags', "params":{"spec":[{"type":"id","data": itemId,"flags":9007199254740991,"mode":1}]}}]}
		out_json(data, iddom = 'clog')
		fres, sres = twlp.requesr(data)
		if not fres:
			print "<span style='color: #a00; font-weight: bold;'>", sres, "</span>"
			out_json(data, iddom = 'clog')
			return
		### Читать все объекты "itemsType":"avl_unit" ИЩЕМ или ПРОВЕРЯЕМ ???
		'''
		data = {'sid': sid, 'svc': 'core/batch', "params":[
			{"svc":"core/search_items","params":{"spec":{"itemsType":"avl_unit","propName":"*","propValueMask":"*","sortType":""},"force":1,"flags":1,"from":0,"to":4294967295}}],
			"flags":0}
		fres, sres = twlp.requesr(data)
		print fres, out_json(sres)
	elif step == 3:
		'''
		params = []
		if request.has_key('uid') and request['uid'].strip():
			params.append ({"svc":"unit/update_device_type","params":{"itemId": itemId,"deviceTypeId": hwTypeId,"uniqueId": request['uid'].strip()}})
	#	if request.has_key('uid') and request['uid'].strip():
		if request.has_key('ph0') and request['ph0'].strip():
			params.append ({"svc":"unit/update_phone","params":{"itemId": itemId,"phoneNumber": request['ph0'].strip()}})
		if request.has_key('ph2') and request['ph2'].strip():
			params.append ({"svc":"unit/update_phone2","params":{"itemId": itemId,"phoneNumber": request['ph2'].strip()}})
		if request.has_key('passwd') and request['passwd'].strip():
			params.append ({"svc":"unit/update_access_password","params":{"itemId": itemId,"accessPassword": request['passwd'].strip()}})
		if request.has_key('oinn') and request['oinn'].strip():
			params.append ({"svc":"item/update_admin_field","params":{"id":0,"n":"inn","v": request['oinn'].strip(),"itemId": itemId,"callMode":"create"}})
		params.append ({"svc":"item/add_log_record","params":{"itemId": itemId,"action":"import_unit_cfg","newValue":"","oldValue":""}})
	#	out_json (params)
		data = {'sid': sid, 'svc': 'core/batch', "params": params, "flags":0}
		fres, sres = twlp.requesr(data)
		if not fres:
			print "<span style='color: #a00; font-weight: bold;'>", sres, "</span>"
			out_json(data, iddom = 'clog')
			return
		print fres, sres
	else:	print "~error|", request

def	main (SCRIPT_NAME, request, referer):
	try:
		print	"~error|~warnn|", os.environ['SERVER_NAME']
#		print "~shadow|", request
		print "~log|ajax.maim ", time.time(), request
		if request.has_key ('shstat'):
			shstat = request ['shstat']
			if shstat == 'connect':
				print "~log|connect <span class='tit'>", time.time(), "</span>"
				import	twlp
				sres = twlp.send_post ({'svc': 'token/login', 'params': "{'token':'%s'}" % twlp.usr2token['wialon']})
				usr = sres['au']
				sid = sres['eid']
				usid = sres['user']['id']
				print "SID:", usr, usid, sid
			#	print "~eval|msg('SID: %s')" % sres['eid']
				print "~eval|$('#wusid').val('%s'); $('#wuser').html('%s');" % (usid, usr)
				print "~eval|$('#wsid').val('%s');" % sres['eid']
				print "~eval|set_shadow('get_hw_types');"
				print "~eval|set_shadow('get_users');"
	#			print "~eval|alert('usid: ' +%s); $('#creatorId').val(%s);" % (usid, usid)
				print "~eval|wialon_timerId = setInterval(function() {set_shadow('continue')}, 120000);"
			elif shstat == 'exit':
				print "~eval|msg('Exit');"
				print "~eval|$('#wsid').val(''); clearInterval(wialon_timerId);"
			elif shstat == 'continue':
				if request.has_key('wsid') and request['wsid']:
					import	twlp
					sres = twlp.send_post ({'svc': 'core/batch', 'params': "{}", 'sid': "%s" % request['wsid']})
				#	print "~log|", str(sres)
				else:	print "~error|", request
			elif shstat == 'get_hw_types':		get_hw_types (request)
			elif shstat == 'get_users':		get_items (request, 'user')
			elif shstat == 'create_unit':
				create_unit (request, 1)
				time.sleep(2)
				create_unit (request, 2)
			else:
				print "~eval|alert ('Unknown shstat: [%s]!');" % request ['shstat']
		else:
			print "~shadow|"
			wdgerror ("Отсутствует request[shstat]",  txt = "request: %s" % str(request), obj = SS.objpkl)
		#	out_widget('warnn', tit = "Отсутствует request[shstat]",  txt = "request: %s" % str(request), obj = SS.objpkl)
		
	except psycopg2.OperationalError:
		exc_type, exc_value = sys.exc_info()[:2]
		print "~eval|alert (\"EXCEPT: ajax Нет доступа к БД:\\n", ddb_map, "\");"
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "~error|<span class='error'>EXCEPT:", exc_type, exc_value, "</span>"
	#	print "~eval|alert (\"EXCEPT: ajax.py shstat: ", shstat, "\\n", exc_type, exc_value, "\");"
