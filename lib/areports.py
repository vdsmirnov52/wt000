#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	os, sys, time, json

LIBRARY_DIR = r"/home/smirnov/Wialon/lib/"
sys.path.insert(0, LIBRARY_DIR)

import	dbtools, cglob

db_agro = dbtools.dbtools('host=212.193.103.20 dbname=agro_test port=5432 user=smirnov')
#	update data_prms d SET iid = (SELECT iid FROM agro_ts a WHERE a.idd = d.idd) WHERE d.iid IS NULL;

dict_reports = {'probeg': 'Пробег транспорта', 'DUT': 'Отчет по ДУТ', #'pro_dut': 'Сводный рапорт', 'pro_test': 'Тестирование',
	'trans_canvas': "Работа транспорта (графики)", 'debug_canvas': "Графики DEBUG"}
default = {'days': 1, }

#	select count(*) FROM vdata_pos d LEFT JOIN data_prms p ON p.t = d.t AND d.idd = p.idd WHERE d.t > 1527832435;

def	list_reports (request):
	print '~rtop|'
	print """<div class='list-group-item list-group-item-action active'><span class='tit'> <i class="fa fa-area-chart fa-lg" aria-hidden="true"></i> Отчеты:</span><span class="float-right">
		<i class="fa fa-times fa-lg" aria-hidden="true" onclick="$('#rmiddle').html('')"></i>&nbsp;</span></div>"""
	for k in dict_reports.keys():
		print """<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'>
			<span class='tit' onclick="set_shadow('view_report&rt=%s')"> %s </span></li>""" % (k, dict_reports[k])
#	print "list_reports"
	opts_report (request)

def	opts_report (request):
	"""  Параметры для формирования отчетов	"""
	# time.strftime("%T %d-%m-%y", time.localtime(r[d.index(c)]))
	currtm = int(time.time())
	sdate_end = request.get('date_end')
	sdate_beg = request.get('date_beg')
	sdate_end = sdate_beg = ''
	if not sdate_beg:
		tm_beg = 86400 * currtm/86400 - (3600*24* default['days'])
		sdate_beg = time.strftime("%d-%m-%Y", time.localtime(tm_beg))
	if not sdate_end:
		tm_end = currtm
		sdate_end = time.strftime("%d-%m-%Y", time.localtime(tm_end))
	print "~rmiddle|"	### Параметры поиска"
#	print time.mktime(time.strptime(sdate_end, "%d-%m-%Y"))

	print """<link rel='stylesheet' type='text/css' href='/css/agro/calendar.css' /> """	#<script type='text/javascript' src='/js/agro/calendar.js'></script>"""
	print """<div class='list-group-item list-group-item-action active'><span class='tit'> <i class="fa fa-area-chart fa-lg" aria-hidden="true"></i> Параметры формирования отчета:</span><span class="float-right">
		<i class="fa fa-times fa-lg" aria-hidden="true" onclick="$('#rmiddle').html('')"></i>&nbsp;</span></div>"""
	print "<div id='div_opts' style=' height: 400px; overflow: auto;'>"
	print """<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'> Период сбора данных
		с: <input id='dp_begin' type='text' name='date_beg' value='%s' maxlength=10 style='width: 8em;' />
		по: <input id='dp_end' type='text' name='date_end' value='%s' maxlength=10 style='width: 8em;' />
		</li>""" % (sdate_beg, sdate_end)	#time.strftime("%d-%m-%Y", time.localtime(tm_beg)), time.strftime("%d-%m-%Y", time.localtime(tm_end)))
	print "</div>Графики"
	print """~eval| $('#dp_begin').datepicker(); $('#dp_end').datepicker({dateFormat: "dd-mm-yy"})"""
#	sys.exit()
	print "~log|"

