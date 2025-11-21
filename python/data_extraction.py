# set of functions in charge of the data extraction (emulators...) from the listed web url

import logging
import time
import mimetypes
import os
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from urllib import parse, request
from urllib.error import URLError, HTTPError
import http.client as http_client

from utils import *
from globals import *
from bs4 import BeautifulSoup

USER_AGENT = 'EmuCampEngine/1.0 (+https://github.com/emucamp)'
MAX_URL_RETRIES = 5
RETRY_DELAY_SECONDS = 2


def _request_with_headers(url):
	return request.Request(url, headers={'User-Agent': USER_AGENT})


def _open_url_with_retries(url, retries=MAX_URL_RETRIES):
	last_error = None
	for attempt in range(retries):
		try:
			return request.urlopen(_request_with_headers(url))
		except (HTTPError, URLError, ValueError, http_client.RemoteDisconnected) as exc:
			last_error = exc
			logging.warning("Failed to fetch %s (attempt %s/%s): %s", url, attempt + 1, retries, exc)
			time.sleep(RETRY_DELAY_SECONDS)
	if last_error:
		logging.warning("Giving up fetching %s after %s attempts.", url, retries)
	return None


def parse_machine_from_xml_source(machine_name):
	machine_desc_filename = SOURCE_ROOT + machine_name + ".xml"
	if os.path.exists(machine_desc_filename):
		tree = ET.parse(machine_desc_filename)
		return tree
	else:
		logging.warning("ParseMachineFromXMLSource() cannot find file : " + machine_desc_filename)
		return None


def extract_text(xml_branch, extract_local_path, file_name='description.txt'):
	for description_child in xml_branch:
		if description_child.tag == 'text':
			description_text = description_child.text
			if description_text is not None:
				description_text = description_text.strip()
				with open(os.path.join(extract_local_path, file_name), 'w', encoding='utf-8') as file_handle:
					file_handle.write(description_text)
				return description_text
	return None


def extract_source_url(xml_branch, extract_local_path, file_name='source.url'):
	for child in xml_branch:
		if child.tag == 'source_url':
			source_url = child.text
			if source_url is not None:
				source_url = source_url.strip()
				with open(os.path.join(extract_local_path, file_name), 'w', encoding='utf-8') as file_handle:
					file_handle.write(source_url)
				return source_url
	return None


def download_emulator_binary(xml_branch, extract_local_path):
	print('DownloadEmulatorBinary() extract_local_path = ' + extract_local_path)
	for child in xml_branch:
		if child.tag == 'source_url':
			download_page_url = child.text
			if download_page_url is not None:
				print('DownloadEmulatorBinary() : download_page_url = ' + download_page_url)

				if download_page_url.find('sourceforge.net') != -1:
					download_result = generic_binary_download(download_page_url, extract_local_path, force_mime=True)
					return {'emulator_local_filename': download_result['emulator_local_filename'],
					        'emulator_filename': download_result['emulator_filename'],
					        'emulator_size': download_result['emulator_size'],
					        'emulator_download_page': download_page_url,
					        'emulator_updated_on': download_result['emulator_updated_on']}

				download_page_url = download_page_url.strip()
				start_with = child.get('start_with')
				end_with = child.get('end_with')

				##	The url of the binary can be found by parsing the HTML page
				if start_with is not None and end_with is not None:
					start_with = start_with.strip()
					end_with = end_with.strip()
					print('DownloadEmulatorBinary() found a start and end tags.')
					logging.debug('DownloadEmulatorBinary() : download_page_url = ' + download_page_url)
					logging.debug('start_with = ' + start_with)
					logging.debug('end_with = ' + end_with)

					req = _open_url_with_retries(download_page_url)

					if req is not None:
						download_page = req.read()
						soup = BeautifulSoup(download_page, 'html.parser')
						#	f = open(os.path.join(extract_local_path, 'download_page.html'), 'w')
						#	f.write(download_page)
						#	f.close()

						for link in soup.find_all('a'):
							download_url = link.get('href')
							if download_url is not None:
								logging.debug('DownloadEmulatorBinary() download_url = ' + download_url)
								start_index = download_url.find(start_with)
								end_index = download_url.find(end_with)
								if end_index > start_index > -1:
									download_url = parse.urljoin(download_page_url, download_url)
									logging.debug('download_url = ' + download_url)

									download_result = generic_binary_download(download_url, extract_local_path)
									return {	'emulator_local_filename':download_result['emulator_local_filename'],
									            'emulator_filename':download_result['emulator_filename'],
									            'emulator_size':download_result['emulator_size'],
												'emulator_download_page':download_page_url,
												'emulator_updated_on':download_result['emulator_updated_on']}

				##	Fallback, the binary can be downloaded directly from the url
				logging.warning('DownloadEmulatorBinary() Trying the direct URL to download the binary.')
				download_result = generic_binary_download(download_page_url, extract_local_path)
				return {	'emulator_local_filename':download_result['emulator_local_filename'], 'emulator_filename':download_result['emulator_filename'], 'emulator_size':download_result['emulator_size'],
							'emulator_download_page':download_page_url, 'emulator_updated_on':download_result['emulator_updated_on']}


