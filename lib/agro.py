# -*- coding: utf-8 -*-

import	cgi, os, sys, time, string
import	json

LIBRARY_DIR = r"/home/smirnov/Wialon/lib/"
sys.path.insert(0, LIBRARY_DIR)

import	dbtools, cglob

CONFIG = None


def	jscripts (ssrc):
	for c in ssrc:
		print "\t<script type='text/javascript' src='%s'></script>" % c

def	rel_css (ssrc):
	for c in ssrc:
		print "\t<link rel='stylesheet' type='text/css' href='%s' />" % c

jsList = [r'//code.jquery.com/jquery-latest.min.js', r'//wialon.rnc52.ru/wsdk/script/wialon.js', 
	r'/jq/jquery.onajax_answer.js', r'/jq/jquery.js', r'/js/calendar.js', r'/js/check_forms.js']

jsLocal =  """$(document).ready(function () {
	$.ajaxSetup({ url: "w.cgi?this=ajax", type: "post", error: onAjaxError, success: onAjaxSuccess, timeout: 30000 });
//	$('#dbody').css({'height': (-210 + document.documentElement.clientHeight) +'px',  'overflow': 'auto'});
//	$('#div_table').css({'height': (-333 + document.documentElement.clientHeight) +'px',  'overflow': 'auto'});

	var	logheight = 90;
	$('#container').css({'height': (-10-logheight + document.documentElement.clientHeight) +'px', 'width': '100%'});
	$('#log').css({'height': logheight +'px', 'overflow': 'auto'});
})
/////////////////////////////////////////////
wialon_timerId = 0
function	msg(text) { $("#log").prepend(text + "<br/>"); }
function	set_shadow (shstat) {	$.ajax({data: 'shstat='+ shstat +'&' +$('form').serialize()});	}
"""

def	dom_head():
	print "<head> <meta name='Author' content='V.Smirnov'> <title>%s</title>" % 'Agro TEST'
	jscripts (jsList)
	rel_css ((r'/css/wlstyle.css', r'/css/calendar.css', r'/css/mmaps.css',
		r"""https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css" integrity="sha384-9gVQ4dYFwwWSjIDZnLEWnxCjeSWFphJiwGPXr1jddIhOegiu1FwO5qRGvFXOdJZ4" crossorigin="anonymous""",
		r'/css/font-awesome/css/font-awesome.min.css'))
	print "\n".join(["<script type='text/javascript'>", jsLocal, "</script>"])
	print "</head>"

#######################################################

def	_main (request, conf):
	global	CONFIG
	global	BDCOBF
	global	DBDS, TOKENS, DB_WL
	CONFIG = conf
	DBDS = dict(CONFIG.items('dbNames'))
	TOKENS = dict(CONFIG.items('usr2token'))
	dom_head()
	"""
	BDCOBF = init_conf ()
	if TOKENS:	### WWW unable to open database file	невозможно открыть файл базы данных для изменений 
		BDCOBF.execute ("update whusers SET token = '%s', token_create = %d WHERE id_whu != 2;" % (TOKENS['wialon'], time.time()))
		BDCOBF.execute ("update whusers SET token = '%s', token_create = %d WHERE id_whu = 2;" % (TOKENS['v.smirnov'], time.time()))
		'''
		print "update whusers SET token = '%s', token_create = %d WHERE id_whu = 2;" % (TOKENS['v.smirnov'], time.time())
		print BDCOBF.last_error 
		rrr = BDCOBF.get_row("SELECT * FROM whusers WHERE id_whu = 2;")
		print rrr, BDCOBF.last_error
		''' 
	elif RES_WUSR:
		d = RES_WUSR[0]
		for r in RES_WUSR[1]:	TOKENS.append("{name: '%s', token: '%s'}" % (r[d.index('login')], r[d.index('token')]))
	else:
		test_db_connects()
		return
	"""