def	view_report (request):
#	'date_end': '04-06-18', 'date_beg': '05-05-18'
#	print "view_report", request
	k = request.get('rt')
	if k:
		rname = dict_reports[k]
	else:	rname = "QWERTY"

	currtm = int(time.time())
	sdate_beg = request.get('date_beg')
	sdate_end = request.get('date_end') + " 23:59:59"
	if not sdate_beg:
		tm_beg = 86400 * currtm/86400 - (3600*24*days)
		sdate_beg = time.strftime("%d-%m-%Y", time.localtime(tm_beg))
	if not sdate_end:
		tm_end = currtm
		sdate_end = time.strftime("%d-%m-%Y 23:59:59", time.localtime(tm_end))
	tm_beg = time.mktime(time.strptime(sdate_beg, "%d-%m-%Y"))
	tm_end = time.mktime(time.strptime(sdate_end, "%d-%m-%Y %H:%M:%S"))
	if tm_beg > tm_end:
		print "~log|<span class='bferr'> Ошибочный интервал поиска с: %s по: %s  </span>" % (time.strftime('%d.%m.%Y', time.localtime(tm_beg)), time.strftime('%d.%m.%Y %T', time.localtime(tm_end))) #request
		return

	iddom = request.get('iddom')
	if iddom:
		print "~%s|<div class='mmodal' style='z-index: 1050; width: 1050px;'>" % iddom
	else:
		print "~widget|<div class='mmodal' style='z-index: 1050;'>"
		print """<div class='list-group-item list-group-item-action active'><span class='tit'> <i class="fa fa-area-chart fa-lg" aria-hidden="true"></i> %s
		с: %s  по: %s		
		</span><span class="float-right">
		<i class="fa fa-times fa-lg" aria-hidden="true" onclick="$('#widget').html('')"></i>&nbsp;</span></div>""" % (rname, sdate_beg, sdate_end)

	if k == 'pro_dut':		pro_dut (request, tm_beg, tm_end)	
	elif k == 'debug_canvas':	debug_canvas (request, tm_beg, tm_end)
	elif k == 'trans_canvas':	trans_canvas (request, tm_beg, tm_end)
	elif k == 'pro_test':
		print """<header>Заголовок (header)</header>
		<section>1. В отчете по пробегу помимо длительности каждой поездки, хотелось бы видеть конкретную дату и время каждой поездки.<br>
		 ВОПРОС:  возможно ли совмещение отчетов по пробегу и по дут????</section>
		<section> 2. Отчет по ДУТ - по каждой машине, по каждому дню остатки на начало и на конец дня, а не только периоды заправки или сливов.
		</section>
		<footer>Подвал (footer)</footer>
		"""
	elif k == 'DUT':
		cols = ['Объекты', 'Ширина агрегата', 'Поле', 'Первый выезд', 'Последний выезд', 'Время движения, Простой', 'Пробег, км', 'Средн. скорость, км/ч', 'Расход, л', 'Общая площадь, га',
		'Обработанная площадь, га', 'Плошадь наложений, га', 'Плошадь необраб. га', 'Производи тельность, га/сутки', 'Расход, л/га', ]
		print "<table><tr align='center' valign='top' bgcolor=#ccccee>"
		for th in cols:
			print "<td valign='top'>%s</td>" % th
		print "</tr><tr>"
		for td in xrange(len (cols)):
			print "<td> val %03d </td>" % td
		print "</tr></table>"
	elif k == 'probeg':
		probeg (request, tm_beg, tm_end)
		return
	else:	print '#'* 55, k
	print "</div>"

def	translit (string, code = 'utf-8'):
	rs = []
	for c in unicode(string, code).encode('koi8-r'):	rs.append (chr(0x7f & ord(c)))
	return	"".join(rs)

