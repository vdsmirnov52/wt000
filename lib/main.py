# -*- coding: utf-8 -*-

import	cgi, os, sys, time, string

LIBRARY_DIR = r"/home/smirnov/Wialon/lib/"
sys.path.insert(0, LIBRARY_DIR)

import	dbtools, cglob

CONFIG = None


def	jscripts (ssrc):
	for c in ssrc:
		print "\t<script type='text/javascript' src='%s'></script>" % c

def	rel_css (ssrc):
	for c in ssrc:
		print "\t<link rel='stylesheet' type='text/css' href='%s' />" % c

jsList = [r'//code.jquery.com/jquery-latest.min.js', r'//wialon.rnc52.ru/wsdk/script/wialon.js', #r'/wjs/wialon_login.js', r'/wjs/wialon_units.js',
	r'/jq/jquery.onajax_answer.js', r'/jq/jquery.js', r'/js/calendar.js', r'/js/check_forms.js']
#import	twlp
#tokens = []
#for k in twlp.usr2token.keys():	tokens.append("{name: '%s', token: '%s'}" % (k, twlp.usr2token[k]))
#jsLocal =  """<script type='text/javascript'>
jsLocal =  """$(document).ready(function () {
	$.ajaxSetup({ url: "w.cgi?this=ajax", type: "post", error: onAjaxError, success: onAjaxSuccess, timeout: 30000 });
	$('#dbody').css({'height': (-210 + document.documentElement.clientHeight) +'px',  'overflow': 'auto'});
	$('#div_table').css({'height': (-333 + document.documentElement.clientHeight) +'px',  'overflow': 'auto'});
	$('#log').css({'height': '90px', 'overflow': 'auto'});
//	init_users();
})
/////////////////////////////////////////////
wialon_timerId = 0
function msg(text) { $("#log").prepend(text + "<br/>"); }

function init_users() {
	for (var i = 0; i < users_token.length; i++){
		var u = users_token[i];
		$("#users").append("<option value='"+ u.token +"'>"+ u.name + "</option>");
	}
	$("#users").change( getSelectedUnitInfo );
}
function sel_users() {
	if (document.myForm.whost.value == '') {
		if (confirm('Не выбран Host!\\nВыбрать test-wialon.rnc52.ru ?')) {
			document.myForm.whost.value = 'test-wialon.rnc52.ru';
			document.myForm.set_whost.value = document.myForm.whost.value;
		} else	return
	}
	$('#token').val($('#users').val());
//	$('#ttoken').html($('#users').val());
	$('#warnn').html("<span class='bfinf'>Token:</span>" + $('#users').val());
	set_shadow ('login');
}"""
jsTests = """
	function	set_shadow (shstat) {	$.ajax({data: 'shstat='+ shstat +'&' +$('form').serialize()});	}
//	function	add_row(tabname) {	$.ajax({data: 'shstat=add_row&table='+ tabname +'&' +$('form').serialize()});	}
	function	set_message(txt) {	$('#message').html(txt);	}
	function	set_val(id, val) {
		alert ('Id: ' +id +' Val: ' + val);
		$(id).val(val)
	}
function	check_form_auto() {
	var	 messg = '';

$('#name').val('EGTS-27083314');
$('#hwTypeId').val('29');
$('#uid').val('863591027083314');
$('#creatorId').val(31);
$('#oinn').val('520123456777');

	if ($('#name').val() == '')	messg += '\\tОтсутствует Наименование объекта!\\n';
	if ($('#hwTypeId').val() == '')	messg += '\\tОтсутствует hwTypeId объекта!\\n';
	if ($('#uid').val() == '')	messg += '\\tОтсутствует  Уникальный ID объекта!\\n';
//	if (!$('#hwTypeId').val() && !$('#creatorId').val())	messg += '\\n  Проверьте соединение с сервером!';
	if (messg != '') {
		alert ('Ошибки в заполнении формы:\\n' +messg);	
		return false;
	} else {
		return true;
	}
}
function	create_auto () {
	if (check_form_auto()) {
		alert('Ok! creatorId: ' + $('#creatorId').val()); set_shadow('create_unit');
	}
}	"""

def	out_head (title = None):
	code_ssys = -1
	print "<div class='box' style='background-color: #ccd;'><table width=100%><tr><td width=120px>"
	if title:	print "<span class='tit'>", title, "</span>"
