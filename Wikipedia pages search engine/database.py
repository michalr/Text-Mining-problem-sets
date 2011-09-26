#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
from base64 import b64decode

def get_cursor(connection, file_name = None):
	if not connection:
		connection = sqlite3.connect(file_name)
	return connection.cursor()
	
def get_base_title_posting_list(cursor, word):
	t = (word.decode('utf-8', 'ignore'), )
	cursor.execute('SELECT val FROM base_title WHERE arg=?', t)
	return cursor.fetchone()[0]
	
def get_base_body_posting_list(cursor, word):
	t = (word.decode('utf-8', 'ignore'), )
	cursor.execute('SELECT val FROM base_body WHERE arg=?', t)
	return cursor.fetchone()[0]

def get_word_title_posting_list(cursor, word):
	t = (word.decode('utf-8', 'ignore'), )
	cursor.execute('SELECT val FROM word_title WHERE arg=?', t)
	return cursor.fetchone()[0]
	
def get_word_body_posting_list(cursor, word):
	t = (word.decode('utf-8', 'ignore'), )
	cursor.execute('SELECT val FROM word_body WHERE arg=?', t)
	return cursor.fetchone()[0]
	
def read_one_number(offset, _buffer):
	finished = False
	i = offset
	first_number_list = []
	while not finished:
		num = ord(_buffer[i])
		i += 1
		if num >= 2 ** 7:
			num -= 2 ** 7
			finished = True
		first_number_list.append(num)
	number = 0
	for j in range(len(first_number_list)):
		number += first_number_list[j] * (128 ** (len(first_number_list) - j - 1))
	return (number, i)	
	
def decode_posting_list(posting_list):
	plain = b64decode(posting_list)
	decoded_posting_list = []
	i = 0
	prev = 0
	while i < len(plain):
		num, i = read_one_number(i, plain)
		decoded_posting_list.append(num + prev)
		prev = num + prev
	return decoded_posting_list
	
if __name__ == '__main__':
	c = get_cursor(None, 'wikipedia.sqlite')
	l = get_base_body_posting_list(c, word = "zapachnieć")
	print decode_posting_list(l)
	
	

	
	
	





