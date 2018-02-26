#!/usr/bin/python
# -*- coding: utf-8 -*-

import	os, sys, time
import	urllib
import	json

LIBRARY_DIR = r"/home/smirnov/Wialon/lib/"
sys.path.insert(0, LIBRARY_DIR)

#	https://sdk.wialon.com/wiki/ru/local/remoteapi1604/apiref/core/search_items?s[]=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA&s[]=%D0%BE%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D0%BE%D0%B2&s[]=%D1%8D%D0%BB%D0%B5%D0%BC%D0%B5%D0%BD%D1%82%D0%BE%D0%B2&s[]=%D0%BF%D0%BE&s[]=%D0%BA%D1%80%D0%B8%D1%82%D0%B5%D1%80%D0%B8%D1%8F%D0%BC

dict_itemsType = {
	'avl_resource': 'ресурс',
	'avl_retranslator': 'ретранслятор',
	'avl_unit': 'объект',
	'avl_unit_group': 'группа объектов',
	'user': 'пользователь',
	'avl_route': 'маршрут',
	}

dict_subitemsType = {
	'avl_resource': ['drivers', 'driver_groups', 'jobs', 'notifications', 'pois', 'trailers', 'trailer_groups', 'zones_library', 'reporttemplates', 'custom_fields', 'admin_fields',],
	'avl_retranslator': ['retranslator_units',],
	'avl_unit': ['unit_sensors', 'unit_commands', 'service_intervals',],
	'avl_unit_group': ['custom_fields', 'admin_fields',],
	'user': ['custom_fields', 'admin_fields',],
	'avl_route': ['rounds', 'route_schedules',],
	}

dict_propName = {	# и «sortType»
	'sys_name': 'имя элемента',
	'sys_id': 'ID элемента',
	'sys_unique_id': 'ID оборудования',
	'sys_phone_number': 'телефонный номер объекта',
	'sys_phone_number2': 'второй телефонный номер объекта',
	'sys_user_creator': 'ID создателя',
	'rel_user_creator_name': 'имя создателя',
	'sys_billing_account_guid': 'ID учетной записи',
	'rel_billing_account_name': 'имя учётной записи',
	'rel_billing_plan_name': 'имя тарифного плана',
	'sys_comm_state': 'состояние оборудования (1 - подключено, 0 - отключено)',
	'rel_hw_type_name': 'имя оборудования',
	'sys_account_balance': 'баланс учётной записи',
	'sys_account_days': 'количество дней для учётной записи',
	'sys_account_enable_parent': 'права дилера (1 - выданы, 0 - не выданы)',
	'sys_account_disabled': 'учётная запись блокирована (1 - да, 0 - нет)',
	'rel_account_disabled_mod_time': 'время последнего изменения свойства sys_account_disabled, UNIX-time',
	'rel_account_units_usage': 'количество объектов в учётной записи',
	'rel_last_msg_date': 'время последнего сообщения, UNIX-time',
	'rel_is_account': 'является ли ресурс учётной записью (1 - да, 0 - нет)',
	'login_date': 'время последнего входа в систему, UNIX-time',
	'retranslator_enabled': 'включен ли ретранслятор ( 1 - да, 0 - нет)',
	'rel_creation_time': 'дата создания',
	'rel_group_unit_count': 'количество объектов в группе',
	}

dict_propType = {
	'property': 'свойство',
	'list': 'список',
	'propitemname': 'имя подэлемента (например геозона является подэлементом ресурса)',
	'creatortree': 'цепочка создателей (поиск с таким типом вернет список элементов, у которых в цепочке создателей есть создатель, указанный в условии поиска)',
	'accounttree': 'цепочка учетных записей (поиск с таким типом вернет список элементов, у которых в цепочке учетных записей есть учетная запись, указанная в условии поиска)',
	'customfield': 'произвольные поля',
	'profilefield': 'характеристики объекта',
	'adminfield': 'административные записи',
	}

