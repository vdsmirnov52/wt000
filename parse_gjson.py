#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	sys, os, time

LIBRARY_DIR = r"/home/smirnov/WT/lib"	# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

import	dbtools
asnow = dbtools.dbtools('host=127.0.0.1 dbname=anti_snow port=5432 user=smirnov')

def	test():
	# Выполним преобразование из долготы-широты в проекцию меркатора на сфере, которая наиболее часто используется в веб-картографии:
	from pyproj import Proj, transform
	lonlat = Proj(init="epsg:4326")		#  web WGS84
	sphmerc = Proj(init="epsg:3857")
	ll = (30, 59)
	sm = transform(lonlat, sphmerc, *ll)
	print '\t', sm
	print '\t', transform(sphmerc, lonlat, *sm)

	# Яндекс-карты используют другую проекцию - меркатор на эллипсоиде.
	# Посмотрим чем отличается координаты в меркаторе на сфере и на эллипсоиде для нашей точки:
	merc = Proj(proj="merc", ellps="WGS84")
	em = transform(lonlat, merc, *ll)
	print '\t', em
	print '\t', sm[0] - em[0], sm[1] - em[1]
	
	# от WGS84 к Pulkovo-1942 
	pulkovo = Proj(init="epsg:4284")
	pp = transform(lonlat, pulkovo, *ll)
	print '\t', pp

	from pyproj import Geod
	wgs84 = Geod(ellps="WGS84")
	print '\t', wgs84.inv(*(ll + pp))


def	parce_coordinates (pl, epsg_in = 'epsg:3857', epsg_out = 'epsg:4326'):
	""" Преобразовать координаты в web WGS84 	"""
	from pyproj import Proj, transform
	
	sphmerc = Proj(init=epsg_in)	#"epsg:3857")
	lonlat = Proj(init=epsg_out)	#"epsg:4326")		#  web WGS84

	pouts = []
	if type(pl) == list:
		for ppl in pl:
			pout = transform (sphmerc, lonlat, *ppl)
			pouts.append(pout[:2])
	#		print '\t', ppl, pout
	return	pouts
	print '#'*22, pouts

#	Рзбовка GeoISON { type: FeatureCollection ... } выборка полигонов уборки снега
"""	Справочники	"""
CATEG =		[]	# категория учачтка
REGION =	[]	# район города
ORGANIZATION =	[]	# организация

rows = asnow.get_rows ("SELECT * FROM scateg ORDER BY cod")
for r in rows:	CATEG.append(r[1])

rows = asnow.get_rows ("SELECT * FROM sregion ORDER BY cod")
for r in rows:	REGION.append(r[1])

rows = asnow.get_rows ("SELECT id_org, oname FROM organization ORDER BY id_org")
for r in rows:	ORGANIZATION.append(r[1])

def	get_json (fname):
	""" Рзбовка GeoISON { type: FeatureCollection ... } выборка полигонов уборки снега 	"""
	global	CATEG, REGION, ORGANIZATION

	f = open(fname, 'r')
	l = f.read()
#	print l[:100]
#	print l[-100:]
	jsn = eval(l)
#	print jsn	#eys()
	for c in CATEG:		print	c,
	print "="*22
	for c in REGION:	print	c,
	print "="*22
