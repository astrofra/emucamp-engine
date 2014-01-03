##	Emucamp-Engine

import os
import shutil
import logging
import urllib2
import urlparse
import mimetypes
import xml.etree.ElementTree as ET
import wikipedia

from utils import *
from data_extraction import *
from globals import *
from bs4 import BeautifulSoup
from quik import FileLoader

##-------------------------
##	Start to build the site
##-------------------------

def	InitMimeDetection():
	mimetypes.init()
	mimetypes.add_type('application/x-debian', '.deb')
	mimetypes.add_type('application/x-windows', '.msi')
	mimetypes.add_type('application/x-amigaos', '.lha')
	mimetypes.add_type('application/x-amigaos', '.lzx')
	mimetypes.add_type('application/x-osx', '.dmg')

def	MainEmucampEngine():

	logging.info('Emucamp-Engine')
	
	##	Copy the Twitter Boostrap to the www root
	for resource_folder in resources_folders:
		extern_dest = os.path.join(site_root, resource_folder)
		if os.path.exists(extern_dest):
			shutil.rmtree(extern_dest)
		shutil.copytree(os.path.join(resources_root, resource_folder), extern_dest)

	##	Initialize the mime type for further detection
	InitMimeDetection()
	
	##	Initialize the template handler (Quik)
	quik_loader = FileLoader(resources_root)
	
	##	Initialize misc variables
	machine_name = ''
	
	for machine_name in machine_list:
		tree = ParseMachineFromXMLSource(machine_name)
		if (tree != None):
			root = tree.getroot()
			if (root.tag == 'data'):
				for child in root:
					logging.debug('child.tag = ' + child.tag)
					##	Look for a 'machine'
					if (child.tag == 'machine'):
						machine = child
						machine_name = machine.get('name')
						machine_type = machine.get('type')
						print('Found this machine : ' + machine_name)
						print('-------------------------------------')
						##	Creates a new html template
						template_machine = quik_loader.load_template(input_pages['machine'])
						
						quik_interface['machine_name'] = machine_name
						quik_interface['machine_filename'] = ConformStringToFilename(machine_name)
						quik_interface['emulator_list'] = []
						
						##	Creates the folder to store the machine's data
						machine_root_path = os.path.join(site_root, ConformStringToFilename(machine_name))
						SafeMakedir(machine_root_path)
						
						found_a_description = False
						
						for machine_child in machine:
							##	Is this the description of the machine ?
							if (machine_child.tag == 'description'):
								quik_interface['machine_description'] = ExtractText(machine_child, machine_root_path)
								quik_interface['machine_description_source_url'] = ExtractSourceURL(machine_child, machine_root_path)
								quik_interface['machine_description_source'] = quik_interface['machine_description_source_url']
								found_a_description = True
	
							##	Is this an emulator for this machine ?
							if (machine_child.tag == 'emulator'):
								emulator = machine_child
								
								##	What is the name of this emulator
								emulator_name = emulator.get('name')
								
								emulator_root_path = os.path.join(machine_root_path, ConformStringToFilename(emulator_name))
								SafeMakedir(emulator_root_path)
								
								current_emulator = {	'name':emulator_name, 'emulator_description':None, 
														'emulator_version_list':[]	}
								
								##	Is this an emulator for this machine
								for emulator_child in emulator:
									##	Is this the description of this emulator ?
									if (emulator_child.tag == 'description'):
										current_emulator['emulator_description'] = ExtractText(emulator_child, emulator_root_path)
										current_emulator['emulator_description_source_url'] = ExtractSourceURL(emulator_child, emulator_root_path)
										current_emulator['emulator_description_source'] = current_emulator['emulator_description_source_url']
										
									if (emulator_child.tag == 'platform'):
										platform = emulator_child
										platform_name = platform.get('name')
										print(emulator_name + ', found a version for the ' + platform_name + ' platform.')
										
										platform_root_path = os.path.join(emulator_root_path, ConformStringToFilename(platform_name))
										SafeMakedir(platform_root_path)
										ExtractSourceURL(platform, platform_root_path, 'download_page.url')
										
										##	Tries to download the binary
										download_result = DownloadEmulatorBinary(platform, platform_root_path)
										if (download_result['emulator_local_filename'] != None):
											emulator_download_url = ConformStringToFilename(machine_name) + '/' +  ConformStringToFilename(emulator_name) + '/' + ConformStringToFilename(platform_name) + '/' + download_result['emulator_filename']
										else:
											emulator_download_url = None
										
										(current_emulator['emulator_version_list']).append({'emulator_platform':platform_name, 
																							'emulator_filename':download_result['emulator_filename'],
																							'emulator_download_url':emulator_download_url,
																							'emulator_size':download_result['emulator_size'],
																							'emulator_download_page':download_result['emulator_download_page'],
																							'emulator_download_page_truncated':urlparse.urlsplit(download_result['emulator_download_page']).netloc,
																							'emulator_updated_on':download_result['emulator_updated_on']
																							})
										
								(quik_interface['emulator_list']).append(current_emulator)
								
						if not(found_a_description):
							try:
								wiki_page = wikipedia.page(machine_name)
								quik_interface['machine_description'] = wikipedia.summary(machine_name, sentences = 3)
								quik_interface['machine_description_source_url'] = wiki_page.url
								quik_interface['machine_description_source'] = wiki_page.url
							except wikipedia.exceptions.DisambiguationError as e:
								print e.options
								quik_interface['machine_description'] = "No description found :'("
								quik_interface['machine_description_source_url'] = ""
								quik_interface['machine_description_source'] = ""
								pass										
							
						##	Creates the new 'machine' page
						##	Render the new html page
						html_output = template_machine.render(quik_interface, quik_loader).encode('utf-8')
						##	Saves the page as a html file
						f = open(os.path.join(site_root, ConformStringToFilename(machine_name) + '.html'), 'w')
						f.write(html_output)
						f.close()
						
						(quik_interface['machine_list'][machine_type.lower()]).append({'name':machine_name, 'page_url':ConformStringToFilename(machine_name) + '.html'})
						
						print('-------------------------------------')
						
	
	##	Builds the main index
	if ((g_create_index) and (len(machine_list) > 0)):
		template_index = quik_loader.load_template(input_pages['index'])
		html_output = template_index.render(quik_interface, quik_loader).encode('utf-8')
		f = open(os.path.join(site_root, 'index.html'), 'w')
		f.write(html_output)
		f.close()
		
	##	Builds the about page
	template_about = quik_loader.load_template(input_pages['about'])
	html_output = template_about.render(quik_interface, quik_loader).encode('utf-8')
	f = open(os.path.join(site_root, 'about.html'), 'w')
	f.write(html_output)
	f.close()
			
	##	soup = BeautifulSoup(html_doc)
			
MainEmucampEngine()
		