#	print """<html xmlns="http://www.w3.org/1999/xhtml">"""
	try:
		print "<body>"
		print """<form name='myForm' action='%s' method='post'><fieldset class='hidd'>
			<!--input name='wuser' type='hidden' id='wuser' /-->
			<input name='whost' type='hidden' id='whost' />
			<input name='wusid' type='hidden' id='wusid' />
			<input name='wsid' type='hidden' id='wsid' />
			<input name='token' type='hidden' id='token' size=76 />
			<input name='fstat' type='hidden' id='fstat' />
			</fieldset>""" % os.environ['SCRIPT_NAME']
		print '<div id="container">'
		print """<div class="container-fluid">
			<div class="row" style="background-color:#2f75a9; padding: 3px; color: #fff; text-align: center;">
			<div id='load_ts' class='col'><div class=' asbutton' onclick="set_shadow ('get_tansport');"><i class="fa fa-refresh" aria-hidden="true"></i> <span class="button-text">Обновить ТС</span></div></div>
			<div id='_submit' class='col'><div class='asbutton' onclick="document.myForm.submit();"><i class="fa fa-refresh" aria-hidden="true"></i> <span class="button-text">Submit</span></div></div>
			</div></div>"""
		'''
		''
	#	print 'REMOTE_ADDR', os.environ['REMOTE_ADDR']
		if os.environ['REMOTE_ADDR'] in ['10.10.2.40', '37.147.195.151']:
			out_head(CONFIG.get('System', 'name'))
			print button_tools
			print "<div id='dbody' class='hidd'>"
		#	print	'<iframe src="http://212.193.103.21/tmp/mmap.html" width="800" height="700"></iframe>'
			print	'<iframe src=" http://wialon.rnc52.ru/locator/index.html?t=1b63c946cfcf86dcce016b989f18f16fD6D553B79EDEDEFB89EDE97EECFB9724E2B64AE1&map_type=2&zoom=17&lang=ru" width="800" height="700"></iframe>'
		#	print	'<iframe src=" http://wialon.rnc52.ru/locator/index.html?u=Агрофирма РУСЬ&zoom=17&lang=ru" width="800" height="700"></iframe>'
			print "</div><!-- dbody       -->"
		else:
			print 'REMOTE_ADDR', os.environ['REMOTE_ADDR']
			print '<h3><img onclick="document.myForm.submit();" title="Обновить" src="../img/reload3.png"> Wialon demo</h3>'
			print	'<iframe src=" http://wialon.rnc52.ru/locator/index.html?t=1d5a4a6ab2bde440204e6bd1d53b3af841235B51D73C0B07786DA3DC363D2008712C05B5&zoom=17&lang=ru" width="1200" height="700"></iframe>'
		#	print	'<iframe src=" http://wialon.rnc52.ru/locator/index.html?t=1b63c946cfcf86dcce016b989f18f16fD6D553B79EDEDEFB89EDE97EECFB9724E2B64AE1&zoom=17&lang=ru" width="800" height="700"></iframe>'
		#	print '<img onclick="document.myForm.submit();" title="Обновить" src="../img/reload3.png">'
		''
	#	print button_autos
		print	"<div id='dbody' class='hidd'>"
	#	out_form_auto ()
		print	"</div><!-- dbody	-->"
		'''
		print '</div>	<!-- container	-->'
#		print	"</form><!-- myForm	-->"
		if request.has_key('message'):
			print "<div id='message' style='text-align:center;'>%s</div>" % request['message']
		else:	print "<div id='message' style='text-align:center;'>message</div>"
	#	print """<script language="JavaScript">setTimeout ("set_message ('')", 10000);</script>"""
		print """<table><tr><td><div id='shadow'>shadow</div></td><div id='widget'>widget</div></td><td><div id='error'>error</div></td><td><div id='warnn'>warnn</div></td></tr></table>"""
		print	"""<div id="log" style='border: 1px solid #bbc; color: #668;'></div>"""
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		perror ("EXCEPT main_page", " ".join(["<pre>", str(exc_type).replace('<', '# '), str(exc_value), "</pre>"]))
		print "<span style='background-color: #ffa; color: #a00; padding: 4px;'> EXCEPT main_page:", exc_type, exc_value, "</span>"
	finally:
		print "</form></body></html>"
#################################	<i class="fa fa-cog" aria-hidden="true"></i>

def	str_time (tm, currtm = None, speed = None):
	if not tm:	return	"<span class='bferr sz12'>Нет данных!</span>"
	if not currtm:	currtm = int(time.time())
	dtm = currtm - tm
	if dtm < 60:	return	"<span class='finf sz12'> &nbsp; <b>%s</b> сек назад</span>%s" % (dtm, str_speed(speed))
	if dtm < 3600:	return	"<span class='fgrey sz12'> &nbsp; <b>%s</b> мин назад</span>%s" % (int(dtm/60), str_speed(speed))
	if dtm < 36000:	return	"<span class='fligt sz12'> &nbsp; в %s </span>%s" % (time.strftime("%T", time.localtime (tm)), str_speed(speed))
	return	time.strftime("<span class='ferr sz12'> %T %d.%m.%Y</span>", time.localtime (tm))
	