def	probeg (request, tm_beg = None, tm_end = None):
	""" Пробег	"""
	conf = aconf.aconf()
	print	'tm_beg', tm_beg, 'tm_end', tm_end
	currtm = 86400 * int(time.time()/86400) - (3600*24*30)
	zrid = 371
	zid = 1
	stm = time.time()	### DEBUG
	print """<div style='height: 400px; overflow: auto; padding: 11px;'><table border=2px width=100%%>
		<tr align='center'><th>Объект</th><th>Дата</th><th> Пробег (км) </th>
		<th> Остаток топлива (л) </th>
		<th> Расход топлива (л) </th>
		<th> Общий пробег (км) </th>
		<th> Общий Расход топлива (л) </th>
		<th> Остаток топлива (л) </th></tr>"""
	jtr = 0
	for gosnum in conf.ts_reports:
		ls_time = [ time.strftime("%d-%m-%y", time.localtime(tm_beg)) ]
		ls_gpsmil = []		# Пробег
		ls_flevel = []		# Расход топлива
		ls_BOflevel = []	# остаток на начало суток
		jtm = tm_beg + 86400

	#	print "<tr id='_%s'><td><span class='bfinf'> %s </span></td>" % (translit(gosnum), gosnum)
		swhere = "d.t > %s AND d.t != %s AND j.gosnum = '%s' AND j.id_dp = d.id_dp ORDER BY d.t " % (tm_beg, tm_end, gosnum)
		res = conf.db_agro.get_table ('journal_ts j, data_pos d', swhere, "j.*, d.t, d.x, d.y, d.sp")
		if res:
			if jtr % 2:	trcolor = "bgcolor=#eeeeff"
			else:		trcolor = ""
			jtr += 1
			print "<tr id='_%s' %s><td><span class='bfinf'> %s </span></td>" % (translit(gosnum), trcolor, gosnum)
			d =	res[0]
			gpsmil0 = None
			flevel0 = Sflevel = Oflevel = BOflevel = None
			flevel_up = False
			'''
			flevel0 =	float(r[d.index('flevel')])
			ftank0 =	float(r[d.index('ftank')])
			ftank10 =	float(r[d.index('ftank1')])
			Sfsp =		float(r[d.index('fsp')])
			Sgpssp =	float(r[d.index('gpssp')])
				Sfsp +=		float(r[d.index('fsp')])
				Sgpssp +=	float(r[d.index('gpssp')])
			'''
			j = 0
			for r in res[1]:
				if r[d.index('gpsmil')]:	# Пробег
					jgpsmil = float(r[d.index('gpsmil')])
					if not gpsmil0:		gpsmil00 = gpsmil0 = jgpsmil
				if r[d.index('t')] > jtm:	# Конец суток
					ls_time.append (time.strftime("%d-%m-%y", time.localtime(jtm)))
					ls_gpsmil.append ('%6.2f' % (jgpsmil - gpsmil0))
					gpsmil0 = jgpsmil
					if type(Sflevel) == float:	ls_flevel.append ('%6.2f' % Sflevel)
					if type(Oflevel) == float:
						BOflevel = Oflevel
						ls_BOflevel.append ('%6.2f' % BOflevel)

					jtm += 86400

					'''
				if r[d.index('gpsmil')]:
					jgpsmil = float(r[d.index('gpsmil')])
					if not gpsmil0:		gpsmil00 = gpsmil0 = jgpsmil
					'''
				if r[d.index('flevel')]:
					Oflevel = jflevel = float(r[d.index('flevel')])
					if not flevel0:
						BOflevel = flevel0 = jflevel
						ls_BOflevel.append ('%6.2f' % BOflevel)
					if jflevel > flevel0:
						if flevel_up == False:
							flevel_up = True
							Sflevel = flevel0 - oflevel
						else:	flevel0 = jflevel
					else:
						flevel_up = False
						oflevel = jflevel

			ls_gpsmil.append ('%6.2f' % (jgpsmil - gpsmil0))
			if type(Sflevel) == float:	ls_flevel.append ('%6.2f' % Sflevel)
			print "<td align='center'> %s </td>" % "<br>".join(ls_time)
			print "<td align='right'> %s </td>" % "<br>".join(ls_gpsmil)
			print "<td align='right'> %s </td>" % "<br>".join(ls_BOflevel)
			print "<td align='right'> %s </td>" % "<br>".join(ls_flevel)

			print "<td align='right'> %6.2f </td>" % (jgpsmil - gpsmil00)
			'''
			'''
			if type(Sflevel) == float:
				print "<td align='right'> %6.2f </td>" % Sflevel
			else:	print "<td> &nbsp; </td>"	#<span class='bferr'> None </span></td>"
			if type(Oflevel) == float:
				print "<td align='right'> %6.2f </td>" % Oflevel
			else:	print "<td> &nbsp; </td>"
		#	print "<td> % </td>"	
		#	print "<td> % </td>"	
		#	print "<td>", r[d.index('gpsmil')], type(r[d.index('gpsmil')]), float(r[d.index('gpsmil')]), "</td>"
	#	else:	print "<td><span class='bferr'> Нет данных!</span></td>"
	#	print "<td>", translit(gosnum), "</td>"
			print "</tr>"
	print "</table></div>"
	print "DTM:", time.time() - stm		### DEBUG
	'''
#	res = db_agro.get_table ('vdata_pos', "point (x,y) @ (select p FROM zborder WHERE rid = %s AND id = %s) AND t > %s ORDER BY idd, t DESC LIMIT 11;" % (zrid, zid, currtm))
	res = db_agro.get_table ('last_prms p, vdata_pos d', "p.tm + p.dtm = d.t AND p.idd = '864287036627022' ORDER BY d.t;", "d.gosnum, d.t, d.sp, p.dtm, p.params")
	out_table(res)
	'''

def	out_table(res):
	d = res[0]
	print "<div id='div_table' style=' height: 400px; overflow: auto;'>"
	print "<table>"
	print "<tr><th>%s</th></tr>" % "</th><th>".join(d)
	for r in res[1]:
		print "<tr><td>"
		for c in d:
			if c == 'idd':		continue
			if c == 'id_dp':	continue
			if c == 't':
				v = time.strftime("%T %d-%m-%y", time.localtime(r[d.index(c)]))
			else:	v = r[d.index(c)]
			print v, "</td><td>",
		print "</td></tr>"
	print "</table>"
	print "<div>"

import	aconf

def	trans_canvas (request, tm_beg = None, tm_end = None, gosnum = 'Н213ВК152'):
	conf = aconf.aconf()
#	gosnum = 'Н213ВК152'
#	gosnum = '52НР9988'
	print "<table border=0 width=100%><tr><td width=5% valign='top'>"
	for gosnum in conf.ts_reports:
		print """<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'>
			<span class='bfinf' onclick="set_shadow('view_report&rt=debug_canvas&gosnum=%s&iddom=trans_canvas')"> %s </span> </i>""" % (gosnum, gosnum)
	print "</td><td id='trans_canvas' style='height: 310px;' valign='top'> &nbsp; </td></tr></table>"