shelp = """
spec 	условия поиска
itemsType 	тип искомых элементов (см. список ниже), если оставить пустым, то поиск будет осуществляться по все типам
propName 	имя свойства, по которому будет осуществляться поиск (см. список возможных свойств ниже)
propValueMask 	значение свойства: может быть использован знак «*»
sortType 	имя свойства, по которому будет осуществляться сортировка ответа
propType 	тип свойства (см. список типов ниже)
force 	0 - если такой поиск уже запрашивался, то вернет полученный результат, 1 - будет искать заново
flags 	флаги видимости для возвращаемого результата (Значение данного параметра зависит от типа элемента, который вы хотите найти. Форматы всех элементов, а так же их флаги описаны в разделе Форматы данных.)
from 	индекс, начиная с которого возвращать элементы результирующего списка (для нового поиска используйте значение 0)
to 	индекс последнего возвращаемого элемента (если 0, то вернет все элементы, начиная с указанного в параметре «from»)
or_logic 	флаг «ИЛИ»-логики для propName-поля (см. ниже) 
"""

select_itemsType = """<select name='itemsType' class='ssel' onchange="set_shadow('select_propName');"><option value=''> </option>
	<option value='avl_unit'> avl_unit  </option>
	<option value='avl_unit_group'> avl_unit_group  </option>
	<option value='avl_resource'> avl_resource </option>
	<option value='user'> user  </option>
	<option value='avl_route'> avl_route </option>
	<option value='avl_retranslator'> avl_retranslator  </option>
	</select>"""

def	select_propName(request):
	print "~set_propName|"
	print """<select name='propName' class='ssel' onchange='document.myForm.sortType.value = document.myForm.propName.value'' ><option value=''> </option>"""
	for v in dict_subitemsType[request['itemsType']]:
		print "<option value='%s'> %s  </option>" % (v, v)
	print """</select>"""
	print """~prop_view|<span class='tit'> Что смотрим: </span>"""
	if request['itemsType'] == 'avl_resource':
		print """<dd>
		<input type='checkbox' name='fild_prp' /> Произвольные свойства 0x00000002 <br />
		<input type='checkbox' name='fild_filds' /> Произвольные поля 0x00000008 <br />
		<input type='checkbox' name='fild_aflds' /> Административные поля 0x00000080 <br />
		<input type='checkbox' name='fild_zl' /> Геозоны 0x00001000 <br />
		<input type='checkbox' name='fild_zg' /> Группы геозон 0x00100000 <br />
		<!--
		<input type='checkbox' name='fild_GUID' /> GUID 0x00000040  <br />
		<input type='checkbox' name='fild_' />  <br />
		-->
		</dd>"""
	elif request['itemsType'] == 'avl_unit':
		print """<dd>
		<input type='checkbox' name='fild_prp' /> Произвольные свойства 0x00000002 <br />
		<input type='checkbox' name='fild_filds' /> Произвольные поля 0x00000008 <br />
		<input type='checkbox' name='fild_aflds' /> Административные поля 0x00000080 <br />
		<input type='checkbox' name='fild_sens' /> Датчики 0x00001000 <br />
		<input type='checkbox' name='fild_cmds' /> Доступные в данный момент команды 0x00000200 <br />
		<b>Дополнительные свойства 0x00000100 </b><br />
		<input type='checkbox' name='fild_uid' /> ID оборудования;
		<input type='checkbox' name='fild_hw' /> тип оборудования;
		<input type='checkbox' name='fild_ph' /> телефонн;
		<input type='checkbox' name='fild_ph2' /> телефонн 2;
		<input type='checkbox' name='fild_psw' /> пароль
		<br>
		<b>Последнее местоположение и сообщение 0x00000400 </b ><br />
		<input type='checkbox' name='fild_pos' /> местоположение
		<input type='checkbox' name='fild_lmsg' /> сообщение
		<br />
		<!--
		<input type='checkbox' name='fild_ugi' /> Изображение объекта 0x00000010 <br />
		<input type='checkbox' name='fild_' />  <br />
		-->
		</dd>"""
	elif request['itemsType'] == 'user':
		print """<dd>
		<input type='checkbox' name='fild_prp' /> Произвольные свойства 0x00000002 <br />
		<input type='checkbox' name='fild_autocomplete' /> autoComplete 
		<input type='checkbox' name='fild_monugr' /> monUGr  
		<input type='checkbox' name='fild_monuv' /> monUV
		<input type='checkbox' name='fild_monu' /> monU  <br />
		<input type='checkbox' name='fild_filds' /> Произвольные поля 0x00000008 <br />
		<input type='checkbox' name='fild_aflds' /> Административные поля 0x00000080 <br />
		<input type='checkbox' name='fild_' />  <br />
		<input type='checkbox' name='fild_' />  <br />
		</dd>"""

def	dom (iddom, request):
	print '~%s|' % iddom
	print 'request[fstat]', request['fstat']
