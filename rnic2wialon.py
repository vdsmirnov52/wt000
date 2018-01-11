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
	inn = None
	update = {}
	delete = []
#	print	"\t%s:" % fl_name
	for k in flags.keys():
		if not flags[k]['v']:	continue
#		print "\t", k, flags[k]['id'], flags[k]['n'], flags[k]['v']	#, type(flags[k]['v'])
		if '\\xd0'in flags[k]['v']:	# зачистить дефектные поля
			flags[k]['v'] = ''
			update[k] = flags[k]
			continue
		if flags[k]['n'] in [u'INN', u'inn', u'ИНН', u'oinn']:
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
			print twlp.requesr (data, host = HOST)
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
			print twlp.requesr (data, host = HOST)
			time.sleep(0.1)
	return	inn

def	check_inn (sid, itemId, dfres, item):
	flds = dfres.keys()
	if len(flds) > 1:
		print "\tDoule INN", dfres
		return

	add_atts = 0
	fld = flds[0]
	k, dfinn = dfres[fld]
	query = "SELECT t.*, a.autos FROM transports t LEFT JOIN atts a ON a.autos = t.id_ts WHERE gosnum = '%s';" % item['nm'].encode('UTF-8')
#	query = "SELECT * FROM transports WHERE gosnum = '%s'" % item['nm'].encode('UTF-8') 
	dts = dbcon.get_dict(query)
	'''
	if dts:		return
	'''
	if dts:
		if dts['autos']:
			add_atts = dts['autos']
	if add_atts:	return

	query = "SELECT id_org, inn, bm_ssys, label, bname, region FROM organizations WHERE inn = %s" % dfinn['v']	# id_org, bm_ssys, region =>	transports
#	print "\t", k, fld, dfinn, query
	dorg = dbcon.get_dict(query)
	if not dorg:
		print "Отсутствует организация ИНН: %s" % dfinn['v']
		return
#	print "ZZZ add_atts", add_atts, item['nm'], type(dorg)

	# INSERT INTO transports (gosnum, marka, modele, vin, vinnumber, year, ptsnumber, registrationnumber, registrationdate, id_org, bm_ssys, region)
	'''
	1 1 vehicle_type Трактор
	3 3 year 2014
	2 2 brand Беларус
	5 5 vin 12036049
	4 4 registration_plate 52НН5225
	6 6 model 1221.2
	'''
	cols = ['gosnum', 'id_org', 'bm_ssys', 'region', 'bm_status', 'device_id']
	vals = ["'%s'" % item['nm'].encode('UTF-8'), "%d" % dorg['id_org'], "%d" % dorg['bm_ssys'], "%d" % dorg['region'], '12', "-%d" % itemId]