'''
<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'>
			<span onclick="mymap.setView([56.824147,43.560653]);"> <span class='bfinf'>52НН5225&nbsp;&nbsp;&nbsp;&nbsp;</span> <span class='fgrey sz12'> &nbsp; <b>2</b> мин назад</span> &nbsp; <span class='bferr sz12'>Стоит </span> </span> <span class="badge badge-primary badge-pill" style="background-color: #ddf; "> <span style="font-size:16px; padding: 2px;" class='bfinf'>
			<i title='Графики' class="fa fa-area-chart" aria-hidden="true" onclick="set_shadow('view_cradar&idd=864287036420295');"></i> 
			<i title='Параметры' class="fa fa-cog" aria-hidden="true" onclick="set_shadow('sets_params&idd=864287036420295');"></i>
			<i class="fa fa-wrench fa-rotate-270" aria-hidden="true"></i>
			</span> </span> </li>
'''
	
def	debug_canvas (request, tm_beg = None, tm_end = None):
	conf = aconf.aconf()
	tm_beg = int (tm_beg)
	tm_end = int (tm_end)
	gosnum = request.get ('gosnum')
	if not gosnum:	gosnum = 'Н213ВК152'
	iddom = request.get ('iddom')	# trans_canvas
	if iddom:	print "~%s|" % iddom

	swhere = "d.t > %s AND d.t != %s AND j.gosnum = '%s' AND j.id_dp = d.id_dp ORDER BY d.t " % (tm_beg, tm_end, gosnum)
#	print "WHERE", swhere
	res = conf.db_agro.get_table ('journal_ts j, data_pos d', swhere, "j.*, d.t, d.x, d.y, d.sp")
	if not res:
		print "<span class='bfinf'>%s</span> <span class='bferr'>Нет данных!</span>" % gosnum
		return
	d = res[0]
	'''
	print d
	dtms = ['01', '02', '03', '04', '05']
	data = ['11', '22', '33', '24', '15']
	dspeed = ['51', '42', '13', '24', '55']
	'''
	Rz = (6378.2450+6356.863019)/2	# Радиус земли km 6371.302
	X0 = (43.5576794388 + 43.5630507866)/2	# Координаты гаража
	Y0 = (56.8218509240 + 56.8249534109)/2

	if (tm_end - tm_beg) < 86400:
		dtime = 300
	else:	dtime = 600	# Интервал усреднения (10 мин)
	t00 = tm_beg
	dtms = [time.strftime('%d %b %H:%M', time.localtime(t00))]
	data = []
	dspeed = []
	dfspeed = []
	dr = pr = 0.0
	dsp = psp = 0.0
	dfsp = pfsp = 0.0
	d_pwr = []
	d_zid = []
	szid = 0
	d_flevel = []
	jpoints = []
	flevel = 0.0
	d_pwr_in = []
	pwr_in = 0

	import	math
	j = 0
	if tm_end > time.time():	tm_end = dtime+ time.time()
	for t00 in xrange (int(tm_beg), int(tm_end), dtime):
		jp = 0
		while j < len (res[1]):
			r = res[1][j]
			rt = r[d.index('t')]
			jp += 1
			if rt > t00:		break	##########
			if r[d.index('zid')] and r[d.index('zid')] > 0:
				szid = 10+ r[d.index('zid')]
			else:	szid = 0

			if r[d.index('x')]:
				pr = ((X0-float(r[d.index('x')]))**2 + (Y0-float(r[d.index('y')]))**2)
				pr = Rz*math.sqrt(pr)*math.pi/180
				if dr == 0.0:	dr = pr
				psp = float(r[d.index('sp')])
				if dsp == 0.0:	dsp = psp
				dr = (dr + pr)/2
				dsp = (dsp + psp)/2
			else:
				dr = dsp = dfsp = 0.0
			j += 1
		if r[d.index('pwr_in')] != None:
			d_pwr_in.append ("%d" % (10*r[d.index('pwr_in')]))
		else:	d_pwr_in.append ('-5')
		if jp > 1:
			jpoints.append ('30')
		else:	jpoints.append ('0')
		if r[d.index('flevel')]:	d_flevel.append ("%5.2f" % (r[d.index('flevel')]/10))
		if r[d.index('pwr')] and r[d.index('pwr')] > 6:
			d_pwr.append(str(int(r[d.index('pwr')])))
		else:	d_pwr.append("0")
		d_zid.append("%d" % (szid))
		data.append("%.1f" % dr)
		dspeed.append("%d" % int(dsp))
		if (t00+10800) % 86400 == 0:
			dtms.append(time.strftime('%d %b %H:%M', time.localtime(t00)))
		else:	dtms.append(time.strftime('%H:%M', time.localtime(t00)))
