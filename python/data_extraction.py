import os
import time
import logging
import urllib2
import urlparse
import mimetypes
import xml.etree.ElementTree as ET

from utils import *
from data_extraction import *
from globals import *
from bs4 import BeautifulSoup

def	ParseMachineFromXMLSource(machine_name):
	machine_desc_filename = source_root + machine_name + '.xml'
	if os.path.exists(machine_desc_filename):
		tree = ET.parse(machine_desc_filename)
		return tree
	else:
		logging.warning('ParseMachineFromXMLSource() cannot find file \"' + machine_desc_filename + '\"')
		return None

def	ExtractText(xml_branch, extract_local_path, file_name = 'description.txt'):
	for description_child in xml_branch:
		if (description_child.tag == 'text'):
			description_text = description_child.text
			if (description_text != None):
				description_text = description_text.strip()
				f = open(os.path.join(extract_local_path, file_name), 'w')
				f.write(description_text)
				f.close()
				return description_text
	return None
			
def	ExtractSourceURL(xml_branch, extract_local_path, file_name = 'source.url'):
	for child in xml_branch:
		if (child.tag == 'source_url'):
			source_url = child.text
			if (source_url != None):
				source_url = source_url.strip()
				f = open(os.path.join(extract_local_path, file_name), 'w')
				f.write(source_url)
				f.close()
				return source_url
	return None
			
def	DownloadEmulatorBinary(xml_branch, extract_local_path):
	print('DownloadEmulatorBinary() extract_local_path = ' + extract_local_path)
	for child in xml_branch:
		if (child.tag == 'source_url'):
			download_page_url = child.text
			if (download_page_url != None):
				print('DownloadEmulatorBinary() : download_page_url = ' + download_page_url)

				if (download_page_url.find('sourceforge.net') > -1):
					download_result = GenericBinaryDownload(download_page_url, extract_local_path, force_mime = True)
					return {	'emulator_local_filename':download_result['emulator_local_filename'], 'emulator_filename':download_result['emulator_filename'], 'emulator_size':download_result['emulator_size'], 
								'emulator_download_page':download_page_url, 'emulator_updated_on':download_result['emulator_updated_on']}

				download_page_url = download_page_url.strip()
				start_with = child.get('start_with')
				end_with = child.get('end_with')
				
				##	The url of the binary can be found by parsing the HTML page
				if ((start_with != None) and (end_with != None)):
					start_with = start_with.strip()
					end_with = end_with.strip()
					print('DownloadEmulatorBinary() found a start and end tags.')
					logging.debug('DownloadEmulatorBinary() : download_page_url = ' + download_page_url)
					logging.debug('start_with = ' + start_with)
					logging.debug('end_with = ' + end_with)
					
					urlopen_retry = 0
					while urlopen_retry < 5:
						try:
							req = urllib2.urlopen(download_page_url)
						except Exception: ##urllib2.HTTPError, e:
							logging.warning('DownloadEmulatorBinary() download_url = ' + download_page_url + ' raised an error') ## + e.msg)
							logging.warning('DownloadEmulatorBinary() urlopen_retry = ' + str(urlopen_retry))
							req = None
							time.sleep(2)
							pass
						
						urlopen_retry += 1
						
						if (req != None):
							break
			
					if (req != None):
						download_page = req.read()
						soup = BeautifulSoup(download_page)
						#	f = open(os.path.join(extract_local_path, 'download_page.html'), 'w')
						#	f.write(download_page)
						#	f.close()
			
						for link in soup.find_all('a'):
							download_url = link.get('href')
							if (download_url != None):	##	FIXME : ELSE STATEMENT IS MISSING
								logging.debug('DownloadEmulatorBinary() download_url = ' + download_url)	
								start_index = string.find(download_url, start_with)
								end_index = string.find(download_url, end_with)
								if ((start_index > -1) and (end_index > -1) and (end_index > start_index)):
									download_url = urlparse.urljoin(download_page_url, download_url)
									logging.debug('download_url = ' + download_url)
									
									download_result = GenericBinaryDownload(download_url, extract_local_path)
									return {	'emulator_local_filename':download_result['emulator_local_filename'], 'emulator_filename':download_result['emulator_filename'], 'emulator_size':download_result['emulator_size'], 
												'emulator_download_page':download_page_url, 'emulator_updated_on':download_result['emulator_updated_on']}

				##	Fallback, the binary can be downloaded directly from the url
				logging.warning('DownloadEmulatorBinary() Trying the direct URL to download the binary.')
				download_result = GenericBinaryDownload(download_page_url, extract_local_path)
				return {	'emulator_local_filename':download_result['emulator_local_filename'], 'emulator_filename':download_result['emulator_filename'], 'emulator_size':download_result['emulator_size'], 
							'emulator_download_page':download_page_url, 'emulator_updated_on':download_result['emulator_updated_on']}
			
