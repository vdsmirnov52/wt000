#!/usr/bin/python -u
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

def	get_allflds (flags):
	pflds = {}
	for k in flags.keys():
		pflds[flags[k]['n']] = flags[k]['v']
	return pflds

marks_inn = [u'INN', u'inn', u'ИНН', u'инн', u'oinn']	### варианты метки поля для ИНН в Wialon

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
		if flags[k]['n'] in marks_inn:		# [u'INN', u'inn', u'ИНН', u'oinn']:
			try:
				if not len(flags[k]['v']) in [10, 12]:
					delete.append(flags[k]['id'])
				elif inn and inn[0]['INN'] == flags[k]['v']:
					delete.append(flags[k]['id'])
				else:
					inn = (flags[k]['id'], flags[k])
					if flags[k]['n'] != u'INN':
						flags[k]['n'] = u'INN'
						update[k] = flags[k]
			except:
				print "\t\x1b[1;33mexcept:\t", inn, flags[k], "\x1b[0m"
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
	return	inn	########################

def	check_inn (sid, itemId, dfres, item, iinn, gosnum):
	""" проверка наличия ИНН в БД contracts	"""
	flds = dfres.keys()
	if len(flds) > 1:
		print "\tDoule INN", dfres
		return

	add_atts = 0
	fld = flds[0]
	k, dfinn = dfres[fld]
	query = "SELECT t.*, a.autos FROM transports t LEFT JOIN atts a ON a.autos = t.id_ts WHERE gosnum = '%s';" % gosnum
	dts = dbContr.get_dict(query)
	if dts:
		if dts['autos']:
			add_atts = dts['autos']
	if add_atts:	return

	query = "SELECT id_org, inn, bm_ssys, label, bname, region FROM organizations WHERE inn = %s" % dfinn['v']	# id_org, bm_ssys, region =>	transports
#	print "\t", k, fld, dfinn, query
	dorg = dbContr.get_dict(query)
	if not dorg:
		print "Отсутствует организация ИНН: %s" % dfinn['v']
		return

	cols = ['gosnum', 'id_org', 'bm_ssys', 'region', 'bm_status', 'device_id']
#	vals = ["'%s'" % item['nm'].encode('UTF-8'), "%d" % dorg['id_org'], "%d" % dorg['bm_ssys'], "%d" % dorg['region'], '12', "-%d" % itemId]
	vals = ["'%s'" % gosnum, "%d" % dorg['id_org'], "%d" % dorg['bm_ssys'], "%d" % dorg['region'], '12', "-%d" % itemId]
#	print "\t", dorg
	pflds = get_allflds (item['pflds'])
	for k in pflds.keys():
	#	print "\t", k, pflds[k], type (pflds[k])
		if not pflds[k]:	continue
		if '\\xd0' in pflds[k]:	continue
	
		if k == 'vehicle_type':
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
	if item.has_key('pos') and item['pos']:
		sdate = time.strftime("'%Y-%m-%d %T'", time.localtime(item['pos']['t']))
	else:	sdate = 'NULL'
	if dts and add_atts == 0:	# reate ATT only
	#	print "\tZZZ Create ATT only"
		querys.append("UPDATE transports SET bm_ssys = %d, region = %d, bm_status = 12, device_id = -%d WHERE id_ts = %d" % (dorg['bm_ssys'], dorg['region'], itemId, dts['id_ts']))
		querys.append("INSERT INTO atts (mark, modele, uin, sim_1, sim_2, last_date, device_id, autos) VALUES ('WialonHost', '%s', '%s', '%s', '%s', %s, -%d, %d)" % (
			HOST, item['uid'].encode('UTF-8'), item['ph'].encode('UTF-8'), item['ph2'].encode('UTF-8'), sdate, itemId, dts['id_ts']))
	else:
		querys.append("INSERT INTO transports (%s) VALUES (%s)" % (", ".join(cols), ", ".join(vals)))
	#	print "\nZZZZ\t", item['uid'], item['ph'], item['ph2'], item['hw'], item['psw']
		querys.append("INSERT INTO atts (mark, modele, uin, sim_1, sim_2, last_date, device_id, autos) VALUES ('WialonHost', '%s', '%s', '%s', '%s', %s, -%d, (SELECT max(id_ts) FROM transports))" % (
			HOST, item['uid'].encode('UTF-8'), item['ph'].encode('UTF-8'), item['ph2'].encode('UTF-8'), sdate, itemId))
#	print "####\t", querys
	print "####\t", ";\n".join(querys), dbContr.qexecute (";\n".join(querys))		########################

