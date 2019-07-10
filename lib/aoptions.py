#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	cgi, os, sys, time	#, string
import	json

LIBRARY_DIR = r"/home/smirnov/Wialon/lib/"
sys.path.insert(0, LIBRARY_DIR)

import	dbtools, cglob
DPARAMS = {'order':	[#'pwr_in',
			'pwr_ext', 'lls1_val', 'lls2_val', 'lls1_temp', 'lls2_temp', 'custom', 'custom1', 'fuel level', 'gps_full_mileage', 'adc'],
	'types':	{'adc': "Аналоговые датчики",
			'lls1_val': "ДУТ 1", 'lls2_val': "ДУТ 2", 'pwr_ext': "Зажигание", 'gps_full_mileage': "Полный пробег в GPS",
			'fuel level': "Топливо, л", 'custom': "Основной бак, л", 'custom1': "Резервный бак, л"},
	'displ':	['pwr_ext', 'custom', 'custom1', 'fuel level', 'adc', 'gps_full_mileage'],
	}
def	isdecimal (sss):
	spl = sss.split('.')
	try:
		if len(spl) == 2 and (spl[0] or spl[1]):	
			if spl[0] and spl[0].isdigit() and spl[1] and spl[1].isdigit():	return	True
			elif spl[0] == '' and spl[1] and spl[1].isdigit():	return	True
			elif spl[1] == '' and spl[0] and spl[0].isdigit():	return	True
		return	False
	except:	return	False
	
def	sets_params (request):
	sidd = request.get('idd')
	dbi = dbtools.dbtools('host=212.193.103.20 dbname=agro_test port=5432 user=smirnov')
	row = dbi.get_dict ("SELECT d.*, p.params FROM last_prms p, vdata_pos d WHERE p.dtm = 0 AND p.tm = d.t AND p.idd = '%s'" % sidd)
	print "~rmiddle|"
	print """<div class='list-group-item list-group-item-action active tit'><span class='tit'> <i class="fa fa-cog fa-lg" aria-hidden="true"></i> %s </span>
                &nbsp; <span class="float-right"><i class="fa fa-times" aria-hidden="true" onclick="$('#rmiddle').html('')"></i>&nbsp;</span>
		&nbsp; <span class="float-right"> Save &nbsp; </span>
		</div> """ % row['gosnum']
	if not row:
		print "Нет данных!"
		return
	sparams = row.get('params')
	if not sparams:
		print "Параметры отсутствуют!"
		return
	params = json.loads(sparams)
#	print params

	print "<table width=90%>"
	for k in DPARAMS['order']:
		if k not in DPARAMS['displ']:	continue
		if DPARAMS['types'].has_key(k):
			pname = DPARAMS['types'][k]
		else:	pname = k
		sval = params.get(k)	#.encode('UTF-8')
		if sval == None:	continue
		
		if sval.isdigit():	pval = int(sval)
		elif isdecimal(sval):	pval = float(sval)
		else:			pval = sval
	#	print k, pval, type(pval)
	#	if pval == None:	continue
		print "<tr><td>&nbsp; %s </td><td align='right'>" % pname ,  pval, "</td><td align='right'> <input type='checkbox' name='%s' /></td></tr>" % k
	print "</table>" 
	'''
		print """<li class='list-group-item list-group-item-action d-flex justify-content-between align-items-center'> %s
		&nbsp; <span class="float-right"> %s &nbsp; 
		&nbsp; <input type='checkbox' name='%s' /> &nbsp; </span>
		</li>""" % ( pname, params[k].encode('UTF-8'), k) 
		print k, pname, type(params[k])
	for k in params.keys():
		if k in	DPARAMS['order']:	continue
		print k, params[k], "<br>"
	'''

if __name__ == "__main__":
	sets_params ({'shstat': 'view_canvas', 'idd': '864287036627493'})

	for s in ['123', '.123', '123.456', '123.', '.', '123.qwe', '11.22.44']:
		print s, '\t', isdecimal(s)