#	print	"""<td width=700>User: <select name='users"' id="users" onchange="sel_users()"><option></option></select> <span id='ttoken'>ttoken</span></td>"""
	print   "<td width=220px>Host:"
	cglob.out_select('set_whost', RES_WHST, ['host_name', 'host_name'], key = None, sopt = 'onchange="document.myForm.whost.value = document.myForm.set_whost.value;" ')
	print	"</td><td>wUser:"
	cglob.out_select('users', RES_WUSR, ['token', 'login'], key = None, sopt = 'id="users" onchange="sel_users()"')
	print	"<span id='ttoken'>ttoken</span></td>"
	print	"<td><b id='wuser'></b></td>"	#<td>HW:<span id='hw_types'></span></td><td></td>"
	print	"""<td align=right><input type='button' class='butt' value='Connect' onclick="set_shadow('connect');" title='Установить (обновить) соединение' />
		<input type='button' class='butt' value='Exit' onclick="set_shadow('exit');" title='Разорвать соединение' />
		<input type='button' class='butt' value='Tokens' onclick="set_shadow('update_token');" title="Читать Tokens из 'sys.ini'." />
		<input type='button' class='butt' value='TsT' onclick="set_shadow('btest');" title="btest" />
		</td>"""
	print	"""<td align=right><img onclick="document.myForm.submit();" title="Обновить" src="../img/reload3.png"></td>"""
	print	"</tr></table></div>"
#	print button_autos

button_tools = """<div class='box' style='background-color: #ccd;'><table width=100%><tr><td width=30% id='flabel' class='tit'>flabel</td>
	<td align=right>
	<input type='button' class='butt' value='Agro Module' onclick="document.myForm.fstat.value = 'form_agro'; set_shadow('form_agro');" title='Агро модуль - инструменты' />
	<input type='button' class='butt' value='get Zone Data' onclick="document.myForm.fstat.value = 'form_szone'; set_shadow('form_szone');" title='Геозоны - подробная информация' />
	<input type='button' class='butt' value='Search Items' onclick="document.myForm.fstat.value = 'form_sitems'; set_shadow('form_sitems');" title='Поиск объектов по критериям' />
	</td></tr></table></div>"""

button_autos = """
	<div class='box' style='background-color: #ccd;'><table width=100%><tr><td>
	<td align=right>
	<input type='button' class='butt' value='check_form_auto' onclick=" check_form_auto();" />
	<input type='button' class='butt' value='GET_users' onclick="set_shadow('get_users');" />
	<input type='button' class='butt' value='GET_hw_types' onclick="set_shadow('get_hw_types');" />
	<input type='button' class='butt' value='GET_avl_unit' onclick="set_shadow('get_avl_unit');" />
	</td></tr></table></div>"""

def	out_form_auto ():
	def_vals = {'creatorId':17, 'dataFlags':4294967295, }
	pars_obj = {
	#'- Основное',
	'name': 'Имя', 'hwTypeId': 'Тип устройства', 'creatorId': 'Создатель', 'uid': 'Уникальный ID', 'ph0': 'Телефонный номер', 'passwd': 'Пароль доступа к объекту', #'dataFlags',
	#'- Характеристики',
	'tts': 'Тип Т/С', 'tvin': 'VIN', 'treg': 'Регистрационный знак', 'tmark': 'Марка', 'tmod': 'Модель', 'tyear': 'Год выпуска',
	#'- Организация', 
	'oinn': 'ИНН', 'odog': 'Договор',
	}
	order = ['- Основное', 'name', 'hwTypeId', 'uid', 'ph0', 'passwd', 'creatorId',
		'- Характеристики', 'tts', 'tvin', 'treg', 'tmark', 'tmod', 'tyear', 
		'- Организация','oinn', 'odog',
	] 
	print """<center><div class='grey' style='background-color: #dde; width: 800px; padding: 10px; margin: 8px;' >
		<div class='box' style='background-color: #ccd;'><table width=100%><tr><td><span class='tit'> Новый объект </span></td>
		<td align=right>
		<input type='button' class='butt' value='check_form_auto' onclick=" check_form_auto();" />
		<input type='button' class='butt' value='Создать' onclick=" create_auto();" />
		</td>
		</tr></table></div>
		<table width=100%>"""
	for vnm in order:
		if vnm[0] == '-':
			print "<tr><th colspan=2 class='tit'> &nbsp; %s &nbsp; </th></tr>" % vnm[1:]
			continue
		print "<tr><td align='right' width=220> %s: </td><td>" % pars_obj[vnm]
		if vnm in ['hwTypeId', 'creatorId']:
			print "<span id='_%s'> %s </span>" % (vnm, vnm.upper())
		else:
			if def_vals.has_key(vnm):
				val = def_vals[vnm]
			else:	val = ''
			print "<input id='%s' name='%s' type='text' value='%s' />" % (vnm, vnm, val)
		print "</td></tr>"
	print "</table>"
	print "<br /><div id='clog' style='border: 1px solid #bbc; color: #668; height: 120px; overflow: auto; text-align: left;'></div>"
	print "</div></center>"