#	print "\t", dorg
	pflds = get_pflds (item['pflds'])
	for k in pflds.keys():
	#	print "\t", k, pflds[k], type (pflds[k])
		if not pflds[k]:	continue
		if '\\xd0' in pflds[k]:	continue
	
		if k == 'vehicle_type':
		#	cols.append('type')
			cols.append('rem')
			vals.append("'%s'" % pflds[k].encode('UTF-8'))
		elif k == 'year':
			cols.append('year')
			vals.append("'%s-01-01'" % pflds[k].encode('UTF-8'))
		elif k == 'brand':
			cols.append('marka')
			vals.append("'%s'" % pflds[k].encode('UTF-8'))
		elif k == 'model':
			cols.append('modele')
			vals.append("'%s'" % pflds[k].encode('UTF-8'))
		elif k == 'vin':
			cols.append('vin')
			vals.append("'%s'" % pflds[k].encode('UTF-8'))
		elif k == 'registration_plate':
			cols.append('registrationnumber')
			vals.append("'%s'" % pflds[k].encode('UTF-8'))
		else:	pass
	
	querys = []
	sdate = time.strftime("%Y-%m-%d %T", time.localtime(item['pos']['t']))
	if dts and add_atts == 0:	# reate ATT only
	#	print "\tZZZ Create ATT only"
		querys.append("UPDATE transports SET bm_ssys = %d, region = %d, bm_status = 12, device_id = -%d WHERE id_ts = %d" % (dorg['bm_ssys'], dorg['region'], itemId, dts['id_ts']))
		querys.append("INSERT INTO atts (mark, modele, uin, sim_1, sim_2, last_date, device_id, autos) VALUES ('WialonHost', '%s', '%s', '%s', '%s', '%s', -%d, %d)" % (
			HOST, item['uid'].encode('UTF-8'), item['ph'].encode('UTF-8'), item['ph2'].encode('UTF-8'), sdate, itemId, dts['id_ts']))
	else:
		querys.append("INSERT INTO transports (%s) VALUES (%s)" % (", ".join(cols), ", ".join(vals)))
	#	print "\nZZZZ\t", item['uid'], item['ph'], item['ph2'], item['hw'], item['psw']
		querys.append("INSERT INTO atts (mark, modele, uin, sim_1, sim_2, last_date, device_id, autos) VALUES ('WialonHost', '%s', '%s', '%s', '%s', '%s', -%d, (SELECT max(id_ts) FROM transports))" % (
			HOST, item['uid'].encode('UTF-8'), item['ph'].encode('UTF-8'), item['ph2'].encode('UTF-8'), sdate, itemId))
#	print "####\t", querys
	print "####\t", ";\n".join(querys), dbcon.qexecute (";\n".join(querys))

def	set_last_date (ts_list):
	""" Обновить last_date в БД contracts	"""
	if not ts_list:
		print 'set_last_date (ts_list):', ts_list
		return
	dts_list = dict(ts_list)
	query = "SELECT id_ts, gosnum, a.id_att, a.last_date, a.bm_wtime, a.mark FROM transports t LEFT JOIN atts a ON id_ts = autos WHERE gosnum IN ('%s')" % "', '".join(dts_list.keys())
#	print query
	row = dbcon.get_rows (query)
	if not row:	return
	sttm = time.localtime(time.time())
	tm_year, tm_mon, tm_mday = sttm[:3]
	stime = time.strftime("%Y-%m-%d %T", time.localtime(time.time()))
	jstime = time.strftime("%Y-%m-%d %T", time.localtime(time.time()- 7200))
	print "\nОбновить last_date", tm_year, tm_mon, tm_mday, stime, jstime
	for r in row:
		id_ts, gosnum, id_att, last_date, bm_wtime, mark = r
		if mark != 'WialonHost':		continue
		if not dts_list.has_key(gosnum):	continue
		jstime = time.strftime("%Y-%m-%d %T", time.localtime(dts_list[gosnum]))
	#	print id_ts, gosnum, id_att, last_date, bm_wtime, mark, jstime
		if jstime > str(last_date):	# > jstime:
			query = "UPDATE atts SET last_date = '%s', bm_wtime = bm_wtime | 512 WHERE id_att = %d;" % (jstime, id_att)
			print gosnum, "\t", query, dbcon.qexecute(query)
	#	else:	print "<<<"

def	fix_pos (ida, uid, nm, pos, inn = None):
	""" Запмсать в БД wialon.last_pos pos & inn	"""
	if not dbwialon:	return

	if inn and inn[1]['v']:
		sinn = inn[1]['v'].encode('UTF-8')
	else:	sinn = 'NULL'
	suid = str(uid)
#	print "uid %s " %uid, sinn, inn
	row = dbwialon.get_row("SELECT id_lp FROM last_pos WHERE ida = %d;" % ida)
	if row:
		query = "UPDATE last_pos SET idd='%s', nm='%s', x=%f, y=%f, t=%d, inn=%s WHERE ida = %d;" % (suid, nm, pos['x'], pos['y'], pos['t'], sinn, ida)
	else:
		query = "INSERT INTO last_pos (ida, idd, nm, x, y, t, inn) VALUES (%d, '%s', '%s', %f, %f, %d, %s);" % (ida, suid, nm, pos['x'], pos['y'], pos['t'], sinn)
	if not dbwialon.qexecute(query):	print query

