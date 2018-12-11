#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	sys, os, time
import	math

LIBRARY_DIR = r"/home/smirnov/WT/lib"	# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

import p4_test as p4
import	dbtools

#asnow = dbtools.dbtools('host=127.0.0.1 dbname=anti_snow port=5432 user=smirnov')
dbrec =	dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')

def	init_mask ():
	print 'init_mask', mask.get_config()
	itm = int (time.time())
#	print	'\t t > %d ORDER BY idd, t DESC' % (itm - 3600)
	res = dbrec.get_table('vdata_pos', 't > %d ORDER BY idd, t DESC' % (itm - 3600))
	if not res:	return
	dx = mask.lnx/mask.des
	dy = mask.lny/mask.des
	K = dx/dy
	d = res[0]
#	print	d	# ['x', 'y', 't', 'sp', 'cr', 'ht', 'st', 'id_lp', 'ida', 'idd', 'inn', 'nm', 'code', 'tinn', 'gosnum', 'marka', 'rem', 'bname']
	print	len (res[1])
	idd_oks = 0
	gx_old = 0.0
	gy_old = 0.0
	for r in res[1]:
		gx = float (r[d.index('x')])
		gy = float (r[d.index('y')])
		if idd_oks and r[d.index('idd')] == idd_oks:
		#	print r[d.index('gosnum')], idd_oks, '\tdX: %f' % (gx_old-gx), '\tdY: %f' % (gy_old-gy) 
			mask.check_line ((gx_old, gy_old), (gx, gy), 0, r[d.index('cr')])
			'''
			'''
		else:
			# (['lon', 'lat', 'curs', 'tcreate', 'tlife', 'stat', 'rem', 'idp'], [(3053, 3570, None, 1532961857, None, None, None, 49)])
			pv = mask.is_pmask([gx, gy])
			if pv:	mask.set_pmask (pv[1][0][:2])
	#		xy = pv[1][0][:2]
	#		print r[d.index('x')], r[d.index('y')], r[d.index('t')], r[d.index('cr')], r[d.index('gosnum')],	#, r[d.index('')]
	#		print '\t', pv, '\txy:', xy
	#		mask.set_pmask(xy)
		idd_oks = r[d.index('idd')]
		gx_old = gx
		gy_old = gy
	#	break

def	inspect_polygons (region = 2):
	""" Просмотр полигонов Района и инспекция наличия описателей в pmask	"""
	asnow = dbtools.dbtools('host=127.0.0.1 dbname=anti_snow port=5432 user=smirnov')
	query = "SELECT idp, id_lab, porder, box(plgn), rname FROM vpolygons WHERE id_lab IN (SELECT id_lab FROM plabel WHERE region = %s) ORDER BY id_lab, porder ;" % region

	rows = asnow.get_rows (query)
	if not rows:	return

	tcreate = int(time.time())
	for r in rows:
		idp, id_lab, porder, box, rname = r
		jbox =  eval(box)
#		mask.point2xy((box[0][1], box[0][0])
		max_p = mask.point2xy (jbox[0])
		min_p = mask.point2xy (jbox[1])
		print "\t", idp, id_lab, porder, box, '\tmin_p', min_p, '\tmax_p', max_p, rname
		if min_p == None or max_p == None:
			print "\tERROR:\t", idp, id_lab, porder, box, '\tmin_p', min_p, '\tmax_p', max_p, rname
			continue
		
		for jx in xrange(min_p[0], max_p[0]):
			for jy in xrange(min_p[1], max_p[1]):
				'''
				rm = mask.get_pmask ("lon = %s AND lat = %s" % (jx, jy))
				if not rm:
					print "\tNOT in mask", (jx, jy)
					continue
			#	print jx, jy, rm, gxy
				'''
				gx, gy = mask.xy2point((jx, jy))
				'''
				print [jx, jy], [gx, gy]
				'''
				query = "SELECT idp, id_lab, porder, phash, rname FROM vpolygons WHERE region = %s AND '(%f, %f)' <@ plgn ORDER BY porder LIMIT 1;" % (region, gx, gy)
			#	print query
				prows = asnow.get_rows(query)
				if not prows:	continue
				if len(prows) > 1:	print "len(prows)", len(prows)
				for prow in prows:
					if idp != prow[0]:
						jpw = mask.is_pmask ((gx,gy))
					#	print "\tidp:", idp, id_lab, porder, prow[0], prow[4], jpw
						if jpw:
							if jpw[1][0][jpw[0].index('idp')] != idp:
								print '\tmask.set_pmask', (jx, jy), mask.set_pmask((jx, jy), "tcreate = %d, stat = 0, idp = %s, region = %s" % (tcreate, idp, region))
						else:
							query = "INSERT INTO pmask (lon, lat, tcreate, idp, region) VALUES (%d, %d, %d, %d, %d)" % (jx, jy, tcreate, idp, region)
							print query, asnow.qexecute (query)
				
	#	break
	return
	gx_old, gy_old = xy_old
	gx, gy = xy
	print	"old: [ %s, %s ]\t [ %s %s ]" % (gx_old, gy_old, gx, gy)

def	check_alist (inn = 5263004131):
#	'5263004131'
#	res = dbrec.get_table('vlast_pos', "tinn = %s" % 5263004131)
	res = dbrec.get_table('vlast_pos', "tinn NOT IN (5262311940, 5256133168, 5246049830, 5256021545)")
	if not res:	return
	
	d = res[0]
#	print d
	for r in res[1]:
		print r[d.index('gosnum')], time.strftime("\t%Y-%m-%d %T", time.localtime(r[d.index('t')]))
		check_aauto (r[d.index('gosnum')])

def	check_aauto (gosnum = 'Н014ОН152'):
	print '='*22, "check_aauto Загрузить трек ", gosnum
	dx = mask.lnx/mask.des
	dy = mask.lny/mask.des
#	print dx, dy

	res = dbrec.get_table('vdata_pos', "gosnum = '%s' " % gosnum)
	if not res:	return
	d = res[0]
	j = 0
	for r in res[1]:
	#	print r[d.index('gosnum')], time.strftime("\t%Y-%m-%d %T", time.localtime(r[d.index('t')]))
		gx = float (r[d.index('x')])
		gy = float (r[d.index('y')])
		if j > 0:
	#		print gx_old, gy_old, gx, gy
			if (math.fabs(gx_old-gx) < 100*dx and math.fabs(gy_old-gy) < 100*dy):
				mask.check_line ((gx_old, gy_old), (gx, gy), 0, r[d.index('cr')])
			else:	print "\tШирокмй шаг", math.fabs(gx_old-gx), math.fabs(gy_old-gy)
		gx_old = gx
		gy_old = gy
		j += 1
	
#	'С517НМ152','С496НМ152','С505НМ152','С526НМ152','С524НМ152','С513НМ152','С522НМ152','С508НМ152','С523НМ152','С520НМ152','С507НМ152','С515НМ152','С491НМ152'

		 
if __name__ == "__main__":
	mask = p4.pmask()
	for p in [3,4,5,6,7]:	# xrange(8):
		print p
		inspect_polygons (1+p)
	'''
	check_alist ()
	init_mask ()
	for j in xrange(5):
		init_mask ()
		time.sleep(60)
	'''
	print "S"*22
