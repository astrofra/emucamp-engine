#   Set of functions in charge of reading the data saved locally

from utils import *
import string
import os
import logging

def fetch_previous_binary_from_disk(platform, platform_root_path):
	logging.warning('fetch_previous_binary_from_disk() platform_root_path = ' + platform_root_path)
	download_result = None
	binary_filename = read_text_content_or_return_none(os.path.join(platform_root_path, 'binary_filename.txt'))
	if binary_filename is not None:
		download_result = {'emulator_updated_on':read_text_content_or_return_none(os.path.join(platform_root_path, 'updated_on.txt')),
		                   'emulator_size':read_text_content_or_return_none(os.path.join(platform_root_path, 'file_size.txt')),
		                   'emulator_filename':binary_filename
		}

	return  download_result

def cache_fetch_emulators_update(machine_site_path):
	logging.info('cache_fetch_emulators_update() path = ' + machine_site_path)
	emulator_list = []
	for root, sub_folders, files in os.walk(machine_site_path):
		for file_name in files:
			if file_name == 'updated_on.txt':
				f = open(os.path.join(root, file_name), 'r')
				updated_on = str(f.read())
				inferred_emulator_platform = root.replace('\\', '/').split('/')[-1]
				inferred_emulator_platform = inferred_emulator_platform.replace('_', ' ')
				inferred_emulator_platform = inferred_emulator_platform.title()

				inferred_emulator_name = root.replace('\\', '/').split('/')[-2]
				inferred_emulator_name = inferred_emulator_name.replace('_', ' ')
				inferred_emulator_name = inferred_emulator_name.title()

				inferred_machine_name = root.replace('\\', '/').split('/')[-3]
				inferred_machine_name = inferred_machine_name.replace('_', ' ')
				inferred_machine_name = inferred_machine_name.title()

				inferred_machine_url = root.replace('\\', '/').split('/')[-3]
				inferred_machine_url += '.html'

				if inferred_emulator_platform.lower().find('firmware') == -1 \
					and inferred_emulator_platform.lower().find('bios') == -1 \
					and inferred_emulator_platform.lower().find('kickstart') == -1 \
					and inferred_emulator_platform.lower().find('rom') == -1:
					emulator_list.append({'emulator_name': inferred_emulator_name, 'machine_name': inferred_machine_name,
					                      'emulator_platform': inferred_emulator_platform, 'updated_on': updated_on,
					                      'machine_url': inferred_machine_url})

	return  emulator_list