def	set_last_date (ts_list):
	""" Обновить last_date в БД contracts	"""
	if not ts_list:
		print 'set_last_date (ts_list):', ts_list
		return
	dts_list = dict(ts_list)
	query = "SELECT id_ts, gosnum, a.id_att, a.last_date, a.bm_wtime, a.mark FROM transports t LEFT JOIN atts a ON id_ts = autos WHERE gosnum IN ('%s')" % "', '".join(dts_list.keys())
#	print query
	rows = dbContr.get_rows (query)
	if not rows:	return
	sttm = time.localtime(time.time())
	tm_year, tm_mon, tm_mday = sttm[:3]
	stime = time.strftime("%Y-%m-%d %T", time.localtime(time.time()))
	jstime = time.strftime("%Y-%m-%d %T", time.localtime(time.time()- 7200))
	print "\nОбновить last_date", tm_year, tm_mon, tm_mday, stime, jstime
	for r in rows:
		id_ts, gosnum, id_att, last_date, bm_wtime, mark = r
		if mark != 'WialonHost':		continue
		if not dts_list.has_key(gosnum):	continue
		jstime = time.strftime("%Y-%m-%d %T", time.localtime(dts_list[gosnum]))
	#	print id_ts, gosnum, id_att, last_date, bm_wtime, mark, jstime
		if not last_date or jstime > str(last_date):	# > jstime:
			query = "UPDATE atts SET last_date = '%s', bm_wtime = bm_wtime | 512 WHERE id_att = %d;" % (jstime, id_att)
			print gosnum, "\t", query, dbContr.qexecute(query)
	#	else:	print "<<<"
	#	set_worktime (r)

def	set_worktime (row):
	print 'set_worktime:', row

def	fix_pos (ida, uid, nm, pos, inn = None):
	""" Запмсать в БД wialon.last_pos pos & inn	"""
	if not dbWialon:	return

	if inn and inn[1]['v']:
		sinn = inn[1]['v'].encode('UTF-8')
	else:	sinn = 'NULL'
	suid = str(uid)
#	print "uid %s " %uid, sinn, inn
	row = dbWialon.get_row("SELECT id_lp FROM last_pos WHERE ida = %d;" % ida)
	if row:
		query = "UPDATE last_pos SET idd='%s', nm='%s', x=%f, y=%f, t=%d, inn=%s WHERE ida = %d;" % (suid, nm, pos['x'], pos['y'], pos['t'], sinn, ida)
		check_work_ts(row[0], pos['t'])
	else:
		query = "INSERT INTO last_pos (ida, idd, nm, x, y, t, inn) VALUES (%d, '%s', '%s', %f, %f, %d, %s);" % (ida, suid, nm, pos['x'], pos['y'], pos['t'], sinn)
	if not dbWialon.qexecute(query):	print query

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
	""" Прописать (проверить) ИНН в записи автомобиля	"""
	flags = 1 +8 +128 +8388608
	for iid in itemIds:
		data = {'sid': sid, 'svc': 'core/search_item', 'params':{'id': int(iid), 'flags': flags}}
		b, sres = twlp.requesr(data, host = HOST)
		if not b:	continue
		r = sres['item']
		'''
		for k in r.keys():
			if r[k]:	print '\t',k, r[k],
		print
		'''
	#	print b, sres.keys(), sres['flags']
		jinn = search_inn ('flds', r['flds'])
	#	print 'jinn', jinn, type(jinn)
		if jinn and jinn == inn:		continue

		time.sleep(0.2)
		gosnum = sres['item']['nm'].encode('UTF-8')	
		pflds = sres['item'].get('pflds')
		if pflds:
		#	print pflds
			reg_plate = get_pflds (sres['item']['pflds'], 'registration_plate')
			if reg_plate == None and gosnum != reg_plate:
				print sres['item']['id'], '\t \x1b[1;33m NM: %s != %s reg_plate \x1b[0m' % (gosnum, reg_plate)
			else:	print sres['item']['id'], '\t \x1b[1;33m NM: %s reg_plate %s \x1b[0m' % (gosnum, reg_plate)
		else:	print sres['item']['id'], '\t NM: %s' % gosnum
		k = 1
		if r.has_key('aflds'):
			k += len(r['aflds'])
			jinn = search_inn ('aflds', r['aflds'])
			if jinn and jinn == inn:
				continue
			else:	
				print '\x1b[1;33mWAR\x1b[0m\t', iid, gosnum, inn, jinn, '\titemIds:', itemIds 
				continue
		print 'UDT\t', iid, gosnum, inn, jinn
		data = {'sid': sid, 'svc': 'item/update_admin_field', 'params':{"itemId": int(iid), 'id': 0, "n": 'INN', "v": inn.encode('UTF-8'), "callMode":"create"}}
		b, upres = twlp.requesr (data, host = HOST)
		if not b:
			print '\t', b, upres, data
	#	break
#	print "###", type(iid)

