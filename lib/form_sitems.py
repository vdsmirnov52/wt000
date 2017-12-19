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

select_itemsType = """<select name='itemsType' class='ssel'><option value=''> </option>
	<option value=''>  </option>
	<option value='avl_unit'> avl_unit  </option>
	<option value='avl_unit_group'> avl_unit_group  </option>
	<option value='avl_resource'> avl_resource </option>
	<option value='user'> user  </option>
	<option value='avl_route'> avl_route </option>
	<option value='avl_retranslator'> avl_retranslator  </option>
	</select>"""

def	dom (iddom, request):
	print '~%s|' % iddom
#	print "ZZZZZZZZZZZZZZ", "<pre>", request, shelp
#	print "</pre>"
#	print """<div class='grey' style='background-color: #dde; padding: 4px; margin: 4px;' >
	print """<div class='grey' style='background-color: #dde; width: 680px; padding: 4px; margin: 4px; top: 54px; left: 800px; position: absolute;' >
		<div class='box' style='background-color: #ccd;'><table width=100%%><tr><td><span class='tit'> условия поиска </span></td>
		<td align=right>
		<input type='button' class='butt' value='Search Items' onclick="set_shadow('search_items');" />
		<input type='button' class='butt' value='Reload' onclick="set_shadow('form_sitems');" />
		<input type='button' class='butt' value='Close' onclick="$('#%s').html('Close');" />
		</td>
		</tr></table></div>""" % iddom
	print "<table width=100%>"
#	print "<tr><td align=right>temsType <td> <input name='itemsType' type='text' size=10 /></td><td> тип искомых элементов, если пусто - поиск по всем типам </td></tr>"
	print "<tr><td align=right>temsType <td>", select_itemsType, "</td><td> тип искомых элементов, если пусто - поиск по всем типам </td></tr>"
	print "<tr><td align=right>propName <td> <input name='propName' type='text' size=10 /></td><td> имя свойства, по которому будет осуществляться поиск </td></tr>"
	print "<tr><td align=right>propValueMask <td> <input name='propValueMask' type='text' size=10 value='*' /></td><td> значение свойства: может быть использован знак «*» </td></tr>"
	print "<tr><td align=right>sortType <td> <input name='sortType' type='text' size=10 /></td><td> имя свойства, по которому будет осуществляться сортировка ответа </td></tr>"
	print "<tr><td align=right>propType <td> <input name='propType' type='text' size=10 /></td><td> тип свойства </td></tr>"
#	print "<tr><td align=right>force <td><input name='force' type='text' size=1 value='0' /></td><td> </td></tr>"
	print "<tr><td align=right>flags <td> <input name='flags' type='text' size=10 /></td><td>флаги видимости для возвращаемого результата [1025] </td></tr>"
#	print "<tr><td align=right> <td><input name='' type='text' size=10 /></td><td> </td></tr>"
	print "</table>"
	print "<div id='set_vals' style='border: 1px solid #bbc; color: #668; min-height: 100px;'>set_vals</div>"
#	print "<br /><div id='clog' style='border: 1px solid #bbc; color: #668; height: 120px; overflow: auto; text-align: left;'></div>"
	print "</div>"