#	print "ZZZZZZZZZZZZZZ", "<pre>", request, shelp
#	print "</pre>"
#	print """<div class='grey' style='background-color: #dde; padding: 4px; margin: 4px;' >
	print """<div id='div_sitems' class='grey' style='background-color: #dde; width: 660px; padding: 4px; margin: 4px; top: 86px; left: 800px; position: absolute;' >
		<div class='box' style='background-color: #ccd;'><table width=100%%><tr><td><span class='tit'> условия поиска </span></td>
		<td align=right>
		<input type='button' class='butt' value='Search Items' onclick="set_shadow('search_items');" />
		<input type='button' class='butt' value='Reload' onclick="set_shadow('form_sitems');" />
		<input type='button' class='butt' value='Close' onclick="$('#%s').html('Close');" />
		</td>
		</tr></table></div>""" % iddom
	print "<table width=100%>"
	print "<tr><td align=right>itemsType <td>", select_itemsType, "</td><td> тип искомых элементов, если пусто - поиск по всем типам </td></tr>"
	print "<tr><td align=right>propName <td id='set_propName'> <input name='propName' type='text' size=15 /></td><td> имя свойства, по которому будет осуществляться поиск </td></tr>"
	print "<tr><td align=right>propValueMask <td> <input name='propValueMask' type='text' size=15 value='*' /></td><td> значение свойства: может быть использован знак «*» </td></tr>"
	print "<tr><td align=right>sortType <td> <input name='sortType' type='text' size=15 /></td><td> имя свойства, по которому будет осуществляться сортировка ответа </td></tr>"
	print "<tr><td align=right>propType <td> <input name='propType' type='text' size=15 /></td><td> тип свойства </td></tr>"
#	print "<tr><td align=right>force <td><input name='force' type='text' size=1 value='0' /></td><td> </td></tr>"
	print "<tr><td align=right>flags <td> <input name='flags' type='text' size=15 /></td><td>флаги видимости для возвращаемого результата [1025] </td></tr>"
#	print "<tr><td align=right> <td><input name='' type='text' size=15 /></td><td> </td></tr>"
	print "</table>"
	print "<div id='prop_view' style='border: 1px solid #bbc; color: #668; min-height: 300px;'>prop_view</div>"
	print "<div id='set_vals' style='border: 1px solid #bbc; color: #668; min-height: 100px;'>set_vals</div>"
#	print "<br /><div id='clog' style='border: 1px solid #bbc; color: #668; height: 120px; overflow: auto; text-align: left;'></div>"
	print "</div>"
	print "~eval|$('#div_sitems').css({'left': (-720 + document.documentElement.clientWidth) +'px'});"
	print "~eval|$('#div_sitems').css({'height': (-233 + document.documentElement.clientHeight) +'px',  'overflow': 'auto'});"

import	wtools, twlp, get

sberr =	lambda val:	"<span class='bferr'> %s </span>" % str(val)
sbinf =	lambda val:	"<span class='bfinf'> %s </span>" % str(val)

def	prn_fild (js, view_filds):
	""" Вернуть значение поля если есть	"""
	sres = []
	for fn in view_filds:
		if js.has_key(fn) and js[fn]:
			if 'pos' == fn:
				print get.ppos(js.get(fn))
			elif fn == 'lmsg':	print "<b> %s </b>" % fn, js.get(fn)
			elif fn == 'prp':	print "<b> %s </b>" % fn, js.get(fn)
			elif type(js[fn]) == dict:
				if fn == 'sens':
					print "<b> %s </b>" % fn, js[fn].keys()	#.encode('UTF-8')
				else:
					for k in js[fn].keys():
						print "<b> %s %s </b>" % (fn, str(k))
						if js[fn][k].has_key('n') and js[fn][k]['n']:
							print " '%s' " % js[fn][k]['n'].encode('UTF-8')
							del (js[fn][k]['n'])
						if js[fn][k].has_key('d') and js[fn][k]['d']:
							print " '%s' " % js[fn][k]['d'].encode('UTF-8')
							del (js[fn][k]['d'])
						print " %s <br />" % str (js[fn][k])
				
			else:	print "<b> %s </b> %s <br />" % (fn, str (js[fn]))
		#	print "<br />"

