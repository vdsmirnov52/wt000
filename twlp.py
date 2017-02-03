#!/usr/bin/python
# -*- coding: utf-8 -*-

import	os, sys, time
import	urllib
import	json
from	wtools import *
from	mobph_wlp import *
from	auto_wlp import *

import	urllib2, random, mimetypes

def	upload_creative(self, account_id, file_path):
	""""""
	boundary = '-----------------------------' + str(int(random.random()*1e10))
	parts = []

	# Set account ID part.
	parts.append('--' + boundary)
	parts.append('Content-Disposition: form-data; name="account_id"')
	parts.append('')
	parts.append(str(account_id))

	# Set creative contents part.
	parts.append('--' + boundary)
	parts.append('Content-Disposition: form-data; name="userfile"; filename="%s"' % file_path)
	parts.append('Content-Type: %s' % mimetypes.guess_type(file_path)[0] or 'application/octet-stream')
	parts.append('')
	# TODO: catch errors with opening file.
	parts.append(open(file_path, 'r').read())

	parts.append('--' + boundary + '--')
	parts.append('')

	body = '\r\n'.join(parts)

	headers = {'content-type': 'multipart/form-data; boundary=' + boundary}
	url = self._resolve_url('/a/creative/uploadcreative')
	req = urllib2.Request(url, headers=headers, data=body)
	res = urllib2.urlopen(req)

	return json.loads(res.read())

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
#	parts.append('Content-Type: %s\r\n' % mimetypes.guess_type(file_path)[0] or 'application/octet-stream')
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

def	send_post (pdict = None, pfile = None):
	if not pdict:	return
	boundary = '--WebKitFormBoundaryh' + str(int(random.random()*1e10))
#	url = r"http://wialon.rnc52.ru/wialon/ajax.html"
	url = r"http://test-wialon.rnc52.ru/wialon/ajax.html"
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
	req = urllib2.Request(url, headers=headers, data=body)
	res = urllib2.urlopen(req)
	return json.loads(res.read())

DEBUG = False
URL =	r"http://test-wialon.rnc52.ru/wialon/ajax.html"

if __name__ == "__main__":
	# Login
#	sres = send_post ({'svc': 'token/login', 'params': "{'token':'%s'}" % usr2token['V.Smirnov']})
	sres = send_post ({'svc': 'token/login', 'params': "{'token':'%s'}" % usr2token['wialon']})
	res = upload_wlp(sres['eid'], 'exchange/import_json')
	ppp(res)
	try:
		DEBUG = True
		usr = sres['au']
		sid = sres['eid']
		usid = sres['user']['id']
		print "User: %s SID: %s UsId: %d" % (usr, sid, usid)
		print "="*44
		data ={'sid': sid}
		'''
		data['svc'] = 'core/get_hw_types'
		data['params'] = { "filterType":"type", "filterValue":["mobile"], "includeType": True }
		res = send_post(data)
		ppp(res, data['svc'])
		print "="*44
		'''
		data['svc'] = 'exchange/import_json'
		res = send_post(data, r'wlp/test_ph1.wlp')
		'''
		data['svc'] = 'core/create_unit'
		data['params'] = {"creatorId": usid,"name":"test_LLL","hwTypeId":"9","dataFlags":"257"}
		res = send_post(data)
		'''
		ppp(res, data['svc'])
	except:
		ppp(sres, 'send_post')
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT:", exc_type, exc_value
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
