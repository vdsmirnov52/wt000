#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	sys, os, time
import	math

LIBRARY_DIR = r"/home/smirnov/WT/lib"	# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

import p4_test as p4
import	dbtools

'''
asnow = dbtools.dbtools('host=127.0.0.1 dbname=anti_snow port=5432 user=smirnov')
snow_opts =	{}

def	get_snow_opts():
	global	snow_opts
	res = asnow.get_table ('snow_opts', "oname LIKE 'snow_fl%' ORDER BY id", 'oname, ival')
	if not res:	return
	for r in res[1]:
		oname, ival = r
		if oname == 'snow_flag':	snow_opts['rall'] = ival
		elif 'snow_fl' in oname:	snow_opts['r'+oname[-2:]] = ival
	print	snow_opts		
	
def	is_snow (rid = None):
	global	snow_opts
	if not snow_opts:
		get_snow_opts()
	rall = snow_opts.get('rall')
	if rall:	return	rall
	elif rid and rid > 0:
		return	snow_opts.get('r%02d' % rid)
'''
	
dbrec =	dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')

def	init_mask ():
#	print 'init_mask', mask.get_config()
	itm = int (time.time())
#	print	'\t t > %d ORDER BY idd, t DESC' % (itm - 3600)
	res = dbrec.get_table('vdata_pos', 't > %d ORDER BY idd, t DESC' % (itm - 360))
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
	old_xy = (0.0, 0.0)
	seend_lines = []
	jline = []
	for r in res[1]:
		snow_lines = {}
		gx = float (r[d.index('x')])
		gy = float (r[d.index('y')])
		if idd_oks and r[d.index('idd')] == idd_oks:
		#	print r[d.index('gosnum')], idd_oks, '\tdX: %f' % (gx_old-gx), '\tdY: %f' % (gy_old-gy) 
			sres = mask.check_line ((gx_old, gy_old), (gx, gy), 0, r[d.index('cr')], r[d.index('gosnum')])
			if sres:
				itm, gosnum, sstat = sres[:3]
	#			print itm, gosnum, "[%s]" % old_gosnum, sstat, sres[3], sres[4]
				if gosnum == old_gosnum:
	#				print itm, gosnum, sstat, sres[3:], old_xy,  sres[3], (old_xy == sres[3])
					if old_xy == sres[3]:
						jline.append(sres[4])
					else:
						seend_lines.append(jline)
						jline = [sres[3], sres[4]]
					old_xy = sres[4]
				else:
					if old_gosnum and seend_lines:
						# Save send Line
						query = "INSERT INTO to_send (tevent, gosnum, quality, slines) VALUES (%d, '%s', '%s', '%s')" % (itm, old_gosnum, old_stat, str(seend_lines))
					#	print	">>\t", old_gosnum, seend_lines
						print ">>\t", query, mask.sql_query (query)
						seend_lines = []
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
	#	break
	if is_snow:
	#	print "seend_lines:", old_gosnum, seend_lines
		if seend_lines:
			query = "INSERT INTO to_send (tevent, gosnum, quality, slines) VALUES (%d, '%s', '%s', '%s')" % (itm, old_gosnum, old_stat, str(seend_lines))
			print ">>\t", query, mask.sql_query (query)
		if is_snow == 1:	dtm =  mask.snow_opts['dt01'] 
		if is_snow == 2:	dtm =  mask.snow_opts['dt02'] 
		mask.stat_decline(dtm) 
	else:	mask.stat_decline()
	query = "DELETE FROM to_send WHERE tevent < %d;" % (int (time.time()) - 12*3600)
	print	"\t", query, mask.sql_query (query)

if __name__ == "__main__":
	mask = p4.pmask()
	init_mask ()
	'''
	for j in xrange(5):
		init_mask ()
		time.sleep(60)
	print "S"*22
	'''
