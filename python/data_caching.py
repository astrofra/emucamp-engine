#   Set of functions in charge of reading the data saved locally

import logging
import os

from utils import *


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
				with open(os.path.join(root, file_name), 'r', encoding='utf-8') as file_handle:
					updated_on = file_handle.read().strip()
				normalized_root = root.replace('\\', '/')
				path_parts = normalized_root.split('/')
				if len(path_parts) < 3:
					continue
				inferred_emulator_platform = path_parts[-1].replace('_', ' ').title()
				inferred_emulator_name = path_parts[-2].replace('_', ' ').title()
				inferred_machine_name = path_parts[-3].replace('_', ' ').title()
				inferred_machine_url = path_parts[-3] + '.html'

				if inferred_emulator_platform.lower().find('firmware') == -1 \
					and inferred_emulator_platform.lower().find('bios') == -1 \
					and inferred_emulator_platform.lower().find('kickstart') == -1 \
					and inferred_emulator_platform.lower().find('rom') == -1:
					emulator_list.append({'emulator_name': inferred_emulator_name, 'machine_name': inferred_machine_name,
					                      'emulator_platform': inferred_emulator_platform, 'updated_on': updated_on,
					                      'machine_url': inferred_machine_url})

	return  emulator_list