def	users_inn ():
	""" Поиск Организаций имеющих ИНН	"""
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

	for r in sres['items']:
		'''
		if 'ДТ-НН' in r['nm'].encode('UTF-8'):	# 720 ДТ-НН СпецДорСтрой 718      5258067224
			print r['nm'], r.keys()
			if r['flds']:	print r['flds']
			if r['aflds']:	print r['aflds']
		'''
		sinn = search_inn ('flds', r['flds'])
		if sinn:
			print r['id'], r['nm'], r['crt'], '\t', sinn
			for u in r['prp'].keys():
				if u == 'monu':
					set_inn_by_autos (sid, json.loads(r['prp'][u]), sinn)	# .encode('UTF-8'))
				'''
				if u[:4] == 'monu':
					ju = json.loads(r['prp'][u])
					if not ju:	continue
					print '\t', u, r['prp'][u], len(ju)
				'''
	print "="*33, "users_inn"	########################

def	autos_inn ():
	""" Поиск ТС имеющих ИНН. Если TS_in_work == True обновление atts.last_date & atts.bm_wtime	"""
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
	iinn = 0
	ts_list = []
	for item in sres['items']:
		chres = {}
		itemId = item['id']
		if TS_in_work and not item['pos']:	continue

		gosnum = item['nm'].encode('UTF-8').strip()
		reg_plate = get_pflds (item['pflds'], 'registration_plate')
		if reg_plate and reg_plate != '':
			gnum = reg_plate
		else:	gnum = gosnum
	#	print ">>>", gosnum, reg_plate
		if not ((item.has_key('aflds') and item['aflds']) or item['flds']):
			if FL_fix_pos and item.has_key('pos') and item['pos']:
			#	fix_pos(itemId, item['uid'].encode('UTF-8'), item['nm'].encode('UTF-8'), item['pos'])
				fix_pos(itemId, item['uid'].encode('UTF-8'), gnum, item['pos'])
			continue
		j += 1
#		if j > 11:	break
		if not (item['aflds'] or item['flds']):	continue
		if item.has_key('flds') and item['flds']:
			fres = check_fflags ('flds', item['flds'], sid, itemId)
			if fres:	chres ["fres"] = fres
		if item.has_key('aflds') and item['aflds']:
			fres = check_fflags ('aflds', item['aflds'], sid, itemId)
			if fres:	chres ["afres"] = fres

		if FL_fix_pos and item.has_key('pos') and item['pos']:
		#	fix_pos(itemId, item['uid'].encode('UTF-8'), item['nm'].encode('UTF-8'), item['pos'], fres)
			fix_pos(itemId, item['uid'].encode('UTF-8'), gnum, item['pos'], fres)

		if chres:
			vals = chres.get('fres')
			if not vals:	vals = chres.get('afres')
		#	print vals, type(vals)
			for iv in vals:
				if type(iv) != dict:	continue
				if iv.has_key('n') and iv['v'] and iv['v'].isdigit():
					iinn = int(iv['v'])
					break
		
			if iinn in [5258067224, 5249006828]:	# 720 ДТ-НН СпецДорСтрой 718 5258067224	# id:918  МУП "Экспресс" 5249006828
				gosnum = reg_plate
			elif gosnum != reg_plate:
				print item['id'], '\t \x1b[1;33m NM: %s != %s reg_plate \x1b[0m' % (gosnum, reg_plate), out_pos(item.get('pos')), iinn
				if reg_plate:
					print "\t", "UPDATE transports SET garnum = '%s', gosnum = '%s' WHERE gosnum = '%s';" % (gosnum, reg_plate, gosnum)
			else:
				print item['id'], '\t', gosnum, out_pos(item.get('pos')), iinn	#, chres
			'''
			check_inn (sid, itemId, chres, item, iinn, gosnum)
			'''
			if TS_in_work:		# бновление atts.last_date & atts.bm_wtime
				if iinn == 5258067224:	# 720 ДТ-НН СпецДорСтрой 718      5258067224
					jss = gosnum.split(' ')
					gosnum = jss[-1]
			#	ts_list.append((item['nm'].encode('UTF-8'), item['pos']['t']))
				ts_list.append((gosnum, item['pos']['t']))
			else:
				check_inn (sid, itemId, chres, item, iinn, gosnum)	# проверка наличия ИНН в БД contracts
		continue
	if ts_list:	set_last_date (ts_list)
	print "="*33, "autos_inn"	########################

def	get_pflds (pflds, key):
	for k in pflds.keys():
		if pflds[k]['n'] == key:	return pflds[k]['v'].encode('UTF-8')

