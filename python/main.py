##	Emucamp-Engine

import shutil
import logging
import wikipedia
import datetime
import codecs

from utils import *
from data_extraction import *
from globals import *
from pouet_bridge import machine_get_pouet_prods
from binary_downloader import better_binary_download

from quik import FileLoader
from data_caching import *
from operator import itemgetter
from machine_timeline import build_machine_timeline



##-------------------------
##	Start to build the site
##-------------------------


def init_mime_detection():
	mimetypes.init()
	mimetypes.add_type('application/x-debian', '.deb')
	mimetypes.add_type('application/x-windows', '.msi')
	mimetypes.add_type('application/x-amigaos', '.lha')
	mimetypes.add_type('application/x-amigaos', '.lzx')
	mimetypes.add_type('application/x-osx', '.dmg')
	mimetypes.add_type('application/x-android', '.apk')


def main_emucamp_engine():
	logging.info('Emucamp-Engine')

	##	Copy the Twitter Boostrap to the www root
	for resource_folder in RESOURCES_FOLDERS:
		extern_dest = os.path.join(SITE_ROOT, resource_folder)
		if os.path.exists(extern_dest):
			shutil.rmtree(extern_dest)
		shutil.copytree(os.path.join(RESOURCES_ROOT, resource_folder), extern_dest)

	##	Initialize the mime type for further detection
	init_mime_detection()

	##	Initialize the template handler (Quik)
	quik_loader = FileLoader(RESOURCES_ROOT)

	##	Main 'machines' loop
	if len(machine_update_only) > 0:
		download_machine_list = machine_update_only
	else:
		download_machine_list = machine_list

	for machine_short_name in download_machine_list:
		tree = parse_machine_from_xml_source(machine_short_name)
		if tree is not None:
			root = tree.getroot()
			if root.tag == 'data':
				for child in root:
					logging.debug('child.tag = ' + child.tag)
					##	Look for a 'machine'
					if child.tag == 'machine':
						machine = child
						machine_name = machine.get('name')
						machine_type = machine.get('type')
						print('Found this machine : ' + machine_name)
						print('-------------------------------------')
						##	Creates a new html template
						template_machine = quik_loader.load_template(INPUT_PAGES['machine'])

						quik_interface['machine_name'] = machine_name
						quik_interface['machine_filename'] = conform_string_to_filename(machine_name)
						quik_interface['emulator_list'] = []

						##	Creates the folder to store the machine's data
						machine_root_path = os.path.join(SITE_ROOT, conform_string_to_filename(machine_name))
						safe_makedir(machine_root_path)

						found_a_description = False

						for machine_child in machine:
							##	Is this the description of the machine ?
							if machine_child.tag == 'description':
								quik_interface['machine_description'] = extract_text(machine_child, machine_root_path)
								quik_interface['machine_description_source_url'] = extract_source_url(machine_child, machine_root_path)
								quik_interface['machine_description_source'] = quik_interface['machine_description_source_url']
								found_a_description = True

							##	Is this an emulator for this machine ?
							if machine_child.tag == 'emulator':
								emulator = machine_child

								##	What is the name of this emulator
								emulator_name = emulator.get('name')

								emulator_root_path = os.path.join(machine_root_path, conform_string_to_filename(emulator_name))
								safe_makedir(emulator_root_path)

								current_emulator = {	'name': emulator_name, 'emulator_description': None,
														'emulator_version_list':[]	}

								##	Is this an emulator for this machine
								for emulator_child in emulator:
									##	Is this the description of this emulator ?
									if emulator_child.tag == 'description':
										current_emulator['emulator_description'] = extract_text(emulator_child, emulator_root_path)
										current_emulator['emulator_description_source_url'] = extract_source_url(emulator_child, emulator_root_path)
										current_emulator['emulator_description_source'] = current_emulator['emulator_description_source_url']

									if emulator_child.tag == 'platform':
										platform = emulator_child
										platform_name = platform.get('name')
										print(emulator_name + ', found a version for the ' + platform_name + ' platform.')

										platform_root_path = os.path.join(emulator_root_path, conform_string_to_filename(platform_name))
										safe_makedir(platform_root_path)
										extract_source_url(platform, platform_root_path, 'download_page.url')

										##	Tries to download the binary
										download_result = download_emulator_binary(platform, platform_root_path)

										##  If the previous method failed, try another technique
										if download_result['emulator_local_filename'] is None:
											for platform_child in platform:
												if platform_child.tag == 'source_url':
													download_page_url = platform_child.text
													if download_page_url is not None:
														print('DownloadEmulatorBinary() : download_page_url = ' + download_page_url)
														download_page_url = download_page_url.strip()
														start_with = child.get('start_with')
														end_with = child.get('end_with')
														download_result = better_binary_download({'machine':  {'short_name': machine_short_name, 'name': machine_name },
																			                        'emulator': {'name': emulator_name,},
																			                        'platform': {'name': platform_name, 'root_path': platform_root_path   },
																			                        'url':      {'download_page': download_page_url, 'start': start_with, 'end': end_with}})

										if download_result['emulator_local_filename'] is not None:
											emulator_download_url = conform_string_to_filename(machine_name) + '/' +  conform_string_to_filename(emulator_name) + '/' + conform_string_to_filename(platform_name) + '/' + download_result['emulator_filename']
										else:
											##  Fetch the previous binary from local disk
											previous_download_result = fetch_previous_binary_from_disk(platform, platform_root_path)
											if previous_download_result is not None:    ## UNFINISHED
												download_result['emulator_filename'] = previous_download_result['emulator_filename']
												download_result['emulator_size'] = previous_download_result['emulator_size']
												# download_result['emulator_download_page'] = '' ## previous_download_result['emulator_download_page']
												emulator_download_url = platform_root_path + '/' + previous_download_result['emulator_filename']
												download_result['emulator_updated_on'] = previous_download_result['emulator_updated_on']
											else:
												emulator_download_url = None

										(current_emulator['emulator_version_list']).append({'emulator_platform':platform_name,
																							'emulator_filename': download_result['emulator_filename'],
																							'emulator_download_url': emulator_download_url,
																							'emulator_size': download_result['emulator_size'],
																							'emulator_download_page': download_result['emulator_download_page'],
																							'emulator_download_page_truncated': urlparse.urlsplit(download_result['emulator_download_page']).netloc,
																							'emulator_updated_on': download_result['emulator_updated_on']
																							})

								(quik_interface['emulator_list']).append(current_emulator)

						##  Get the description of the machine
						if not found_a_description:
							try:
								wiki_page = wikipedia.page(machine_name)
								quik_interface['machine_description'] = wikipedia.summary(machine_name, sentences = 3) ##.encode('utf-8')
								quik_interface['machine_description_source_url'] = wiki_page.url
								quik_interface['machine_description_source'] = wiki_page.url
							except Exception: ##wikipedia.exceptions.DisambiguationError as e:
								##  print e.options
								quik_interface['machine_description'] = "No description found :'("
								quik_interface['machine_description_source_url'] = ""
								quik_interface['machine_description_source'] = ""
								pass

						##  Connect to Pouet and see if there's any prod (game, demo) to download
						print('----------------------------------------------------------------------')
						print('Connect to Pouet and see if there is any prod (game, demo) to download')
						# machine_get_pouet_prods(machine_short_name)
						print('----------------------------------------------------------------------')

						print('----------------------------')
						print('Creates the new machine page')
						##	Creates the new 'machine' page
						##	Render the new html page
						html_output = template_machine.render(quik_interface, quik_loader) ##.encode('utf-8')
						##	Saves the page as a html file
						f = codecs.open(os.path.join(SITE_ROOT, conform_string_to_filename(machine_name) + '.html'), 'w', 'utf-8')
						f.write(html_output)
						f.close()

						print('------------------------------')

	##
	## index.html
	##
	##	Builds the main index
	##  Loop through the whole list of machine
	for machine_name in machine_list:
		tree = parse_machine_from_xml_source(machine_name)
		if tree is not None:
			root = tree.getroot()
			if root.tag == 'data':
				for child in root:
					logging.debug('child.tag = ' + child.tag)
					##	Look for a 'machine'
					if child.tag == 'machine':
						machine = child
						machine_name = machine.get('name')
						machine_type = machine.get('type')

						machine_site_path = os.path.join(SITE_ROOT, conform_string_to_filename(machine_name))
						if os.path.exists(machine_site_path):
							##  Add this machine into the main list
							(quik_interface['machine_list'][machine_type.lower()]).append({'name': machine_name, 'page_url': conform_string_to_filename(machine_name) + '.html'})
							##  Fetch the latest downloaded emulators
							tmp_emulator_update_list = cache_fetch_emulators_update(machine_site_path)
							for _update in tmp_emulator_update_list:
								quik_interface['emulator_update_list'].append(_update)

	##  Generates the Index page based on the whole list
	if G_CREATE_INDEX and len(machine_list) > 0:

		##  Sort the list of updates by date.
		if len(quik_interface['emulator_update_list']) > 0:
			sorted_emulator_update_list = sorted(quik_interface['emulator_update_list'], key = itemgetter('updated_on'), reverse = True)
			quik_interface['emulator_update_list'] = sorted_emulator_update_list[0:5]
			quik_interface['emulator_full_update_list'] = sorted_emulator_update_list

			for _year in range(datetime.date.today().year + 1, 1970, -1):
				year_list = []
				for emu_update in sorted_emulator_update_list:
					if emu_update['updated_on'].find(str(_year)) != -1:
						# print(emu_update['updated_on'])
						year_list.append(emu_update)

				if len(year_list) > 0:
					logging.info('emulator_full_update_list_by_year[] : found ' + str(len(year_list)) + ' emulators.')
					quik_interface['emulator_full_update_list_by_year'].append({'year':_year, 'update_list':year_list})

		template_index = quik_loader.load_template(INPUT_PAGES['index'])
		html_output = template_index.render(quik_interface, quik_loader).encode('utf-8')
		f = codecs.open(os.path.join(SITE_ROOT, 'index.html'), 'w', 'utf-8')
		f.write(html_output)
		f.close()

		template_index = quik_loader.load_template(INPUT_PAGES['update_log'])
		html_output = template_index.render(quik_interface, quik_loader).encode('utf-8')
		f = codecs.open(os.path.join(SITE_ROOT, 'update_log.html'), 'w', 'utf-8')
		f.write(html_output)
		f.close()

	##
	## about.html
	##
	##	Builds the about page
	template_about = quik_loader.load_template(INPUT_PAGES['about'])
	html_output = template_about.render(quik_interface, quik_loader).encode('utf-8')
	f = codecs.open(os.path.join(SITE_ROOT, 'about.html'), 'w', 'utf-8')
	f.write(html_output)
	f.close()

	##
	## timeline
	# build_machine_timeline(machine_list)

	##	soup = BeautifulSoup(html_doc)

# If the script is not imported, execute the main function
if __name__ == "__main__":
	main_emucamp_engine()
