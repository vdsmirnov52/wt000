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
				'''
				sid = usid = un_name = hwid = None
				if request.has_key('wsid') and request['wsid']:		sid = request['wsid']
				if request.has_key('wusid') and request['wusid']:	usid = request['wusid']
				if request.has_key('un_name') and request['un_name']:	un_name = request['un_name']
				if request.has_key('hwTypeId') and request['hwTypeId']:	hwid = request['hwTypeId']
				if sid and usid and un_name and hwid:
					data ={'sid': sid, 'svc': 'core/create_unit', 'params': {"creatorId": usid, "name": un_name,"hwTypeId": hwid,"dataFlags":"257"}}
					out_json(data)
				else:	print "~error|", request
				'''
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