def	str_speed (sp):
	if sp == None:	return	""
	elif sp:	return	" &nbsp; <span class='fligt sz12'> v:<b>%s</b>км/ч </span>" % sp
	return 	""" &nbsp; <span class='bferr sz12'>Стоит </span>"""


def	get_tansport (request):
	""" Читать транспорт по ИНН	"""
	# CREATE  VIEW vlast_pos AS SELECT p.*, t.idd AS code, t.inn AS tinn, gosnum, marka, t.rem, bname FROM last_pos p INNER JOIN recv_ts t ON p.ida = t.device_id INNER JOIN org_desc o ON t.inn = o.inn;
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=agro_test port=5432 user=smirnov')

	org_inn = '5248037326'	#request.get('org_inn')
	bm_ssys = None	# request.get('bm_ssys')
	
	if org_inn and org_inn.isdigit() and int(org_inn) > 0:
		res = dbi.get_table('vlast_pos', 'tinn = %s ORDER BY t DESC' % org_inn)
	elif bm_ssys and bm_ssys.isdigit():
		res = dbi.get_table('vlast_pos', 'tinn IN (SELECT inn FROM org_desc WHERE bm_ssys & %s = %s) ORDER BY t DESC' % (bm_ssys, bm_ssys))
	else:	res = dbi.get_table('vlast_pos', 'tinn >0 ORDER BY t DESC')
	if not res:	return	# data
	d = res[0]
#	print 'org_inn', org_inn, len(res[1]), 'bm_ssys:', bm_ssys
	ddd = []
	gosnum = '??? '
	jtm = int(time.time())
	for r in res[1]:
		tr = r[d.index('t')]
		if jtm - tr > 3600*24:
			icon = 'grey'
		elif jtm - tr > 3600:
			icon = 'blue'
		else:	icon = 'green'
		if r[d.index('gosnum')]:
			gosnum = '%s' % r[d.index('gosnum')]
		else:	gosnum = '%s' % r[d.index('nm')]
		'''
		if r[d.index('sp')] and r[d.index('sp')] > 0:
			gosnum += ' &nbsp; v:%dкм/ч' % r[d.index('sp')]
		else:	gosnum += ' <span class=bferr>Стоит</span>'
		'''
		gosnum = gosnum.replace("'", '')	#'QWERTY'
		if res:
			opts = {'icon': icon, 'gosnum': gosnum, 'dt': '%s' % str_time (r[d.index('t')], jtm).replace("'", '')}
			'''
			if r[d.index('bname')] and r[d.index('bname')] != '':
				opts['bn'] = "<span class=bfligt>%s </span><br />" % r[d.index('bname')].replace('"', " ")
			'''
			if r[d.index('sp')] and r[d.index('sp')] > 0:
				opts['sp'] = ' &nbsp; v:%dкм/ч' % r[d.index('sp')]
			else:	opts['sp'] = ' &nbsp; <span class=bferr>Стоит</span>'
			if r[d.index('y')] and r[d.index('x')]:
				ddd.append([[float(r[d.index('y')]), float(r[d.index('x')])], opts])
			else:	ddd.append([[0.0, 0.0], opts])
		else:
			if r[d.index('bname')] and r[d.index('bname')] != '':
				gosnum += '<br><b>%s</b>' % r[d.index('bname')].replace('"', " ")
			if r[d.index('marka')]:	gosnum += '<br>' +r[d.index('marka')]
			ddd.append([float(r[d.index('x')]), float(r[d.index('y')]), '%s' % str_time (r[d.index('t')], jtm).replace("'", ''), gosnum, icon])
	return	ddd
'''
#	371 	Агрофирма РУСЬ 	item 
def	search_szone (itemId = 371):
	import	twlp
	cols = []
	for j in xrange(255):   cols.append(j)
	data = {'sid': request['wsid'], 'svc': 'resource/get_zone_data', 'params': {'itemId': itemId, 'col': cols, 'flags': -1}}
	fres, sres = twlp.requesr(data)
	print   sres
'''

'''
var polyline = new L.Polyline([
  [-45, 45],
  [45, -45],[33,-33]
], {
  color: 'green',
  weight: 5,
  opacity: 0.5
}).addTo(map);
'''
def	set_gzone (request):
	""" Показать / Скрыть геозону	"""
	gzid = request.get('gzid')
	if not (gzid and gzid.isdigit()):
		print 'set_gzone', request, gzid
		return
