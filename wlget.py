#!/usr/bin/python
# -*- coding: utf-8 -*-

import  os, sys, time
import	json
import	getopt

LIBRARY_DIR = r"/home/smirnov/WT/lib"          # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

CONF_PATHNAME = r"/home/smirnov/Wialon/sys.ini"
CONFIG = None
if os.access (CONF_PATHNAME, os.F_OK):
	import ConfigParser
	CONFIG = ConfigParser.ConfigParser()
	CONFIG.read (CONF_PATHNAME)
	usr2token = dict(CONFIG.items('usr2token'))
	DBDS = dict(CONFIG.items('dbNames'))

import	twlp

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
#		import	twlp
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
#	out_json (obj)
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

def	out_items (obj, **keywords):
	print "out_items keywords:", keywords
	pobj(obj)	#, keywords['itt'])

def	pobj(obj, level = 0):
	ll = []
	dd = {}
#	print obj
	if type(obj) == list:
		spr = "\t"*level
		if type(obj[0]) in (list, dict):
			print "[\n", spr,
		else:	print "[", 
		for o in obj:
			if type(o) == unicode:		print "'%s'," % o.encode('UTF-8'),
			elif type(o) in [int, float]:	print "%s," % str(o),
			else:	ll.append(o)
		for o in ll:
			if o:	pobj(o, level+1)
			else:	print "%s," % str(o),
		print "]",
	elif type(obj) == dict:
		spr = "\t"*level
		print spr,
		print "{", #level 
		for key in obj.keys():
			val = obj[key]
			if type(val) == unicode:		print "'%s': '%s'," % (key.encode('UTF-8'), val.encode('UTF-8')),
			elif type(val) in [int, float]:		print "'%s': %s," % (key.encode('UTF-8'), str(val)) ,
			else:	dd[key] = val
	#	print "DDD", dd.keys()
		for key, val in dd.iteritems():
			print "%s'%s':" % (spr, key), #val
			if val:		pobj(val, level+1)
			else:		print str(val),
		print "}"
	#	print spr, "}"
	elif type(obj) == unicode:
		print "'%s'" % obj ,
	elif type(obj) in [int, float]:
		print obj ,
	else:	print type(obj)

def	get_items (request, itype, func = out_json, **keywords):
	itemsType = ['user', 'avl_unit', 'avl_unit_group', 'avl_resource', 'avl_retranslator']
	if itype not in itemsType:
		print "~error| get_items. Неизвестный itemsType: '%s'" % itype
		return
	if keywords.has_key('flags'):
		flags = keywords['flags']
	else:	flags = 0x0101	# 257
	print "flags", flags
	if request.has_key('wsid') and request['wsid']:
		sid = request['wsid']