marks_inn = [u'INN', u'inn', u'ИНН', u'инн', u'oinn']

def	search_inn (flname, flags):
	sinn = None
	update = {}
	for k in flags.keys():
		if not flags[k]['v']:	continue
#		print "\t", k, flags[k]['id'], flags[k]['n'], flags[k]['v']	#, type(flags[k]['v'])
		if '\\xd0'in flags[k]['v']:	# зачистить дефектные поля
			flags[k]['v'] = ''
			update[k] = flags[k]
		if flags[k]['n'] in marks_inn:
			if len (flags[k]['v']) in [10,12] and flags[k]['v'].isdigit():
				sinn = flags[k]['v']
			else:	print '\tBad INN:', flname, flags[k]['n'], flags[k]['v'], len (flags[k]['v'])

	if update:	print 'ZZZ update', update
	return	sinn

def	set_inn_by_autos (sid, itemIds, inn):
	flags = 1 +8 +128
	for iid in itemIds:
		data = {'sid': sid, 'svc': 'core/search_item', 'params':{'id': int(iid), 'flags': flags}}
		b, sres = twlp.requesr(data, host = HOST)
		if not b:	continue
		r = sres['item']
	#	print b, sres.keys(), sres['flags']
		jinn = search_inn ('flds', r['flds'])
		if jinn and jinn == inn:		continue

		time.sleep(0.1)
		k = 1
		if r.has_key('aflds'):
			k += len(r['aflds'])
			jinn = search_inn ('aflds', r['aflds'])
			if jinn and jinn == inn:	continue
		print '\t', iid, sres['item']['nm'], inn, jinn
		data = {'sid': sid, 'svc': 'item/update_admin_field', 'params':{"itemId": int(iid), 'id': 0, "n": 'INN', "v": inn.encode('UTF-8'), "callMode":"create"}}
		b, upres = twlp.requesr (data, host = HOST)
		print b, upres, data
												 
		break

	print "###", type(iid)

def	users_inn ():
	""" Поиск Организаций имеющих ИНН	"""
#	help (users_inn)
	print	'Поиск Организаций c ИНН\n\tUSER:', USER, '\tHOST:', HOST
	if not usr2token.has_key(USER):
		print	"Unknown user Wialon '%s'." % USER
		return
	data = {'svc': 'token/login', 'params': {'token':'%s' % usr2token[USER] }}
	b, sres = twlp.requesr(data, host = HOST)
	if not b:
		print b, sres
		return

	sid = sres['eid']
	flags = -1
	data = {'sid': sid, 'svc': 'core/search_items', 'params':{'spec':{'itemsType':'user','propName':'sys_name','propValueMask':'*','sortType':'sys_user_creator'},'force':1,'flags': flags,'from':0,'to':0}}
	b, sres = twlp.requesr(data, host = HOST)
	if not b:
		print b, sres
		return
	print 'ZZZ', sid, b
	for r in sres['items']:
#		if not r.has_key('pop'):
		sinn = search_inn ('flds', r['flds'])
		if sinn:
			print 'ZZZZZZZZZZZZZZZZZZ sinn', sinn

			print r['id'], r['nm'], r['crt']
			for u in r['prp'].keys():
				if u == 'monu':
					set_inn_by_autos (sid, json.loads(r['prp'][u]), sinn)	# .encode('UTF-8'))
				'''
				if u[:4] == 'monu':
					ju = json.loads(r['prp'][u])
					if not ju:	continue
				#	print '\t', u, ju, len(ju)
					print '\t', u, r['prp'][u], len(ju)
				'''
		
	print "="*33, "get_user"


