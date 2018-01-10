#!/usr/bin/python
# -*- coding: utf-8 -*-

import	os, sys, time
import	urllib
import	json

LIBRARY_DIR = r"/home/smirnov/Wialon/lib/"
sys.path.insert(0, LIBRARY_DIR)

rem = '''~div_left|<pre>
[		/* массив, с данными о геозонах */
	{
		"n":<text>,	/* название  геозоны*/
		"d":<text>,	/* описание */
		"id":<long>,	/* ID геозоны внутри ресурса/учётной записи */
		"rid":<long>,	/* ID ресурса/учётной записи*/
		"t":<byte>,	/* тип: 1 - линия, 2 - полигон, 3 - круг */
		"w":<uint>,	/* толщина линии или радиус круга */
		"f":<uint>,	/* флаги геозон (см. ниже) */
		"c":<uint>,	/* цвет (ARGB) */
		"tc":<uint>,	/* цвет надписи RGB */
		"ts":<uint>,	/* размер шрифта */
		"min":<uint>,	/* отображать на карте начиная с этого масштаба */
		"max":<uint>,	/* отображать на карте до этого масштаба */
		"i":<ushort>,	/* контрольная сумма изображения (CRC16) */
		"path":<text>,	/* укороченный путь до дефолтной иконки */
		"ar":<double>,  /* площадь */
		"pr":<double>,  /* периметр */
		"libId":<uint>,	/* id библиотеки иконок, 0 - id дефолтной библиотеки */
		"b":{		/* границы */
			"min_x":<double>,	/* минимальная долгота */
			"min_y":<double>,	/* минимальная широта */
			"max_x":<double>,	/* максимальная долгота */
			"max_y":<double>,	/* максимальная широта */
			"cen_x":<double>,	/* долгота центра  */
			"cen_y":<double>	/* широта центра */
		},
		"p":[		/* массив точек геозоны */
			{
				"x":<double>,	/* долгота */
				"y":<double>,	/* широта */
				"r":<uint>	/* радиус */
			},
			...
		],
		"ct":<uint>,    /* время создания */  
		"mt":<uint>     /* время последнего изменения */
	},
	...
]
</pre>'''

rem = '''~div_left|<pre>
ООО «АФГ Националь Нижний Новгород»
	1. Видеть расход ГСМ (ДУТ)
	2. Видеть местоположение техники (БТ)
	3. Видеть с каким прицепным оборудованием работает та или иная единица (радиометки на навесное оборудование)
	4. Видеть сколько фактически было выработано Га
	5. Видеть кто конкретно и в какое время работал на той или иной технике (карты считывателя водителя)
	6. Интеграция в «1С» 
	7. Возможно, ваше ведение еженедельных или ежемесячных отчётов. (если есть такие услуги)
</pre>'''


widget = """~div_right|
	<div class="grey" style="background-color: #dde; width: 652px; padding: 4px; margin: 4px; top: 54px;">
	<div class="box" style="background-color: #ccd;">
	<table width="100%"><tr><td class='tit'>Геозоны - подробная информация</td>
	<td align="right" id='dt_butt'>
	<input class="butt" value="Геозоны Wialon" onclick="set_shadow('list_wzones');" type="button" title='Список геозон Wialon' />
	<input class="butt" value="Search Zone" onclick="set_shadow('search_szone');" type="button" title='Искать геозону' />
	</td>
	<td align=right><img onclick="set_shadow('form_agro');" title="Обновить" src="../img/reload3.png"></td>
	</tr></table>
	</div>
	<dt><span class='tit'> itemId </span>	ID ресурса/учётной записи</dt>
	<dd><input type='text' id='itemId' name='itemId' size=6 />
	<span title='массив идентификаторов геозон'> &nbsp; col: <input id='zcol' type='text' name='zcol' size=44 /></span>
	<dt><span class='tit'> flags </span> флаги, определяющие формат возвращаемого JSON </dt><dd> <input type='text' name='flags' size=6 value='-1' /></dd>
	FORM
	<div id="set_vals" style="min-height: 300px; max-height: 450px; overflow: auto;">set_vals</div>
	<div id="rlog" style="border: 1px solid #bbc; color: #668; min-height: 100px">set_vals</div>
	</div>
	</div>
	"""

def	dom (iddom, request):
	print "~widget|"
	print "~%s|" % iddom
	print "<table border=0><tr style='vertical-align: top;'><td id='td_left'></td><td id='td_right'></td></tr></table>"
	print "~td_left|<div id='div_left' style='border: 1px solid rgb(187, 187, 204); color: rgb(12, 12, 36); overflow: auto; min-width: 700px;'> ERROR </div>"
	print "~td_right|<div id='div_right' > ", request, " </div>"
	print "~eval|$('#div_left').css({'height': (-233 + document.documentElement.clientHeight) +'px',  'overflow': 'auto'});"
	print "~eval|$('#div_left').css({'width': (-700 + document.documentElement.clientWidth) +'px',  'overflow': 'auto'});"
	print rem
	print widget

