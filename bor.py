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
	
def find_routes (depot_id = 128):
	res = u8api_nimbus(cmnd = 'depot/%s/stops' % depot_id, token = TOKEN)
	print res.keys()
	print res['stops'][0].keys()
	j = 0
	for s in res.get('stops'):
		stop_id = s.get('id')
		# stop_name = s.get('n')
		# print "%5d\t %s \t[ %s ]" % (stop_id, stop_name, s.get('d')),
		get_panel(depot_id, stop_id)
		'''
		fls_dict = is_flstop (depot_id, stop_id, stop_name)
		if fls_dict:
			# j += 1
		if j > 11:  break
		'''
	for rout in ROUTES.keys():
		print rout, ROUTES[rout]

if __name__ == '__main__':
	print 'Main bor'
	# print help(nimbus)
	find_routes()
