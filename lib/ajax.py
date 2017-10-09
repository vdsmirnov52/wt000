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
def	create_unit(request, step = 2, sres = None):
	import	twlp
	sid = usid = un_name = hwid = None
	if not (request.has_key('wsid') and request['wsid']):
		print """~eval| msg("<span style='color: #a00; font-weight: bold;'>Птеряно соединение с сервером!</span>")"""
		return	False, None
	if not (request.has_key('uid') and request['uid'].strip()):
		print """~eval| msg("<span style='color: #a00; font-weight: bold;'>Отсутствует Уникальный ID!</span>")"""
		return  False, None
	UID = request['uid'].strip()
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
			return	fres, sres
		else:	out_json(data, iddom = 'clog')
	elif step == 2:
	#	sres = {'item': {'uacl': 880265986047, 'uid2': '', 'uid': '', 'hw': 29, 'psw': '', 'm': 0, 'ph2': '', 'ph': '', 'cls': 2, 'id': 250, 'nm': 'EGTS-27085418'}, 'flags': 257}
		itemId = sres['item']['id']
		hwTypeId = sres['item']['hw']
	#	data = {'sid': sid, 'svc': 'core/update_data_flags', "params":{"spec":[{"type":"id","data": itemId,"flags":9007199254740991,"mode":1}]}}
		data = {'sid': sid, 'svc': 'core/batch', "params":[{'svc': 'core/update_data_flags', "params":{"spec":[{"type":"id","data": itemId,"flags":9007199254740991,"mode":1}]}}]}
		out_json(data, iddom = 'clog')
		fres, sres = twlp.requesr(data)
		if not fres:
			print "<span style='color: #a00; font-weight: bold;'>", sres, "</span>"
			out_json(data, iddom = 'clog')
			return	False
		data = {'sid': sid, 'svc': "unit_group/update_units", "params": {"itemId": 245, "units":[itemId]}}	# Добавить itemId в Группу 'Вторя Test'
		fres, sres = twlp.requesr(data)
		if fres:
			out_json(sres, iddom = 'clog')
		else:	print "<span style='color: #a00; font-weight: bold;'>", sres, "</span>"
		### Читать все объекты "itemsType":"avl_unit" ИЩЕМ или ПРОВЕРЯЕМ что и зачем ???
		# ПРОВЕРЯЕМ UID 
		'''
		data = {'sid': sid, 'svc': 'core/batch', "params":[
			{"svc":"core/search_items","params":{"spec":{"itemsType":"avl_unit","propName":"*","propValueMask":"*","sortType":""},"force":1,"flags":1,"from":0,"to":4294967295}}],
			"flags":0}
		fres, sres = twlp.requesr(data)
		print fres, out_json(sres)

		if request.has_key('uid') and request['uid'].strip():
			params.append ({"svc":"unit/update_device_type","params":{"itemId": itemId,"deviceTypeId": hwTypeId,"uniqueId": request['uid'].strip()}})
		'''
		params = []
		params.append ({"svc":"unit/update_device_type","params":{"itemId": itemId,"deviceTypeId": hwTypeId,"uniqueId": UID}})
	#	if request.has_key('uid') and request['uid'].strip():
		ph = ph2 = passwd = ""
		if request.has_key('ph0') and request['ph0'].strip():		ph = request['ph0'].strip()
		if request.has_key('ph2') and request['ph2'].strip():		ph2 = request['ph2'].strip()
		if request.has_key('passwd') and request['passwd'].strip():	passwd = request['passwd'].strip()
		params.append ({"svc":"unit/update_phone","params":{"itemId": itemId,"phoneNumber": ph}})
		params.append ({"svc":"unit/update_phone2","params":{"itemId": itemId,"phoneNumber": ph2}})
		params.append ({"svc":"unit/update_access_password","params":{"itemId": itemId,"accessPassword": passwd}})
		params.append ({"svc":"item/add_log_record","params":{"itemId": itemId,"action":"import_unit_cfg","newValue":"","oldValue":""}})

		### Характеристики
	#	svc=item/update_profile_field&params={"itemId":<long>, "n":["vehicle_type" "vin" "registration_plate" "brand" "model" "year"], "v":<text>
		vehicle_type = vin = registration_plate = brand = model = year = ""
		if request.has_key('tts') and request['tts'].strip():		vehicle_type = request['tts'].strip()
		if request.has_key('tvin') and request['tvin'].strip():		vin = request['tvin'].strip()
		if request.has_key('treg') and request['treg'].strip():		registration_plate = request['treg'].strip()
		if request.has_key('tmark') and request['tmark'].strip():	brand = request['tmark'].strip()
		if request.has_key('tmod') and request['tmod'].strip():		model = request['tmod'].strip()
		if request.has_key('tyear') and request['tyear'].strip():	year = request['tyear'].strip()
		params.append ({"svc":"item/update_profile_field", "params":{"itemId": itemId, "n":"vehicle_type", "v": vehicle_type}})
		params.append ({"svc":"item/update_profile_field", "params":{"itemId": itemId, "n":"vin", "v": vin}})
		params.append ({"svc":"item/update_profile_field", "params":{"itemId": itemId, "n":"registration_plate", "v": registration_plate}})
		params.append ({"svc":"item/update_profile_field", "params":{"itemId": itemId, "n":"brand", "v": brand}})
		params.append ({"svc":"item/update_profile_field", "params":{"itemId": itemId, "n":"model", "v": model}})
		params.append ({"svc":"item/update_profile_field", "params":{"itemId": itemId, "n":"year", "v": year}})

		### Произвольные поля
	#	svc=item/update_admin_field&params={"itemId":<long>, "id":<long>,"callMode":(create, update, delete), "n":<text>, "v":<text>}
		'''
		oinn = odog = ""
		if request.has_key('oinn') and request['oinn'].strip():	oinn = request['oinn'].strip()
		params.append ({"svc":"item/update_admin_field","params":{"itemId": itemId, "id":0,"n":"inn","v": oinn, "callMode":"create"}})
		if request.has_key('odog') and request['odog'].strip():	odog = request['odog'].strip()
		params.append ({"svc":"item/update_admin_field","params":{"itemId": itemId, "id":1,"n":"dog","v": odog, "callMode":"create"}})
		'''
		j = 0
		for n in ['oinn', 'odog']:	# Имена полей в форме 
			v = ""
			if request.has_key(n) and request[n].strip():	v = request[n].strip()
			params.append ({"svc":"item/update_admin_field","params":{"itemId": itemId, "id": j, "n": n, "v": v, "callMode":"create"}})
			j += 1

	#	out_json (params)
		data = {'sid': sid, 'svc': 'core/batch', "params": params, "flags":0}
		fres, sres = twlp.requesr(data)
		if not fres:
			print "<span style='color: #a00; font-weight: bold;'>", sres, "</span>"
			out_json(data, iddom = 'clog')
			return
		print fres, sres
	else:	print "~error|", request

