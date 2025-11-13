##	Utils

import os
import string

def read_text_content_or_return_none(fname):
	if os.path.exists(fname) and os.path.getsize(fname) > 0:
		with open(fname, 'r', encoding='utf-8') as file_handle:
			return file_handle.read()
	return None


def	conform_string_to_filename(value):
	value = value.replace(' ', '_')
	valid_chars = "-_%s%s" % (string.ascii_letters, string.digits)
	value = ''.join(c for c in value if c in valid_chars)
	return value.lower()


def	safe_makedir(dirpath):
	os.makedirs(dirpath, exist_ok=True)


def	format_byte_size_to_string(byte_size):
	try:
		byte_size = int(byte_size)
	except (TypeError, ValueError):
		byte_size = 0
	if byte_size != 0 and byte_size < 1024:
		byte_size = 1024

	if byte_size < 1024 * 1024:
		return str(byte_size // 1024) + ' KB'

	byte_size = byte_size / 1024.0 / 1024.0
	byte_size = round(byte_size, 2)
	return str(byte_size) + ' MB'
