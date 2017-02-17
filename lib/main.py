# -*- coding: utf-8 -*-

import	cgi, os, sys, time, string

LIBRARY_DIR = r"/home/smirnov/Wialon/lib/"
sys.path.insert(0, LIBRARY_DIR)
CONFIG = None


def	jscripts (ssrc):
	for c in ssrc:
		print "\t<script type='text/javascript' src='%s'></script>" % c

def	rel_css (ssrc):
	for c in ssrc:
		print "\t<link rel='stylesheet' type='text/css' href='%s' />" % c

jsList = [r"//code.jquery.com/jquery-latest.min.js", r"//wialon.rnc52.ru/wsdk/script/wialon.js", r"/wjs/wialon_login.js", r"/wjs/wialon_units.js",
	r'/jq/jquery.onajax_answer.js', r'/jq/jquery.js', r'/js/calendar.js', r'/js/check_forms.js']
jsLocal =  """<script type='text/javascript'>
	$(document).ready(function () {
	$.ajaxSetup({ url: "w.cgi?this=ajax", type: "post", error: onAjaxError, success: onAjaxSuccess, timeout: 30000 });
	$('#dbody').css({'height': (-210 + document.documentElement.clientHeight) +'px',  'overflow': 'auto'});
	$('#div_table').css({'height': (-333 + document.documentElement.clientHeight) +'px',  'overflow': 'auto'});
	$('#log').css({'height': '100px', 'overflow': 'auto'});
	init_users();
	})
	function	set_shadow (shstat) {	$.ajax({data: 'shstat='+ shstat +'&' +$('form').serialize()});	}
	function	add_row(tabname) {	$.ajax({data: 'shstat=add_row&table='+ tabname +'&' +$('form').serialize()});}
	function	set_message(txt) {	$('#message').html(txt);}
	
	function	set_val(id, val) {
		alert ('Id: ' +id +' Val: ' + val);
		$(id).val(val)
	}
/////////////////////////////////////////////
function msg(text) { $("#log").prepend(text + "<br/>"); }
var	users_token = [
	{name: "wialon",	token:	"1d5a4a6ab2bde440204e6bd1d53b3af891F531BAA376794D25274B3EAD44CAF9BACCD247"},
	{name: "V.Smirnov",	token:	"c5a76d06f77af04aa4c9fa0699d465c2A1C15592645215DBA63B6D2A21AE9A379DB51D75"},
	]
function init_users() {
	for (var i = 0; i < users_token.length; i++){
		var u = users_token[i];
		$("#users").append("<option value='"+ u.token +"'>"+ u.name + "</option>");
	}
	$("#users").change( getSelectedUnitInfo );
}
function sel_users() {
	if ($('#users').val()) {
		$("#log").html('');
		logout();
		$('#token').val($('#users').val());
		$('#ttoken').html($('#users').val());
		setTimeout(login, 200);
	}
}
	</script>"""

def	out_head (title = None):
	code_ssys = -1
	print "<div class='box' style='background-color: #ccd;'><table width=100%><tr><td width=25%>"
	if title:	print "<span class='tit'>", title, "</span>"
	print	"""<td width=700>User: <select name='users"' id="users" onchange="sel_users()"><option></option></select> <span id='ttoken'>ttoken</span></td>"""
	print	"<td>wuser: <b id='wuser'></b></td><td>HW:<span id='hw_types'></span></td><td></td>"
	print	"<td align=right>"
	print	"""<input type='button' class='butt' value='TEST get_hw_types' onclick="set_shadow('get_hw_types');" />"""
	print	"""<input type='button' class='butt' value='Connect' onclick="set_shadow('connect');" />"""
	print	"""<input type='button' class='butt' value='Exit' onclick="set_shadow('exit');" />"""
	print	"</td>"
	print	"""<td align=right><img onclick="document.myForm.submit();" title="Обновить" src="../img/reload3.png"></td>"""
	print	"</tr></table></div>"

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

def	main (request, conf):
	global	CONFIG
	CONFIG = conf
#	print """<html xmlns="http://www.w3.org/1999/xhtml">"""
	try:
		print "<head> <meta name='Author' content='V.Smirnov'> <title>%s</title>" % CONFIG.get('System', 'title')
		rel_css ((r'/css/style.css', r'/css/calendar.css'))
		jscripts(jsList)
	#	jscripts ((r'/jq/jquery.onajax_answer.js', r'/jq/jquery.js', r'/js/calendar.js', r'/js/check_forms.js'))
		print jsLocal, "</head>"
		print "<body>"
		print """<form name='myForm' action='/cgi/w.cgi' method='post'><fieldset class='hidd'>
			<!--input name='wuser' type='hidden' id='wuser' /-->
			<input name='wusid' type='hidden' id='wusid' />
			<input name='wsid' type='hidden' id='wsid' />
			<input name='token' type='hidden' id='token' size=76 />
			</fieldset>"""
		out_head(CONFIG.get('System', 'name'))
		print	"<div id='dbody' class='hidd'>"
		print	"""perror (txt = "MAIN "*3)"""
		print	"</div><!-- dbody	-->"
		print	"""<div id="log" style='border: 1px solid #bbc; color: #668;'></div>"""
#		print	"</form><!-- myForm	-->"
		if request.has_key('message'):
			print "<div id='message' style='text-align:center;'>%s</div>" % request['message']
		else:	print "<div id='message' style='text-align:center;'>message</div>"
		print """<script language="JavaScript">setTimeout ("set_message ('')", 1000);</script>"""
		print """<table><tr><td><div id='shadow'>shadow</div></td><td><div id='shadow2'>shadow2</div></td><td>
		<div id='widget'>widget</div></td><td><div id='error'>error</div></td><td><div id='warnn'>warnn</div></td></tr></table>"""
	#	print os.environ['REMOTE_ADDR']
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		perror ("EXCEPT main_page", " ".join(["<pre>", str(exc_type).replace('<', '# '), str(exc_value), "</pre>"]))
		print "<span style='background-color: #ffa; color: #a00; padding: 4px;'> EXCEPT main_page:", exc_type, exc_value, "</span>"
	finally:
		print "</form></body></html>"