#	print 'ZZZZZ set_gzone', request, gzid
	igzid = int(gzid)
	rid = igzid/1000
	rzid = igzid%1000
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=agro_test port=5432 user=smirnov')
	if rzid == 0:	# Сканировать ВСЕ зоны
		list_zids = []
		rzids = dbi.get_rows("SELECT id FROM zborder WHERE rid = %s" % rid)
		for r in rzids:		list_zids.append(r[0])
		print "~eval| clear_map_object(list_regionn);"
	else:
		list_zids = [rzid]
	gzids = []
	for zid in list_zids:
		dzon = dbi.get_dict("SELECT * FROM zborder WHERE rid = %s AND id = %s" % (rid, zid))
	#	print dzon['p']
		gzids.append(1000*rid +zid)
		plist = []
		for p in dzon['p'][1:-1].replace('),(', '):(').split(':'):
			xy = p[1:-1].split(',')
			plist.append(xy[1] +','+ xy[0])
		print "~eval| list_regionn[%s] = L.polygon([[%s]], {color: '#%06x'}).addTo(mymap).bindPopup('%s');" % ((1000*rid +zid), '],['.join(plist), (0xffffff & dzon['c']), dzon['n'])
	if rzid == 0:
		print "~eval| check_gzone_list (%s); " % str(gzids)

def	view_gzones (request):
	itemId = 371
	print '~rmiddle|'
	print '~rtop|'
	print """<div class='list-group-item list-group-item-action active tit'><span class='tit'> <i class="fa fa-object-ungroup fa-lg" aria-hidden="true"></i> Поля:</span>
		<span class="float-right" onclick="set_zone_list ('%s'); "> Показать все </span></div>""" % (1000*itemId)

	inn = request.get('org_inn')
	if not (inn and inn.isdigit()):	return
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=agro_test port=5432 user=smirnov')
	res = dbi.get_table ('zborder', 'rid = (SELECT iid FROM org_desc WHERE inn = %s) ORDER BY id' % inn)	#itemId)
	if not res:	return
	d = res[0]
	gzids = []
	for r in res[1]:
		gzid = 1000*itemId + r[d.index('id')]
		gzids.append(gzid)
		print """<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center' >
			<span id='li%s' onclick="set_zone_list ('%s');"> %s </span> <span class="badge badge-primary badge-pill" style="background-color: #%06x; color: #%06x; opacity: 0.8">%s
			<span onclick="set_shadow('gzon_infoww&gzid=%s');">&nbsp; <i class="fa fa-flag fa-lg" aria-hidden="true"></i>&nbsp;</span>
			</span></li>""" % (
			gzid, gzid, r[d.index('n')], (0xffffff & r[d.index('c')]), (0xffffff & (0xffffff ^ r[d.index('c')])), r[d.index('c')], gzid)
	print "~eval| check_gzone_list (%s); " % str(gzids)

