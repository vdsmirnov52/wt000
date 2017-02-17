
// Login to server using entered username and password
function login() {
	var sess = wialon.core.Session.getInstance(); // get instance of current Session
	var user = sess.getCurrUser(); // get current User
	if( user ) { // if user exists - you are already logged, print username to log
		msg("You are logged as '" + user.getName()+"', click logout button first");
		return; 
	}
  
//	if not logged
	var token = $("#token").val(); // get token from input
	if (!token) { // if token is empty - print message to log
		msg("Enter token");
		return;
	} 

	msg("Trying to login with token '"+ token +"'");
//	sess.initSession("https://hst-api.wialon.com"); // initialize Wialon session
	sess.initSession("http://wialon.rnc52.ru"); // initialize Wialon session
	sess.loginToken(token, "", // trying login 
		function (code) { // login callback
			if (code) msg(wialon.core.Errors.getErrorText(code)); // login failed, print error
			else { msg("Logged successfully"); // login succeed
				getUser();
			}
		}
	);
}

// Logout
function logout() {
	var user = wialon.core.Session.getInstance().getCurrUser(); // get current user
	if (!user){ msg("You are not logged, click 'login' button"); return; } 
	wialon.core.Session.getInstance().logout( // if user exist - logout
		function (code) { // logout callback
			if (code) msg(wialon.core.Errors.getErrorText(code)); // logout failed, print error
			else msg("Logout successfully"); // logout suceed
		}
	);
}

// Get current user and prints its name to log
function getUser() {
	var user = wialon.core.Session.getInstance().getCurrUser(); // get current user
	// print message 
	if (!user) msg("You are not logged, click 'login' button"); // user not exists
	else msg("You are logged as '" + user.getName() + "' Id: " + user.getId()); // print current user name
}