def	search_items (request):
	""" Выполнить запрос "Поиск элементов"	"""
	params = {'force':1, 'flags':1025, 'from':0, 'to':0}
	spec = {'itemsType': None, 'propName': '*', 'propValueMask': '*', 'sortType':'sys_name', 'propType':'sys_name'}
	for k in spec.keys():
		if request.has_key(k) and request[k]:	spec[k] = request[k]
	for k in params.keys():
		if request.has_key(k) and request[k]:	params[k] = int(request[k])
	view_filds = []
	for k in request.keys():
		if 'fild_' in k[:5] and request[k] == 'on':
			view_filds.append(k[5:])
	
	try:
		print spec, "<br />"
		params['spec'] = spec
	#	print params, "<br />"
		data = {'sid': request['wsid'], 'svc': 'core/search_items' , 'params': params}
		fres, sres = twlp.requesr(data)
		if fres:
			print "~log|", sbinf(fres), '</span>', params
			print '<br />totalItemsCount:', sbinf(sres['totalItemsCount'])	#, '<hr />'
			print "~dbody|"
			print "<table>"
			for i in sres['items']:
				if i.has_key('pos') and i['pos']:
					print "<tr><td>", i['id'], "</td><td>", sbinf (i['nm'].encode('UTF-8')), i['cls'], '</td><td>', get.ppos(i.get('pos')), "</td></tr>"
				else:	print "<tr><td>", i['id'], "</td><td>", sbinf (i['nm'].encode('UTF-8')), i['cls'], '</td><td>', "</td></tr>"
				if not view_filds:	continue
				
				if i.has_key('prp'):
					if 'monugr' in view_filds and i['prp'].has_key('monugr') and len(i['prp']['monugr']) > 2:
						print "<tr><td> </td><td>", sbinf('monUGr'), "</td><td>", i['prp']['monugr'], "</td></tr>"
					if 'monuv' in view_filds and i['prp'].has_key('monuv') and len(i['prp']['monuv']) > 2:
						print "<tr><td> </td><td>", sbinf('monUV'), "</td><td>", i['prp']['monuv'], "</td></tr>"
					if 'monu' in view_filds and i['prp'].has_key('monu') and len(i['prp']['monu']) > 2:
						print "<tr><td> </td><td>", sbinf('monU'), "</td><td>", i['prp']['monu'], "</td></tr>"
					if 'autocomplete' in view_filds and i['prp'].has_key('autocomplete'):
						print "<tr><td> </td><td>", sbinf('autoCompltte'), "</td><td>", i['prp']['autocomplete'].encode('UTF-8'), "</td></tr>"

				print "<tr><td> </td><td colspan=2>"
				sjs = prn_fild (i, view_filds)
				if sjs:	print sjs
				print "</td></tr>"
				"""
			#	print spec
			#	print i['id'], i['nm'].encode('UTF-8')
				if spec['itemsType'] == 'avl_resource':
					'''
					print i['id'], i['nm'].encode('UTF-8')
					if i.has_key('zl') and i['zl']:
						print i['id'], i['nm'].encode('UTF-8')
						for k in i['zl'].keys():
						#	print i['zl'][k]['b']
							print '<li>'
							print i['zl'][k]['id']
							print i['zl'][k]['n'].encode('UTF-8')
							print i['zl'][k]['d'].encode('UTF-8')
							print '<br />'
					'''
					if i.has_key('zg') and i['zg']:
					#	print i['id'], i['nm'].encode('UTF-8')
					#	print i['id'], i['zg']
						for k in i['zg'].keys():
							print i['zg'][k]['id']
							print i['zg'][k]['n'].encode('UTF-8'), i['zg'][k]['d'].encode('UTF-8')
							print i['zg'][k]['zns']
					#		print '<br />'
				else:
					'''
				#	print fres, sres['items']
				#	wtools.ppp(sres['items'])
					'''
					wtools.ppp(i, 'item')	#out_json(i)	#sres['items'])
				print "</td></tr>"
				"""
			#	print '<br />'
			print "</table>"
			print	'#'*22
		else:
			print "~log|", sberr (sres), params
			print "~eval| set_shadow('connect');"
	except:	print sberr (wtools.sexcept ('search_items"'))

def	ajax (request):
	shstat = request['shstat']
	if shstat == 'search_items':
		print "~set_vals|"
		search_items (request)
	elif shstat == 'select_propName':
		select_propName(request)
	else:	print "~eval|alert ('form_sitems: Unknown shstat: [%s]!');" % request ['shstat']