#	print d_pwr_in
	'''
	for r in res[1]:
	#	if not gosnum:	gosnum = r[d.index('gosnum')]
	#	if not r[d.index('x')]:	continue
		rt = r[d.index('t')]
		
		if r[d.index('zid')] and r[d.index('zid')] > 1:
			szid = r[d.index('zid')]
		else:	szid = int(4*szid/5)

#		print time.strftime("<br> %D %T", time.localtime(rt)), pr
		if r[d.index('x')]:
			pr = ((X0-float(r[d.index('x')]))**2 + (Y0-float(r[d.index('y')]))**2)
			pr = Rz*math.sqrt(pr)*math.pi/180
			if dr == 0.0:	dr = pr
			psp = float(r[d.index('sp')])
			if dsp == 0.0:	dsp = psp

			if r[d.index('fsp')]:	pfsp = float(r[d.index('fsp')])
			if dfsp == 0.0:	dfsp = pfsp

		if rt > t00 + dtime:
			data.append("%.1f" % dr)	#int(dr + 0.5))
			dspeed.append("%d" % int(dsp))
			dfspeed.append("%d" % int(dfsp))
			if r[d.index('flevel')]:	d_flevel.append ("%5.2f" % (r[d.index('flevel')]/10))
			if r[d.index('pwr')] and r[d.index('pwr')] > 6:
				d_pwr.append(str(2*int(r[d.index('pwr')])))
			else:	d_pwr.append("0")
			d_zid.append("%d" % (5*szid))
			t00 += dtime
#			print	time.strftime('%T %d.%m.%Y', time.localtime(t00)), dr, int(dr + 0.5), "<br>"
			if (t00+10800) % 86400 == 0:
				dtms.append(time.strftime('%d %b %H:%M', time.localtime(t00)))
			else:	dtms.append(time.strftime('%H:%M', time.localtime(t00)))
		dr = (dr + pr)/2
		dsp = (dsp + psp)/2
		dfsp = (dfsp + pfsp)/2
#	print "<hr>", rt,  (rt-tm_beg)/3600, time.strftime('%T %d.%m.%Y', time.localtime(r[d.index('t')])) 
#	return
	'''
	print "<div id='debug_canvas' style='height: 300px;'></div>"	
	print "</div>"
	chart = "type: 'spline'"
	title = "text: '<b>%s</b>'" % gosnum
	xAxis = "visible: true, categories: ['%s'], title: {text: ''}" % "','".join(dtms)
	yAxis = "visible: true, min: 0.0, title: { text: '' }"	# "visible: true, min: 0.0, title: { text: 'Расстояние до гаража' }"
	exits = "name: 'Расстояние км', data: [%s]" % ",".join(data)
	speed = "name: 'Скрость км/ч', color: '#ff6666', data: [%s]" % ",".join(dspeed)
	fspeed = "name: 'V GPS км/ч', color: '#ee66bb', data: [%s]" % ",".join(dfspeed)
#	power = "name: 'pwr', color: '#dddddd', data: [%s]" % ",".join(d_pwr)
	series_list =  [exits, speed]
	if jpoints:	series_list.append ("name: 'jPoint', color: '#00ffcc', fillOpacity: 0.5, data: [%s]" % ",".join(jpoints))
	if dfspeed:	series_list.append ("name: 'Скрость км/ч', color: '#ff6666', data: [%s]" % ",".join(dspeed))
	if d_flevel:	series_list.append ("name: 'Уровеннь топлива, x10 л', color: '#aa7700', data: [%s]" % ",".join(d_flevel))
	if d_pwr:	series_list.append ("name: 'Зажигание', color: '#ccccdd', data: [%s]" % ",".join(d_pwr))
	if d_pwr_in:	series_list.append ("name: 'pwr_in', color: '#ccccff', data: [%s]" % ",".join(d_pwr_in))
	if d_zid:	series_list.append ("name: 'Поле', color: '#00aa00', data: [%s]" % ",".join(d_zid))

	series = "},\n{".join(series_list)
	print """~eval|
	$(function () {hchart_test = Highcharts.chart('%s', { chart: { %s }, title: { %s }, xAxis: { %s }, yAxis: { %s },
	series: [{ %s }]
	}); });
	""" % ('debug_canvas', chart, title, xAxis, yAxis, series)
	sys.exit()

