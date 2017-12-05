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
	$('#log').css({'height': '100px', 'overflow': 'auto'});
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
	print "<div class='box' style='background-color: #ccd;'><table width=100%><tr><td width=200px>"
	if title:	print "<span class='tit'>", title, "</span>"
#	print	"""<td width=700>User: <select name='users"' id="users" onchange="sel_users()"><option></option></select> <span id='ttoken'>ttoken</span></td>"""
	print   "<td width=200px>Host:"
	cglob.out_select('set_whost', RES_WHST, ['host_name', 'host_name'], key = None, sopt = 'onchange="document.myForm.whost.value = document.myForm.set_whost.value;" ')
	print	"</td><td>wUser:"
	cglob.out_select('users', RES_WUSR, ['token', 'login'], key = None, sopt = 'id="users" onchange="sel_users()"')
	print	"<span id='ttoken'>ttoken</span></td>"
	print	"<td><b id='wuser'></b></td>"	#<td>HW:<span id='hw_types'></span></td><td></td>"
	print	"""<td align=right><input type='button' class='butt' value='Connect' onclick="set_shadow('connect');" />"""
	print	"""<input type='button' class='butt' value='Exit' onclick="set_shadow('exit');" /></td>"""
	print	"""<td align=right><img onclick="document.myForm.submit();" title="Обновить" src="../img/reload3.png"></td>"""
	print	"</tr></table></div>"
#	print button_autos

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
		rel_css ((r'/css/style.css', r'/css/calendar.css', r'/css/new_widow.css'))
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

#RES_WHU	= None
DB_WL	= None
DBDS	= None	# описатели соединений с Базами Данных
TOKENS	= []
try:
	DB_WL	= dbtools.dbtools('host=127.0.0.1 dbname=wialon port=5432 user=smirnov')
	RES_WHST = DB_WL.get_table("whosts", "id_wh > 0 ORDER BY id_wh")
	RES_WUSR = DB_WL.get_table("whusers", "id_whu IN (5,6) ORDER BY id_whu")
#	if RES_WUSR:
#		d = RES_WUSR[0]
#		for r in RES_WUSR[1]:	TOKENS.append("{name: '%s', token: '%s'}" % (r[d.index('login')], r[d.index('token')]))
except:
	exc_type, exc_value = sys.exc_info()[:2]
	perror ("EXCEPT: Init TOKENS in main.py", " ".join(["<pre>", str(exc_type).replace('<', '# '), str(exc_value), "</pre>"]))

#######################################################

def	main (request, conf):
	global	CONFIG
	global	DBDS, TOKENS, DB_WL
	CONFIG = conf
	DBDS = dict(CONFIG.items('dbNames'))
	TOKENS = dict(CONFIG.items('usr2token'))
	if TOKENS:
		DB_WL.qexecute ("update whusers SET token = '%s', token_create = now() WHERE id_whu != 6;" % TOKENS['wialon'])
		DB_WL.qexecute ("update whusers SET token = '%s', token_create = now() WHERE id_whu = 6;" % TOKENS['v.smirnov'])
	elif RES_WUSR:
		d = RES_WUSR[0]
		for r in RES_WUSR[1]:	TOKENS.append("{name: '%s', token: '%s'}" % (r[d.index('login')], r[d.index('token')]))
	else:
		test_db_connects()
		return

#	print """<html xmlns="http://www.w3.org/1999/xhtml">"""
	try:
		print "<head> <meta name='Author' content='V.Smirnov'> <title>%s</title>" % CONFIG.get('System', 'title')
		rel_css ((r'/css/style.css', r'/css/calendar.css'))
		jscripts(jsList)
	#	jscripts ((r'/jq/jquery.onajax_answer.js', r'/jq/jquery.js', r'/js/calendar.js', r'/js/check_forms.js'))
	#	print jsLocal, "</head>"
	#	print "\n".join(["<script type='text/javascript'>", jsLocal, "var users_token = [\n%s\n];" % ',\n'.join(tokens), jsTests, "</script></head>"])
	#	print "\n".join(["<script type='text/javascript'>", jsLocal, "var users_token = [\n%s\n];" % ',\n'.join(TOKENS), jsTests, "</script></head>"])
		print "\n".join(["<script type='text/javascript'>", jsLocal, jsTests, "</script></head>"])
		print "<body>"
		print """<form name='myForm' action='/cgi/w.cgi' method='post'><fieldset class='hidd'>
			<!--input name='wuser' type='hidden' id='wuser' /-->
			<input name='whost' type='hidden' id='whost' />
			<input name='wusid' type='hidden' id='wusid' />
			<input name='wsid' type='hidden' id='wsid' />
			<input name='token' type='hidden' id='token' size=76 />
			</fieldset>"""
		'''
		'''
		out_head(CONFIG.get('System', 'name'))
	#	print button_autos
		print	"<div id='dbody' class='hidd'>"
	#	out_form_auto ()
		print	"</div><!-- dbody	-->"
		print	"""<div id="log" style='border: 1px solid #bbc; color: #668;'></div>"""
#		print	"</form><!-- myForm	-->"
		if request.has_key('message'):
			print "<div id='message' style='text-align:center;'>%s</div>" % request['message']
		else:	print "<div id='message' style='text-align:center;'>message</div>"
		print """<script language="JavaScript">setTimeout ("set_message ('')", 10000);</script>"""
		print """<table><tr><td><div id='shadow'>shadow</div></td><td><div id='shadow2'>shadow2</div></td><td>
		<div id='widget'>widget</div></td><td><div id='error'>error</div></td><td><div id='warnn'>warnn</div></td></tr></table>"""
	#	print os.environ['REMOTE_ADDR']
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		perror ("EXCEPT main_page", " ".join(["<pre>", str(exc_type).replace('<', '# '), str(exc_value), "</pre>"]))
		print "<span style='background-color: #ffa; color: #a00; padding: 4px;'> EXCEPT main_page:", exc_type, exc_value, "</span>"
	finally:
		print "</form></body></html>"
