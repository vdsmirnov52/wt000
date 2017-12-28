#!/usr/bin/python
# -*- coding: utf-8 -*-

import	os, sys, time
import	urllib
import	json

LIBRARY_DIR = r"/home/smirnov/Wialon/lib/"
sys.path.insert(0, LIBRARY_DIR)

'''
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
'''
rem = '''~div_left|<pre>
Параметры
	Название 	Описание + Комментарии
	itemId 		ID ресурса 	
	col 		массив идентификаторов геозон 	
	flags 		флаги, определяющие формат возвращаемого JSON 	необязательный, по умолчанию 0x1С

Флаги «flags»:
	Значение 	Описание
	0x01 	площадь
	0X02 	периметр
	0X04 	границы и координаты центра
	0X08 	точки
	0X10 	базовые свойства
	</pre>'''

widget = """~div_right|
	<div class="grey" style="background-color: #dde; width: 652px; padding: 4px; margin: 4px; top: 54px;">
	<div class="box" style="background-color: #ccd;">
	<table width="100%"><tr><td class='tit'>Геозоны - подробная информация</td>
	<td align="right">
	<input class="butt" value="Veew Zones" onclick="set_shadow('view_szones');" type="button" title='Список геозон' />
	<input class="butt" value="Search Zone" onclick="set_shadow('search_szone');" type="button" title='Искать геозону' />
	<input class="butt" value="Reload" onclick="set_shadow('form_szone');" type="button" title='Обновить форму' />
	<input class="butt" value="Close" onclick="$('#widget').html('Close');" type="button" title='' />
	</td></tr></table>
	</div>
	<dt><span class='tit'> itemId </span>	ID ресурса/учётной записи</dt>
	<dd><input type='text' name='itemId'>	</dd>
	<dt><span class='tit'> col </span>	массив идентификаторов геозон </dt>
	<dd><textarea name='col' maxlength=256 rows=1 cols=80>%s</textarea> </dd>
	<dt><span class='tit'> flags </span>	флаги, определяющие формат возвращаемого JSON </dt>
	<dd>
	<input type='checkbox' name='flag_001' /> площадь </br>
	<input type='checkbox' name='flag_002' /> периметр </br>
	<input type='checkbox' name='flag_004' checked /> границы и координаты центра </br>
	<input type='checkbox' name='flag_008' checked /> точки </br>
	<input type='checkbox' name='flag_016' checked /> базовые свойства </br>
	</dd>
	FORM
	<div id="set_vals" style="border: 1px solid #bbc; color: #668; min-height: 100px">set_vals</div>
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

	print "~set_vals|"
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
	print '<hr />'
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
	#	print float(i['c'])/0xff000000
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

def	view_szones (iddom, request):
	import	twlp
	print "~%s|" % iddom
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
		else:	print i['id']
#	print zgids[371]['zg']
	print zlids.keys(), zgids.keys()
	print 'totalItemsCount:', sres['totalItemsCount'], len(zlids), len(zgids), '<hr />'
	print "<table cellpadding=2 cellspacing=0><tr><th>Id</th><th>Наименование</th><th>Описание</th><th></th></tr>"
	for i in zgids.keys():
		item = zgids[i]
		pitem (item)
	for i in zlids.keys():
		pitem (zlids[i])
	print "</table>"

def	pitem (item):
		print "<tr class='mark tit'><td>", item['id'], "</td><td>", item['nm'].encode('UTF-8'), "</td><td> item </td><td></td></tr>"	#, item['d'].encode('UTF-8'), "</td><td></td></tr>"
		for k in item['zg'].keys():
			print "<tr><td>", k, "</td><td>", item['zg'][k]['n'].encode('UTF-8'), "</td><td>", item['zg'][k]['d'].encode('UTF-8'), "</td><td>"
			print item['zg'][k]['zns']
			print "</td><td></td></tr>"
			'''
			for j in item['zg'][k]['zns']:
				print "<tr><td>", j, "</td><td>"
	#			print zlids.keys()
			'''

def	pzone (zd):
	return str(zd)
	