def	view_tranports (request):
	itemId = 371
	inn = request.get('org_inn')
	print '~rtop|'# request['org_inn']
	print """<div class='list-group-item list-group-item-action active'><span class='tit'> <i class="fa fa-truck fa-lg" aria-hidden="true"></i> Транспорт:</span><span class="float-right">
		<i class="fa fa-times fa-lg" aria-hidden="true" onclick="$('#rmiddle').html('')"></i>&nbsp;</span></div>"""
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=agro_test port=5432 user=smirnov')
#	res = dbi.get_table ('agro_ts', 'inn = %s AND iid > 0 ORDER BY gosnum' % inn)
	res = dbi.get_table ('agro_ts t LEFT JOIN last_pos p ON t.idd = p.idd', 't.inn = %s AND t.iid > 0 ORDER BY gosnum' % inn, 't.*, p.x, p.y, p.t, p.sp, p.st')
	if not res:
		if not dbi.last_error:	print "<span class='bfinf'> Нет данных! </span>"
		return
	d = res[0]
	for r in res[1]:
		if len(r[d.index('gosnum')]) < 14:
			gosnum = r[d.index('gosnum')] + '&nbsp;' * (14 - len(r[d.index('gosnum')]))
		if not r[d.index('t')]:
			onclick = "alert('Нет данных!')"
			gosnum = "<span class='bferr'>%s</span>" % gosnum	# r[d.index('gosnum')]
			buttons = """<span style="font-size:16px; padding: 2px;">
			<i class="fa fa-area-chart" aria-hidden="true"></i> 
			<i class="fa fa-cog" aria-hidden="true"></i>
			<i class="fa fa-wrench fa-rotate-270" aria-hidden="true"></i>
			<i class="fa fa-flag" aria-hidden="true"></i>
			</span>"""
		else:
		#	onclick = "set_shadow('view_cradar&idd=%s'); mymap.setView([%s,%s]);" % (r[d.index('idd')], r[d.index('y')], r[d.index('x')])	#, r[d.index('idd')])
			onclick = "mymap.setView([%s,%s]);" % (r[d.index('y')], r[d.index('x')])
			gosnum = "<span class='bfinf'>%s</span>" % gosnum	# r[d.index('gosnum')]
			buttons = """<span style="font-size:16px; padding: 2px;" class='bfinf'>
			<i title='Графики' class="fa fa-area-chart" aria-hidden="true" onclick="set_shadow('view_cradar&idd=%s');"></i> 
			<i title='Параметры' class="fa fa-cog" aria-hidden="true" onclick="set_shadow('sets_params&idd=%s');"></i>
			<i class="fa fa-wrench fa-rotate-270" aria-hidden="true"></i>
			</span>""" % (r[d.index('idd')], r[d.index('idd')])
		'''
		print onclick, gosnum, str_time(r[d.index('t')])"<br>"
		'''
		print """<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'>
			<span onclick="%s"> %s %s </span> <span class="badge badge-primary badge-pill" style="background-color: #ddf; "> %s </span> </li>""" % (
			onclick, gosnum, str_time(r[d.index('t')], speed = r[d.index('sp')]), buttons )	#, r[d.index('iid')], r[d.index('iid')])

def	view_canvas (request):
#	print "~rmiddle|"
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=agro_test port=5432 user=smirnov')
	sidd = request.get('idd')
	if not (sidd and sidd.isdigit()):
		sidd = '864287036627055'	#'864287036627501'
		print "DEBUG"
	dayss = 86400	# Интервал просмотра (1 день)
	dtime = 600	# Интервал усреднения (10 мин)
	t00 = int ((time.time()/dtime)) *dtime - dayss
	t24 = t00 +dayss
#	ГАРАЖ                     | 43.5576794388 | 43.5630507866 | 56.8218509240 | 56.8249534109
	X0 = (43.5576794388 + 43.5630507866)/2
	Y0 = (56.8218509240 + 56.8249534109)/2
	print time.strftime("<br>\tt00 %D %T", time.localtime(t00))
	print time.strftime("<br>\tt24 %D %T", time.localtime(t24))
	t_24 = int(time.time()/dtime ) * dtime - dayss -2*dtime 
	print time.strftime("<br>\tt_24 %D %T", time.localtime(t_24))
#	res = dbi.get_table ('data_pos', "idd = '%s' AND t > %s AND t < %s ORDER BY t" % (sidd, t00, t24))
	swhere = "idd = '%s' AND t > %s  ORDER BY t " % (sidd, t_24)
	print swhere, '\n'
	res = dbi.get_table ('vdata_pos', swhere)	#"idd = '%s' AND t > %s  ORDER BY t " % (sidd, t_24))
	if not res:
		print "<span class='bferr'>Нет данных!</span>"
		return
	d = res[0]
	data = []
	dtms = []
	dspeed = []
	dr = pr = 0.0
	dsp = psp = 0.0
	Rz = (6378.2450+6356.863019)/2	# Радиус земли km 6371.302
	gosnum = None
	import	math
	points = []
	for r in res[1]:
		if not gosnum:	gosnum = r[d.index('gosnum')]
	#	if not r[d.index('x')]:	continue
		rt = r[d.index('t')]
		
#		print time.strftime("<br> %D %T", time.localtime(rt)), pr
		if r[d.index('x')]:
			points.append("[%s,%s]" % (float(r[d.index('y')]), float(r[d.index('x')])))
			pr = ((X0-float(r[d.index('x')]))**2 + (Y0-float(r[d.index('y')]))**2)
			pr = Rz*math.sqrt(pr)*math.pi/180
			psp = float(r[d.index('sp')])
			if dr == 0.0:	dr = pr
			if dsp == 0.0:	dsp = psp
		if rt > t00 + dtime:
			data.append("%.1f" % dr)	#int(dr + 0.5))
			dspeed.append("%d" % int(dsp))
			t00 += dtime
