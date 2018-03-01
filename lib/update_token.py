#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	os, sys, time
import	ConfigParser

LIBRARY_DIR = r"/home/smirnov/Wialon/lib/"
CONF_PATHNAME = r"/home/smirnov/Wialon/sys.ini"
sys.path.insert(0, LIBRARY_DIR)

import	dbsqlite

def	update_token ():
	if not os.access (CONF_PATHNAME, os.F_OK):	return

	config = ConfigParser.ConfigParser()
	config.read (CONF_PATHNAME)
	tokens = dict(config.items('usr2token'))
	if not tokens:	return

	dbconf = dbsqlite.dbsqlite(os.path.join(r'/home/smirnov/Wialon/dblite/', 'config.db'))
	for k in tokens.keys():
		print tokens[k], k, dbconf.execute ("UPDATE whusers SET token = '%s', token_create = %d WHERE login='%s';" % (tokens[k], time.time(), k)), '<br />'
	dbconf.close()

if __name__ == "__main__":
	update_token()
