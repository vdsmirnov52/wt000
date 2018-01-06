#!/usr/bin/python
# -*- coding: utf-8 -*-

import	os, sys, time
import	urllib
import	json

LIBRARY_DIR = r"/home/smirnov/Wialon/lib/"
sys.path.insert(0, LIBRARY_DIR)

def	ppp(obj, oname = 'objName', level = 0):
	if type(obj) == dict and obj.has_key('error'):
		print obj,
		try:
			print err_dict[obj['error']]
		except:	print "Код неизвестен"
		return
	if oname != '':
		print "\t"*level, "'%s':" % oname ,
	if type(obj) == dict:
		if not obj:
			print "{}"
			return
		print "\t"*level, "{"
		for key, val in obj.iteritems():
			ppp (val, key, level+1)
		print "\t"*level, "}"
	elif type(obj) == list:
		if not obj:
			print "()"
			return
		print "("
		for o in obj:
			ppp (o, '', level+1)
		print "\t"*level, ")"
	elif type(obj) == tuple:
		if not obj:
			print "[]"
			return
		print "["
		for o in obj:
			ppp (o, '', level+1)
		print "]"
		'''
	elif type(obj) == type('') or type(obj) == type(u''):
		if obj[0] in "{([":
			o = json.loads(obj)
			ppp (o, '', level+1)
		else:	print "\t"*level, obj
		'''
	elif type(obj) == type(u''):
		print 'u"%s"' % obj.encode('UTF-8')
	elif type(obj) == type(''):
		print '"%s"' % obj
	else:	print obj

err_dict = {
	0:	'Удачное выполнение операции',
	1:	'Недействительная сессия',
	2:	'Неверное имя сервиса',
	3:	'Неверный результат',
	4:	'Неверный ввод',
	5:	'Ошибка выполнения запроса',
	6:	'Неизвестная ошибка',
	7:	'Доступ запрещен',
	8:	'Неверный пароль или имя пользователя',
	9:	'Сервер авторизации недоступен, пожалуйста попробуйте повторить запрос позже',
	1001:	'Нет сообщений для выбранного интервала',
	1002:	'Элемент с таким уникальным свойством уже существует',
	1003:	'Только один запрос разрешается в данный момент времени',
	}
def	perror (ecod):
	try:	print "\tERR:", err_dict[ecod]
	except:	print "cod =", ecod

def	sexcept (label = None):
	if not label:	label = 'except:'
	exc_type, exc_value = sys.exc_info()[:2]
	return	"%s: %s %s" % (label, escape(str(exc_type)), exc_value)

def	escape(s):
	s = s.replace("&", "&amp;") # Must be done first!
	s = s.replace("<", "&lt;")
	s = s.replace(">", "&gt;")
	return s

sess =		None	# sid - Session Identificator
account =	None

def	login (token = None):
	global	sess
	url = r"http://wialon.rnc52.ru/wialon/ajax.html?svc=token/login&params={'token':'%s'}" % usr2token['wialon']
	if not token:
		sess = json.load(urllib.urlopen(url))
	else:	sess = json.load(urllib.urlopen(r"http://wialon.rnc52.ru/wialon/ajax.html?svc=token/login&params={'token':'%s'}" % token))	
	return	sess

def	logout(sid):
	res = json.load(urllib.urlopen(r"http://wialon.rnc52.ru/wialon/ajax.html?svc=core/logout&params={}&sid=%s" % sid))
	print "\tlogout", res

def	find_key (dct, key):
	if type(dct) == dict:
		if dct.has_key(key):
		#	print "ZZZ", dct[key]
			return	dct[key]
		for k in dct.keys():
			print k
			rrr = find_key (dct[k], key)
			if rrr:		return	rrr
	elif type (dct) == []:
		for k in dct:
			rrr = find_key (dct[k], key)
			if rrr:		return	rrr
	else:	return	#	pass	#	print type (dct)

def test_login ():
	print "test_login", login()
	for uname in usr2token.keys():
	#	time.sleep(1)
		print "\t", uname, "\t",
		res = login(usr2token[uname])
		if  res.has_key('eid'):
			sid = res['eid']
			print res['eid']
		#	print res['user'] 
			print find_key (res['user'], 'monugr')
	#		time.sleep(1)
			logout(sid)
		elif res.has_key('error'):
			perror (res['error'])
		else:	print "\nRES:", res

############################################
def	init_conf ():
	print """ Инициализация доступа к Wialon	"""
	global	RES_WHST, RES_WUSR, usr2token
	import	dbsqlite

	dbconf = dbsqlite.dbsqlite(os.path.join(r'/dblite/', 'config.db'))	#LIBRARY_DIR, 'config.db'))
	RES_WHST = dbconf.get_table("whosts", "id_wh > 0 ORDER BY id_wh")
	RES_WUSR = dbconf.get_table("whusers", "id_whu > 0 ORDER BY id_whu")

	d = RES_WUSR[0]
	for r in RES_WUSR[1]:	usr2token[r[d.index('login')]] = r[d.index('token')]
#	dbconf.close()
	return	usr2token

usr2token = {}
if __name__ == "__main__":
	init_conf ()
#	print RES_WUSR
	d = RES_WUSR[0]
	for r in RES_WUSR[1]:	usr2token[r[d.index('login')]] = r[d.index('token')]
	host = RES_WHST[1][0][1]
	print '#'*22, usr2token
	print r"http://%s/wialon/ajax.html?svc=token/login&params={'token':'%s'}" % (host, usr2token['wialon'])

	test_login()