def	perror (tit = None, txt = None):
	if not tit:	tit = ''
	print	"<div class='error'><b>%s</b> %s</div>" % (str(tit), str(txt))

def	new_widow (request, conf):
	global	CONFIG
	CONFIG = conf
	try:
		print "<head> <meta name='Author' content='V.Smirnov'> <title>%s</title>" % CONFIG.get('titWindows', request['wname'])
		rel_css ((r'/css/wlstyle.css', r'/css/calendar.css', r'/css/new_widow.css'))
		jscripts ((r'/jq/jquery.onajax_answer.js', r'/jq/jquery.js', r'/js/calendar.js', r'/js/check_forms.js'))
		print jsLocal, "</head>"
		if request.has_key('wname') and request['wname'] == 'listalarms':
			bgc = '#fa6'
		else:	bgc = '#440'
		print """<body id='id_body' style='background-color: %s; padding: 0px;'>
			<form name='myForm' action='/cgi/w.cgi' method='post'><fieldset class='hidd'>
			<input name='orderby' type='hidden' value='' />
			<input name='valid' type='hidden' value='' />
			<input name='fform' type='hidden' value='new_widow' />""" % bgc
		print "new_widow", request
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		perror ("EXCEPT new_widow", " ".join(["<pre>", str(exc_type).replace('<', '# '), str(exc_value), "</pre>"]))
		print "<span style='background-color: #ffa; color: #a00; padding: 4px;'> EXCEPT new_widow:", exc_type, exc_value, "</span>"
	finally:
		print "</form></body></html>"

def	test_db_connects():
	""" Контроль соединения с Базами Данных	"""
	print "Контроль соединения с Базами Данных<pre>"
	for k in DBDS.keys():
		print	k, DBDS[k],
		dbi = dbtools.dbtools(DBDS[k])
		if dbi:	print 'Ok'
		else:	print 'Err'
	print "</pre>"

DB_WL	= None
DBDS	= None	# описатели соединений с Базами Данных
TOKENS	= []

def	init_conf():
	global	BDCOBF
	global	DBDS, RES_WHST, RES_WUSR, DB_WL
	import	dbsqlite

	dbconf = dbsqlite.dbsqlite(os.path.join(r'/dblite/', 'config.db'))

	RES_WHST = dbconf.get_table("whosts", "id_wh > 0 ORDER BY host_name")
	RES_WUSR = dbconf.get_table("whusers", "id_whu > 0 ORDER BY id_whu")
	return	dbconf
'''
	DB_WL	= dbtools.dbtools('host=127.0.0.1 dbname=wialon port=5432 user=smirnov')
	RES_WHST = DB_WL.get_table("whosts", "id_wh > 0 ORDER BY id_wh")
	RES_WUSR = DB_WL.get_table("whusers", "id_whu IN (5,6) ORDER BY id_whu")
'''
def	dom_head ():
		print "<head> <meta name='Author' content='V.Smirnov'> <title>%s</title>" % CONFIG.get('System', 'title')
		rel_css ((r'/css/wlstyle.css', r'/css/calendar.css'))
		jscripts(jsList)
	#	jscripts ((r'/jq/jquery.onajax_answer.js', r'/jq/jquery.js', r'/js/calendar.js', r'/js/check_forms.js'))
	#	print jsLocal, "</head>"
	#	print "\n".join(["<script type='text/javascript'>", jsLocal, "var users_token = [\n%s\n];" % ',\n'.join(tokens), jsTests, "</script></head>"])
	#	print "\n".join(["<script type='text/javascript'>", jsLocal, "var users_token = [\n%s\n];" % ',\n'.join(TOKENS), jsTests, "</script></head>"])
		print "\n".join(["<script type='text/javascript'>", jsLocal, jsTests, "</script></head>"])

#######################################################

