#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""
Отображение данных о движение транспорта Wialon -> NimBus API
"""
import	os, sys, time
LIBRARY_DIR = r"/home/smirnov/pylib"
sys.path.insert(0, LIBRARY_DIR)

import	dbtools
import	nimbus

TOKENS = [
	('30e04452062e435a9b48740f19d56f45', 'ПП МУП Борское ПАП'),
	('5eb103d95c204a87a27c74e4b8f6bae0', 'ПП МУП Павловское ПАП'),
	('4f4b994b468d4ac79b90c074da708904', 'ПП МУП Экспресс - Дзержинск'),
	('fbe7170fb4954cfc93f9a9cf95ca0ac8', 'ПП МУП АПАТ Арзамасский'),
	]
'''
так я получаю лист маршрутов 		http://212.193.103.21/cgi-bin/ajax.cgi?this=ajax&shstat=nimbus&cmd=depot/128/routes
так делаю по каждому итему листа GET 	http://212.193.103.21/cgi-bin/ajax.cgi?this=ajax&shstat=nimbus&cmd=depot/128/route/N
потом складываю uid->номер мсаршрута в уникальный словарь
'''
def	get_routes2uid (depot = 128):
	cmd = "depot/%s/routes" % depot
	cmd = "depot/%s/route/%s" % (depot, rid)
	
stime = lambda tm:	time.strftime('\t%T %d/%m/%Y', time.localtime (tm))
curr_date = int(time.time()/ 86400)* 86400

def	view_nimbus (request):
	print	"""<head> <title>NimBus View</title>
	<style>\n.hidd   {padding: 0px; margin: 0px; border-style: hidden;}\n</style>
	</head>"""
#	print	"view_nimbus", request
#	token = '5eb103d95c204a87a27c74e4b8f6bae0'	# ПП МУП Павловское ПАП		depot=89&stop_id= 17125
#	token = '30e04452062e435a9b48740f19d56f45'	# ПП МУП Борское ПАП		depot=128&stop_id=20423	20881
#	this = view_nimbus
	this = token = depot = stop_id = ''
	if request.has_key('this') and request['this'].strip():			this = request['this'].strip()
	if request.has_key('token') and request['token'].strip():		token = request['token'].strip()
	if request.has_key('depot') and request['depot'].strip().isdigit():     depot = request['depot'].strip()
#	if request.has_key('stop_id') and request['stop_id'].strip().isdigit(): stop_id = request['stop_id'].strip()
	if request.has_key('stop_id') and request['stop_id'].strip().isdigit(): stop_id = '20421'
	print	"""<body><form name='myForm' action='/cgi-bin/abus.cgi' method='post'><fieldset class='hidd'>
	<input name='this' type='hidden' value='%s' /> 
	<input name='token' type='hidden' value='%s' /> 
	<input name='depot' type='hidden' value='%s' /> 
	<input name='stop_id' type='hidden' value='%s' />
	</fieldset>""" % (this, token, depot, stop_id)
	URL = request.get('URL')
#	window.open('/curr_status_TC.html', 'health_status_TC', params).focus(); return false;
	print	"""<input name='URL' type='text' size=64 value='%s' /> <input type='submit' value='Submit' />
		<input type='button' value='View Panel' onclick="alert ('URL: ' +'%s'); window.open('/cgi-bin/abus.cgi%s', 'abus_panel').focus()" />""" % (URL, URL, URL)
	#	<input type='button' value='Get JSON' onclick="alert ('JSON'); document.myForm.this='json'; document.myForm.submit();" />
	select_view = {'stops':'Остановки', 'routes':'Маршруты', 'rides':'Рейсы'}	#, '':'', '':'', }
	print """<select name='set_view'><option value=''> </option>"""
	set_view = request.get('set_view')
	for k in select_view.keys():
		if k == set_view:
			print "<option value='%s' selected> %s </option>" % (k, select_view[k])
		else:	print "<option value='%s'> %s </option>" % (k, select_view[k])
	print	"</select><pre>"

	res = None
	for t, n in TOKENS:
			if t == token:
				jstyle = 'background-color: #fc0;'
			else:	jstyle = ''
			print	"""<span style="cursor: pointer; %s" onclick="document.myForm.token.value='%s'; document.myForm.URL.value='?token=%s';">""" % (jstyle, t, t), t, n, "</span>"
	try:
		if token:
			print "<hr width=90%/>    Депо\tНаименование" 
			res = nimbus.u8api_nimbus('depots', "Token " +token)
			for dpt in res.get('depots'):
				if depot == str(dpt['id']):
					jstyle = 'background-color: #fc0;'
				else:	jstyle = ''
				print """<span style="cursor: pointer; %s" onclick="document.myForm.depot.value='%s'; document.myForm.URL.value='?token=%s&depot=%s'; document.myForm.stop_id.value='';">%8d\t%s </span>""" % (
						jstyle, dpt['id'], token, dpt['id'], dpt['id'], dpt['n'])
		print	"set_view:<b>", set_view, "</b>"
		if depot and set_view == 'rides':
			cmnd = 'depot/%s/rides' % depot
			print "cmnd:", cmnd, stime(curr_date)
			res = nimbus.u8api_nimbus(cmnd, "Token " +token)
			rides = res.get('rides')
			print	rides[0].keys()
		#	['a', 'd', 'pt', 'f', 'i', 'bid', 'si', 'tm', 'u', 'at', 'tid', 'id']
			
			for rrr in rides:
				if not rrr.get('at'):		continue
				if rrr['tm'] < curr_date:	continue
				print rrr['id'], rrr['d'], stime (rrr['tm']), rrr['a'],
				print "\tUnit id:", rrr['u'],
				print "\tОстановки First: %s, Current: %s" % (rrr.get('si'), rrr.get('i'))
				if rrr['u']:
					print "\tat:", rrr.get('at')
					print "\tpt:", rrr.get('pt')
				print "\ttid:", rrr.get('tid'),
				print "\tbid:", rrr.get('bid'),
				print "\tf:", rrr.get('f')
			'''
			'''
			return
		if depot and set_view == 'routes':
			cmnd = 'depot/%s/routes' % depot
			print "cmnd:", cmnd, stime(curr_date)
			res = nimbus.u8api_nimbus(cmnd, "Token " +token)
			routes = res.get('routes')
			#	['a', 'd', 'tt', 'tp', 'st', 'tm', 'u', 'isc', 'n', 'id']
			for rrr in routes:
			#	if not rrr['u']:	continue
				print rrr['id'], rrr['n'], rrr['d'], rrr['a'],
				print "\ttm", rrr['tm'], stime (rrr['tm']),
				print "\tisc", rrr['isc']
				if not rrr['tt']:	continue
				'''
				print "\ttt",  rrr['tt'][0].keys()
				'''
				for rt in rrr['tt']:
					if not rt['bid']:	continue
					if not rt['u']:	continue
					
					print "\tbid: %s, id: %s, Unit id: %s" % (rt['bid'], rt['id'], rt['u'])
				#	print (rt['d'])
			#		print time(rt['tm'])	# Last update UNIX time
			#	print "\tst", rrr['st']		# Описание трасс маршрута от первой до последней остановки
			#	print "\tu", rrr['u']
		###		print
			cmnd = 'depot/%s/route/%s' % (depot, 3399)
			print "cmnd:", cmnd
			res = nimbus.u8api_nimbus(cmnd, "Token " +token)
			print res
			print res.keys()
			print res['id'], res['n'], res['d'], res['a'],
			print "\ttm", res['tm'],
			print "\tisc", res['isc']
			print "\ttt",  res['tt']
			print "\tst", res['st']
			print "\tu", res['u']
			print "</pre>"
			return
		if depot:
			cmnd = 'depot/%s/stops' % depot
			print "cmnd:", cmnd
			res = nimbus.u8api_nimbus(cmnd, "Token " +token)
			stops = res.get('stops')
			print	'Keys:', stops[0].keys()
			for stp in stops:
				if stop_id and stop_id == str(stp['id']):
					print """<span style="cursor: pointer; background-color: #fc0;" onclick="document.myForm.stop_id.value='%s'; document.myForm.URL.value='?token=%s&depot=%s&stop_id=%s';">%8d %s </span>""" % (
						stp['id'], token, depot, stp['id'], stp['id'] , stp['n'].strip()), '\t[ %s ]' % stp['d'], '\t', stp['p']
				elif not stop_id:
					print """<span style="cursor: pointer;" onclick="document.myForm.stop_id.value='%s'; document.myForm.URL.value='?token=%s&depot=%s&stop_id=%s';">%8d %s </span>""" % (
						stp['id'], token, depot, stp['id'], stp['id'] , stp['n'].strip()), '\t[ %s ]' % stp['d'], '\t', stp['p'] 
		if stop_id:
			cmnd = 'depot/%s/stop/%s/panel' % (depot, stop_id)
			print "cmnd:", cmnd
			res = nimbus.u8api_nimbus(cmnd, "Token " +token)
	#		print	res
			print time.strftime('\t%T %d-%m-%Y', time.localtime(res.get('tm')))
			for r in res.get('r'):
			#	print r
				print r['n'], r['fs'], r['d'], '->', r['ls']
				if r['tt']:
				#	print "\t", r['tt']	#, r['eta']
					for jtt in r['tt']:
				#		print jtt
						print time.strftime('\t%T %d-%m-%Y', time.localtime(jtt.get('pt'))), #jtt['eta'],
						for k in jtt.keys():
							if k == 'pt':	continue
							if jtt[k]:	print "|", k, jtt[k],
						print
			
		print	"</pre>", prn_request (request)
	
	except:
		if res:	print   'res:', res
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT:", exc_type, str(exc_value).strip()
	finally:
		print	"</form></body>"

def	prn_request (request):
	print "<pre>prn_request:"
	for k in request.keys():	print "%20s:" % k, request[k]
	print "</pre>"

def	ajax (SCRIPT_NAME, request):
	""" Вывод (обновление) данных на панеть	"""
	num_tr = 4	# К-во строк на странице
	curr_page = 0
	tm = int(time.time())
	print	"~curr_tm|%s&nbsp;" % time.strftime("%H:%M", time.localtime (tm))
	try:
	#	print "~eval| alert('ajax');"
	#	print "~log|SCRIPT_NAME", SCRIPT_NAME, request
		token = request.get('token')
		depot = request.get('depot')
		stop_id = request.get('stop_id')
		if not (stop_id and stop_id.isdigit() and depot and depot.isdigit() and token and len(token) > 30):
			print	"~trid_01|<td colspan=4 align='center'><span style='color: #a00; font-weight: bold;'>", request, "</span></td>"
			return

		curr_page = 0
		jpage = request.get('jpage')
		if jpage and jpage.isdigit():	curr_page = int(jpage)

		cmnd = 'depot/%s/stop/%s/panel' % (depot, stop_id)
		'''
		cmnd = 'depot/128/stop/20423/panel'		# ПП МУП Борское ПАП, 126, 20423 Вокзал 
		token ='30e04452062e435a9b48740f19d56f45'
		'''
		res = nimbus.u8api_nimbus (cmnd, token = 'Token ' +token)
	#	print cmnd, res
		if not res:
			print "~trid_01|<td colspan=4 align='center'><span style='color: #a00; font-weight: bold;'> Нет связи! </span></td>"
		else:
			print "~log|"
			panel = res.get('r')
			if not panel:
				print "~trid_01|<td colspan=4 align='center'><span style='color: #a00; font-weight: bold;'> Нет данных! </span></td>"
			else:
				snumm = '901'
				dtm = 22
				sname = 'Станция'
				tlist = [(999,'', '')]
				twait = 50
				for r in panel:
					if r['tt']:
						snumm = r['n']
					#	sname = "%s >> %s" % (r['fs'], r['ls'])
						sname =  r['ls']
						eta = r['tt'][0]['eta']
						if eta and eta.has_key('tt'):
							dtm = eta['tt']/60
						else:
							dtm = int (-(tm - r['tt'][0]['pt']) / 60)
							continue
						if dtm == 0:		continue
						if dtm > twait:		continue
						for k in xrange(len(tlist)):
							kt, kn, kl = tlist[k]
							'''
							if kt == dtm and kn == snumm and kl == sname:
								print "new (", dtm, snumm, sname, "), tlist[",k,"]", kt, kn, kl
								continue
							'''
							if dtm < kt:
								tlist.insert(k, (dtm, snumm, sname))
								break
					
				jl = 0
				if curr_page * num_tr > (len(tlist) -2):	curr_page = 0
				print	"jpage:", jpage, curr_page, len(tlist), 
				for k in xrange(len(tlist)):
					dtm, snumm, sname = tlist[k]
					koi_sname = unicode(sname, 'utf-8').encode('koi8-r')
					if dtm > twait:		break
					if jl >= num_tr:	break
					if k > curr_page * num_tr:
						jl += 1
					if jl == 0:	continue
					sdtm = "%02d" % dtm
					'''
					if dtm < 10 and dtm >= 0:
						sdtm = '&nbsp; %s' % dtm
					else:	sdtm = str(dtm)
					'''
				#	if len (sname) > 26:
					if len (koi_sname) > 12:
						print "~trid_%02d|<td>%3s</td><td style='color: #880;'>%s</td><td colspan='2'><marquee behavior='alternate' scrollamount='1' scrolldelay='240' > %s </marquee></td>" % (
							jl, snumm, sdtm, sname)
					else:
						sname = unicode(koi_sname[:10], 'koi8-r').encode('utf-8')
						print "~trid_%02d|<td>%3s</td><td style='color: #880;'>%s</td><td colspan='2'>%s</td>" % (jl, snumm, sdtm, sname)
				
				if jl < num_tr:
					curr_page = 222
				else:	curr_page += 1
				while jl < num_tr:	# Очистить строки
					jl += 1
					print "~trid_%02d|<td colspan='4'> &nbsp; </td>" % jl

		#		print "~trid_01|<td>%s</td><td>%s</td><td colspan='2'>%s</td>" % (snumm, dtm, sname)
	#	print "~log|tlist"	, tlist
		print "~eval| document.myForm.jpage.value='%s'" % curr_page
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "except: ajax", exc_type, exc_value	#request

#	<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css" integrity="sha384-9gVQ4dYFwwWSjIDZnLEWnxCjeSWFphJiwGPXr1jddIhOegiu1FwO5qRGvFXOdJZ4" crossorigin="anonymous">
#	<link rel='stylesheet' type='text/css' href='/css/font-awesome/css/font-awesome.min.css' />
style =	"""
	<style>
	body	{width: 98px; height: 64px; padding:0; margin:0px; cursor: none; color: #880; padding:0px; margin:0px, line-height: 10px;}
	body	{font-family: 'MS Sans Serif',  serif; font-size: 8px; background-color: #000000;}
	table	{line-height: 10px;}
	.hidd   {padding: 0px; margin: 0px; border-style: hidden;}
	</style>"""
jscr =	"""
	<script type='text/javascript' src='/jq/jquery.onajax_answer.js'></script>
	<script type='text/javascript' src='/jq/jquery.js'></script>
	<script type='text/javascript'>
	function set_shadow (shstat) {
		$.ajax({data: 'shstat='+ shstat +'&' +$('form').serialize()});  }
	var intervalID = null;
	/*
	if (intervalID == null) {
		intervalID = setInterval(set_shadow, 20000, 'get_info');
	}
	*/
	$(document).ready(function () {
	$.ajaxSetup({ url: "/cgi-bin/abus.cgi?this=ajax", type: "post", error: onAjaxError, success: onAjaxSuccess, timeout: 30000 });
	intervalID = setInterval(set_shadow, 20000, 'get_info');

	set_shadow('get_info');
	});
	</script>"""

def	main (request):
	token = depot = stop_id = ''
	if request.has_key('token') and request['token'].strip():		token = request['token'].strip()
	if request.has_key('depot') and request['depot'].strip().isdigit():	depot = request['depot'].strip()
#	if request.has_key('stop_id') and request['stop_id'].strip().isdigit():	stop_id = request['stop_id'].strip()
	if request.has_key('stop_id') and request['stop_id'].strip().isdigit():	stop_id = '20421'
	if not (stop_id and stop_id.isdigit() and depot and depot.isdigit() and token and len(token) > 30):
	#	print "main request", request
		return  view_nimbus (request)

#	res = nimbus.get_panel (depot, stop_id, token = "Token " +token)
	cmnd = 'depot/%s/stop/%s/panel' % (depot, stop_id)
#	print "cmnd:", cmnd
#	res = nimbus.api_nimbus(cmnd, "Token " +token)
	res = nimbus.u8api_nimbus(cmnd, "Token " +token)
	sname = 'None'
	tm = int (time.time())
	if res:
		mlist = []
		sname = res.get('n')
		if sname:	sname = sname	#.encode('utf-8')
		panel = res.get('r')
		if panel:
			for r in panel:
				if r['tt']:
					mlist.append ("<span style='color: #3a3;'> %s %s %s </span>" % (r['n'], time.strftime("%H:%M", time.localtime (r['tt'][0]['pt'])), r['ls']))
				#	mlist.append ("<span style='color: #3a3;'> %s %s %s </span>" % (r['n'].encode('utf-8'), time.strftime("%H:%M", time.localtime (r['tt'][0]['pt'])), r['ls'].encode('utf-8')))
		#		else:	mlist.append ("<span style='color: #aa3;'> %s &nbsp;&nbsp;&nbsp;-&nbsp;-&nbsp;&nbsp;&nbsp; %s </span>" % (r['n'].encode('utf-8'), r['ls'].encode('utf-8')))
			if mlist:
				plist = '<br>\n'.join(mlist)
			else:	plist = "<span style='color: #aa3;'> Нет транспорта </span>"
		else:	plist = "<span style='color: #a00;'> Нет данных </span>"
	
#	style = ""
	print """<head> <title>А %s </title> %s %s </head>""" % (sname, style, jscr)

	print	"""<body><form name='myForm' action='/cgi/index.cgi' method='post'><fieldset class='hidd'>
	<input name='token' type='hidden' value='%s' />
	<input name='depot' type='hidden' value='%s' />
	<input name='stop_id' type='hidden' value='%s' />
	<input name='jpage' type='hidden' value='0' />
	</fieldset>""" % (token, depot, stop_id)
	clock = '<i class="fa fa-clock-o" aria-hidden="true"></i>'
	print	"""<table width="98px" id="ptable" cellpadding="1" cellspacing="0" valign="top" >
	<tr style='background-color: #004;'><td> № </td><td> м. </td><td> Куда </td><td align='right' id='curr_tm'> %s &nbsp; </td></tr>
	""" % time.strftime("%H:%M", time.localtime (tm))
	print	"<tr id='trid_01' style='color: #080;'><td>#</td><td>123</td><td colspan='2'><marquee behavior='scroll' scrollamount='1' scrolldelay='240' bgcolor=#000000>%s</marquee></td></tr>" % "Куда едем ???"
	print	"<tr id='trid_02' style='color: #080;'><td colspan=4>##2</td></tr>"
	print	"<tr id='trid_03' style='color: #080;'><td colspan=4>##3</td></tr>"
	print	"<tr id='trid_04' style='color: #080;'><td colspan=4>##4</td></tr>"
	print	"<tr style='color: #080;'><td colspan=4> &nbsp; </td></tr>"
	print	"</table>"

	print	"<div id='log'>", plist, "</div>"
	print	"</form></body>"

def	test ():
	print "TEST lib/busstations.py"

if __name__ == "__main__":
	test ()
