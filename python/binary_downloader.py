##

import logging
import os
import shutil
import time
from email.utils import parsedate_to_datetime
from urllib import request

import wget

from utils import *
from globals import *

USER_AGENT = 'EmuCampEngine/1.0 (+https://github.com/emucamp)'


def _open_with_user_agent(url):
	opener = request.build_opener()
	opener.addheaders = [('User-agent', USER_AGENT)]
	return opener.open(url)

def better_binary_download(req):
	logging.warning('better_binary_download() : download_page = ' + req['url']['download_page'])
	return_dict = {'emulator_local_filename': None,
					'emulator_filename': None,
					'emulator_size': None,
					'emulator_download_page': req['url']['download_page'],
					'emulator_updated_on': ' '}

	if req['url']['start'] is None and req['url']['end'] is None:
		if req['url']['download_page'].lower().find('cgi?') > -1:
			local_filename = wget.download(req['url']['download_page'])
			print("local_filename = " + local_filename)
			target_filename = local_filename

			##  wget could not find the proper name for this file
			##  infer the file from and urllib2 request (url)
			if target_filename.find('.cgi') > -1:
				response = _open_with_user_agent(req['url']['download_page'])
				try:
					target_filename = response.url.split('/')[-1].split('#')[0].split('?')[0]
				finally:
					response.close()

			##  previous method could not find the proper name for this file
			##  infer the file from and urllib2 request (filetype found in the header)
			if target_filename.find('.cgi') > -1:
				response = _open_with_user_agent(req['url']['download_page'])
				try:
					file_ext = guess_file_extension_from_header(response.headers.get_content_type())
				finally:
					response.close()
				if file_ext is not None:
					target_filename = conform_string_to_filename(req['emulator']['name']) + file_ext

			if target_filename.find('.cgi') < 0:

				##  Check file size
				byte_size = os.path.getsize(local_filename)

				##  If the file has an acceptable size (at least 10KB)
				if byte_size > 1024 * 10:

					##  Check modified date
					response = _open_with_user_agent(req['url']['download_page'])
					try:
						header_date = response.headers.get('Last-Modified')
					finally:
						response.close()

					file_date = ' '
					if header_date:
						try:
							file_date = parsedate_to_datetime(header_date).strftime("%Y-%b-%d")
						except (TypeError, ValueError):
							file_date = ' '

					##  copy the binary from the temp folder to the final folder
					shutil.copy(local_filename, os.path.join(req['platform']['root_path'], target_filename))

					##	Store the size
					byte_size = format_byte_size_to_string(byte_size)
					with open(os.path.join(req['platform']['root_path'], 'file_size.txt'), 'w', encoding='utf-8') as file_handle:
						file_handle.write(byte_size)

					##	Store the filename
					with open(os.path.join(req['platform']['root_path'], 'binary_filename.txt'), 'w', encoding='utf-8') as file_handle:
						file_handle.write(target_filename)

					if file_date != ' ':
						with open(os.path.join(req['platform']['root_path'], 'updated_on.txt'), 'w', encoding='utf-8') as file_handle:
							file_handle.write(file_date)

					os.remove(local_filename)

					return_dict['emulator_local_filename'] = os.path.join(req['platform']['root_path'], target_filename)
					return_dict['emulator_filename'] = target_filename
					return_dict['emulator_size'] = byte_size
					return_dict['emulator_updated_on'] = file_date

	return return_dict


def guess_file_extension_from_header(_header):

	if _header.find('application/x-apple-diskimage') > -1:
		return '.dmg'
	if _header.find('application/x-bzip2') > -1:
		return '.bz2'
	if _header.find('application/x-gzip') > -1:
		return '.gz'
	if _header.find('application/x-lzip') > -1:
		return '.lz'
	if _header.find('application/x-lzma') > -1:
		return '.lzma'
	if _header.find('application/x-7z-compressed') > -1:
		return '.7z'
	if _header.find('application/vnd.android.package-archive') > -1:
		return '.apk'
	if _header.find('application/x-lzh') > -1:
		return '.lha'
	if _header.find('application/vnd.ms-cab-compressed') > -1:
		return '.cab'
	if _header.find('application/x-lzx') > -1:
		return '.lzx'
	if _header.find('application/x-rar-compressed') > -1:
		return '.rar'
	if _header.find('application/x-stuffitx') > -1:
		return '.sitx'
	if _header.find('application/x-gtar') > -1:
		return '.tar.gz'
	if _header.find('application/x-tar') > -1:
		return '.tar'
	if _header.find('application/zip') > -1:
		return '.zip'

	return None