def	pro_dut (request, tm_beg = None, tm_end = None):
	print """ Пробег + ДУТ	"""
	
	currtm = int(time.time())
	if not tm_beg:		tm_beg = 86400 * currtm/86400 - (3600*24* default['days'])
	if not tm_end:		tm_end = currtm

	print	'tm_beg', tm_beg, time.strftime('%d.%m.%Y %T', time.localtime(tm_beg)), 'tm_end', time.strftime('%d.%m.%Y %T', time.localtime(tm_end))
	print "<div id='div_table' style=' height: 400px; overflow: auto;'>"
	GZ = gzohes(db_agro) 
	stm = time.time()	### DEBUG
	conf = aconf.aconf()
#	print conf.gz_reports
	print """<table width=100%><tr><th>Объекты</th><th>Поле</th><th>Выезд</th><th>В поле</th>
		</tr>"""
	for gosnum in conf.ts_reports:
	#	res = conf.db_agro.get_table ('journal_ts j, data_pos d', "d.t > %s AND gosnum = '%s' AND j.id_dp = d.id_dp " % (tm_beg, gosnum), "j.*, d.t")
		res = conf.db_agro.get_table ('journal_ts j, data_pos d', "d.t > %s AND gosnum = '%s' AND j.id_dp = d.id_dp AND (j.t_in > 0 OR j.t_out > 0)  " % (tm_beg, gosnum), "j.*, d.t")
		if res:
			d = res[0]
		#	pwr  | gpsmil  | flevel
			print "<tr><td>", gosnum, "</td>"
#			print "<td>", len(res[1]), "</td>"
			j = 0
			zid = 0
			t_in = 0
			gpsmil = flevel = 0.0
			while j < len(res[1]):
				r = res[1][j]
				j += 1
				if r[d.index('zid')]:
					if r[d.index('zid')] != zid:
						zid = r[d.index('zid')]
						t_in = r[d.index('t')]
						gpsmil = r[d.index('gpsmil')]
						flevel = r[d.index('flevel')]
				elif r[d.index('t_out')]:
					if zid == 0:	continue
					print "<td> ", zid, gpsmil, flevel, " </td>"
				else:
					 print "<td> ??? </td>"
				'''
					continue
				elif r[d.index('zid')] > 0:
					zid = r[d.index('zid')]
					if jtr:	print "<tr><td> ## </td>"
					print "<td> %s </td>" % conf.gz_reports[zid]['name']
					if r[d.index('t_in')]:
						print "<td> %s </td>" % time.strftime('%T', time.localtime(r[d.index('t_in')]))
					else:	print "<td> </td>"
				else:
					if r[d.index('t_out')]:
						print "<td> %s </td>" % time.strftime('%T', time.localtime(r[d.index('t_out')]))
					else:	print "<td> </td>"
				'''
					
			print "</tr>"
		else:	print "<td>Нет данных!</td>"
	print "</table>"
	return
#	SELECT j.*, d.t, d.x, d.y FROM journal_ts j, data_pos d  WHERE gosnum = '52НР0741' AND j.id_dp = d.id_dp AND j.pwr IS NULL ORDER BY d.t  ;
	res = db_agro.get_table ("vdata_pos d LEFT JOIN data_prms p ON p.t = d.t AND d.idd = p.idd", "d.t > %s AND d.t < %s ORDER BY d.gosnum, d.t" % (tm_beg, tm_end), "d.*, p.iid, p.params")
	if not res:
		print "<span class='bferr'> pro_dut: tm_beg: %s tm_end: %s  </span>" % (time.strftime('%d.%m.%Y', time.localtime(tm_beg)), time.strftime('%d.%m.%Y', time.localtime(tm_end))), request
		print "d.t > %s AND d.t < %s ORDER BY d.gosnum, d.t" % (tm_end, tm_beg), 'RES', res
		return
	d = res[0]
	
	dict_ts = {}
	ordr_ts = []
	for r in res[1]:
		if not r[d.index('x')]:	continue
		z = GZ.find_gzone(float(r[d.index('x')]), float(r[d.index('y')]))
		if not z:	continue
		gosnum = r[d.index('gosnum')]
		if gosnum in ordr_ts:
			continue
			if z in dict_ts [gosnum]['gzs']:	continue
			else:
				dict_ts [gosnum]['gzs'].append(z)
				dict_ts [gosnum][z] = {'t0': time.strftime("%T %d-%m-%y", time.localtime(r[d.index('t')]))}
		else:
			ordr_ts.append (gosnum)
			dict_ts [gosnum] = {'gzs': [z], z: {'t0': time.strftime("%T %d-%m-%y", time.localtime(r[d.index('t')]))} }	#, GZ.gzdict[z]['name'], r[d.index('t')]]}
		'''
		'''
		print r[d.index('gosnum')], GZ.gzdict[z]['name'], time.strftime("%T %d-%m-%y", time.localtime(r[d.index('t')])), r[d.index('params')], "<br>"
#	print ordr_ts
#	print dict_ts
	print '#'*33
	for g in ordr_ts:
		print g, dict_ts[g], "<br>"
	print "<div>"
	print "Dtm:", (time.time() - stm)	### DEBUG