def	is_successfully (label, sres):
	try:
		sid = sres['eid']
		usr = sres['au']
		usid = sres['user']['id']
		print label, "<span class='bfinf'> successfully </span> SID:", sid, "User:", usr, "UsId:", usid
		print "~eval|$('#wusid').val('%s'); $('#wuser').html('%s');" % (usid, usr)
		print "~eval|$('#wsid').val('%s');" % sid	#sres['eid']
	except:	print label, "<span class='bferr'> Result:</span>", sres

import	urllib
import	twlp

def	login (request):
	data = {'svc': 'token/login', 'params': {'token':'%s' % request['users']}}
	b, sres = twlp.requesr(data, host = request['whost'])

#	url = r"http://%s/wialon/ajax.html?svc=token/login&params={'token':'%s'}" % (request['whost'], request['users'])
#	sres = json.load(urllib.urlopen(url))
	if b:	#sres: 
		is_successfully ('Login:', sres)
	else:
		print	"<span class='bferr'>", sres, "</span>"
	return	sres

def	logout(request):
	if request.has_key('wsid') and request['wsid'] != '':
		data = {'svc': 'core/logout', 'sid': request['wsid'], 'params': {}}
		b, txt = twlp.requesr(data, host = request['whost'])
		if b:
			print "<span class='bfinf'>", txt, "</span>"
		else:	print "<span class='bferr'>", txt, "</span>"
	else:	print "<span class='bferr'> you are already logouted </span>"
	return
	res = json.load(urllib.urlopen(r"http://wialon.rnc52.ru/wialon/ajax.html?svc=core/logout&params={}&sid=%s" % sid))
	print "\tlogout", res

def	main (SCRIPT_NAME, request, referer):
	try:
		print "~error|~warnn|",# os.environ['SERVER_NAME']
		print "~shadow|ajax.maim", request
#		print "~log|ajax.maim ", time.time(), request
		if request.has_key ('shstat'):
			shstat = request['shstat']
			if shstat == 'connect':
				print "~log|"
				import	twlp
				sres = twlp.send_post ({'svc': 'token/login', 'params': "{'token':'%s'}" % request['token']})	#twlp.usr2token['wialon']})
				if sres:
					is_successfully ("Connect:", sres)
			#		print "~eval|set_shadow('get_users');"
			#		print "~eval|alert('usid: ' +%s); $('#creatorId').val(%s);" % (usid, usid)
			#		print "~eval|wialon_timerId = setInterval(function() {set_shadow('continue')}, 120000);"
			elif shstat == 'login':
				print "~log|", 	login(request)
			elif shstat == 'exit':
				print "~log|Logout:"
				if request.has_key('wsid') and request['wsid'] != '':
					logout(request)
				else:	print "<span class='bferr'> you are already logouted </span>"
		#		print "~eval|$('#wsid').val(''); $('#wusid').val(''); $('#wuser').html('');"
			elif shstat == 'continue':
				if request.has_key('wsid') and request['wsid']:
					import	twlp
					sres = twlp.send_post ({'svc': 'core/batch', 'params': "{}", 'sid': "%s" % request['wsid']})
				#	print "~log|", str(sres)
				else:	print "~error|", request
			elif shstat == 'get_hw_types':		get_hw_types (request)
			elif shstat == 'get_users':		get_items (request, 'user')
			elif shstat == 'create_unit':
				fres, sres = create_unit (request, 1)
				if fres:
					time.sleep(2)
					create_unit (request, 2, sres)
				else:	print "~error|<span style='color: #a00; font-weight: bold;'>", sres, "</span>"
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