#	return
	for f in jsn['features']:
		print "F:\t", f.keys(), f['geometry']['type']
	#	print '\t', f['properties']
	#	print '\t', f['properties']['CATEG'], f['properties']['REGION'], f['properties']['ORGANIZATION']
		if f.has_key('id'):
			sid = f['id']
		else:
			sid = "NONE_ID_%s" % time.time()
			print "NONE_ID\t", f
			continue
		row = asnow.get_row ("SELECT id_lab FROM plabel WHERE sid = '%s'" % sid)
		if not row:
			vplabel = {'sid': "%s" % sid}
			for n in f['properties'].keys():
				print '\t%s:\t' % n, f['properties'][n]
				if n == 'CATEG':
					if f['properties'][n] in CATEG:
						vplabel['CATEG'] = 1 + CATEG.index(f['properties'][n])
					else:
						CATEG.append(f['properties'][n])
						vplabel['CATEG'] = len('CATEG')
						query = "INSERT INTO scateg (cod, sname) VALUES (%d, '%s')" % (len((CATEG)), f['properties'][n])
						print query, asnow.qexecute (query)
				elif n == 'REGION_ID':
					continue
					if f['properties'][n] and f['properties'][n] > 0:
						vplabel['REGION'] = f['properties'][n]
				elif n == 'REGION':
					if f['properties'][n] in REGION:
						vplabel['REGION'] = 1 + REGION.index(f['properties'][n])
					else:
						REGION.append(f['properties'][n])
						query = "INSERT INTO sregion (cod, sname) VALUES (%d, '%s')" % (len((REGION)), f['properties'][n])
						print query, asnow.qexecute (query)
				elif n == 'ORGANIZATION':
					if f['properties'][n] in ORGANIZATION:
						vplabel['id_org'] = 1 + ORGANIZATION.index(f['properties'][n])
					else:
						ORGANIZATION.append(f['properties'][n])
						vplabel['id_org'] = len('ORGANIZATION')
						query = "INSERT INTO organization (oname) VALUES ('%s')" % (f['properties'][n])
						print query, asnow.qexecute (query)
				else:
					vplabel[n] = f['properties'][n]
	
			cols = []
			vals = []
			for k in vplabel.keys():
			#	print k, vplabel[k]
				cols.append(k)
				vals.append("'%s'" % vplabel[k])
			query =	"INSERT INTO plabel (%s) VALUES (%s); SELECT max(id_lab) FROM plabel;" % (", ".join(cols), ", ".join(vals))
			print query
			row = asnow.get_row(query)
		if not row:	return
		id_lab = row[0]
		'''
		print "geometry type:\t", f['geometry']['type']
		'''
		jporder = 0
		itm  = int (time.time())
	#	asnow.qexecute ("DELETE FROM polygons WHERE id_lab = %s" % id_lab)
		for g in f['geometry']['coordinates']:
			if f['geometry']['type'] == 'MultiPolygon':
				for s in g:
					jporder += 1
					sp = str (parce_coordinates (s))
					phash = hash(sp)
					query = "INSERT INTO polygons (id_lab, porder, plgn, phash, tcreate) VALUES (%d, %d, '(%s)', %d, %d)" % (id_lab, jporder, sp[1:-1], phash, itm)
					print query, asnow.qexecute (query)
			elif f['geometry']['type'] == 'Polygon':
				sp = str (parce_coordinates (g))
				phash = hash(sp)
				query = "INSERT INTO polygons (id_lab, porder, plgn, phash, tcreate) VALUES (%d, %d, '(%s)', %d, %d)" % (id_lab, jporder, sp[1:-1], phash, itm)
				print query , asnow.qexecute (query)
			else:
				print len(g), 'ZZZ\t', g
####	get_json	#######################

def	get_base_json ():
	ddd = { 1: r'data/autozavod.json',
		2: r'/kanavino.json', 3: r'/lenin.json', 4: r'/moskva.json', 5: r'/nijegorod.json', 6: r'/priofski.json', 8: r'/sormovo.json', 7: r'/sovetski.json' }
	print "Start", sys.argv[0], time.strftime("%Y-%m-%d %T", time.localtime(time.time()))
	if len(sys.argv) == 1:
		print "\tОтсутствует путь к файлам формата GeoJson."
	for fname in sys.argv[1:]:
		if not os.path.isfile(fname):
			print "\tФайл '%s' не найден!" % fname
		else:
			print "\tРазбор файла '%s':" % fname
			get_json (fname)
	print

def	get_patch_json (fname):
	"""
	diff territory.json territory-OLD.json
	< - add
	> - del
	"""
	f = open(fname, 'r')
	l = f.readline()
	j = 0
	try:
		while l:
		#	print l[:100]
			if l[0] in "<>{":
				desc, geom = l.strip().split('@')
				if l[0] == '{':
					ddesc = eval (desc)
					flag = 'ADD'
				else:
					print desc
					ddesc = eval (desc[2:])
					if l[0] == '<':	flag = 'ADD'
					if l[0] == '>':	flag = 'DEL'
				region = ddesc.get('REGION_ID')
				icateg = ddesc.get('CATEG_ID')
				opid = ddesc.get('ID')
		#		print	flag, region, icateg, opid
				dpols = eval (geom)	#[:111]
				for g in  dpols['coordinates']:
					if dpols['type'] == 'MultiPolygon':
						for s in g:	uptate_asnow (flag, opid, icateg, region, s)
					elif dpols['type'] == 'Polygon':
						uptate_asnow (flag, opid, icateg, region, g)
					else:	print flag, region, icateg, opid, dpols['type']
				j += 1
			else:
				print l
			l = f.readline()
	#		if j > 11:	break
		return	j
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT get_patch_json:", exc_type, str(exc_value).strip(), "\n\t", query
		return	False

