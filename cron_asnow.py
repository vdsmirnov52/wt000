#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	sys, os, time
import	math

LIBRARY_DIR = r"/home/smirnov/WT/lib"	# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

import	p4_test as p4
import	dbtools

'''	<- bu/tmp.20180914.py
'''

dbrec =	dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')

def	init_mask ():
	""" АнтиСнег	"""
	mask = p4.pmask()
#	print 'init_mask', mask.get_config()
	itm = int (time.time())
#	print	'\t t > %d ORDER BY idd, t DESC' % (itm - 3600)
	query = "DELETE FROM data_pos WHERE t < %d;" % (itm - 31*24*3600)
	print query, dbrec.qexecute(query)
#	res = dbrec.get_table('vdata_pos', 't > %d ORDER BY idd, t DESC' % (itm - 360))
	res = dbrec.get_table('vdata_pos', 't > %d AND tinn IN (SELECT inn FROM org_desc WHERE bm_ssys = 131072 AND stat > 0) ORDER BY idd, t DESC' % (itm - 360))
	if not res:	return
	dx = mask.lnx/mask.des
	dy = mask.lny/mask.des
	K = dx/dy
	d = res[0]
#	print	d	# ['x', 'y', 't', 'sp', 'cr', 'ht', 'st', 'id_lp', 'ida', 'idd', 'inn', 'nm', 'code', 'tinn', 'gosnum', 'marka', 'rem', 'bname']
#	print	len (res[1])
	idd_oks = 0
	gx_old = 0.0
	gy_old = 0.0
#	mask.is_debug = True
	is_snow = mask.is_snow()
	print	"len (res[1]):", len (res[1]), '\tmask.is_snow', is_snow 

	old_gosnum = ""
	old_stat = 0
	old_t = 0
	old_xy = (0.0, 0.0)
	seend_lines = []
	jline = []
	sspeed = 0.0	# сумма скоростей в треке
	jsspeed = 1	# точек в треке
	for r in res[1]:
		snow_lines = {}
		gx = float (r[d.index('x')])
		gy = float (r[d.index('y')])
		###	gps_speed (self, dX, dY, dT)	# Расчет скорости движениея по данным навигатора
		###	Проверка курса !!!
		if idd_oks and r[d.index('idd')] == idd_oks:
		#	print r[d.index('gosnum')], idd_oks, '\tdX: %f' % (gx_old-gx), '\tdY: %f' % (gy_old-gy) 
			sres = mask.check_line (r[d.index('t')], (gx_old, gy_old), (gx, gy), 0, r[d.index('cr')], r[d.index('gosnum')])
			if sres:
			#	itm, gosnum, sstat = sres[:3]
			#	print 'sres:\t', sres
				itm, gosnum, sstat, old_gxy, gxy, categ, bcurs = sres
				speed = mask.gps_speed (gx_old-gx, gy_old-gy, old_t-r[d.index('t')])
	#			print itm, gosnum, "[%s]" % old_gosnum, sstat, sres[3], sres[4]
				if gosnum == old_gosnum:
					sspeed += speed	# (sspeed + speed)/2
					jsspeed += 1
				#	print	"\tРасчет скорости", speed, sspeed, gosnum
				#	print itm, gosnum, sstat, sres[3:], old_xy,  sres[3], (old_xy == sres[3])
					if old_xy == sres[3]:
						jline.append(sres[4])
					else:
						seend_lines.append(jline)
						jline = [sres[3], sres[4]]
					old_xy = sres[4]
				else:
					if old_gosnum:
						print	"\t\tРасчет скорости", sspeed/jsspeed, jsspeed, old_gosnum
					if old_gosnum and seend_lines:
						# Save send Line
						query = "INSERT INTO to_send (tevent, gosnum, quality, slines) VALUES (%d, '%s', '%s', '%s')" % (itm, old_gosnum, old_stat, str(seend_lines))
					#	print	">>\t", old_gosnum, seend_lines
						mask.sql_query (query)
					#	print ">>\t", query, mask.sql_query (query)
						seend_lines = []
					sspeed = speed
					jsspeed = 1
					jline = [sres[3], sres[4]]
					old_gosnum = gosnum
					old_stat = sstat
					old_xy = sres[4]
			'''
			print 'is_snow', is_snow()
			'''
		else:
			# (['lon', 'lat', 'curs', 'tcreate', 'tlife', 'stat', 'rem', 'idp'], [(3053, 3570, None, 1532961857, None, None, None, 49)])
			pv = mask.is_pmask([gx, gy])
			if pv:	mask.set_pmask (pv[1][0][:2])
		idd_oks = r[d.index('idd')]
		gx_old = gx
		gy_old = gy
		old_t = r[d.index('t')]
	#	break
	if is_snow:
	#	print "seend_lines:", old_gosnum, seend_lines
		if seend_lines:
			print   "\t\tРасчет скорости", sspeed/jsspeed
			query = "INSERT INTO to_send (tevent, gosnum, quality, slines) VALUES (%d, '%s', '%s', '%s')" % (itm, old_gosnum, old_stat, str(seend_lines))
			mask.sql_query (query)
		#	print "S>\t", query, mask.sql_query (query)
		if is_snow == 1:	dtm =  mask.snow_opts['dt01'] 
		if is_snow == 2:	dtm =  mask.snow_opts['dt02'] 
		mask.stat_decline(dtm) 
	else:	mask.stat_decline()
	query = "DELETE FROM to_send WHERE tevent < %d;" % (int (time.time()) - 12*3600)
	print	"\t", query, mask.sql_query (query)

if __name__ == "__main__":
	'''
	print	p4.lonlat2merc (37.617778,55.751667)
	print	p4.lonlat2merc (37.617778,55.751667, True)	#'Ellipse')
	print	p4.wgs2merc ([37.617778,55.751667])
	print   p4.lonlat2merc (37.617778,89.0)
	'''
#	mask = p4.pmask()
	init_mask ()
	'''
	for j in xrange(5):
		init_mask ()
		time.sleep(60)
	print "S"*22
	'''