def	update_work_ts (sttmr):
	tm_mon, tm_mday = time.localtime(sttmr)[1:3]
	dd = 24*3600
	itm = (int(sttmr/dd)-tm_mday) *dd
	print 'update_work_ts', tm_mon, tm_mday, time.strftime("%Y-%m-%d %T", time.localtime(itm)) 
	query = "SELECT id_lp, t, inn FROM last_pos WHERE t > %d;" % itm
	rows = dbWialon.get_rows (query)
	if not rows:	return
	for r in rows:
		id_lp, t, inn = r
		if not inn:	continue
		check_work_ts(id_lp, t, tm_mon)
	print "="*33, "update_work_ts"	########################

def	check_work_ts(id_lp, t, tm_mon = None):
#	print id_lp, t, tm_mon
	stm = time.strftime("%Y-%m-%d %T", time.localtime(t))
	wquery = "SELECT * FROM work_ts WHERE id_lp = %d;" % id_lp
	dts = dbWialon.get_dict (wquery)
	if dts:
		uquery = None
	#	print dts, dts['where_set'], stm
		if stm > str(dts['where_set']):
			if dts['jw_time'] > 3 and dts['is_work'] == 0:
				uquery = "UPDATE work_ts SET is_work = 1, jw_time = jw_time +1, where_set = '%s' WHERE id_lp = %d;" % (stm, id_lp)
			else:	uquery = "UPDATE work_ts SET jw_time = jw_time +1, where_set = '%s' WHERE id_lp = %d;" % (stm, id_lp)
			print uquery, dbWialon.qexecute (uquery)
	else:
		if tm_mon == None:	tm_mon = time.localtime(time.time())[1]
		uquery = "INSERT INTO work_ts (id_lp, month, is_work, jw_time, where_set) VALUES (%d, %d, %d, %d, '%s');" % (id_lp, tm_mon, 0, 1, stm)
		print uquery, dbWialon.qexecute (uquery)

def	init_work_ts (sttmr):
	""" Инициализация work_ts - начоло сбора данных о работе машин на Wialon	"""
	tm_mon = time.localtime(sttmr)[1]
	print 'init_work_ts', time.localtime(sttmr)
	query = "SELECT gosnum, bm_wtime, bm_status, last_date FROM wtransports WHERE bm_status & 3072 = 0 AND amark = 'WialonHost' ORDER BY bm_wtime"
	rows = dbContr.get_rows (query)
	if not rows:	return
	unknown_nm = []
	print "Clear work_ts", dbWialon.qexecute ("DELETE FROM work_ts;")
	for r in rows:
		gosnum, bm_wtime = r[:2]
		if r[-1]:
			where_set = "'%s'" % str(r[-1])
		else:	where_set = 'NULL'
	#	print r[0], r[1], r[2:], gosnum, bm_wtime
		wquery = "SELECT * FROM last_pos WHERE nm = '%s';" % gosnum
		dts = dbWialon.get_dict (wquery)
		if dts:
			print gosnum, bm_wtime, '\t=',
	#		print dts['id_lp'], dts['nm']
			if (bm_wtime & 0x1ff) > 0:
				jw_time = 3
				is_work = 1
			elif bm_wtime == 0x200:
				is_work = 0
				jw_time = 1
			else:	jw_time = is_work = 0
			iquery = "INSERT INTO work_ts (id_lp, month, is_work, jw_time, where_set) VALUES (%d, %d, %d, %d, %s);" % (dts['id_lp'], tm_mon, is_work, jw_time, where_set)
			print iquery, dbWialon.qexecute(iquery)
		else:	unknown_nm.append(gosnum)
	if unknown_nm:
		print "Unknown gosnum: '%s'" % "', '".join(unknown_nm)
	print "="*33, "init_work_ts"	########################
	

def	outhelp ():
	print "outhelp", sys.argv
	print """
	-t	Test (проверка наличия соединения с сервером Wialon БД РНИС)
	-a	Поиск ТС имеющих ИНН, проверка наличия в БД contracts и добавление (при необходимости)
	-aw	Поиск ТС имеющих ИНН и обновление atts.last_date & atts.bm_wtime
	-u	Поиск Организаций имеющих ИНН, проверка наличия ТС (добавление ИНН при необходимости)
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
	dbWialon = None
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
				dbWialon = dbtools.dbtools(DBDS['wialon'])
				update_work_ts (sttmr)

		dbContr = dbtools.dbtools(DBDS['contracts']) #	contracts
		if TS_in_work:
			dbWorkt = dbtools.dbtools(DBDS['worktime']) #	worktime
		#	init_work_ts (sttmr)
		else:	dbWorkt = None
		if is_exec == 'autos':	autos_inn ()
		if is_exec == 'users':	users_inn ()

	except	getopt.GetoptError:
		print "Ошибка в параметрах!\n",	outhelp()
	print "dt %9.4f" % (sttmr - time.time())
