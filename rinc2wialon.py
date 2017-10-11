#!/usr/bin/python
# -*- coding: utf-8 -*-

import  os, sys, time
import	json
import	getopt

LIBRARY_DIR = r"/home/smirnov/WT/lib"          # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

CONF_PATHNAME = r"/home/smirnov/Wialon/sys.ini"
CONFIG = None
if os.access (CONF_PATHNAME, os.F_OK):
	import ConfigParser
	CONFIG = ConfigParser.ConfigParser()
	CONFIG.read (CONF_PATHNAME)
	print	"\nSystem\t", CONFIG.get('System', 'title')
	usr2token = dict(CONFIG.items('usr2token'))
	DBDS = dict(CONFIG.items('dbNames'))

import	twlp
import	dbtools	#, cglob

#WHOST =	r"http://wialon.rnc52.ru/wialon/"

def	out_pos (pos):
	if not pos:	return	"None pos"
	sout = "\t[%s %3.9f, %3.9f, %d]" % (time.strftime("%Y-%m-%d %T", time.localtime(pos['t'])), pos['x'], pos['y'], pos['z'])
	return	sout

def	get_pflds (flags):
	pflds = {}
	for k in flags.keys():
		pflds[flags[k]['n']] = flags[k]['v']
	return pflds

def	check_fflags (fl_name, flags, sid, itemId):
	""" Проверка наличия флагов 'flds', 'aflds'	"""
	update = {}
	inn = None
	delete = []
#	print	"\t%s:" % fl_name
	for k in flags.keys():
		if not flags[k]['v']:	continue
#		print "\t", k, flags[k]['id'], flags[k]['n'], flags[k]['v']	#, type(flags[k]['v'])
		if '\\xd0'in flags[k]['v']:	# зачистить дефектные поля
			flags[k]['v'] = ''
			update[k] = flags[k]
			continue
		if flags[k]['n'] in [u'INN', u'inn', u'ИНН']:
			if not len(flags[k]['v']) in [10, 12]:
				delete.append(flags[k]['id'])
			elif inn and inn[0]['INN'] == flags[k]['v']:
				delete.append(flags[k]['id'])
			else:
				inn = (flags[k]['id'], flags[k])
				if flags[k]['n'] != u'INN':
					flags[k]['n'] = u'INN'
					update[k] = flags[k]
			continue
	if delete:
	#	print "delete", delete
		if fl_name == 'flds':
			svc = 'item/update_custom_field'
		else:	svc = 'item/update_admin_field'
		for k in delete:
			data = {'sid': sid, 'svc': svc, 'params':{"itemId": itemId, "id": k, "callMode":"delete"}}
			print twlp.requesr (data, host = 'wialon.rnc52.ru')
			time.sleep(0.1)

	if update:
	#	print	"update:", update
		for k in update:
			n = update[k]['n']
			v = update[k]['v']
			if fl_name == 'flds':
				svc = 'item/update_custom_field'
			else:	svc = 'item/update_admin_field'
			data = {'sid': sid, 'svc': svc, 'params':{"itemId": itemId, "id": k, "n": n, "v": v, "callMode":"update"}}
			print twlp.requesr (data, host = 'wialon.rnc52.ru')
			time.sleep(0.1)
	return	inn
	
def	check_inn (sid, itemId, dfres, item):
	flds = dfres.keys()
	if len(flds) > 1:
		print "\tDoule INN", dfres
		return

	fld = flds[0]
	k, dfinn = dfres[fld]
	query = "SELECT * FROM transports WHERE gosnum = '%s'" % item['nm'].encode('UTF-8') 
	dts = dbcon.get_dict(query)
	if dts:		return

	query = "SELECT id_org, inn, bm_ssys, label, bname, region FROM organizations WHERE inn = %s" % dfinn['v']	# id_org, bm_ssys, region =>	transports
	print "\t", k, fld, dfinn, query
	dorg = dbcon.get_dict(query)
	if not dorg:	return

	# INSERT INTO transports (gosnum, marka, modele, vin, vinnumber, year, ptsnumber, registrationnumber, registrationdate, id_org, bm_ssys, region)
	'''
	1 1 vehicle_type Трактор
	3 3 year 2014
	2 2 brand Беларус
	5 5 vin 12036049
	4 4 registration_plate 52НН5225
	6 6 model 1221.2
	'''
	cols = ['gosnum', 'id_org', 'bm_ssys', 'region']
	vals = ["'%s'" % item['nm'].encode('UTF-8'), "%d" % dorg['id_org'], "%d" % dorg['bm_ssys'], "%d" % dorg['region']]
	print ", ".join(vals)
