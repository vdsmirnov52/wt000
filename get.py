#!/usr/bin/python
# -*- coding: utf-8 -*-

import	os, sys, time
import	urllib
import	json
from	wtools import *

def	request (sid, svc, params = None):
	if not params:	params = ''
	url = r"http://wialon.rnc52.ru/wialon/ajax.html?sid=%s&svc=%s&params={%s}" % (sid, svc, params)
	res = json.load(urllib.urlopen(url))
	if not res:	print url
	return res

def	rPOST():
	params = urllib.url_encode({'spam': 1, 'eggs': 2, 'text': "ТЕКСТ TEXT"})
	f = urllib.urlopen(url, params)
	print f.read()

def	get_autos (sid):
	""" найти все машины	"""
	res = request (sid, svss['search_items'], "'spec':{'itemsType':'avl_unit','propName':'*','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':1025,'from':0,'to':0")
	if res:
		if res.has_key('error'):
			print "error:", res['error']
		elif res.has_key('items') and res['items']:
			print "Len res['items']", len(res['items'])
			j = 0
			for item in  res['items']:
				j += 1
				print item['nm'].encode('UTF-8'), ppos(item['pos']),
				if item['pos']:
					tpos = item['pos']['t']
				else:	tpos = None
				if item.has_key('lmsg'):
					print plmsg(item['lmsg'], tpos)
				else:	print ""
		#		ppp (item, "%3d" %j)
		else:
			ppp(res)
	else:	print res

def	ppos (pos):
	if not pos:	return "\tpos None"
	if pos.has_key('t'):
		return	"\tX:%10.6f, Y:%10.6f %s" % (pos['x'], pos['y'], time.strftime("%Y-%m-%d %T", time.localtime(pos['t'])))
	else:	return  "\tX:%10.6f, Y:%10.6f" % (pos['x'], pos['y'])

def	plmsg (lmsg, tpos):
	if not lmsg:		return "\tlmsg None"
	if tpos == lmsg['t']:	return ""
	if lmsg.has_key('pos'):
		return  "\tlmsg %s %s" % (time.strftime("%Y-%m-%d %T", time.localtime(lmsg['t'])), ppos(lmsg['pos']))
	else:	return  "\tlmsg %s" % time.strftime("%Y-%m-%d %T", time.localtime(lmsg['t']))
	ppp (lmsg)

def	create_unit (sid, name = 'ZZZ_1234', creatorId = 17, hwTypeId = 96266):
	# https://sdk.wialon.com/wiki/ru/local/remoteapi1604/codesamples/update_item#udalenie_obekta
	params={
		"creatorId": creatorId,
		"name": name,
		"hwTypeId": hwTypeId,
		"dataFlags":1
	}
#	help (json)
	print jsqn.string(params)
#	res = request (sid, svss['create_unit'], "'spec':{'itemsType':'user','propName':'sys_name','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':%s,'from':0,'to':0" % flags)
	
svss = {
	'curr_account': 'core/get_account_data',	# Информация о текущей учетной записи type {1|2} ( минимальная | детальная )
	'search_items': 'core/search_items',		# Поиск объектов (элементов) по критериям
	'create_unit':	'core/create_unit',		# Создать объект (элемент)
	'delete_item':	'item/delete_item',		# Удалить объект (элемент)
	'export_wlp': 'exchange/export_json',
	'token_list': 'token/list',
	}

def	get_user (sid, flags = 1 | 0x0040 | 0x0080 | 0x0100):
	res = request (sid, svss['search_items'], "'spec':{'itemsType':'user','propName':'sys_name','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':%s,'from':0,'to':0" % flags)
	ppp(res)
	
if __name__ == "__main__":
	sess = {}
	try:
		for uname in usr2token.keys():
			print "#"*33, uname
			sess = login()
			sid = sess['eid']
		#	get_autos (sid)
			get_user (sid)
			logout(sid)
		create_unit (sid, 'ZZZ', 17)
	except:
		if sess.has_key('error'):
			perror(sess['error'])
		else:	print sess
		
		'''
	if sess and sess.has_key('eid'):
		sid = sess['eid']
#		ppp(sess)
		print "sid:", sid
		print "sess['user']['id']", sess['user']['id']
	#	res = request (sid, svss['token_list'], "'userId': 17")
		# найти всех пользователей 
		flags = 1 | 0x0040 | 0x0080 | 0x0100	# | 0x0200 # уведомления пользователя
	#	res = request (sid, svss['search_items'], "'spec':{'itemsType':'user','propName':'sys_name','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':%s,'from':0,'to':0" % flags)
		res = request (sid, svss['search_items'], "'spec':{'itemsType':'user','propName':'sys_name','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':%s,'from':0,'to':0" % flags)
		ppp(res)
		# найти все машины
	#	get_autos ()
		res = request (sid, svss['search_items'], "'spec':{'itemsType':'avl_unit','propName':'*','propValueMask':'*','sortType':'sys_name'},'force':1,'flags':1025,'from':0,'to':0")
	#	print res
		ppp(res['items'], 'items')
		
		if sess['user']['prp']['monu']:
		#	print sess['user']['prp']['monu']
			smonu = json.loads(sess['user']['prp']['monu'])
			monu = []
			for s in smonu:
				monu.append(int(s))
				print s,
			print "<", monu, len (monu)
		if sess['user']['prp']['monugr']:
			o = json.loads(sess['user']['prp']['monugr'])
			for k in o.keys():
				print k, len (o[k]), ":\t",
				if o[k]:
					for s in o[k]:
						print s,
						if s in monu:
							print "t,",
						else:	print "f,",
				print ""
#		account = request (sid, svss['curr_account'], "'type': 2")
		logout(sid)
	else:
		ppp(sess)
		'''
