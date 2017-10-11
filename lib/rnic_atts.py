#!/usr/bin/python
# -*- coding: utf-8 -*-

import	os, sys, time

DEBUG =	True
dict_egts = {}

def	received_egts (uid, du):
	if not uid.isdigit():
		print "err uid\t", uid,
		for k in du.keys():	print "\t", k, du[k],
		print
		return
	ss = '0'*15
	uid = ''.join((uid, ss))[:15]
	if DEBUG:
		print uid,
		for k in du.keys():	print "\t", k, du[k],
		print
	dict_egts[uid] = du
	
	
def	get_atts (fname = r"./conf/RNIC_atts.txt", receiv_type = 'GPRS'):
	d = {}
	# Перечень столбцов в исходном файле fname
	# uid	Код прибора     
	# ph	Номер телефона  
	# icc	ICC ID 1        
	# ph2	Номер телефона 2        
	# icc2	ICC ID 2        
	# vid	Вид прибора навигации   
	# nm	Гаражный номер ТС       
	# as	Аналоговые входы        
	# ds	Дискретные входы        
	# pg	Приоритетная группа
	cols = ['uid', 'ph', 'icc', 'ph2', 'icc2', 'vid', 'nm', 'as', 'ds', 'pg']
	cign = ['icc', 'icc2', 'as', 'ds']	# столбци исключенные из обработки
	
	f = open (fname, 'r')
	sl = f.readline()
	print sl
	lsl = sl.split('\t')
	j = 0
	for c in lsl:
		print cols[j], c
		j += 1
	jj = 0
	while sl:
		sl = f.readline()
		j = 0
		dunit = {}
		for c in sl.strip().split('\t'):
			c = c.strip()
			if j == 0:
				uid = c
				if len(c) > 6:	break
				print "%4d\t" % jj,
				j = 1
				continue
			j += 1
			if cols[j-1] in cign:	continue
			dunit[cols[j-1]] = c
		if j:
			received_egts (uid, dunit)
			jj += 1
			if jj > 1111:	break
	f.close()

import	cPickle as pickle

def	save_pkl (objpkl, filename = r"./conf/RNIC_atts.pkl"):
	fid = open (filename, 'w+b')
	pickle.dump(objpkl, fid)


def	get_pkl (filename = r"./conf/RNIC_atts.pkl"):
	if not os.path.isfile (filename):
		print "Отсутствует файл '%s'" % filename
		return 
	fid = open (filename, 'r+b')
	objpkl = pickle.load(fid)
	return	objpkl
	
if __name__ == "__main__":
	if DEBUG:
		print get_pkl()
	else:
		get_atts ()
		if dict_egts:	save_pkl (dict_egts)
