#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""	Утилита crontab
	Обмен данными с ИС МКУ ГЦГиА (БД Oracle)	АнтиСнег
"""
'''	v.smirnov@rnc52.ru	41Tvjlby
	хост: geonn.grad-nn.ru	порт 1521
	логин: RNITS		пароль WwX5W9

	SELECT * FROM NNOVGOROD3785_UAG.NS_UBORKA_SAD_SNEG	- Флаг начала уборки ROWID

	Кодировка CP1251
от Кати работает (убрать ; в запросе)
	SELECT NNOVGOROD3785_UAG.ora2geojson.sdo2geojson('select * from udc_uborka_avtoz',ROWID, geometry) FROM NNOVGOROD3785_UAG.udc_uborka_avtoz
Только дороги, только категории А и Б 
SELECT NNOVGOROD3785_UAG.ora2geojson.sdo2geojson('select * from V_PORTAL2_SAD_AVTOZ',ROWID, geometry) FROM NNOVGOROD3785_UAG.V_PORTAL2_SAD_AVTOZ
SELECT NNOVGOROD3785_UAG.ora2geojson.sdo2geojson('select * from V_PORTAL2_SAD_KAN',ROWID, geometry) FROM NNOVGOROD3785_UAG.V_PORTAL2_SAD_KAN
SELECT NNOVGOROD3785_UAG.ora2geojson.sdo2geojson('select * from V_PORTAL2_SAD_LEN',ROWID, geometry) FROM NNOVGOROD3785_UAG.V_PORTAL2_SAD_LEN
SELECT NNOVGOROD3785_UAG.ora2geojson.sdo2geojson('select * from V_PORTAL2_SAD_MSK',ROWID, geometry) FROM NNOVGOROD3785_UAG.V_PORTAL2_SAD_MSK
SELECT NNOVGOROD3785_UAG.ora2geojson.sdo2geojson('select * from V_PORTAL2_SAD_SORM',ROWID, geometry) FROM NNOVGOROD3785_UAG.V_PORTAL2_SAD_SORM
SELECT NNOVGOROD3785_UAG.ora2geojson.sdo2geojson('select * from V_PORTAL2_SAD_SOV',ROWID, geometry) FROM NNOVGOROD3785_UAG.V_PORTAL2_SAD_SOV
SELECT NNOVGOROD3785_UAG.ora2geojson.sdo2geojson('select * from V_PORTAL2_SAD_NIG',ROWID, geometry) FROM NNOVGOROD3785_UAG.V_PORTAL2_SAD_NIG
SELECT NNOVGOROD3785_UAG.ora2geojson.sdo2geojson('select * from V_PORTAL2_SAD_PRIO',ROWID, geometry) FROM NNOVGOROD3785_UAG.V_PORTAL2_SAD_PRIO
	'V_PORTAL2_SAD_AVTOZ','V_PORTAL2_SAD_KAN','V_PORTAL2_SAD_LEN','V_PORTAL2_SAD_MSK','V_PORTAL2_SAD_NIG','V_PORTAL2_SAD_PRIO','V_PORTAL2_SAD_SORM','V_PORTAL2_SAD_SOV'

'''

import	os, sys, time
os.environ["NLS_LANG"] = "Russian.AL32UTF8"	# query = u"..."  cur.execute(query.encode("cp1251"))
import	cx_Oracle
import	json

class	dboracle:
	"""
	"""
	print_error = 1	# Вывод ошибок на печать (0 - отменить печать)
	last_error = None
	desc = []	# Список наименования полей последнего запроса
	def	__init__ (self, desc_db ="RNITS/WwX5W9@geonn.grad-nn.ru:1521/orcl", perror = 1):
		self.print_error = perror
		try:
			self.conn = cx_Oracle.connect (desc_db)
			self.curs = self.conn.cursor()
		except:
			exc_type, exc_value = sys.exc_info()[:2]
			self.last_error = (exc_type, exc_value)
			print "EXCEPT __init__:", exc_type, str(exc_value).strip()

	def	execute (self, query):
		try:
			self.curs.execute (query)
			res = True
		except	:
			self.perrs ()
			res = False
		finally:
			self.conn.commit()
		if res:	self.last_error = None
		return	res

	def	get_rows (self, query):
		return	self.get (query, 1)

	def	get_row (self, query):
		return	self.get (query, 0)

	def	get (self, query, fall):
		try:
			self.curs.execute (query)
			self.desc = [f[0] for f in self.curs.description]
			if fall:	return	self.curs.fetchall()
			else:		return	self.curs.fetchone()
		except	:
			self.perrs ()
		finally:
			self.conn.commit()
	def	perrs (self, label = 'EXCEPT'):
		exc_type, exc_value = sys.exc_info()[:2]
		self.last_error = (exc_type, exc_value)
		if self.print_error:
			print	label, exc_type
			print	exc_value

########	dboracle:

LIBRARY_DIR = r"/home/smirnov/WT/lib"	# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import	dbtools

def	parce_coordinates (pl, epsg_in = 'epsg:3857', epsg_out = 'epsg:4326', resln = None):
	""" Преобразовать координаты в web WGS84 	"""
	from pyproj import Proj, transform
	
	sphmerc = Proj(init=epsg_in)	#"epsg:3857")
	lonlat = Proj(init=epsg_out)	#"epsg:4326")		#  web WGS84

	pouts = []
	if type(pl) == list:
		for ppl in pl:
			pout = transform (sphmerc, lonlat, *ppl)
			if resln == 3:
				pouts.append((pout[0],pout[1], 0))
			else:	pouts.append(pout[:2])
	#		print '\t', ppl, pout
	return	pouts
	print '#'*22, pouts

def	send_lines (starttm = None):
	print "\t Отправить треки проезда уборочной техники"
	asnow = dbtools.dbtools('host=127.0.0.1 dbname=anti_snow port=5432 user=smirnov')
	if starttm and starttm > 0:
		query = "SELECT id, tevent,  gosnum, quality, slines FROM to_send WHERE tevent > %d" % (starttm -180)
	else:	query = "SELECT id, tevent,  gosnum, quality, slines FROM to_send LIMIT 3"
	print query
	rows = asnow.get_rows(query)
	j = 0
	tevent = 0
	for r in rows:
		rid, tevent,  gosnum, quality, sline = r
		lines = eval (sline)
	#	print len(lines), '\t', lines
		jrid = 100*rid
		jres = 0
		jinf = ['1,2,1']
		jord = []
		jlen = 1
		for l in lines:
		#	print len(l), '\t', l
			lp = parce_coordinates (l, 'epsg:4326', 'epsg:3857', 3)
			jlen += 3*len(lp)
			jinf.append ('%d,2,1' % jlen)	#(3*len(lp) +1))
			jord.append (str(lp)[1:-1].replace('(', '').replace(')', ''))
		info = ', '.join(jinf[:len(jord)])
		orditate = ',\n'.join(jord)
		query = """INSERT INTO NNOVGOROD3785_UAG.NS_UBORKA_SAD_TREK (id, tevent, color, IS_ACTUAL, GEOMETRY) VALUES (%d, %d, %s, 1, MDSYS.SDO_GEOMETRY(3002, 3857,NULL, MDSYS.SDO_ELEM_INFO_ARRAY(%s), MDSYS.SDO_ORDINATE_ARRAY (\n%s)))""" % (
			rid, tevent, quality, info, orditate)
	#	print query
		res = dbo.execute (query)
		if not res:	print	"Error\t", query
#		print "DELETE", ris
		# Зачистить отправленное в anti_snow
		if not asnow.qexecute ("DELETE FROM to_send WHERE id = %d" % rid):	print	"Error\t",  "DELETE FROM to_send WHERE id = %d" % rid
#		if j > 3:	break
		j += 1
	if tevent > 0:
		query = "UPDATE NNOVGOROD3785_UAG.NS_UBORKA_SAD_TREK SET IS_ACTUAL = 0 WHERE IS_ACTUAL > 0 AND tevent < %d" % (tevent - 4*3600)
		if not dbo.execute (query):	print 	"Error\t", query
"""
Марина
4       [[[43.983135, 56.308678], [43.983223, 56.308998], [43.983902, 56.30986]], [[43.983273, 56.310425], [43.981812, 56.310699]], [[43.981567, 56.311954], [43.981636, 56.312218]], [[43.983513, 56.316311], [43.983246, 56.316727]]]
INSERT INTO NNOVGOROD3785_UAG.NS_UBORKA_SAD_TREK (id, color, GEOMETRY) VALUES (5400301, 1, MDSYS.SDO_GEOMETRY(2002, NULL,NULL, MDSYS.SDO_ELEM_INFO_ARRAY(1,2,1),
                        MDSYS.SDO_ORDINATE_ARRAY (4896180.1916918075, 7620111.733604805, 4896189.987806999, 7620175.9506659135, 4896265.573741246, 7620348.938050696)))
