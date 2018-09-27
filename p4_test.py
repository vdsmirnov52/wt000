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
	sphmerc = Proj(init="epsg:3857")	# сферическим Меркатором epsg:3857
	ll = (30, 59)
	sm = transform(lonlat, sphmerc, *ll)
	print 'merc\t', sm
	print 'wgs\t', transform(sphmerc, lonlat, *sm)

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

def	lonlat2merc (lon, lat, tmerc = 'Spher'):
	""" Пересчет координат из широты/долготы в проекцию Меркатора/WGS84 Сферический (Элиптичкский)	"""
#	print	lonlat2merc(37.617778,55.751667)  -> Spher (4187591.891734409, 7509137.581101679) or Ellipse: (4187591.891734409, 7473789.461896971)
 	if lat > 89.5:	lat = 89.5
	if lat < -89.5:	lat = -89.5
 
	rLat = math.radians(lat)
	rLong = math.radians(lon)
 
	a = 6378137.0
	x = a*rLong
	if tmerc == 'Spher':
		y = a*math.log(math.tan(math.pi/4+rLat/2))
	else:	# Ellipse
		b = 6356752.3142
		f = (a-b)/a
		e = math.sqrt(2*f-f**2)
		y = a*math.log(math.tan(math.pi/4+rLat/2)*((1-e*math.sin(rLat))/(1+e*math.sin(rLat)))**(e/2))
	return	x, y
#	WKID:43041 PROJ.4:ortho. 

def	wgs2merc (mpoint):
#	print mpoint
	from pyproj import Proj, transform
	return	transform (Proj(init="epsg:4326"), Proj(init="epsg:3857"), *mpoint)

def	merc2wgs (wpoint):
#	print wpoint
	from pyproj import Proj, transform
	return transform (Proj(init="epsg:3857"), Proj(init="epsg:4326"), *wpoint)

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

import	math

class	pmask:
	Rz = (6378245.0+6356863.019)/2	# Радиус земли (м)
#	zone = [ [43.742758, 56.392561], [44.171311, 56.159955] ]
	zone = [ [43.7250, 56.3956], [44.1648, 56.1625] ]
	lnx = zone[1][0]-zone[0][0]
	lny = zone[0][1]-zone[1][1]
#	print '\tlnx:', lnx, '\tlny:', lny
	x0 = zone[0][0]
	y0 = zone[1][1]
	des = 5000
	stpx = lnx/des
	stpy = lny/des
	snow_opts = {}
	d_curs = 12		# +- допустимое отклонение курса
	max_speed = 41.0	# максимальная скорость при уборке снега