def	uptate_asnow (flag, nopid, ncat, nreg, cpol):
	""" Проверка наличия описателя полигона, обновление или создание	"""
	itm = int (time.time())
	sp = str (parce_coordinates (cpol))
	phash = hash(sp)
	query = "SELECT opid, idp, categ, region  FROM polygons WHERE phash = %s" % phash
	try:
		pr = asnow.get_row (query)
		if pr:
			opid, idp, categ, region = pr
			if flag == 'DEL' and opid == nopid:
				query = "DELETE FROM polygons WHERE opid = %s AND phash = %s" % (nopid, phash)
				print 'flag\t', flag, querya, asnow.qexecute (query)
				return
			if not (nopid == opid and ncat == categ and nreg == region):
				query = "UPDATE polygons SET opid = %d, categ = %d, region =%d WHERE idp =%d" % (nopid, ncat, nreg, idp)
				asnow.qexecute (query)
			###	Проверить описаниев полигона в pmask
			mcount = asnow.get_row("SELECT count(*) FROM pmask WHERE idp = %d" % idp)
			if mcount[0] == 0:
				init_pmask (idp, itm)
			return
		if flag != 'ADD':
			print "W flag\t", flag, nopid, ncat, nreg, cpol
			return
		###	Добавить Новый полигон
		print "NEW", nopid, ncat, nreg, phash
		query = "INSERT INTO polygons (plgn, phash, tcreate, opid, categ, region) VALUES ('(%s)', %d, %d, %d, %d, %d); SELECT max(idp) FROM polygons;" % (sp[1:-1], phash, itm, nopid, ncat, nreg)
		ridp = asnow.get_row (query)
		init_pmask (ridp[0], itm)
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT uptate_asnow:", exc_type, str(exc_value).strip(), "\n\t", query

import	p4_test as p4
import	math

def	init_pmask (idp, tcreate):
	mask = p4.pmask()
	query = "SELECT idp, region, categ, box(plgn) FROM polygons WHERE idp = %d" % idp
#	print "init_pmask", query
#	mask.is_debug = False
	try:
		row = asnow.get_row (query)
		idp, region, categ, box = row
		jbox =  eval(box)
		max_p = mask.point2xy (jbox[0])
		min_p = mask.point2xy (jbox[1])
		if min_p == None or max_p == None:
			print "\tERROR:\t", idp, region,  box, '\tmin_p', min_p, '\tmax_p', max_p
			return
		for jx in xrange(min_p[0], max_p[0]):
			for jy in xrange(min_p[1], max_p[1]):
				gx, gy = mask.xy2point((jx, jy))
				query = "SELECT idp, region, categ FROM polygons WHERE '(%f, %f)' <@ plgn ORDER BY categ" % (gx, gy)
				prows = asnow.get_rows(query)
				if not prows:	continue

				dmsk = mask._is_pmask ((gx,gy))
				if not dmsk:
					query = "INSERT INTO pmask (lon, lat, tcreate, idp, categ, region) VALUES (%d, %d, %d, %d, %d, %d)" % (jx, jy, tcreate, idp, categ, region)
					print "\t", query, asnow.qexecute (query)
					continue
				if not dmsk['categ'] or dmsk['categ'] > categ:	# Приоритет категорий А, Б, ...	???
					print '\tmask.set_pmask', mask.set_pmask((jx, jy), "idp = %d, tcreate = %d, categ = %s, region = %s" % (idp, tcreate, categ, region))
					continue

				'''
				print	"###\t idp,  region,  categ", idp, region, categ
				print	"\tmask._is_pmask ((gx,gy))", dmsk
				for jr in prows:
					if len(prows) == 1 and row[:3] == jr:
						print '\tmask.set_pmask', mask.set_pmask((jx, jy), "tcreate = %d, categ = %s, region = %s" % (tcreate, categ, region)
					else:
						jidp, jregion, jcateg = jr
						print	"\tjidp, jregion, jcateg", jidp, jregion, jcateg
				'''
		
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT init_pmask:", exc_type, str(exc_value).strip(), "\n\t", query

#	sql/anti_snow.A.20180905.sql	БД с изменениями структуры opid categ
#	SELECT count(*) FROM polygons WHERE idp IN (SELECT  DISTINCT idp FROM pmask);

#	territory.json		20181102-territory.json
#	territory-20181102.json	territory.json

if __name__ == "__main__":
#	get_base_json ()
#	fname = r'territory.json'
	fname = r'/home/smirnov/MyTests/Wialon/data/patch.json'
	fdir = r'/home/smirnov/MyTests/Wialon/data'
	fpatch = 'patch.json'
	fname = os.path.join (fdir, 'patch.json')
	if os.path.isfile(fname):
		jres = get_patch_json (fname)
		print "get_patch_json jres:", jres, fname
		if jres and jres > 0:
			dmark = time.strftime("%Y%m%d", time.localtime(time.time()))
			npatch = os.path.join (fdir, 'patch-%s.json' % dmark)
			cmd = [
			"mv %s %s" % (fname, os.path.join (fdir, 'patch-%s.json' % dmark)),
			"mv %s %s" % (os.path.join (fdir, 'territory.json'),  os.path.join (fdir, '%s-territory.json' % dmark)),
			"mv %s %s" % (os.path.join (fdir, 'territory-%s.json' % dmark),       os.path.join (fdir, 'territory.json'))
			]
			print "\n".join(cmd)
			os.system ("\n".join(cmd))
		#	os.system ("mv %s /home/smirnov/MyTests/Wialon/data/patch-%s.json" % (fname, dmark))
	else:
		print "Отсутствует файл", fname
#	get_patch_json (r'patch.json')
