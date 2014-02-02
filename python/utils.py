##	Utils

import os
import string

def read_text_content_or_return_none(fname):
	if os.path.exists(fname):
		if os.path.getsize(fname) > 0:
			f = open(fname, 'r')
			return f.read()

	return None

def	conform_string_to_filename(str):
	str = str.replace(' ', '_')
	valid_chars = "-_%s%s" % (string.ascii_letters, string.digits)
	str = ''.join(c for c in str if c in valid_chars)
	str = str.lower()
	return  str


def	safe_makedir(dirpath):
	if not os.path.exists(dirpath):
		os.makedirs(dirpath)


def	format_byte_size_to_string(byte_size):
	if byte_size != 0 and byte_size < 1024:
		byte_size = 1024

	if byte_size < 1024 * 1024:
		byte_size = str(byte_size / 1024) + ' ' + 'KB'
	else:
		byte_size = float(byte_size / 1024) / 1024.0
		byte_size = round(byte_size, 2)
		byte_size = str(byte_size) + ' ' + 'MB'
		
	return	byte_size