INSERT INTO NNOVGOROD3785_UAG.NS_UBORKA_SAD_TREK (id, color, GEOMETRY) VALUES (5400302, 1, MDSYS.SDO_GEOMETRY(2002, NULL,NULL, MDSYS.SDO_ELEM_INFO_ARRAY(1,2,1),
                        MDSYS.SDO_ORDINATE_ARRAY (4896195.553781538, 7620462.325171447, 4896032.916005489, 7620517.3135117935)))
INSERT INTO NNOVGOROD3785_UAG.NS_UBORKA_SAD_TREK (id, color, GEOMETRY) VALUES (5400303, 1, MDSYS.SDO_GEOMETRY(2002, NULL,NULL, MDSYS.SDO_ELEM_INFO_ARRAY(1,2,1),
                        MDSYS.SDO_ORDINATE_ARRAY (4896005.642730244, 7620769.181206776, 4896013.323775112, 7620822.164787411)))
INSERT INTO NNOVGOROD3785_UAG.NS_UBORKA_SAD_TREK (id, color, GEOMETRY) VALUES (5400304, 1, MDSYS.SDO_GEOMETRY(2002, NULL,NULL, MDSYS.SDO_ELEM_INFO_ARRAY(1,2,1),
                        MDSYS.SDO_ORDINATE_ARRAY (4896222.27045933, 7621643.6578402, 4896192.548155286, 7621727.156810341)))