def generic_binary_download(download_url, local_path, force_mime = False):
	print('GenericBinaryDownload() download_url = ' + download_url + ', local_path = ' + local_path)
	##	Is this an emulator binary ?
	mime = mimetypes.guess_type(download_url)
	download_type = None

	if force_mime or (mime[0] is not None and mime[0].find('application') > -1):
		if mime[0] is not None:
			print('DownloadEmulatorBinary() : mime type = ' + mime[0])
		download_type = 'binary'
	else:
		logging.warning('GenericBinaryDownload() : mime type is unknown for url : ' + download_url)

	if local_path.lower().find('javascript') == -1 and download_type == 'binary':
		##	Store the download url
		with open(os.path.join(local_path, 'binary.url'), 'w', encoding='utf-8') as file_handle:
			file_handle.write(download_url)

		#	Get the filename of the binary
		file_radical, file_ext = os.path.splitext(os.path.basename(parse.urlsplit(download_url).path))
		filename = file_radical + file_ext
		if filename.find('.php') > -1:
			logging.warning('GenericBinaryDownload() : found a \'php\' string in the binary filename : ' + filename)
			##	The script was fooled by the request
			##	Search for the actual filename using another technique
			filename = 'Binary'
			bin_ext = '.exe'
			for bin_ext in ['.exe', '.zip', '.rar', '.dmg', '.gz', '.deb', '.lha', '.bin', '.prg', '.apk']:
				if download_url.find(bin_ext) > -1:
					##	There's a binary filename inside the url
					url_split_by_dot = download_url.replace('/', '.').replace('?', '.').split('.')
					extension_idx = 0
					for url_split_part in url_split_by_dot:
						logging.debug('GenericBinaryDownload() : url_split_part = ' + url_split_part)
						if url_split_part == bin_ext:
							break
						extension_idx += 1

					if extension_idx > 1:
						filename = url_split_by_dot[extension_idx - 2] + bin_ext
						print('Alternate filename found : ' + filename)
						break

		filename = filename.replace('%20', ' ')

		logging.debug('GenericBinaryDownload() : filename = ' + filename)

		##	Download the file
		##	Open the url
		local_filename = os.path.join(local_path, filename)
		logging.debug('GenericBinaryDownload() : download_url = ' + download_url)

		req = _open_url_with_retries(download_url)

		if req is not None:
			##	No 404 error, we go on.
			##	Get the modification date
			header_date = req.headers.get('Last-Modified')
			emulator_updated_on = ' '
			if header_date:
				try:
					emulator_updated_on = parsedate_to_datetime(header_date).strftime('%Y-%m-%d')
				except (TypeError, ValueError):
					emulator_updated_on = ' '

			if force_mime:
				file_url = req.geturl()
				print('req.geturl() = ' + file_url)
				filename, file_extension = os.path.splitext(os.path.basename(parse.urlsplit(file_url).path))
				filename += file_extension
				local_filename = os.path.join(local_path, filename)
				if (local_filename[-1] == '/') or (local_filename[-1] == '\\' or (local_filename.find('.html') > -1)):
					local_filename = None

			if local_filename is not None:
				print('GenericBinaryDownload() : local_filename = ' + local_filename)

				##	Read the bytes, chunk by chunk
				CHUNK = 128 * 1024
				byte_size = 0
				with open(local_filename, 'wb') as fp:
					while True:
						chunk = req.read(CHUNK)
						print('.', end='', flush=True)
						if not chunk:
							break
						fp.write(chunk)
						byte_size = fp.tell()
						if G_TEST_MODE and byte_size > 16:
							break
				print('\n')

				##	Store the download url
				if (len(filename) > 0):
					if filename.find('.htm') == -1 and filename.find('.php') == -1 and filename.find('.cgi') == -1:
						with open(os.path.join(local_path, 'binary_filename.txt'), 'w', encoding='utf-8') as file_handle:
							file_handle.write(filename)

				##	Get the size of the file
				byte_size = format_byte_size_to_string(byte_size)

				with open(os.path.join(local_path, 'file_size.txt'), 'w', encoding='utf-8') as file_handle:
					file_handle.write(byte_size)

				if emulator_updated_on != ' ':
					with open(os.path.join(local_path, 'updated_on.txt'), 'w', encoding='utf-8') as file_handle:
						file_handle.write(emulator_updated_on)

				return {'emulator_local_filename': local_filename, 'emulator_filename': filename, 'emulator_size': byte_size, 'emulator_updated_on': emulator_updated_on}

	##	Something went wrong
	logging.warning('GenericBinaryDownload() : Cannot download ' + download_url)
	return {'emulator_local_filename':None, 'emulator_filename':None, 'emulator_size':0, 'emulator_updated_on':''}
