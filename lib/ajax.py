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

def	shw_types (obj, sname = 'hwTypeId', idom = 'hw_types'):
	print "~%s|" % idom
	print "<select id='%s' class='ssel' name='%s' ><option value=''>  </option>" % (sname, sname)
	for dl in obj:
		if dl.has_key('hw_category'):
			name = "%s (%s)" % (dl['name'], dl['hw_category'])
		else:	name = dl['name']
		print "<option value='%s'> %s </option>" % (dl['id'], name)
	print "</select>"

def	out_json(obj, idom = 'log'):
	print "~%s|" % idom
	if type(obj) == list:
		print "<pre> List:"
		for l in obj:
			print l
		print "</pre>"
	else:
		print "Type", type(obj)

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
				print "~eval|$('#wusid').val('%s'); $('#wuser').html('%s')" % (usid, usr)
				print "~eval|$('#wsid').val('%s'); wialon_timerId = setInterval(function() {set_shadow('continue')}, 120000);" % sres['eid']
			elif shstat == 'exit':
				print "~eval|msg('Exit');"
				print "~eval|$('#wsid').val(''); clearInterval(wialon_timerId);"
			elif shstat == 'continue':
				if request.has_key('wsid') and request['wsid']:
					import	twlp
					sres = twlp.send_post ({'svc': 'core/batch', 'params': "{}", 'sid': "%s" % request['wsid']})
				#	print "~log|", str(sres)
				else:	print "~error|", request
			elif shstat == 'get_hw_types':
				if request.has_key('wsid') and request['wsid']:
					sid = request['wsid']
					import	twlp
					vtype = ["auto", "mobile", "soft", "tracker"]
					data ={'sid': sid, 'svc': 'core/get_hw_types', 'params': { "filterType":"type", "filterValue":["auto", "mobile", "soft", "tracker"], "includeType": True}}
					sres = twlp.send_post(data)
					out_json(sres)
					shw_types(sres)
			#		print "~log|", str(sres)
				else:	print "~error|", request
			elif shstat == 'create_unit':
				sid = usid = un_name = hwid = None
				if request.has_key('wsid') and request['wsid']:		sid = request['wsid']
				if request.has_key('wusid') and request['wusid']:	usid = request['wusid']
				if request.has_key('un_name') and request['un_name']:	un_name = request['un_name']
				if request.has_key('hwTypeId') and request['hwTypeId']:	hwid = request['hwTypeId']
				if sid and usid and un_name and hwid:
					data ={'sid': sid, 'svc': 'core/create_unit', 'params': {"creatorId": usid, "name": un_name,"hwTypeId": hwid,"dataFlags":"257"}}
					out_json(data)
				else:	print "~error|", request
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