#			print	time.strftime('%T %d', time.localtime(t00)), dr, int(dr + 0.5)
			dtms.append(time.strftime('%H:%M', time.localtime(t00)))
		dr = (dr + pr)/2
		dsp = (dsp + psp)/2
	'''
	#	print dr
#	print data
#	data.reverse()
	print '<br>', dtms, len (dtms), t_24
#	dtms.reverse()
	print '<br>', dtms, len (dtms)
	print '<br>', data, len (data)
	'''
	print "~rmiddle|<div style='height: 200px;'>"	#<canvas id='timeChart' width=400 height=200></canvas></div>"
	###	Highcharts.chart
	print "<div id='QWERTY' style='height: 300px;'></div>"
	print """~eval|$(function () { 
	hchart_test = Highcharts.chart('QWERTY', {
        chart: { type: 'spline' },
        title: { text: '<b>%s</b>' },
        xAxis: { visible: true, categories: ['%s'], title: {text: 'Время'}},
        yAxis: { visible: true, min: 0.0, title: { text: 'Расстояние до гаража' } },
        series: [{ name: 'Расстояние км', data: [%s]
        	},{ name: 'Скрость км/ч', color: '#ff6666', data: [%s]
        }] }); }); """ % (gosnum, "','".join(dtms), ",".join(data), ",".join(dspeed))
#	print "~eval| list_tracks['red'] = new L.Polyline([ [56.5,44], [57,44], [57,43.5], [56.5, 43.5] ], { color: 'red', weight: 3, opacity: 0.5 }).addTo(mymap);       mymap.fitBounds(list_tracks['red'].getBounds());"

	print "~eval| clear_map_object(list_tracks); list_tracks['blue'] = new L.Polyline([%s], { color: 'blue', weight: 3, opacity: 0.5 }).addTo(mymap);       mymap.fitBounds(list_tracks['blue'].getBounds());" % ",".join(points)

'''
	print """~eval| big_canvas('#timeChart', '%s', '%s');""" % (json.dumps(dtms), json.dumps(data))
	print "~eval| view_canvas('#timeChart');"
	print "~eval| my_canvas('#timeChart', '%s');" % json.dumps(data)
'''

def	ajax (sname, request, referer):
	shstat = request.get('shstat')
	print "~log|"	#AJAX:", request, '<br />'	#, referer, sname
	if shstat in ['view_report', 'list_reports', 'gzon_infoww']:
		import	areports
		if shstat == 'list_reports':
			areports.list_reports (request)
			print "~eval| document.myForm.status.value='%s';" % shstat
		elif shstat == 'view_report':	areports.view_report (request)
		elif shstat == 'gzon_infoww':	areports.gzon_infoww (request)
		else:	print "#"*11, shstat
		return

	if shstat == 'get_tansport':
		ts_list = get_tansport (request)
		print "~jtime|", time.strftime("%T", time.localtime (time.time()))
		if ts_list:
			print "~eval|out_data('%s');" % json.dumps(ts_list)
		#	print "~eval| mymap.setView([56.8238, 43.5598], 14)"
		else:	print '~eval| alert("ZZZ");'
	elif shstat == 'view_canvas':
		ts_list = get_tansport (request)
		print "~jtime|", time.strftime("%T", time.localtime (time.time()))
		if ts_list:
			print "~eval|out_data('%s');" % json.dumps(ts_list)
		status = request.get('status')
		if status == 'view_tranports':	view_tranports (request)
	elif shstat == 'set_gzone':		set_gzone (request)
	elif shstat == 'view_cradar':		view_canvas (request)
	elif shstat == 'view_gzones':
		view_gzones (request)
		print "~eval| document.myForm.status.value='%s';" % shstat
	elif shstat == 'view_tranports':
		view_tranports (request)
		print "~eval| document.myForm.status.value='%s';" % shstat
	elif shstat == 'view_gosnum':
		isview = request.get('view_gosnum')
		if not isview or isview != 'on':
			print "~eval|view_gosnumber(1);"
		else:	print "~eval|view_gosnumber(2);"
	elif shstat == 'sets_params':
		import	aoptions
		aoptions.sets_params (request)
	else:
		print sname, request, referer

def	main (request, conf):
	fname = r'/home/smirnov/MyTests/html/ddd.html'
	f = open (fname, 'r')
	s = f.readline()	#'f.readline()'
	s = f.readline()	#'f.readline()'
	while s:
		s = f.readline()
		print s.strip()

if __name__ == "__main__":
#	main(None, None)
#	search_szone ()
	view_canvas ({'shstat': 'view_canvas', 'idd': '864287036626578'})