#	out_table(res)

def	gzon_infoww (request):
	""" Кто Работа в поле	"""
	days = 1	# Сколько дней
	gzid = request.get('gzid')
	if not (gzid and gzid.isdigit()):
		print "<span class='bferr'> gzon_infoww </span>", request
		return
	igzid = int(gzid)
	zrid = int (igzid/1000)
	zid = igzid % 1000
	print '~rmiddle|'
	dzone = db_agro.get_dict ("select * FROM zborder WHERE rid = %s AND id = %s" % (zrid, zid))
	print """<div class='list-group-item list-group-item-action active'><span class='tit'> <i class="fa fa-truck fa-lg" aria-hidden="true"></i> Выезд в %s </span><span class="float-right">
		<i class="fa fa-times fa-lg" aria-hidden="true" onclick="$('#rmiddle').html('')"></i>&nbsp;</span></div>""" % dzone['n']


	stm = time.time()	### DEBUG
	currtm = 86400 * int(time.time()/86400) - (3600*24*days)
	res = db_agro.get_table ('vdata_pos', "x > 0 AND point (x,y) @ (select p FROM zborder WHERE rid = %s AND id = %s) AND t > %s ORDER BY t DESC;" % (zrid, zid, currtm))
	'''
	res = db_agro.get_table ('vdata_pos', "x > 0 ORDER BY idd, t DESC;")
	GZ = gzohes(db_agro, zrid)
	'''
	if not res:
		if not db_agro.last_error:	print "<span class='bfinf'> Нет данных! </span>"
		return
	print "Dtm:", (time.time() - stm)	### DEBUG
	print "<div id='div_table' style=' height: 300px; overflow: auto;'>"
	d = res[0]
#	print "lem", len(res[1])
	order = []
	wdict = {}
	for r in res[1]:
		gosnum = r[d.index('gosnum')]
		if gosnum in order:
			wdict[gosnum].append(r[d.index('t')])
		else:
			order.append (gosnum)
			wdict[gosnum] = [ r[d.index('t')] ]
#	jtm = int(time.time()) +11111
	print "<table width=100%%><tr><th> Объекты </th><th> с: %s </th><th> по: %s </th></tr>" % (time.strftime("%H:%M %d.%m.%y", time.localtime(currtm)), time.strftime("%H:%M %d.%m.%y", time.localtime(stm)))
	for g in order:
#		print g, time.strftime("%D %T", time.localtime(wdict[g][0])), time.strftime("%D %T", time.localtime(wdict[g][-1])), len(wdict[g])
		print "<tr class='tit'><td valign='top'>", g, "</td><td>", time.strftime("%H:%M %d.%m.%y", time.localtime(wdict[g][-1])), "</td><td>", time.strftime("%H:%M %d.%m.%y", time.localtime(wdict[g][0])), "</rd><tr>"
		ta = wdict[g][0]
		jtm = wdict[g][0]
		for t in wdict[g]:
		#	print t, jtm
			if jtm - t > 2*900:	# sec
				sstm = time.strftime("\t с %H:%M %d.%m.%y", time.localtime(jtm))
				if ta - jtm > 11*3600:
					spotm = time.strftime("\tпо %H:%M %d.%m.%y", time.localtime(ta))
				else:	spotm = time.strftime("\tпо %H:%M", time.localtime(ta))
				print "<tr><td> </td><td>", sstm, "</td><td>", spotm, "</td><td>", (ta-jtm)/60, "</rd><tr>"
		#		print "\tjtm-t", (jtm - t), "\tta", ta, "\tjtm", jtm,  "\tt", t, "\tta-jtm", (ta-jtm)
				ta = t
			jtm = t

	print "</table>"
	print "</div>"
	return
	oiid = ''
	ot = 0
	osp = 0
	print "<table width=100%><tr><th> Объекты </th><th> Первый </th><th> Последний </th><th> скорость </th><th> ZZZ </th></tr>"
	for r in res[1]:
#		if not GZ.in_gzone (zid, float(r[d.index('x')]), float(r[d.index('y')])):	continue
		if oiid != r[d.index('idd')]:
			osp = r[d.index('sp')]
	#		print r[d.index('gosnum')], time.strftime("%D %T", time.localtime(r[d.index('t')])), time.strftime("%D %T", time.localtime(ot)), "<br>"
			print "<tr><td>", r[d.index('gosnum')], "</td><td>", time.strftime("%D %T", time.localtime(r[d.index('t')])), "</td><td>"
			if ot > 0:	print time.strftime("%D %T", time.localtime(ot))
			print "</td><td>", osp
			print "</td></tr>"
		
		osp = (osp + r[d.index('sp')])/2
		oiid = r[d.index('idd')]
		ot = r[d.index('t')]
	print "</table>"
	print "Dtm:", (time.time() - stm)	### DEBUG

