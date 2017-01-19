#!/usr/bin/python
# -*- coding: utf-8 -*-

import	os, sys, time
import	urllib
import	json

def	ppp(obj, oname = 'objName', level = 0):
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
		print "u'%s'" % obj.encode('UTF-8')
	elif type(obj) == type(''):
		print "'%s'" % obj
	else:
		print obj
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
	try:
		print "\tERR:", err_dict[ecod]
	except:	print "cod =", ecod
		
sess =	None
account =	None
usr2token = {
	'wialon':	"1d5a4a6ab2bde440204e6bd1d53b3af891F531BAA376794D25274B3EAD44CAF9BACCD247",
	'V.Smirnov':	"c5a76d06f77af04aa4c9fa0699d465c2A1C15592645215DBA63B6D2A21AE9A379DB51D75",
	}

url = r"http://wialon.rnc52.ru/wialon/ajax.html?svc=token/login&params={'token':'1d5a4a6ab2bde440204e6bd1d53b3af891F531BAA376794D25274B3EAD44CAF9BACCD247'}"
def	login (token = None):
	global	sess
	if not token:
		sess = json.load(urllib.urlopen(url))
	else:	sess = json.load(urllib.urlopen(r"http://wialon.rnc52.ru/wialon/ajax.html?svc=token/login&params={'token':'%s'}" % token))	
	return	sess

def	logout(sid):
	res = json.load(urllib.urlopen(r"http://wialon.rnc52.ru/wialon/ajax.html?svc=core/logout&params={}&sid=%s" % sid))
	print "\tlogout", res

def test_login ():
	print "test_login"
	for uname in usr2token.keys():
	#	time.sleep(1)
		print "\t", uname, "\t",
		res = login(usr2token[uname])
		if  res.has_key('eid'):
			sid = res['eid']
			print res['eid']
	#		time.sleep(1)
			logout(sid)
		elif res.has_key('error'):
			perror (res['error'])
		else:
			print res

if __name__ == "__main__":
	test_login()