#	print "\t", dorg
	pflds = get_pflds (item['pflds'])
	for k in pflds.keys():
		print "\t", k, pflds[k], type (pflds[k])
		if not pflds[k]:	continue
		if '\\xd0' in pflds[k]:	continue
	#	continue
		if k == 'vehicle_type':
			cols.append('type')
			vals.append("'%s'" % pflds[k].encode('UTF-8'))
		elif k == 'year':
			cols.append('year')
			vals.append("'%s'" % pflds[k])
		elif k == 'brand':
			cols.append('marka')
			vals.append("'%s'" % pflds[k].encode('UTF-8'))
		elif k == 'model':
			cols.append('modele')
			vals.append("'%s'" % pflds[k].encode('UTF-8'))
		elif k == 'vin':
			cols.append('vin')
			vals.append("'%s'" % pflds[k])
		elif k == 'registration_plate':
			cols.append('registrationnumber')
			vals.append("'%s'" % pflds[k].encode('UTF-8'))
		else:	pass
		'''
		elif k == 'year':
			cols.append('year')
			vals.append("'%s'" % pflds[k])
	print ", ".join(cols),
	print ", ".join(vals)
		'''
	print cols, vals
	for v in vals:	print v,
	print "#############"
#	twlp.ppp(item['prms'], "prms")
#	twlp.ppp(item['rfc'], "rfc")
#	twlp.ppp(item['pflds'], "pflds")
#	os.exit()

def	autos ():
	print	USER
	if not usr2token.has_key(USER):
		print	"Unknown user Wialon '%s'." % USER
		return
	data = {'svc': 'token/login', 'params': {'token':'%s' % usr2token[USER] }}
	b, sres = twlp.requesr(data, host = 'wialon.rnc52.ru')
	if not b:
		print b, sres
		return
	sid = sres['eid']
	flags = -1	#0x0409
	itype = 'avl_unit'
	data = {'sid': sid, 'svc': 'core/search_items', 'params':{'spec':{'itemsType':itype,'propName':'*','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':flags,'from':0,'to':0}}
	b, sres = twlp.requesr(data, host = 'wialon.rnc52.ru')
	if not b:
		print b, sres
		return
	j = 0
	for item in sres['items']:
		chres = {}
		if not item['pos']:			continue
		if not ((item.has_key('aflds') and item['aflds']) or item['flds']):	continue
		j += 1
#		if j > 11:	break
		itemId = item['id']
		if not (item['aflds'] or item['flds']):	continue
	#	print item['nm'].encode('UTF-8'), out_pos(item['pos'])
		if item.has_key('flds') and item['flds']:
			fres = check_fflags ('flds', item['flds'], sid, itemId)
			if fres:	chres ["fres"] = fres
		if item.has_key('aflds') and item['aflds']:
			fres = check_fflags ('aflds', item['aflds'], sid, itemId)
			if fres:	chres ["afres"] = fres

		if chres:
			print item['nm'].encode('UTF-8'), out_pos(item['pos'])
			check_inn (sid, itemId, chres, item)
		continue
'''
#	print json.dumps(sres)
#	json.loads('["foo", {"bar":["baz", null, 1.0, 2]}]') ==> obj
#	help (json)
'''

def	outhelp ():
	print "outhelp", sys.argv
	print """
	-t	Test (проверка наличия соединения с сервером Wialon БД РНИС)
	-a	autos
	-U	USER = [wialon] or v.smirnov
	-h	Настоящая справка.
	"""
	sys.exit()

def	tests ():
	print "Test (проверка наличия соединения с сервером Wialon БД РНИС)"
	if CONFIG:
		print "CONFIG [usr2token]:"
		for k in usr2token:
			print "\t%s =>\t" % k, usr2token[k],
			data = {'svc': 'token/login', 'params': {'token':'%s' % usr2token[k] }}
			b, sres = twlp.requesr(data, host = 'wialon.rnc52.ru')
			print	"\t%s" % b
	if DBDS:
		print "CONFIG ['dbNames']:"
		for k in DBDS:
			print "\t%s =>\t" % k,	DBDS[k],
			dbi = dbtools.dbtools(DBDS[k])
			if dbi:		print "\tOK"
	sys.exit()

if __name__ == "__main__":
	sttmr = time.time()
	USER = 'wialon'
	print "Start PID: %i\t" % os.getpid(), sys.argv, time.strftime("%Y-%m-%d %T", time.localtime(sttmr))
	is_exec = None
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'thaU:')
		if not optlist:		outhelp()


		for o in optlist:
			if o[0] == '-U':	USER = o[1]
			if o[0] == '-h':	outhelp ()
			if o[0] == '-t':	tests ()
			if o[0] == '-a':	is_exec = 'autos'

		dbcon = dbtools.dbtools(DBDS['contracts']) #	contracts
		if is_exec == 'autos':	autos ()

	except	getopt.GetoptError:
		print "Ошибка в параметрах!\n",	outhelp()
	print "dt %9.4f" % (sttmr - time.time())