class	gzohes:
	print_error = 1 ## Вывод ошибок на печать (0 - отменить печать)
	gzdict = {}
	n2id = {}
	def	__init__ (self, iddb, rid = 371, perror = 1):
		self.print_error = perror
		try:
			res = iddb.get_table ('zborder', 'rid=%s' % rid)
			d = res[0]
			for r in res[1]:
				zid = r[d.index('id')]
				self.n2id [r[d.index('n')]] = zid	#r[d.index('id')]
				jgzd = {}
				jgzd ['name'] = r[d.index('n')]
				jgzd ['type'] = r[d.index('t')]
				jgzd ['centr'] = [ float(r[d.index('cen_x')]), float(r[d.index('cen_y')]) ]
				if r[d.index('t')] == 2:
					min_x = float(r[d.index('min_x')])
					min_y = float(r[d.index('min_y')])
					jgzd ['box'] = [ float(r[d.index('min_x')]), float(r[d.index('min_y')]), float(r[d.index('max_x')]), float(r[d.index('max_y')]) ]
					px = []
					py = []
					for sp in r[d.index('p')][2:-2].split('),('):
						sx, sy = sp.split(',')
						px.append (int((float(sx)-min_x) * 1000000))
						py.append (int((float(sy)-min_y) * 1000000))
					jgzd ['px'] = px
					jgzd ['py'] = py
						
				self.gzdict [zid] = jgzd

		except:
			exc_type, exc_value = sys.exc_info()[:2]
			self.last_error = str(exc_value).strip()
			if perror:	print "EXCEPT __init__:", exc_type, self.last_error
			return	False

	def     in_gzone (self, zid, X, Y):
		try:
			box = self.gzdict[zid].get('box')
			if X > box[0] and X < box[2] and Y > box[1] and Y < box[3]:
				x = int((X-box[0]) * 1000000)
				y = int((Y-box[1]) * 1000000)
				xp = self.gzdict[zid].get('px')
				yp = self.gzdict[zid].get('py')
				c = 0
				for i in range(len(xp)):
					if (((yp[i]<=y and y<yp[i-1]) or (yp[i-1]<=y and y<yp[i])) and (x > (xp[i-1] - xp[i]) * (y - yp[i]) / (yp[i-1] - yp[i]) + xp[i])): c = 1 - c
				if c == 1:      return  True
			else:   return  False
		except: return  False

	def	find_gzone (self, X, Y):
		for j in self.gzdict.keys():
			box = self.gzdict[j].get('box')
	#		return	box
			if X > box[0] and X < box[2] and Y > box[1] and Y < box[3]:
				x = int((X-box[0]) * 1000000)
				y = int((Y-box[1]) * 1000000)
				xp = self.gzdict[j].get('px')
				yp = self.gzdict[j].get('py')
	#			return	(x, y, xp, yp)
	#			if inPolygon (x, y, xp, yp):	return	j	#self.gzdict[j]	
				c = 0
				for i in range(len(xp)):
					if (((yp[i]<=y and y<yp[i-1]) or (yp[i-1]<=y and y<yp[i])) and (x > (xp[i-1] - xp[i]) * (y - yp[i]) / (yp[i-1] - yp[i]) + xp[i])): c = 1 - c
				if c == 1:	return	j
		else:	return	False
		'''
		'''
			
	def	get_key (self, key = None):
		if key:	return	self.gzdict.get(key)
		else:	return	self.gzdict
		
		
def inPolygon(x, y, xp, yp):
    c=0
    for i in range(len(xp)):
        if (((yp[i]<=y and y<yp[i-1]) or (yp[i-1]<=y and y<yp[i])) and (x > (xp[i-1] - xp[i]) * (y - yp[i]) / (yp[i-1] - yp[i]) + xp[i])): c = 1 - c    
    return c
 
if __name__ == "__main__":
	gzon_infoww ({'status': 'view_gzones', 'this': 'ajax', 'org_inn': '5248037326', 'gzid': '371008'})
	'''
	print( inPolygon(100, 0, (-100, 0, 100, 100, -100), (100, 150, 100, -100, -100)))
	print( inPolygon(-100, 0, (-100, 0, 100, 100, 0, -100), (100, 150, 100, -100, -50, -100)))
#	probeg ({'shstat': 'view_canvas', 'idd': '864287036626578'})
	GZ = gzohes(db_agro)
#	for k in GZ.n2id.keys():	print '\t', GZ.n2id[k], '\t', k
	print GZ.get_key(1)
	print "GZ.find_gzone:\t", GZ.find_gzone(43.560877, 56.823572)
	print "GZ.find_gzone:\t", GZ.find_gzone(43.559246, 56.822786)
	'''