serr =  lambda txt:     "<span class='bferr'> %s </span>" % txt

def	search_szone(iddom, request):
	import	twlp
	ztype = {1: 'линия', 2: 'полигон', 3: 'круг'}

	print "~rlog|"
	if not (request.has_key('itemId') and request['itemId'].isdigit()):
		print serr ("Отсутствует или невернр задан 'itemId'.")
		return
	cols = []
	if not (request.has_key('col') and request['col'].strip()[0].isdigit()):
		for j in xrange(255):	cols.append(j)
	else:
		print request['col'].strip().split()
		for js in request['col'].strip().split():
			js = js.replace(',', '').replace(';', '').strip()
			print js
			if js and js.isdigit():	cols.append(int(js))

	flags = 0
	for k in request.keys():
		if 'flag_' in k[:5] and request[k] == 'on':
			flags += int (k[5:])
	if flags == 0:	flags = -1
#	print '<hr />'
	itemId = int(request['itemId'])
	data = {'sid': request['wsid'], 'svc': 'resource/get_zone_data', 'params': {'itemId': itemId, 'col': cols, 'flags': flags}}
#	print data
	fres, sres = twlp.requesr(data)
	if not fres:
		print serr(sres), str(data)
		return
	print "~%s|" % iddom
#	print	sres
	print '<table>'
	for i in sres:
		print '<tr class="tit"><td>', i['rid'], i['id'], '</td><td>', i['n'].encode('UTF-8'), '</td><td>', i['d'].encode('UTF-8')
		print time.strftime("</td><td>mt: %Y.%m.%d %T", time.localtime (i['mt']))
		op = float(i['c'])/0xff000000
		print op
		print "<span style='background-color: #%x; opacity: %.2f;, color: #%x;'> nin: %s, max: %s </span>" % (0xffffff & int(i['c']), op, int(i['tc']), i['min'], i['max'])
		if i['t'] in ztype.keys():
			print ztype[i['t']]
		else:	print '###'
		out_filds (i, flags)
		if flags == -1:
			print '<tr><td> </td><td colspan=3>'
		if i.has_key('b') and i.has_key('p'):
			prn_svg (i['b'], i['p'], i['c'], i['n'].encode('UTF-8'), i['t'])
		print '</td></tr>'
	print	'</table>'

from math import sin, cos, tan, pi
def	prn_svg (b, points, c, name, ztype = 1, k = 20000):
	#  {u'min_x': 43.5576794388, u'min_y': 56.821850924, u'max_x': 43.5630507866, u'max_y': 56.8249534109, u'cen_x': 43.5603651127, u'cen_y': 56.8234021675} 
	Rz = (6378245.0+6356863.019)/2	# Радиус земли
	min_x = float(b['min_x'])
	min_y = float(b['min_y'])
	max_x = float(b['max_x'])
	max_y = float(b['max_y'])
	if k*(max_x - min_x) > 1100:	# Нормализовать X к 1100
		k = 1100/(max_x - min_x)
		print '#'*33, "Xk:", int(k), "<br />"
	if k*(max_y - min_y) > 500:	# Нормализовать Y к 500
		k = 500/(max_y - min_y)
		print '#'*33, "Yk:", int(k), "<br />"
	K = k*cos(pi * (min_x+max_x)/360)
	w = int(K*(max_x - min_x))
	h = int(k*(max_y - min_y))
	cl = 0xffffff & int(c)
#	print Rz, Rz*cos(pi * min_x/180), (max_x-min_x), (max_x-min_x)*cos(pi * min_x/180), K
	print "<svg width=%dpx height=%dpx fill='#%x' border=1px xmlns='http://www.w3.org/2000/svg'>" %(w, h, cl)
	print "<text x=10 y=30 font-size=13>%s</text>" % name
	pp = []
	if ztype in [1,2]:
		for p in points:
			x = int(K * (float(p['x']) - min_x))
			y = int(k * (max_y - float(p['y'])))	# - min_y))
			pp.append('%d %d' % (x, y))
		if ztype == 1:	# Линия
			print """<path id="Line" fill="none" stroke="#%x" stroke-width="5" opacity="0.4" d="M %s" />""" % (cl, 'L '.join(pp))
		else:		# Полигон
			print """<polygon stroke="#868686" stroke-width="1" fill="#%x" opacity="0.4" points="%s"></polygon>""" % (cl, ' '.join(pp))
	else:	# Круг
		r = int(h/2)	#points[0]['r'])
	#	print points
		print "<circle r='%d' cx='%d' cy='%d' fill='#%x' opacity='0.4'></circle>" % (r, r, r, cl)
	print "</svg>"