#	config = { 'debug': is_debug, 'zone': zone, 'ln_xy': [lnx, lny], 'stp_xy': [stpx, stpy], 'des': des }

	def	__init__ (self, debug = False):
		self.is_debug = debug
		self.config = {
			'debug': self.is_debug, 'zone': self.zone, 'ln_xy': [self.lnx, self.lny], 'stp_xy': [self.stpx, self.stpy], 'des': self.des,
			'd_curs': self.d_curs, 'max_speed': self.max_speed,
			}
		if self.is_debug:	print "__init__ pmask"

	def	get_config (self):
		return	self.config

	def	set_config (self, opts):
		if type(opts) != dict:	return	False
		for k in opts.keys():
			if self.config.has_key(k):
				self.config[k] = opts[k]
			elif self.is_debug:
				print	'\t"%s" is not in config.keys:' % k, self.config.keys()

	def	sql_query (self, query):
		return	asnow.qexecute (query)

	def	cteare (self):
		print "\n mask_cteare", self.zone
		print "\tx0:", self.x0, "\ty0:", self.y0, "#"*22 , self.stpx, self.stpy
		asnow.qexecute ("TRUNCATE pmask;")
		tcreate = int (time.time())
		x = self.x0
		j = 0
		while True:
			j += 1
			print	"%6d" % j, '\t', x, '\r',
			y = self.y0
			k = 0
			while True:
				k += 1
				query = "SELECT idp, id_lab, porder, phash, tcreate FROM polygons WHERE '(%f, %f)' <@ plgn;" % (x, y)
				row = asnow.get_row (query)
				if row:
					query = "INSERT INTO pmask (lon, lat, tcreate, idp) VALUES (%d, %d, %d, %d)" % (j, k, tcreate, row[0])
					print j, '\t', k, '\t', y, '\t', query, asnow.qexecute (query)
				#	print row
				if y > self.zone[0][1]:	break
				y += self.stpy
			if x > self.zone[1][0]:	break
			x += self.stpx

	def	point2xy (self, p):
		""" Градусы в Позицию маски	"""
		x = p[0]
		y = p[1]
	#	print ">>>\t", x, y, self.zone[1][0]
		if x >= self.x0 and x <= self.zone[1][0] and y >= self.y0 and y <= self.zone[0][1]:
			jx = int (.5 + (x - self.x0)/self.stpx)
			jy = int (.5 + (y - self.y0)/self.stpy)
			return jx, jy

	def	xy2point (self, xy):
		""" Позицию маски в Градусы	"""
		x = self.x0 + xy[0] * self.stpx
		y = self.y0 + xy[1] * self.stpy
		return	x, y

	def	get_pmask (self, swhere = None):
		""" Читать описатель точки	"""
		if not swhere:
			query = "SELECT * FROM pmask WHERE stat >= 0;"
		elif swhere == 'all':
			query = "SELECT * FROM pmask"
		else:
			query = "SELECT * FROM pmask WHERE %s;" % swhere
		if self.is_debug:	print "get_pmask", query
		rows = asnow.get_rows (query)
		return rows

	def	set_pmask (self, xy, sset = None):
		""" Изменить описатель точки	"""
		tcreate = int (time.time())
		if not sset:
			query = "UPDATE pmask SET tcreate = %d, stat = 0 WHERE lon = %d AND lat = %d" % (tcreate, xy[0], xy[1])
		else:
			query = "UPDATE pmask SET %s WHERE lon = %d AND lat = %d" % (sset, xy[0], xy[1])
			'''
			if 'tcreate' in sset:
				query = "UPDATE pmask SET %s WHERE lon = %d AND lat = %d" % (sset, xy[0], xy[1])
			else:	query = "UPDATE pmask SET tcreate = %d, %s WHERE lon = %d AND lat = %d" % (tcreate, sset, xy[0], xy[1])
			'''
		res = asnow.qexecute (query)
		if self.is_debug:
			print	query, res
		return	res
		
	def	is_pmask (self, p):
		""" Проверить наличие	"""
	#	print p
		xy = self.point2xy(p)
		if xy:	return	asnow.get_table('pmask', "lon = %d AND lat = %d" % (xy[0], xy[1]))

	def	_is_pmask (self, p):
		""" Проверить наличие. Вернуть dict	"""
		xy = self.point2xy(p)
		if xy:	return	asnow.get_dict ("SELECT * FROM pmask WHERE lon = %d AND lat = %d" % (xy[0], xy[1]))

	def	gps_speed (self, dX, dY, dT):
		""" Расчет скорости движениея по данным навигатора	"""
		if dT == 0:	dT = 1
		s = self.Rz*math.sqrt(dX**2 + dY**2)*math.pi/180
		sp = s*3.6/dT
		return	sp

	def	stat_decline (self, dtm = None):
		""" Снижение статуса точки в pmask	"""
		if not dtm:	dtm = 4*3600
		query = "UPDATE pmask SET stat = stat-1 WHERE stat > 0 AND tlife < %d" % (int (time.time()) -dtm)
		print dtm, "\t",  query, asnow.qexecute (query), asnow.get_row ("SELECT count(*) FROM pmask WHERE stat > 0")
	#	row = asnow.get_row ("SELECT count(*) FROM pmask WHERE stat > 0")
	#	print row

	def	get_snow_opts(self):
		res = asnow.get_table ('snow_opts', "ival > 0 ORDER BY id", 'oname, ival')
		if not res:	return
		for r in res[1]:
			oname, ival = r
			if oname == 'snow_flag':	self.snow_opts['rall'] = ival
			elif 'snow_fl' in oname:	self.snow_opts['r'+oname[-2:]] = ival
			elif oname == 'dtime_01':	self.snow_opts['dt01'] = ival
			elif oname == 'dtime_02':	self.snow_opts['dt02'] = ival
	#	print	self.snow_opts		
	
	def	is_snow (self, rid = None):
		if not self.snow_opts:
			self.get_snow_opts()
		rall = self.snow_opts.get('rall')
		if rall:	return	rall
		elif rid and rid > 0:
			return	self.snow_opts.get('r%02d' % rid)
		elif rid == None:
			for k in self.snow_opts.keys():
				if k[0] == 'r' and self.snow_opts(k) > 0:
					return	self.snow_opts(k)

	def	check_line (self, itm, old, act, stat = 0, curs = 0, gosnum = None):
		""" Проверки принадлежности отрезка зоне уборки.
		itm - время в точке act
		Корректировка описателя точки в соотретствии со stat:
		0 - прокладка треков в зоне уборки
		2 - уборка, формировать трека ТС
 
		Структура pmask (коментарии)
		stat:
			0 	- зона движения транспорта (есть отметка трекера)
			1-7 	- интекнсивность прохождения в режиме уборка (stat = 2)
		tlife 	- время последнего прохождения уборочной техники
		curs	- направление движения
		"""
	#	itm  = int (time.time())
		dx = self.lnx/self.des
		dy = self.lny/self.des

		gx, gy = act
		gx_old, gy_old = old

	#	print '\tcheck_line [ %f %f ]' % (dx, dy), '[ %f %f ]' % (math.fabs(gx_old-gx), math.fabs(gy_old-gy)), '[ %s %s]' % ((math.fabs(gx_old-gx) < dx), (math.fabs(gy_old-gy) < dy))
	#	if stat == 0 and math.fabs(gx_old-gx) < dx and math.fabs(gy_old-gy) < dy:	return
		if (math.fabs(gx_old-gx) < dx and math.fabs(gy_old-gy) < dy):	return
		jdp = self._is_pmask([gx, gy])
		if not jdp:		return	# Мимо кассы

		sset_pmask = ""
		sstat = 0
		sdtime = 0
		if jdp['categ'] and jdp['categ'] > 0:
			categ = jdp['categ']
		else:	categ = 3
		dpstart = self._is_pmask([gx_old, gy_old])
		if dpstart:
			itm_old = dpstart['tlife']
			categ_old = dpstart['categ']
			if dpstart['region']:
				ssnow = self.is_snow(dpstart['region'])
				if ssnow == 1:	sdtime = self.snow_opts['dt01']
				if ssnow == 2:	sdtime = self.snow_opts['dt02']
		#		print	dpstart, ssnow, dtime
				if dpstart['tlife'] == None or dpstart['tlife'] < itm - sdtime:
					sstat = 1
				elif dpstart['gosnum'] == None or dpstart['gosnum'] != gosnum:
					if dpstart['stat'] == 2:
						sstat = 2
					else:	sstat = 1
				if dpstart['categ'] and dpstart['categ'] > 2:	sstat += 1
				if ssnow > 0:
					sset_pmask = ", tlife = %d, gosnum = '%s', stat = %d" % (itm, gosnum, sstat)
		if self.is_debug:
			print	'old\t', gx_old, gy_old, dpstart
			print	'act\t', gx, gy, jdp

		gdx = gx_old - gx
		gdy = gy_old - gy
		lnx = int (.5 + gdx/dx)
		lny = int (.5 + gdy/dy)

		curs, bcurs = self.calc_curs(curs, (gdx, gdy))
		if bcurs:	sstat += 1	### ???
			
		if math.fabs(lnx) < math.fabs(lny):
			if lny > 0:	stp = 1
			else:		stp = -1
			for j in xrange(0, lny, stp):
				jy = gy_old - j*dy
				jx = gx_old - j*gdx/lny
				jpw = self.is_pmask([jx, jy])
				'''
				'''
				if jpw:		self.set_pmask (jpw[1][0][:2], 'curs = %d %s' % (curs, sset_pmask))
				else:		return
		#		print j, '[ %f %f ]' % (jx, jy), jpw
		else:
			if lnx > 0:	stp = 1
			else:		stp = -1
			for j in xrange(0, lnx, stp):
				jx = gx_old - j*dx
				jy = gy_old - j*gdy/lnx
				jpw = self.is_pmask([jx, jy])
				if jpw:		self.set_pmask (jpw[1][0][:2], 'curs = %d %s' % (curs, sset_pmask))
		#		print '>>', j, '[ %f %f ]' % (jx, jy), jpw
		if sstat:
		#	print gosnum, '\tstat:', sstat,  (gx_old, gy_old), (gx, gy), itm
			return	(itm, gosnum, sstat, [gx_old, gy_old], [gx, gy], categ, bcurs)

	def	calc_curs (self, curs, gdxy):
		""" Расчет курса по геометрии трека	"""
		gdc = self.d_curs	# отклонение курса (+ -)
		gdx, gdy = gdxy
		try:
			K = gdy/gdx
		except ZeroDivisionError:
			K = gdy * 1.8e+300
		gcurs = 180*math.atan (K)/math.pi

		if gdx >= 0 and gdy >= 0:		gcurs = 90 - gcurs
		elif gdx >= 0 and gdy <= 0:		gcurs = 90 - gcurs
		elif gdx < 0 and gdy < 0:		gcurs = 270 - gcurs
		elif gdx < 0 and gdy > 0:		gcurs = 270 - gcurs	
		else:	gcurs = 0

		cdelta = math.fabs (gcurs-curs)
		if (curs - gdc < 0) and (cdelta+gdc > 360):	cdelta = 360 - cdelta
