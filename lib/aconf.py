#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	os, sys	#, time, json
import	math

LIBRARY_DIR = r"/home/smirnov/WT/lib"          # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

import	dbtools
#import	dbsqlite

class	aconf:
	Rz = (6378245.0+6356863.019)/2	# Радиус земли (м)
	db_agro = None
	gz_reports = {}
	ts_reports = ['52НН5225', '52НН5226', '52НН5227', '52НР0741', '52НР5739', '52НР9988', 'Н213ВК152', 'Н303ВК152', 'Н402КХ152']
	last_err = None

	def __init__ (self, dbname = 'agro_test'):
		try:
			self.db_agro = dbtools.dbtools('host=212.193.103.20 dbname=%s port=5432 user=smirnov' % dbname)
		#	res = self.db_agro.get_table ("zborder", "rid = 371 AND id > 1", "id, n, c")
			res = self.db_agro.get_table ("zborder", "rid = 371", "id, n, c")
			if res:
				for r in res[1]:
					zid, n, c = r
					self.gz_reports[zid] = { 'name': n, 'color': c } 
		except:	self.last_err = "except: __init__"

	def gps_way (self, p1, p2):
		dY = abs(p1[0] - p2[0])
		if dY > 5.:	return
		dX = abs(p1[1] - p2[1])
		if dX > 5.:	return
		print p1, p2, '\tRz', self.Rz, '\tr', self.Rz * math.cos((p1[0] + p2[0])*math.pi/360)
		print dX, dY, '1'*11, (p1[0] + p2[0])/2, '\tdY', dY * math.cos((p1[0] + p2[0])*math.pi/360)
	#	dY = dY * self.Rz * math.cos((p1[0] + p2[0])*math.pi/360) * math.pi/180
		dY = dY / math.cos((p1[0] + p2[0])*math.pi/360)
		print dX, dY, '2'*11
	#	return	p1, p2
		return	self.Rz*math.sqrt(dX**2 + dY**2)*math.pi/180

	def gps_speed (self, dX, dY, dT):
		""" Расчет скорости движениея по данным навигатора	"""
		if dT == 0:	dT = 1
		s = self.Rz*math.sqrt(dX**2 + dY**2)*math.pi/180
		sp = s*3.6/dT
		return	sp

if __name__ == "__main__":
	points = [ [56.392561, 43.742758], [56.392561, 44.171311], [56.159955, 44.171311], [56.159955, 43.742758], [56.392561, 44.171311] ]
	a = aconf ()
	for j in xrange (len (points) -1):
		print 'S =\t', a.gps_way (points[j], points[j+1]) 

#	for j in xrange(12500):	print j, '\t', 56.392561 - j*1.860848e-05