#		import	twlp
		# svss['search_items'], "'spec':{'itemsType':'avl_unit','propName':'*','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':1025,'from':0,'to':0")
		data = {'sid': sid, 'svc': 'core/search_items', 'params':{'spec':{'itemsType':itype,'propName':'*','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':flags,'from':0,'to':0}}
		fres, sres = twlp.requesr(data)
		if fres:
			if itype == 'user':
				select_users(sres['items'], key = 'id', val = 'nm', iddom = '_creatorId', sid = 'creatorId')	#, keywords)
			else:	func(sres, itt = itype)
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
def	create_unit(request, step = 1, sres = None):
#	import	twlp
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
		'''	request['wusid'] request['name'] request['hwTypeId'] request['creatorId']
		'''
		if request.has_key('wusid') and request['wusid']:	usid = request['wusid']
		if request.has_key('name') and request['name']:		un_name = request['name']
		if request.has_key('hwTypeId') and request['hwTypeId']:	hwid = request['hwTypeId']
		if request.has_key('creatorId') and request['creatorId']:
			crid = request['creatorId']
		else:	crid = usid
		if sid and crid and un_name and hwid:
			data = {'sid': sid, 'svc': 'core/create_unit', 'params': {"creatorId": crid, "name": un_name,"hwTypeId": hwid,"dataFlags":"257"}}
			fres, sres = twlp.requesr(data)
			if fres:
				out_json(sres, iddom = 'clog')
			return	fres, sres
		else:	#ut_json(data, iddom = 'clog')
			print sid, csid, un_name, hwid
			return	False, request
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
		if request.has_key('ph') and request['ph'].strip():		ph = request['ph'].strip()
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
	#	out_json (params)	
		data = {'sid': sid, 'svc': 'core/batch', "params": params, "flags":0}
		fres, sres = twlp.requesr(data)
		if not fres:
			print "<span style='color: #a00; font-weight: bold;'>", sres, "</span>"
			out_json(data, iddom = 'clog')
	#		print fres, sres
			return

	elif step == 3:
		### Произвольные поля
	#	svc=item/update_admin_field&params={"itemId":<long>, "id":<long>,"callMode":(create, update, delete), "n":<text>, "v":<text>}
		j = 0
		for n in ['oinn', 'odog', 'vid', 'pg']:	# Имена полей в форме 
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
	#		print fres, sres
			return
	else:	print "~error|", request

###	ID avl_unit_group
GID_noData =	256
GID_2Test =	245
GID_1Test =	36
#GID_Virtual =	657	#353469047066127
#GID_VDS =	2220

list_unit_groups = {}	# 

def	add_into_group (sid, group_id, units = None, del_units = None):
	""" Добавить units в группу group_id	"""
	global	list_unit_groups

	if not units:			units = []	#return
	if not del_units:		del_units = []
	if not (units or del_units):	return
	if not list_unit_groups:	get_items ({'wsid': sid}, 'avl_unit_group', func = get_unit_from_group)

	units_list = []
	units_old = list_unit_groups[group_id]
	while True:
		if units and units_old:
			if units[0] > units_old[0]:
				unid = units_old.pop(0)
				if unid not in del_units:
					units_list.append(unid)	#units_old.pop(0))
				else:	print "unid\t", unid
			elif units[0] < units_old[0]:
				units_list.append(units.pop(0))
			else:
				units_list.append(units.pop(0))
				print "==\t", units_old.pop(0) 
			#	del units_old[0]
		elif units:
			for i in units:		units_list.append(i)
			break
		elif units_old:
			for i in units_old:
				if i not in del_units:
					units_list.append(i)
				else:	print "i\t", i
			break
		else:
			print "Not units in groups by ID:", group_id, "units:", units, "del_units:", del_units, "units_old:", units_old
			break
	data = {'sid': sid, 'svc': "unit_group/update_units", "params": {"itemId": group_id, "units": units_list}}
	fres, sres = twlp.requesr(data)
	if fres:
		out_json(sres, iddom = 'clog')
	else:	print "<span style='color: #a00; font-weight: bold;'>", sres, "</span>"

def     get_unit_from_group (obj, **keywords):
	""" Читать список объектов items['u'] в группе	"""
	global	list_unit_groups
#	print "get_unit_from_group", keywords
	if not (obj and obj.has_key('items') and obj['items']):	return
#	print obj['items']
	for item in obj['items']:
		list_unit_groups [item['id']] = item['u'] 

def	main (request):
	global	sid, usid
	try:
		if request.has_key ('shstat'):
			shstat = request ['shstat']
			if shstat == 'connect':
		#		sres = twlp.send_post ({'svc': 'token/login', 'params': "{'token':'%s'}" % twlp.usr2token['wialon']})
				fres, sres = twlp.requesr({'svc': 'token/login', 'params': "{'token':'%s'}" % twlp.usr2token['wialon']})
				if not fres:
					print sres
					return
				usr = sres['au']
				sid = sres['eid']
				usid = sres['user']['id']
				print "SID:", usr, usid, sid
			elif shstat == 'get_hw_types':		get_hw_types (request)
			elif shstat == 'get_users':		get_items (request, 'user')
			elif shstat == 'create_unit':
				fres, sres = create_unit (request, 1)
				if fres:
					time.sleep(1)
					print	create_unit (request, 2, sres)
					time.sleep(1)
					print	create_unit (request, 3, sres)
				else:	print "~error|<span style='color: #a00; font-weight: bold;'>", sres, "</span>"
			else:
				print "~eval|alert ('Unknown shstat: [%s]!');" % request ['shstat']
		else:
			print "~shadow|request: %s" % str(request)
		
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "~error|<span class='error'>EXCEPT:", exc_type, exc_value, "</span>"

HW_EGTS =	29
def	check_doube_items (items_uid, dict_atts):
	""" Проверка старых UID (дублей), Создание (добавление) новых avl_unit 	"""
	print "UIDs:\t", items_uid
	fres, sres = twlp.requesr({'svc': 'token/login', 'params': "{'token':'%s'}" % twlp.usr2token['wialon']})
	if not fres:
		print sres
		return	False
	usr = sres['au']
	sid = sres['eid']
	usid = sres['user']['id']
	flags = 0x0101
	data = {'sid': sid, 'svc': 'core/search_items', 'params':{'spec':{'itemsType':'avl_unit','propName':'*','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':flags,'from':0,'to':0}}
	fres, sres = twlp.requesr(data)
	if not fres:
		print sres
		return	False
	jitems_uid = ":".join(items_uid)
#	print jitems_uid
	for it in sres['items']:
		jhw_type = HW_EGTS
		if it['hw'] == jhw_type:	#29:	# EGTS
			juid = it['uid'].encode('UTF-8')
			if juid and not juid in jitems_uid:	continue
			# Найден дубликат uid 
			#print "Double\t", it['id'], juid, it['nm'].encode('UTF-8'), suid
			print "Double\t", it['id'], juid, it['nm']
			del dict_atts[juid]
			'''
			j = 0
			for suid in items_uid:
				if juid in suid:	break
				j += 1
			del items_uid[j]
			if suid == juid:	continue
		#	svc=unit/update_unique_id&params={"itemId":<long>, "uniqueId":<text new unique ID>}
			### {"params":[{"svc":"unit/update_device_type","params":{"itemId":118,"deviceTypeId":"29","uniqueId":"863591027131527"}}],"flags":0}
			data = {'sid': sid, 'svc': 'unit/update_device_type', 'params':{"deviceTypeId": jhw_type, "itemId": it['id'], "uniqueId": "%s" % suid}}
		#	data = {'sid': sid, 'svc': 'unit/update_unique_id', 'params':{"itemId": it['id'], "uniqueId": "%s" % suid}}
			print data
			fres, sres = twlp.requesr(data)
			print fres, sres, data
			'''
	print "UIDs:\t", dict_atts.keys()
	items_id = []
	request = {'wsid': sid, 'hwTypeId': 29, 'creatorId': 31,}
	for suid in dict_atts.keys():	#items_uid:
		if not suid.isdigit():	continue
		if suid[-8:] == '0':	continue
		request['uid'] = suid
		print dict_atts[suid].keys()
	#	request['wusid']
		request['name'] = dict_atts[suid]['nm']	#"EGTS-%s" % suid[-8:]
		request['ph'] = dict_atts[suid]['ph']
		request['ph2'] = dict_atts[suid]['ph2']
		request['vid'] = dict_atts[suid]['vid']
		request['pg'] = dict_atts[suid]['pg']
		'''
		print request
		'''
		fres, sres = create_unit (request, 1)
		if fres:
			print sres['item']['nm']
			items_id.append(sres['item']['id'])
			time.sleep(2)
			create_unit (request, 2, sres)
	#	print fres, sres

	print "IDs:\t", items_id
	'''
	return	# DEBUG
	group_id = GID_Virtual
	group_id = GID_VDS
	group_id = GID_2Test	# 'Вторя Test'
	'''
	group_id = GID_1Test
	add_into_group (sid, group_id, units = items_id)

import	rnic_atts

def	check_receved_log (fileLog):
	""" Проверка наличия объектов Вне системы (стучатся не описаны) 	"""
	atts = rnic_atts.get_pkl()	# Описание машины в РНИС
	atts_keys = atts.keys()
	if not atts:	return
		
	fileTmp = r"/tmp/Received.ID.log"
#	cmd = "tail -n 22 %s | grep Received > %s" % (fileLog, fileTmp)
	cmd = "fgrep Received /home/wialon/wlocal/logs/egts.log | tail -n 11 > %s" % fileTmp
#	print cmd
	os.system (cmd)
	f = open (fileTmp, 'r')
	ffs = f.read()
	if not ffs:
		os.system("ls -l %s" % fileTmp)
		return
	fs = ffs.split('\n')
	list_idd = []
	dict_atts = {}
	for s in fs:
		ss = s.strip()
		if not ss:			continue
		ls = s.split()
		if 'ID:' in ls:
			unit = ls[ls.index('ID:') -1]
			idd = ls[ls.index('ID:') +1]
			if not idd.isdigit():		continue
			if idd[:6] in "115149:116118":	continue	# Бракованный ID
		if not idd in list_idd:
			list_idd.append(idd)
			if idd in atts_keys:
				dict_atts[idd] = atts[idd]
		print unit, idd
	print list_idd
	for k in list_idd:
		if not dict_atts.has_key(k):	print k
		else:
			print k, dict_atts[k]['nm'], dict_atts[k]['pg']
	dict_atts_keys = dict_atts.keys()
	if dict_atts_keys:	check_doube_items (dict_atts_keys, dict_atts)
#	if (list_idd):	check_doube_items (list_idd)

def	out_pos (obj, **keywords):
	""" Показать последние (текущие) координаты объектов.
	Добавление в группу 'No Data' если нет данных более 30 дней.	"""
	not_pos = []
	is_data = []
	curr_tm = time.time()
	for item in obj['items']:
		print "%6d '%s'\t" % (item['id'], item['nm'].encode('UTF-8')) ,
		if not item['pos']:
			not_pos.append(item['id'])
			print item['pos']
		else:
			tm = item['pos']['t']
			print " %9.5f %9.5f %6.1f\t%s" %(item['pos']['x'], item['pos']['y'], item['pos']['z'], time.strftime("%Y-%m-%d %T", time.localtime(item['pos']['t'])))
			if (curr_tm - tm) > 30*24*3600:
				not_pos.append(item['id'])
			else:	is_data.append(item['id'])
	print "#"*22, not_pos
	if not_pos:
		add_into_group (sid, GID_noData, units = not_pos, del_units = is_data)

#	svc=unit/update_access_password&params={"itemId":<long>,"accessPassword":<text>}
def	update_apasswd (opt):
	print "update_apasswd", opt
	sys.exit()

def	outhelp():
	print "outhelp", sys.argv
	print """
	-i	Поиск и добавление активного оборудования (hwType = EGTS)
	-t	Test (проверка наличия соединения с сервером)
	-U	Список пользователей 
	-u	описания для тип [ avl_unit | avl_unit_group | avl_resource ]
	-p	Показать координаты, добавить в группу 'No Data'
	-w	Список оборудования hwTypes
	-P	Пароль доступа к объекту
	"""
	if CONFIG:	print "CONFIG[usr2token]:\n\t", usr2token
	sys.exit()

if __name__ == "__main__":
	sttmr = time.time()
	print "Start PID: %i\t" % os.getpid(), sys.argv, time.strftime("%Y-%m-%d %T", time.localtime(sttmr))
	FlTesr =	False
	FlHWTyps =	False
	FlUsers =	False
	FlOUnits =	False
	FlgetLog =	False
	FlNoData = 	False
	itemTypes = ['avl_unit', 'avl_unit_group', 'avl_resource']
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'thwpUu:i:P:')
		if not optlist:	outhelp()

		for o in optlist:
			if o[0] == '-P':	update_apasswd (o[1:])
			if o[0] == '-h':	outhelp()
			if o[0] == '-t':	FlTesr =	True
			if o[0] == '-w':	FlHWTyps =	True
			if o[0] == '-U':	FlUsers =	True
			if o[0] == '-p':	FlNoData =	True
			if o[0] == '-u':
				FlOUnits = True
				itemType = o[1]
			if o[0] == '-i':
				FlgetLog = True
				fileLog = o[1]

		main ({'shstat': 'connect'})
		if FlTesr:
			add_into_group (sid, 36, [336, 337])
			'''
			for k in list_unit_groups.keys():	print "%4d\t" % k,  list_unit_groups[k]
			get_items ({'wsid': sid}, 'avl_unit', func = out_pos, flags = 0x0401)
			'''
			sys.exit()
		print "#"*22, sys.argv[1:]
		if FlNoData:	get_items ({'wsid': sid}, 'avl_unit', func = out_pos, flags = 0x0401)
		if FlHWTyps:	main ({'shstat': 'get_hw_types', 'wsid': sid}) 
		if FlUsers:	main ({'shstat': 'get_users', 'wsid': sid})
		if FlOUnits:
			if itemType in itemTypes:
				get_items ({'wsid': sid}, itemType, func = out_items)
			else:	"Ошибка типа '%s'!\n" % itemType , outhelp()
		if FlgetLog:
	#		fileLog = r"/home/wialon/wlocal/logs/egts.log"
			if not os.path.isfile(fileLog):
				print "Отсутствует файд '%s'!" % fileLog
				outhelp()
			check_receved_log (fileLog)
			'''
			for itt in itemTypes:
				get_items ({'wsid': sid}, itt, func = out_items, )
		get_items ({'wsid': sid}, 'user', func= None)
		main ({'shstat': ''}) 
			'''
	except	getopt.GetoptError:
		print "Ошибка в параметрах!\n",	outhelp()
	print "dt %9.4f" % (sttmr - time.time())