INSERT INTO NNOVGOROD3785_UAG.NS_UBORKA_SAD_TREK(ID,GEOMETRY)
	VALUES(NS_UBORKA_SAD_TREK_SEQ.NEXTVAL, MDSYS.SDO_GEOMETRY(2002, NULL, NULL,  --линия
	MDSYS.SDO_ELEM_INFO_ARRAY(1,2,1,  7,2,1,  11,2,1,  15,2,1),   --4 линии:1-я линия с 1-ого числа, 2-я линия с 7-го числа...
	MDSYS.SDO_ORDINATE_ARRAY(
	4896180.1916918075, 7620111.733604805, 4896189.987806999, 7620175.9506659135, 4896265.573741246, 7620348.938050696,  --1-я линия
	4896195.553781538, 7620462.325171447, 4896032.916005489, 7620517.3135117935,   --2 линия
	4896005.642730244, 7620769.181206776, 4896013.323775112, 7620822.164787411,  --3 
	4896222.27045933, 7621643.6578402, 4896192.548155286, 7621727.156810341  --4
	))) 
"""

def	test (conn, tname = 'NNOVGOROD_UAG.NS_UBORKA_AVTOZ'):
	print	'tname:\t', tname
	cursor = conn.cursor()
#	query = 'SELECT sdo_util.to_wkbgeometry(geometry) FROM NNOVGOROD3785_UAG.%s ' % tname
#	query = "SELECT %s.ora2geojson.sdo2geojson('select * from udc_uborka_avtoz',ROWID, geometry) FROM %s.udc_uborka_avtoz" % (prefix, prefix)
	query = "SELECT %s.ora2geojson.sdo2geojson('select * from %s',ROWID, geometry) FROM %s.%s" % (prefix, tname, prefix, tname)
#	query = 'SELECT geometry FROM %s%s ' % (prefix, tname)
#	query =	"SELECT NNOVGOROD3785_UAG.ora2geojson.sdo2geojson('select * from udc_uborka_avtoz',ROWID, geometry) FROM NNOVGOROD3785_UAG.udc_uborka_avtoz"
	print '\t', query
#	cursor.execute('SELECT * FROM NNOVGOROD3785_UAG.NS_UBORKA_SAD_SNEG')
	cursor.execute(query)
	columns = [i[0].lower() for i in cursor.description]
	j = 0
	for r in cursor.fetchall():
		for c in r:
			print type(c)
			if type(c) == str:
				print c.encode('UTF-8')	#('CP1251')
			else:	print c, '\t',
			'''
			print c, '\t',
			'''
		print
		j += 1
		if j > LIMIT:	break
	cursor.close()
'''
def	get_table (conn, tname, scols = None):

	if scols:
		query = "SELECT %s FROM %s.%s" % (scols, prefix, tname)
	else:	query = "SELECT * FROM %s.%s" % (prefix, tname)
	print '\t', query
	cursor = conn.cursor()
	cursor.execute(q_ins)
	cursor.execute(query)
	columns = [i[0].lower() for i in cursor.description]
	print columns
	print	cursor.description
	j = 0
	for r in cursor.fetchall():
		for c in r:
			print "\t", c,
		print
#		break
		j += 1
	#	if j > LIMIT:	break
	cursor.close()
	conn.commit()
	print "#"*22, tname, j
'''
	
def	get_geometry (tname, scols = None):
	print "get_geometry:", tname
	if scols:
		query = "SELECT %s, %s.ora2geojson.sdo2geojson('select * from %s',ROWID, geometry) FROM %s.%s" % (scols, prefix, tname, prefix, tname)
	else:	query = "SELECT %s.ora2geojson.sdo2geojson('select * from %s',ROWID, geometry) FROM %s.%s" % (prefix, tname, prefix, tname)
	print '\t', query
	rows = dbo.get_rows(query)
	j = 0
	print dbo.desc
	for r in rows:	#cursor.fetchall():
		for c in r:
			print "\t", c
		j += 1
		if j > LIMIT:	break
	#ursor.close()

def	get_territory (tname, scols = None):
	print	"get_territory:", tname, scols
	if scols:
		query = "SELECT %s, %s.ora2geojson.sdo2geojson('select * from %s',ROWID, geometry) AS GEOMETRY FROM %s.%s ORDER BY ID" % (scols, prefix, tname, prefix, tname)
	else:	query = "SELECT %s.ora2geojson.sdo2geojson('select * from %s',ROWID, geometry) AS GEOMETRY FROM %s.%s ORDER BY ID" % (prefix, tname, prefix, tname)
#	print '\t', query
	print >> fout, '\t', query
	rows = dbo.get_rows(query)
	j = 0
#	print dbo.desc
	for r in rows:
		check_row (dbo.desc, r)
		j += 1
	#	if j > LIMIT:	break
		

def	check_row (d, r):
	""" Контроль описателя полигона	"""
	region =  r[d.index('REGION_ID')]
	categ = r[d.index('CATEG')]
	pols = r[d.index('GEOMETRY')]
	pid = r[d.index('ID')]
	if region and region.isdigit():
		region = int(region)
	else:	region = 0
	icateg = 1
	for c in ['Дороги категории А', 'Дороги категории Б']:
		if c == categ:	break
		icateg += 1
	spols = str(pols).replace('"REGION": "REGION_ID": ', '')
#	print "{'ID': %d, 'REGION_ID': %d, 'CATEG_ID': %d}@%s" % (pid, region, icateg, spols)
	print >> fout, "{'ID': %d, 'REGION_ID': %d, 'CATEG_ID': %d}@%s" % (pid, region, icateg, spols)
	return
	#################	bu/temp_20180906.py

def	send_autos ():
	print	"\t Отправить координаты ТС"

	dbrec = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	dbo = dboracle()
	query = "SELECT gos_nomer, tevent FROM NNOVGOROD3785_UAG.NS_UBORKA_SAD_PLOW"
	rows = dbo.get_rows (query)
	if dbo.last_error:	return

	list_autos = {}
	for r in rows:
		list_autos[r[0]] = r[1]
#	print list_autos
#	query = "SELECT * FROM vlast_pos WHERE x > 0 ORDER BY t"
	### Список ИНН организаци участвующих в уборке снега 
	query = "SELECT * FROM vlast_pos WHERE x > 0 AND tinn IN (SELECT inn FROM org_desc WHERE bm_ssys = 131072 AND stat > 0) ORDER BY t"
	rrows = dbrec.get_rows (query)
	d = dbrec.desc
#	print d
	for r in rrows:
		gosnum = r[d.index('gosnum')]
	#	for v in r:	print "\t", v,
		x = float(r[0])
		y = float(r[1])
		try:
			X,Y = parce_coordinates([[x,y]], 'epsg:4326', 'epsg:3857')[0]
		except RuntimeError:	continue
#		print x,y, "\t=>", X,Y
		gpoint = "MDSYS.SDO_GEOMETRY( 3001, 3857, MDSYS.SDO_POINT_TYPE(%s, %s, NULL), NULL, NULL)" % (X,Y)
		if r[d.index('rem')]:
			marka = r[d.index('rem')]
		else:	marka = r[d.index('marka')]
		if gosnum in list_autos.keys():
		#	print "UPDATE"
			if r[d.index('t')] <= list_autos[gosnum]:	continue
			query = "UPDATE NNOVGOROD3785_UAG.NS_UBORKA_SAD_PLOW SET tevent = %s, geometry = %s, marka='%s' WHERE gos_nomer = '%s'" % (r[d.index('t')], gpoint, marka, gosnum)
		#	query = "UPDATE NNOVGOROD3785_UAG.NS_UBORKA_SAD_PLOW SET tevent = %s, geometry = %s WHERE gos_nomer = '%s'" % (r[d.index('t')], gpoint, gosnum)
			if not dbo.execute(query):	print	"Error:\t", query
		else:
		#	print "INSERT"
			query = "INSERT INTO NNOVGOROD3785_UAG.NS_UBORKA_SAD_PLOW (tevent, geometry, gos_nomer, marka, inn, name_obj) VALUES (%s, %s, '%s', '%s', '%s', '%s')" % (
			r[d.index('t')], gpoint, gosnum, marka, r[d.index('tinn')], r[d.index('bname')])
		#	r[d.index('t')], gpoint, gosnum, r[d.index('marka')], r[d.index('tinn')], r[d.index('bname')])
		#	print query, dbo.execute(query)
			if not dbo.execute(query):	print	"Error:\t", query
 
	query = "DELETE FROM NNOVGOROD3785_UAG.NS_UBORKA_SAD_PLOW WHERE ID < 50"
	print query, dbo.execute(query)
#	print	"send_autos", "#"*33


def	check_tsnow (dbo = None):
	""" Оперативный контроль состояния транспорта	"""
	if not dbo:	dbo = dboracle()
	dbrec = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')

#	query = "SELECT * FROM NNOVGOROD3785_UAG.NS_UBORKA_TEHNIKA "
	query = "SELECT * FROM NNOVGOROD3785_UAG.NS_UBORKA_TEH "
	rows = dbo.get_rows (query)
	for c in dbo.desc:	print '\t', c,
	print query, dbo.desc
	print dbo.curs.description
	for r in rows:
	#	for c in r:	print '\t', c,
		orid = r[dbo.desc.index('ID')]
		categ = r[dbo.desc.index('CATEG')]
		sgn = r[dbo.desc.index('NOMER')].strip().replace(' ', '') +'%' 
		if 'MARKA' in dbo.desc and r[dbo.desc.index('MARKA')]:
			marka = "'%s'" % r[dbo.desc.index('MARKA')].strip()
		else:	marka = 'NULL'
		query = "SELECT * FROM vrecv_ts WHERE gosnum LIKE '%s'" % sgn 
		trows = dbrec.get_rows(query)
		d = dbrec.desc
		if trows and len(trows) == 1:
			gosnum = trows[0][dbrec.desc.index('gosnum')]
			if gosnum == sgn[:-1]:
				if int(categ) != int(trows[0][d.index('stat_ts')]) or (marka != 'NULL' and trows[0][d.index('rem')] != marka[1:-1]):
					query = "UPDATE recv_ts SET rem = %s, stat_ts = %s WHERE gosnum = '%s'" % (marka, categ, gosnum)
					print 'dbrec\t', query, dbrec.qexecute(query)
			else:
				query = "UPDATE NNOVGOROD3785_UAG.NS_UBORKA_TEHNIKA SET NOMER = '%s' WHERE id = %s" % (gosnum, orid)
			#	qres = dbo.execute(query)
				print '\t', query
				'''
				if qres:
					query = "UPDATE recv_ts SET rem = '%s', stat_ts = %s WHERE gosnum = '%s'" % (marka, categ, gosnum)
					print 'dbrec\t', query, dbrec.qexecute(query)
				'''
		else:
			gosnum = 'None'
			print	"\t>>\t%s \t%s \t%s \t" % (sgn, marka, categ), gosnum, (gosnum == sgn[:-1])
	#	print	"\t>>\t", r[dbo.desc.index('CATEG')], r[dbo.desc.index('NOMER')].strip().replace(' ', ''), r[dbo.desc.index('MARKA')].strip()
	#	print 
	return

LIMIT = 5
prefix = 'NNOVGOROD3785_UAG'
gtables = [ 'V_PORTAL2_SAD_AVTOZ','V_PORTAL2_SAD_KAN','V_PORTAL2_SAD_LEN','V_PORTAL2_SAD_MSK','V_PORTAL2_SAD_NIG','V_PORTAL2_SAD_PRIO','V_PORTAL2_SAD_SORM','V_PORTAL2_SAD_SOV' ]

import	getopt

def	update_inn ():
	""" Обновить записи в NNOVGOROD3785_UAG.NS_UBORKA_SAD_PLOW	"""
	dbo = dboracle()
	dbrec = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	query = "SELECT gosnum, marka, inn, bname FROM vrecv_ts WHERE inn IN (SELECT inn FROM org_desc WHERE bm_ssys = 131072 AND stat > 0)"
	rows = dbrec.get_rows(query)
	if not rows:	return
	j = jnt = 0
	for r in rows:
		gosnum, marka, inn, bname = r
		orow = dbo.get_row ("SELECT GOS_NOMER, MARKA, INN, NAME_OBJ FROM NNOVGOROD3785_UAG.NS_UBORKA_SAD_PLOW WHERE GOS_NOMER = '%s'" % gosnum)
		if not orow:
			print	"\tNot: %s\t%s\t%s" % (gosnum, marka, inn) , bname
			jnt += 1
			continue
		MARKA, INN, NAME_OBJ = orow[1:]
		if inn != int(INN):
		#	print	"\tINN:", gosnum, marka, inn, bname, "<>", INN
			query = "UPDATE NNOVGOROD3785_UAG.NS_UBORKA_SAD_PLOW SET MARKA = '%s', INN = '%s', NAME_OBJ = '%s' WHERE GOS_NOMER = '%s'" % (marka, inn, bname, gosnum)
			res = dbo.execute(query)
			print query, res
			if res:	j += 1
		#	break
	if jnt:
		print "Нет %s записей"
	print "Обновлено %s записей NNOVGOROD3785_UAG.NS_UBORKA_SAD_PLOW" % j

def	otest (swhere = None):
	print "otest"
	dbo = dboracle()
	query = "SELECT * FROM NNOVGOROD3785_UAG.NS_UBORKA_SAD_SNEG"	# Флаг начала уборки ROWID
	print   "Флаги начала уборки:\n\t", dbo.get_rows (query), "\n"

#	query = "SELECT count(*) FROM NNOVGOROD3785_UAG.NS_UBORKA_SAD_TREK WHERE IS_ACTUAL >1"
#	query = "SELECT * FROM NNOVGOROD3785_UAG.NS_UBORKA_SAD_TREK ORDER BY TEVENT"
#	query = """DELETE FROM NNOVGOROD3785_UAG.NS_UBORKA_SAD_PLOW WHERE NAME_OBJ = 'МП"Сергачский автобус"'"""
#	print query, dbo.execute (query)
#	query = """SELECT * FROM NNOVGOROD3785_UAG.NS_UBORKA_SAD_PLOW WHERE NAME_OBJ = 'МП"Сергачский автобус"'"""
	swhere = "INN = 5256133168 "	# 5256021545
	if swhere:
		query = "SELECT * FROM NNOVGOROD3785_UAG.NS_UBORKA_SAD_PLOW WHERE %s" % swhere
	else:	query = "SELECT * FROM NNOVGOROD3785_UAG.NS_UBORKA_SAD_PLOW"	# ORDER BY TEVENT"
	print query
	rows = dbo.get_rows (query)
	print dbo.desc
#	print rows
	if rows:
		print	"len(rows):\t", len(rows), dbo.desc
#		print	"rows[0]:\t", 	rows[0]
		for r in rows:
			for k in dbo.desc:
				if k == 'GEOMETRY':	continue
				if k == 'TEVENT':
					print time.strftime("\t%T %d.%m.%Y", time.localtime(sttmr)),
					continue
				print	'\t', r[dbo.desc.index(k)],
			print
	outhelp()

def	outhelp():
	print	"""
	Утилита crontab
	Обмен данными с ИС МКУ ГЦГиА (БД Oracle)
	-g	Читать данные о территориях (полигонах) уборки снега	Oracle:	V_PORTAL2_SAD_XXXX
	-s	Передача данных о ходе уборки снега 		Oracle: NS_UBORKA_SAD_TREK
	-a	Передача данных о текущем местоположении ТС	Oracle: NS_UBORKA_SAD_PLOW
	-d	Очистить Oracle:  NS_UBORKA_SAD_TREK
	-c	Проверка статуса ТС 	Oracle:	NS_UBORKA_TEHNIKA
	-o	Обновить записи в NNOVGOROD3785_UAG.NS_UBORKA_SAD_PLOW
	-h	Справка
	-t	Тестирование обмена с БД Oracle 
	"""
	sys.exit()

def	lock_file(fname = r'/tmp/dboracle.lock'):
	""" Монопольный доступ к файлу (lockfile) 
	часто применяется когда нужно предотвратить запуск нескольких копий приложения, 
	либо просто монопольный доступ на запись	"""
	import	fcntl
	_lock_file = open(fname, 'a+')
	try:
		fcntl.flock(_lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
	except	IOError:	return	None
	return	_lock_file

if __name__ == "__main__":
	sttmr = int (time.time())
	id_flock = lock_file()
	if not id_flock:
		print "Break lock_file", sys.argv, time.strftime("%Y-%m-%d %T", time.localtime(sttmr))
		sys.exit()

	print "Start %i" % os.getpid(), sys.argv, time.strftime("%Y-%m-%d %T", time.localtime(sttmr))
	sfunc = None
	fout = sys.stdout
	flasttm = r'/tmp/NS_UBORKA_SAD_TREK.lasttime'
	foutjsn = r'/home/smirnov/MyTests/Wialon/data/territory-%s.json' % time.strftime("%Y%m%d", time.localtime(sttmr))
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'hdsagtco')
		for o in optlist:
			if o[0] == '-h':	outhelp()
			if o[0] == '-g':	sfunc = "get_territory"
			if o[0] == '-s':	sfunc = "send_lines"
			if o[0] == '-a':	sfunc = "send_autos"
			if o[0] == '-d':	sfunc = "del_trek"
			if o[0] == '-c':	sfunc =	"check_tsnow"
			if o[0] == '-o':	sfunc =	"update_inn"
			if o[0] == '-t':	sfunc = otest()

		dbo = dboracle()
#		print "dbo", dbo, dbo.last_error
		if not dbo or dbo.last_error:
			print "Can't connected fo dboracle"
			sys.exit()
	#	print "\t", sfunc

		if sfunc == "get_territory":
			print "foutjsn:\t", foutjsn
			fout = open (foutjsn, 'w')
			'''
			print >> fout, "TEST ZZZZZZZ", foutjsn
			'''
			for tname in gtables:
				get_territory (tname, 'id, region, region_ID, CATEG')
			fout.close()
			os.system ("diff %s /home/smirnov/MyTests/Wialon/data/territory.json > /home/smirnov/MyTests/Wialon/data/patch.json" % foutjsn)
		elif sfunc == "send_lines":
			starttm = 0
			if os.path.isfile (flasttm):
				f = open (flasttm)
				stm = f.readline().strip()
				if stm.isdigit():	starttm = int (stm)
				f.close()
			if sttmr - starttm > 360:	starttm = sttmr -360
			send_lines (starttm)
			os.system ('echo %s > %s' % (int (time.time() -30), flasttm))
			send_autos ()
		elif sfunc == "send_autos":
			send_autos ()
		elif sfunc == "del_trek":
			query = "DELETE FROM %s.%s" % (prefix, 'NS_UBORKA_SAD_TREK')
			print query, dbo.execute (query)
		elif sfunc == "check_tsnow":
			check_tsnow ()
		elif sfunc == "update_inn":
			update_inn ()
		else:	outhelp()
	except	SystemExit:	pass
	except  getopt.GetoptError:	outhelp()
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT __main__:", exc_type, exc_value
	id_flock.close()
	print 	'#'*22, "dtime = %d \n" % (int(time.time()) - sttmr)
	'''
#	query = "SELECT %s FROM %s.%s" % ("%s.ora2geojson.sdo2geojson('select * from %s',ROWID, geometry)" % (prefix, 'NS_UBORKA_SAD_TREK'), prefix, 'NS_UBORKA_SAD_TREK')
	query = "SELECT %s FROM %s.%s" % ('*', prefix, 'NS_UBORKA_CATEG')	# 'NS_UBORKA_SAD_TREK')
	print	query
	print	dbo.get_rows(query)
	print	dbo.desc
	query = "DELETE FROM %s.%s" % (prefix, 'NS_UBORKA_SAD_TREK')
	print query, dbo.execute (query)
	print 	'#'*22, '\n'

#	send_lines ()
#	get_geometry ('NS_UBORKA_SAD_TREK', 'id, color')
#	get_territory ('V_PORTAL2_SAD_AVTOZ', 'id, region, region_ID, CATEG')
	for tname in gtables:
		get_territory (tname, 'id, region, region_ID, CATEG')
	'''
