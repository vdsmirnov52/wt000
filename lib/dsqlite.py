#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	sys
import	sqlite3

class dsqlite:
	r""" Работа с SQLite
	Warning('You can only execute one statement at a time.',) ... только одно заявление за раз
Функции:
	execute (query)		- Исполняет SQL запрос.	Возвращает: {True|False}
	get_row  (query)	- Читает одну запись.   Возвращает: row = (val1, val2, ...)
	get_rows (query)	- Читает несколько записей      Возвращает: rows = [(row1), (row2), ...]
	get (query, fall)       - Исполняет запрос и читает данные. Если fall: 1 - fetchall() иначе 0 - fetchone())
	get_table (tname, [swhere], [cols])
Переменные:
	desc = []	- Список наименования полей последнего запроса
	last_error      = (exc_type, exc_value) последняя оштбка доступа к БД
	"""
	last_error =	None
	desc = []	## Список наименования полей последнего запроса
	def __init__ (self, file_db = './sqlite.db'):
	#	try:
			self.conn = sqlite3.connect(file_db)
			self.curs = self.conn.cursor()
	#	except:

	def	execute (self, query):
		try:
			self.curs.execute (query)
			self.last_error = None
			return	True
		except (sqlite3.OperationalError, sqlite3.IntegrityError, sqlite3.Warning):
			self.last_error = sys.exc_info()[:2]
			return	False

	def	get_row (self, query):
		return  self.get (query, 0)

	def	get_rows (self, query):
		return  self.get (query, 1)

	def     get (self, query, fall):
		self.last_error = None
		try:
			self.curs.execute (query)
			self.desc = [f[0] for f in self.curs.description]
			if fall:	return  self.curs.fetchall()
			else:		return  self.curs.fetchone()
		except (sqlite3.OperationalError, sqlite3.Warning):
			print 'except:', query
			self.last_error = sys.exc_info()[:2]
		finally:
			self.conn.commit()

	def	get_table (self, tname, swhere = None, cols = None):
		""" Читать таблицу из БД "SELECT {*|<cols>} FROM <tname> [WHERE <swhere>];"	"""
		if not cols:	cols = '*'
		if not swhere:
			query = "SELECT %s FROM %s;" % (cols, tname)
		else:	query = "SELECT %s FROM %s WHERE %s;" % (cols, tname, swhere)
		self.rows = self.get_rows (query)
		if self.rows:	return	self.desc, self.rows

if __name__ == '__main__':
	sqls =	["DROP TABLE tst;",
	"CREATE TABLE tst (id integer PRIMARY KEY, name text);",
	"INSERT INTO tst (id, name) VALUES (1, 'QWE asdfg');",
	"INSERT INTO tst (id, name) VALUES (2, 'Привет ЙЦУКЕН');",
	"INSERT INTO tst (id, name) VALUES (3, 'POIUYTREWQ');",
	]
	lite = dsqlite('ZZZ.db')
	for sql in sqls:
		print sql, lite.execute(sql), lite.last_error
	print 'SQLite version:', lite.execute('SELECT SQLITE_VERSION()')
	print 'get_row:', lite.get_row('SELECT SQLITE_VERSION()')
	print 'get_rows:', lite.get_rows('SELECT * FROM tst WHERE id < 0'), lite.last_error, lite.desc
	print 'get_table:', lite.get_table ('tst'), lite.last_error
