#!/usr/bin/python
# -*- coding: utf-8 -*-

import	os, sys, time
import	urllib
import	json
#from	wtools import *
#from	mobph_wlp import *
#from	auto_wlp import *

import	urllib2, random

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
	'error':	'Неизвестный код ошибки ',
	'nores':	'Отсутствует результат ',
	}
def	requesr (data, host = None):
	res = send_post(data, host = host)
	if res:
		if type(res) == dict and res.has_key('error'):
			if res['error'] != 0:
				if err_dict.has_key(res['error']):
					return False, err_dict[res['error']]
				else:	return False, err_dict['error'] +str(res['error'])
			else:	return True, err_dict[0]
		else:	return True, res
	else:	return False, err_dict['nores']

def	upload_wlp(sid, svc):
	print "upload_wlp", "#"*33, "\n"
	url = r"http://wialon.rnc52.ru/wialon/ajax.html?sid=%s&svc=%s" % (sid, svc)
#	print url
	boundary = '--WebKitFormBoundaryh' + str(int(random.random()*1e10))
	parts = ['']
	parts.append('Request URL:' + url)
	parts.append('Request Method: POST')
	parts.append('Connection: keep-alive')
	parts.append('Cache-Control: no-cache	')
	parts.append('Content-Type: multipart/form-data; boundary=' + boundary)
	parts.append('Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
	parts.append('Accept-Charset: windows-1251,utf-8;q=0.7,*;q=0.3')
	parts.append('Accept-Encoding: gzip,deflate,sdch')
	parts.append('Accept-Language: ru,en-US;q=0.8,en;q=0.6')
	parts.append('')
	parts.append('--' + boundary)
	parts.append('Content-Disposition: form-data; name="params"')
	parts.append('\r\n{"eventHash":"jUploadForm1372772377019"}')
	parts.append('--' + boundary)
	parts.append('Content-Disposition: form-data; name="eventHash"')
	parts.append('\r\njUploadForm1372772377019')
	parts.append('--' + boundary)
	file_path = r'wlp/test_ph1.wlp'
	parts.append('Content-Disposition: form-data; name="import_file"; filename="%s"' % file_path)
#	parts.append('Content-Type: application/octet-stream\r\n')
	parts.append('Content-Type: application/json\r\n')
	parts.append(open(file_path, 'r').read())
#	parts.append('{"afields":[],"fields":[],"general":{"hw":"WiaTag","n":"QQQ-WWW","ph":"","ph2":"","psw":"","uid":"864359028200000","uid2":""},"hwConfig":{"fullData":1,"hw":"WiaTag","params":{}},"icon":{"lib":"3","url":"Z_11.png"},"imgRot":"0","mu":0,"type":"avl_unit","version":"b4"')
	parts.append('--' + boundary + '--\r\n')
	body = '\r\n'.join(parts)
	print  body
	headers = {'User-Agent' : 'Mozilla 5.10'}
	'''
	headers = {'content-type': 'multipart/form-data; boundary=' + boundary}
	files = {'file': ('userfile', open('wlp/test_ph.wlp.gz', 'rb')), 'account_id': 12345}
#	req = urllib2.Request(url, headers=headers, data=body)
#	help (requests.post)
	res = requests.post("http://212.193.103.20:7778", files=files, data=body, headers=headers)
	return
	req = urllib2.Request("http://212.193.103.20:7778", headers=headers, data=body)
	req = urllib2.Request(r"http://wialon.rnc52.ru/wialon/ajax.html", headers=headers, data=body)
	req = urllib2.Request(url, data=body)
	'''
	req = urllib2.Request(url, headers=headers, data=body)
	res = urllib2.urlopen(req)
#	print "urllib2.Request:\n", res.info()
	return json.loads(res.read())

def	send_post (pdict = None, pfile = None, host = None):
	if not pdict:	return
	boundary = '--WebKitFormBoundaryh' + str(int(random.random()*1e10))
#	url = r"http://wialon.rnc52.ru/wialon/ajax.html"
	if not host:
		url = r"http://test-wialon.rnc52.ru/wialon/ajax.html"
	else:	url = r"http://%s/wialon/ajax.html" % host
	parts = ['']
	for k in pdict:
		parts.append('--' + boundary)
		parts.append('Content-Disposition: form-data; name="%s"\r\n' % k)
		if type(pdict[k]) == dict:
			parts.append('%s' % json.dumps(pdict[k]))
		else:	parts.append('%s' % pdict[k])
	if pfile:
		parts.append('Content-Disposition: form-data; name="import_file"; filename="%s"' % pfile)
		parts.append('Content-Type: application/json\r\n')
		parts.append(open(pfile, 'r').read())
	parts.append('--' + boundary + '--\r\n')
	body = '\r\n'.join(parts)
	if DEBUG:
		print  body
	#	return
	headers = {
		'content-type': 'multipart/form-data; boundary=' + boundary,
		'User-Agent' : 'Mozilla 5.10'}
	try:
		req = urllib2.Request(url, headers=headers, data=body)
		res = urllib2.urlopen(req)
	except urllib2.URLError:
		return (-1, 'EXCEPT urllib2.URLError IN send_post')
	return json.loads(res.read())

DEBUG = False
URL =	r"http://wialon.rnc52.ru/wialon/ajax.html"
usr2token = {	# //find_routes-wialon.rnc52.ru/login.html?access_type=-1	# Полный доступ
	'wialon':	"1d5a4a6ab2bde440204e6bd1d53b3af88D19DFFEDD8F1FBCEAFCDAEEB21419C1B4C7A875",
	'V.Smirnov':	"c5a76d06f77af04aa4c9fa0699d465c272899BB584F98F199F951746467AA85947F7A9F5",
	}

def	ppp (obj, label = None):
	if label:	print label.upper(),
	if type(obj) == list:
		print "List:"
		for l in obj:		print l
	#	print "</pre>"
	elif type(obj) == dict:
		if obj.has_key('error'):
			print 'error', err_dict[obj['error']]
			return
		print "Dict:"
		for k in obj.keys():	print k, "=>\t", obj[k]	# ppp(obj[k])
	#	print "</pre>"
	elif obj:
		print obj
	else:	pass
	#	print "Type", type(obj)

st = [
	{'i': 0, 'p': '', 'id': 20421},
	{'i': 1, 'p': 'q{~vI_c{kG@@^cBRaBCyAIu@QeAIY}@}D?I_@sBO{@_@}AKo@yAeHCK}@wEcBqIUyA\\s@N_@D_@d@uABB', 'id': 20422}, 
	{'i': 2, 'p': 'we_wIud}kGCCH_@bAgDrAaFJ_@Nu@^iAr@wBrAoDb@y@tCsE|@gBlBiCnEcEhAgAlFuD^Y`Ak@AG', 'id': 20423}, 
	{'i': 3, 'p': 'g|}vI{`_lG@F@AvAiAz@u@t@y@`CgDZo@fAiBd@e@lA}@jByAxBwBFG??', 'id': 20433}, 
	{'i': 4, 'p': 'qc}vIoz_lG??xA}ATY~@_A\\e@dDqDzFaH~@_Bx@cB|@_C~D_MZcA?A', 'id': 20432}, 
	{'i': 5, 'p': 'mc|vIkjalG?@Le@l@cB~BsHN_@n@sAx@mAh@o@RStAeB|AcBBE?D', 'id': 20431}, 
	{'i': 6, 'p': 'ar{vIwfblG?EPODI|CiDxD{El@u@^y@^m@Xo@l@oBTy@N}@f@uBAA', 'id': 20430}, 
	{'i': 7, 'p': 'o~zvIkeclG@@Ly@jFqU~@_DbCeHDW|@cC@D', 'id': 20424}, 
	{'i': 8, 'p': 'inzvIqpdlGAE`@iA|@sBxAaFbBgG^_AXc@^Yb@Kd@IbCEnAMx@a@n@g@UmEC|AKdAOl@_@n@STAE', 'id': 20429}, 
	{'i': 9, 'p': 'wyyvImkelG@Dx@a@n@g@k@}Ii@eHE_@BA', 'id': 20428}, 
	{'i': 10, 'p': 'cyyvIwbflGC@GoA{AuSIy@Eu@A?', 'id': 20427}, 
	{'i': 11, 'p': '}|yvIk}flG@?i@oGE_AaAwLa@uGIoA?iAPu@`AuDnA}FT_ARyA?e@EyBYkI?eAA?', 'id': 20426}, 
	{'i': 12, 'p': 'm|yvIyhilG@?@eH?mEAwCD{AXqBD_B_@{@_@MYDe@k@]y@cJsWSg@O{@@A', 'id': 20873}, 
	{'i': 13, 'p': 'ilzvIwgklGA@]}Ae@cB_@eAOY_AwCS_@U_@e@Kc@@yC\\wAZoAb@c@Xi@h@Y@[AcCsDwAgBa@c@?I', 'id': 20874}, 
	{'i': 14, 'p': 'wk{vIa}klG?HyCuC{AsAUSU?YBUTMN_G~Lc@x@c@h@[Zi@b@YXUXMOKSi@Y_@KgGkFc@_@eD_DyIqGeAeAe@m@]k@DK', 'id': 20876}
	]
	
if __name__ == "__main__":
	# Login
#	sres = send_post ({'svc': 'token/login', 'params': "{'token':'%s'}" % usr2token['V.Smirnov']})
#	sres = send_post ({'svc': 'token/login', 'params': "{'token':'%s'}" % usr2token['wialon']}, host='wialon.rnc52.ru')
	data = {'svc': 'token/login', 'params': {'token':'%s' % usr2token['wialon'] }}
	b, sres = requesr (data, host = 'wialon.rnc52.ru')
	print sres.keys()
#	res = upload_wlp(sres['eid'], 'exchange/import_json')
#	ppp(res, "upload_wlp exchange/import_json")
	try:
	#	DEBUG = True
		usr = sres['au']
		sid = sres['eid']
		usid = sres['user']['id']
		print "User: %s SID: %s UsId: %d" % (usr, sid, usid)
		print "="*44
		data ={'sid': sid}
		import json_convertation as jsc
		print jsc.pres(sres).keys()
		# Просмотр сообщение (треков машин) 1126 1054
		crtm = int (time.time())
		data['svc'] = "messages/load_interval"
		data['params'] = { "itemId": 1054, "timeFrom": (crtm -3600*24), "timeTo": crtm, "flags": 0, "flagsMask": 0xff00, "loadCount": 10000 }
		print data
		b, sres = requesr (data, host = 'wialon.rnc52.ru')
		if b and sres.has_key('messages'):
			for m in sres['messages']:
				sm = jsc.pres(m)
			#	print sm.keys()
				print time.strftime("%Y-%m-%d %T\t", time.localtime(sm['t'])), sm['pos']
			print	"count:", sres['count']
		else:
			print b, jsc.pres(sres)
	#	print jsc.pres(sres)
		print "ZZZZZZZZZZZZZZZZZ", data
		'''
		data['svc'] = 'core/get_hw_types'
		data['params'] = { "filterType":"type", "filterValue":["mobile"], "includeType": True }
		res = send_post(data)
		ppp(res, data['svc'])
		print "="*44
		''
		data['svc'] = 'exchange/import_json'
		res = send_post(data, r'wlp/test_ph1.wlp')
		''
		data['svc'] = 'core/create_unit'
		data['params'] = {"creatorId": usid,"name":"test_LLL","hwTypeId":"9","dataFlags":"257"}
		res = send_post(data)
		ppp(res, data['svc'])
		'''
	except:
		ppp(sres, 'send_post')
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT twlp:", exc_type, exc_value
	"""
#	print auto_wlp
	auto_wlp['general']['n'] = "ГОС-123456"
	auto_wlp['afields'] = [{ 'id': 1, 'n': "inn", 'v': "520000000999" }]
#	print json.dumps(auto_wlp)
	sess = login(usr2token['V.Smirnov'])
	sid = sess['eid']
	res = upload_wlp(sid, 'exchange/import_json')
	print "upload_wlp res:", res
	print "="*33
	get_post (sid, 'core/get_hw_types')
	"""
	'''
	for root, dirs, files in os.walk(r'./wlp'):
		print root, dirs, files
		for fname in files:
			if fname[-4:] != '.wlp':	continue
			f = open(os.path.join(root, fname))
			st = f.readline()
			js = json.loads(st)
			ppp(js, fname)
	'''