def	out_filds (js, flags):
	if flags == -1:		return
	if not flags & 0x0f:    return
	print '<tr><td> </td><td colspan=3>'
	if flags & 1:	# площадь
		print "площадь:", js['ar'], '<br />'
	if flags & 2:	# периметр
		print "периметр:", js['pr'], '<br />'
	if flags & 4:	# границы и координаты центра
		print "границы:", js['b'], '<br />'
	if flags & 8:	# точки
		for p in js['p']:
			print p, '<br />'
#	print '</td></tr>'

def	list_wzones (iddom, request):
	import	twlp
	print "~rlog|"
	params = {'spec': {'propType': 'sys_name', 'sortType': 'sys_name', 'itemsType': 'avl_resource', 'propName': '*', 'propValueMask': '*'}, 'force': 1, 'to': 0, 'from': 0, 'flags': -1,}
	data = {'sid': request['wsid'], 'svc': 'core/search_items' , 'params': params}
	fres, sres = twlp.requesr(data)
	if not fres:
		print serr(sres), str(data)
		return
#	print sres['items'][0]	#.keys()
	zlids = {}
	zgids = {}
	for i in sres['items']:
		if i.has_key('zg') and i['zg']:
			zgids[i['id']] = i
		elif i.has_key('zl') and i['zl']:
			zlids[i['id']] = i
		else:	pass	#print i['id']
#	print zgids[371]['zg']
#	print zlids.keys(), zgids.keys()
	print 'totalItemsCount:', sres['totalItemsCount'], len(zgids), len(zlids)
	print "<br>zgids.keys:", zgids.keys(), "<br>zlids.keys:", zlids.keys()
	print "~%s|" % iddom
	print "<table id='tbl_wzones' cellpadding=2 cellspacing=0><tr><th>Id</th><th> Наименование</th><th>Описание</th><th></th></tr>"
	for i in zgids.keys():
		item = zgids[i]
		'''
		K = int (item['id'])
		print "<tr><td>", i, K
		print "<tr id='%05d' class='tit'><td>" % (100*K), item['id'], "</td><td>", item['nm'].encode('UTF-8'), "</td><td> ZZZ </td><td></td></tr>"
		'''
		pitem (item)
	for i in zlids.keys():
		pitem (zlids[i])
	print "</table>"
	'''	###	????????????????? 
	print """<script type='text/javascript'>
	$('#tbl_wzones tr.line').hover (function () { $('#tbl_wzones tr').removeClass('mark'); $(this).addClass('mark'); $('#shadow').text('')})
			.click (function (e) { $('#tbl_wzones tr').removeClass('mark'); $(this).addClass('mark');
			$.ajax ({data: 'shstat=mark_row&table=tbl_wzones&pkname=id_contr&idrow=' +$(this).get(0).id +'&X=' +e.clientX +'&Y=' +e.clientY +'&' +$('form').serialize() }); });
	</script>"""
	'''

def	pitem (item):
		K = int (item['id'])
#		print item['id'], K
		print """<tr id='%05d' class='line tit' onclick=" $('#itemId').val('%s'); $('#tbl_wzones tr').removeClass('mark'); $('#%05d').addClass('mark'); "><td>""" % ((100*K), str(item['id']), (100*K))
		print item['id'], "</td><td>", item['nm'].encode('UTF-8'), "</td><td> item </td><td></td></tr>"
#		return
		for k in item['zg'].keys():
			print "<tr id='%05d' class='mark'><td>" % (100*K +int(k)), k, "</td><td>", item['zg'][k]['n'].encode('UTF-8'), "</td><td>", item['zg'][k]['d'].encode('UTF-8'), "</td><td>"
			print item['zg'][k]['zns']
			print "</td><td></td></tr>"
			'''
			for j in item['zg'][k]['zns']:
				print "<tr><td>", j, "</td><td>"
	#			print zlids.keys()
			'''

def	pzone (zd):
	return str(zd)
	
###########################################

def	ajax (request):
	print "~shadow2|ZZZ form_agro.ajax", request['shstat']
	shstat = request['shstat']
	iddom = 'div_left'
	if shstat == 'list_wzones':
		list_wzones ('set_vals', request) 
	elif shstat == 'search_szone':	### Геозоны - подробная информация
		search_szone('div_left', request)
	else:	print "~eval|alert ('form_agro: Unknown shstat: [%s]!');" % request ['shstat']