def	autos_inn ():
	""" Поиск ТС имеющих ИНН	"""
	print	'Поиск ТС имеющих ИНН\n\tUSER:', USER, '\tHOST:', HOST, '\tTS_in_work:', TS_in_work
	if not usr2token.has_key(USER):
		print	"Unknown user Wialon '%s'." % USER
		return
	data = {'svc': 'token/login', 'params': {'token':'%s' % usr2token[USER] }}
	b, sres = twlp.requesr(data, host = HOST)
	if not b:
		print b, sres
		return
	sid = sres['eid']
	flags = -1	#0x0409
	itype = 'avl_unit'
	data = {'sid': sid, 'svc': 'core/search_items', 'params':{'spec':{'itemsType':itype,'propName':'*','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':flags,'from':0,'to':0}}
	b, sres = twlp.requesr(data, host = HOST)
	if not b:
		print b, sres
		return
	j = 0
	ts_list = []
	for item in sres['items']:
		chres = {}
		itemId = item['id']
		if not item['pos']:			continue
		if not ((item.has_key('aflds') and item['aflds']) or item['flds']):
			if FL_fix_pos:	fix_pos(itemId, item['uid'].encode('UTF-8'), item['nm'].encode('UTF-8'), item['pos'])
			continue
		j += 1
#		if j > 11:	break
		if not (item['aflds'] or item['flds']):	continue
	#	print item['nm'].encode('UTF-8'), out_pos(item['pos'])
		if item.has_key('flds') and item['flds']:
			fres = check_fflags ('flds', item['flds'], sid, itemId)
			if fres:	chres ["fres"] = fres
		if item.has_key('aflds') and item['aflds']:
			fres = check_fflags ('aflds', item['aflds'], sid, itemId)
			if fres:	chres ["afres"] = fres

		if FL_fix_pos:	fix_pos(itemId, item['uid'].encode('UTF-8'), item['nm'].encode('UTF-8'), item['pos'], fres)

		if chres:
			print item['nm'].encode('UTF-8'), out_pos(item['pos'])
			if TS_in_work:
				ts_list.append((item['nm'].encode('UTF-8'), item['pos']['t']))
			else:
				check_inn (sid, itemId, chres, item)
		continue
	if ts_list:	set_last_date (ts_list)
'''
#	print json.dumps(sres)
#	json.loads('["foo", {"bar":["baz", null, 1.0, 2]}]') ==> obj
#	help (json)
'''
def	outhelp ():
	print "outhelp", sys.argv
	print """
	-t	Test (проверка наличия соединения с сервером Wialon БД РНИС)
	-a	Поиск ТС имеющих ИНН, проверка наличия в БД contracts и добавление (при необходимости)
	-aw	Поиск ТС имеющих ИНН и обновление atts.last_date & atts.bm_wtime
	-u	Поиск Организаций имеющих ИНН, проверка наличия у них ТС имеющих ИНН (при необходимости)
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
			b, sres = twlp.requesr(data, host = HOST)
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
	TS_in_work = False
	FL_fix_pos = False
	dbwialon = None
	USER = 'wialon'
	HOST = 'wialon.rnc52.ru'
	print "Start PID: %i\t" % os.getpid(), sys.argv, time.strftime("%Y-%m-%d %T", time.localtime(sttmr))
	is_exec = None
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'thuawpU:')
		if not optlist:		outhelp()


		for o in optlist:
			if o[0] == '-U':	USER = o[1]
			if o[0] == '-w':	TS_in_work = True
			if o[0] == '-h':	outhelp ()
			if o[0] == '-t':	tests ()
			if o[0] == '-u':	is_exec = 'users'
			if o[0] == '-a':	is_exec = 'autos'
			if o[0] == '-p':
				FL_fix_pos = True		### UPDATE wialon.last_pos
				dbwialon = dbtools.dbtools(DBDS['wialon'])

		dbcon = dbtools.dbtools(DBDS['contracts']) #	contracts
		if is_exec == 'autos':	autos_inn ()
		if is_exec == 'users':	users_inn ()

	except	getopt.GetoptError:
		print "Ошибка в параметрах!\n",	outhelp()
	print "dt %9.4f" % (sttmr - time.time())