def	GenericBinaryDownload(download_url, local_path, force_mime = False):
	print('GenericBinaryDownload() download_url = ' + download_url + ', local_path = ' + local_path)
	##	Is this an emulator binary ?
	mime = mimetypes.guess_type(download_url)
	download_type =	None

	if (force_mime or ((mime[0] != None) and (mime[0].find('application') > -1))):
		if (mime[0] != None):
			print('DownloadEmulatorBinary() : mime type = ' + mime[0])
		download_type = 'binary'
	else:
		logging.warning('GenericBinaryDownload() : mime type is unknown for url : ' + download_url)
		
	if (download_type == 'binary'):
		##	Store the download url
		f = open(os.path.join(local_path, 'binary.url'), 'w')
		f.write(download_url)
		f.close()
		
		##	Get the filename of the binary
		file_radical, file_ext = os.path.splitext(os.path.basename(urlparse.urlsplit(download_url).path))
		filename = file_radical + file_ext
		if (filename.find('.php') > -1):
			logging.warning('GenericBinaryDownload() : found a \'php\' string in the binary filename : ' + filename)
			##	The script was fooled by the request
			##	Search for the actual filename using another technique
			filename = 'Binary'
			bin_ext = '.exe'
			if (download_url.find(bin_ext) > -1):
				##	There's a binary filename inside the url
				url_split_by_dot = string.split(string.replace(string.replace(download_url, '/', '.'), '?', '.'), '.')
				extension_idx = 0
				for url_split_part in url_split_by_dot:
					logging.debug('GenericBinaryDownload() : url_split_part = ' + url_split_part)
					if url_split_part == bin_ext:
						break
					extension_idx += 1
					
				if (extension_idx > 1):
					filename = url_split_by_dot[extension_idx - 2] + bin_ext
					print('Alternate filename found : ' + filename)

		logging.debug('GenericBinaryDownload() : filename = ' + filename)

		##	Download the file
		##	Open the url
		local_filename = os.path.join(local_path, filename)
		logging.debug('GenericBinaryDownload() : download_url = ' + download_url)
		
		urlopen_retry = 0
		while urlopen_retry < 5:
			try:
				req = urllib2.urlopen(download_url)
			except Exception: ##urllib2.HTTPError, e:
				logging.warning('GenericBinaryDownload() download_url = ' + download_url + ' raised an error') ## + e.msg)
				logging.warning('GenericBinaryDownload() urlopen_retry = ' + str(urlopen_retry))
				req = None
				time.sleep(2)
				pass
			
			urlopen_retry += 1
			
			if (req != None):
				break

		if (req != None):
			##	No 404 error, we go on.
			##	Get the modification date
			url_info = req.info()
			file_date = url_info.getdate('last-modified')
			if (file_date != None):
				emulator_updated_on = str(file_date[2]) + '/' + str(file_date[1]) + '/' + str(file_date[0])
			else:
				emulator_updated_on = ' ' 

			if force_mime:
				file_url = req.geturl()
				print('req.geturl() = ' + file_url)
				filename, file_extension = os.path.splitext(os.path.basename(urlparse.urlsplit(file_url).path))
				filename = filename + file_extension
				local_filename = os.path.join(local_path, filename)
				if (local_filename[-1] == '/') or (local_filename[-1] == '\\' or (local_filename.find('.html') > -1)):
					local_filename = None

			if local_filename != None:
				print('GenericBinaryDownload() : local_filename = ' + local_filename)
		
				##	Read the bytes, chunk by chunk
				CHUNK = 128 * 1024
				byte_size = 0
				with open(local_filename, 'wb') as fp:
					while True:
						chunk = req.read(CHUNK)
						print '.',
						if not chunk:
							break
						fp.write(chunk)
						byte_size = fp.tell()
						if ((g_test_mode) and (byte_size > 16)):
							break
				print('\n')
				
				##	Get the size of the file
				byte_size = ConvertByteSizeToString(byte_size)
		
				f = open(os.path.join(local_path, 'file_size.txt'), 'w')
				f.write(byte_size)
				f.close()
					
				return {'emulator_local_filename':local_filename, 'emulator_filename':filename, 'emulator_size':byte_size, 'emulator_updated_on':emulator_updated_on}

	##	Something went wrong
	logging.warning('GenericBinaryDownload() : Cannot download ' + download_url)
	return {'emulator_local_filename':None, 'emulator_filename':None, 'emulator_size':0, 'emulator_updated_on':''}