#		print	"int(gcurs)", int(gcurs), "Dcurs:", int(cdelta), (cdelta < gdc)
		return	int(gcurs), (cdelta < gdc)

if __name__ == "__main__":
	print parce_coordinates ([[4897277.406402833,7623525.841707473],[4899522.7441087095,7624574.46218926]])
	test()					# пересчт координвт
	print	'wgs2merc:\t', wgs2merc ([43.99299144744873, 56.325687123111706])
	print	'merc2wgs:\t', merc2wgs ([4897277.406402832, 7623525.841707474])
	
	'''
	mask = pmask()
	step = 1
	for jx in xrange (mask.des / step):	#  Контроль принадлежности точки pmask полигону
		for jy in xrange (mask.des / step):
			gx, gy = mask.xy2point ((jx, jy))
			query = "SELECT idp, id_lab, porder, phash, tcreate FROM polygons WHERE '(%f, %f)' <@ plgn;" % (gx, gy)
			row = asnow.get_row (query)
			if row:	print "lon:%6d, lat:%6d\t" % (jx, jy) , mask.is_pmask((gx, gy))

		print mask.point2xy (mask.xy2point ((j*step, 0))), mask.point2xy (mask.xy2point ((0, j*step))), mask.point2xy (mask.xy2point ((j*step, j*step))),
		print mask.is_pmask(mask.xy2point ((j*step, j*step)))
	mask.cteare()
	print	mask.get_config()
	print	mask.set_config({'debug': True, 'qwer': "QWER"})
	print	mask.get_config()
	print "mask.is_pmask:\t", mask.is_pmask([44.005818, 56.326787])
	print 'mask.point2xy \t', mask.point2xy ([44.001181, 56.325124])	# 44.008578, 56.325124
	print "\t\t", mask.xy2point (mask.point2xy ([44.001181, 56.325124]))

	print 'mask.point2xy \t', mask.point2xy ([44.008578, 56.325124])
	print "\t\t", mask.xy2point (mask.point2xy ([44.008578, 56.325124]))
#	print mask.get_pmask ()
	'''