def	main (request, conf):
	global	CONFIG
	global	BDCOBF
	global	DBDS, TOKENS, DB_WL
	CONFIG = conf
	DBDS = dict(CONFIG.items('dbNames'))
	TOKENS = dict(CONFIG.items('usr2token'))
	dom_head()
	BDCOBF = init_conf ()
	if TOKENS:	### WWW unable to open database file	невозможно открыть файл базы данных для изменений 
		BDCOBF.execute ("update whusers SET token = '%s', token_create = %d WHERE id_whu != 2;" % (TOKENS['wialon'], time.time()))
		BDCOBF.execute ("update whusers SET token = '%s', token_create = %d WHERE id_whu = 2;" % (TOKENS['v.smirnov'], time.time()))
		'''
		print "update whusers SET token = '%s', token_create = %d WHERE id_whu = 2;" % (TOKENS['v.smirnov'], time.time())
		print BDCOBF.last_error 
		rrr = BDCOBF.get_row("SELECT * FROM whusers WHERE id_whu = 2;")
		print rrr, BDCOBF.last_error
		''' 
	elif RES_WUSR:
		d = RES_WUSR[0]
		for r in RES_WUSR[1]:	TOKENS.append("{name: '%s', token: '%s'}" % (r[d.index('login')], r[d.index('token')]))
	else:
		test_db_connects()
		return

#	print """<html xmlns="http://www.w3.org/1999/xhtml">"""
	try:
		print "<body>"
		print """<form name='myForm' action='%s' method='post'><fieldset class='hidd'>
			<!--input name='wuser' type='hidden' id='wuser' /-->
			<input name='whost' type='hidden' id='whost' />
			<input name='wusid' type='hidden' id='wusid' />
			<input name='wsid' type='hidden' id='wsid' />
			<input name='token' type='hidden' id='token' size=76 />
			<input name='fstat' type='hidden' id='fstat' />
			</fieldset>""" % os.environ['SCRIPT_NAME']
		'''
		'''
	#	print 'REMOTE_ADDR', os.environ['REMOTE_ADDR']
		if os.environ['REMOTE_ADDR'] in ['10.10.2.40', '37.147.195.151']:
			out_head(CONFIG.get('System', 'name'))
			print button_tools
			print "<div id='dbody' class='hidd'>"
		#	print	'<iframe src="http://212.193.103.21/tmp/mmap.html" width="800" height="700"></iframe>'
			print	'<iframe src=" http://wialon.rnc52.ru/locator/index.html?t=1b63c946cfcf86dcce016b989f18f16fD6D553B79EDEDEFB89EDE97EECFB9724E2B64AE1&map_type=2&zoom=17&lang=ru" width="800" height="700"></iframe>'
		#	print	'<iframe src=" http://wialon.rnc52.ru/locator/index.html?u=Агрофирма РУСЬ&zoom=17&lang=ru" width="800" height="700"></iframe>'
			print "</div><!-- dbody       -->"
		else:
			print 'REMOTE_ADDR', os.environ['REMOTE_ADDR']
			print '<h3><img onclick="document.myForm.submit();" title="Обновить" src="../img/reload3.png"> Wialon demo</h3>'
			print	'<iframe src=" http://wialon.rnc52.ru/locator/index.html?t=1d5a4a6ab2bde440204e6bd1d53b3af841235B51D73C0B07786DA3DC363D2008712C05B5&zoom=17&lang=ru" width="1200" height="700"></iframe>'
		#	print	'<iframe src=" http://wialon.rnc52.ru/locator/index.html?t=1b63c946cfcf86dcce016b989f18f16fD6D553B79EDEDEFB89EDE97EECFB9724E2B64AE1&zoom=17&lang=ru" width="800" height="700"></iframe>'
		#	print '<img onclick="document.myForm.submit();" title="Обновить" src="../img/reload3.png">'
		'''
	#	print button_autos
		print	"<div id='dbody' class='hidd'>"
	#	out_form_auto ()
		print	"</div><!-- dbody	-->"
		'''
		print	"""<div id="log" style='border: 1px solid #bbc; color: #668;'></div>"""
#		print	"</form><!-- myForm	-->"
		if request.has_key('message'):
			print "<div id='message' style='text-align:center;'>%s</div>" % request['message']
		else:	print "<div id='message' style='text-align:center;'>message</div>"
		print """<script language="JavaScript">setTimeout ("set_message ('')", 10000);</script>"""
		print """<table><tr><td><div id='shadow'>shadow</div></td><td><div id='shadow2'>shadow2</div></td><td>
		<div id='widget'>widget</div></td><td><div id='error'>error</div></td><td><div id='warnn'>warnn</div></td></tr></table>"""
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		perror ("EXCEPT main_page", " ".join(["<pre>", str(exc_type).replace('<', '# '), str(exc_value), "</pre>"]))
		print "<span style='background-color: #ffa; color: #a00; padding: 4px;'> EXCEPT main_page:", exc_type, exc_value, "</span>"
	finally:
		print "</form></body></html>"
