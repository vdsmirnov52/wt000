#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""
	Утилита crontab
	Поиск данных о наличии ТС на маршрутах (рейсах) МУП "Борское ПАП"
	API NimBus
"""
import sys
LIBRARY_DIR = r"/home/smirnov/Wialon/lib"          # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

# '''
from nimbus import u8api_nimbus
import  dbtools
# '''

TOKEN = 'Token 30e04452062e435a9b48740f19d56f45'
ROUTES = {}

def get_panel (depot_id, stop_id):
	cmnd = r'depot/%s/stop/%s/panel' % (depot_id, stop_id)
	panel = u8api_nimbus(cmnd, TOKEN)
	rlist = panel.get('r')
	for k in xrange(len(rlist)):
		rout = rlist[k].get('n')
		tt = rlist[k].get('tt')
		if tt:
			for i in xrange(len(tt)):
				uid = tt[i]['uid']
				if uid:
					if not ROUTES.has_key(rout):    ROUTES[rout] = []
					if uid not in ROUTES[rout]:     ROUTES[rout].append(tt[i]['uid'])
	# return rlist[0].get('fs')
	# unit_id = '%s' % panel['r'][k]['tt'][i]['uid']
	# rnum = "%s" % panel['r'][k]['n']
	return  panel.keys()
	
def is_flstop (depot_id, stop_id, stop_name):
	cmnd = r'depot/%s/stop/%s/panel' % (depot_id, stop_id)
	panel = u8api_nimbus(cmnd, TOKEN)
	rlist = panel.get('r')
	fls_names = []
	fls_dict = {}
	for k in xrange(len(rlist)):
		fs = rlist[k].get('fs')
		if fs and fs not in fls_names:			fls_names.append(fs)
		ls = rlist[k].get('fs')
		if ls and ls not in fls_names:          fls_names.append(ls)
	
	if stop_name in fls_names:
			rout = rlist[k].get('n')
			tt = rlist[k].get('tt')
			if tt:
				for i in xrange(len(tt)):
					if tt[i]['uid']:
						if not fls_dict.has_key(rout):  fls_dict[rout] = []
						fls_dict[rout].append(tt[i]['uid'])
				
				# fls_dict[rout] = tt
	if fls_dict:    return fls_dict
		# return fls_names
	
def routes_all_stops (depot_id = 128):
	"""
	Поиск маршрутов по ВСЕМ остановкам  Time ~ 3.52m
	:param depot_id:
	:return: ROUTES
	"""
	res = u8api_nimbus(cmnd = 'depot/%s/stops' % depot_id, token = TOKEN)
	# print res.keys()
	# print res['stops'][0].keys()
	j = 0
	for s in res.get('stops'):
		stop_id = s.get('id')
		stop_name = s.get('n')
		print "%5d\t %s \t[ %s ]" % (stop_id, stop_name, s.get('d'))
		get_panel(depot_id, stop_id)
		'''
		fls_dict = is_flstop (depot_id, stop_id, stop_name)
		if fls_dict:
			# j += 1
		if j > 11:  break
		'''

def update_data_route (dbgeo, dbrec):
	if not ROUTES:  return
	for rout in ROUTES.keys():
		if not ROUTES[rout]:    continue
		# Поиск ГосНомеров ТС
		idd_list = []
		for i in ROUTES[rout]:  idd_list.append("%s" % i)
		rgosns = dbrec.get_rows("SELECT idd, gosnum, marka FROM recv_ts WHERE idd IN ('%s');" % "', '".join(idd_list))
		if not rgosns:  return

		gosns = []
		for r in rgosns:
			# idd2gosn[int(r[0])] = r[1]
			gosns.append(r[1])

		drout = dbgeo.get_dict("SELECT * FROM data_route WHERE organization_id = 2 AND title = '%s';" % rout)
		print rout, ROUTES[rout],
		if not drout:
			query = """INSERT INTO data_route (title, organization_id) VALUES ('%s', 2); SELECT * FROM data_route WHERE organization_id = 2 AND title = '%s';""" % (rout, rout)
			drout = dbgeo.get_dict(query)
			# print query
		route_id = drout.get('id')
		query = "UPDATE data_transport SET route_id = %s WHERE organization_id = 2 AND number IN ('%s');" % (route_id, "', '".join(gosns))
		print "\t", query, dbgeo.qexecute(query)


def routes_end_stops (depot_id = 128):
	"""
	Поиск маршрутов по конечным остановкам  Time ~ 0.30m
	:param depot_id:
	:return: ROUTES
	"""
	res = u8api_nimbus(cmnd = 'depot/%s/routes' % depot_id, token = TOKEN)
	routes = res.get('routes')
	end_stops = []
	for r in routes:
		print r.get('n'), r.get('id'), r.get('u')
		fs = r['st'][0]['id']
		ls = r['st'][-1]['id']
		if not fs in end_stops:     end_stops.append(fs)
		if not ls in end_stops:     end_stops.append(ls)

	print '#'*22, 'len(end_stops)', len(end_stops)
	for sid in end_stops:
		get_panel(depot_id, sid)
		
	
if __name__ == '__main__':
	print 'Поиск данных о наличии ТС на маршрутах (рейсах) МУП "Борское ПАП"'

	dbrec = dbtools.dbtools('host=10.10.2.241 dbname=receiver port=5432 user=smirnov')
	# dbrec = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	dbgeo = dbtools.dbtools('host=212.193.103.21 dbname=geonornc52ru port=5432 user=smirnov')

	if not dbgeo or dbgeo.last_error:   sys.exit()
	if not dbrec or dbrec.last_error:   sys.exit()
	print 'Ok'
	# print help(nimbus)
	# routes_all_stops()
	routes_end_stops()
	update_data_route(dbgeo, dbrec)

	print '#'*22
