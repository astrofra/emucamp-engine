#   Set of functions in charge of reading the data saved locally

import string
import os
import logging


def cache_fetch_emulators_update(machine_site_path):
	logging.info('cache_fetch_emulators_update() path = ' + machine_site_path)
	emulator_list = []
	for root, sub_folders, files in os.walk(machine_site_path):
		for file_name in files:
			if file_name == 'updated_on.txt':
				f = open(os.path.join(root, file_name), 'r')
				updated_on = str(f.read())
				inferred_emulator_platform = string.replace(root, '\\', '/').split('/')[-1]
				inferred_emulator_platform = string.replace(inferred_emulator_platform, '_', ' ')
				inferred_emulator_platform = inferred_emulator_platform.title()

				inferred_emulator_name = string.replace(root, '\\', '/').split('/')[-2]
				inferred_emulator_name = string.replace(inferred_emulator_name, '_', ' ')
				inferred_emulator_name = inferred_emulator_name.title()

				inferred_machine_name = string.replace(root, '\\', '/').split('/')[-3]
				inferred_machine_name = string.replace(inferred_machine_name, '_', ' ')
				inferred_machine_name = inferred_machine_name.title()

				inferred_machine_url = string.replace(root, '\\', '/').split('/')[-3]
				inferred_machine_url += '.html'

				if inferred_emulator_platform.lower().find('firmware') == -1 \
					and inferred_emulator_platform.lower().find('bios') == -1 \
					and inferred_emulator_platform.lower().find('kickstart') == -1 \
					and inferred_emulator_platform.lower().find('rom') == -1:
					emulator_list.append({'emulator_name': inferred_emulator_name, 'machine_name': inferred_machine_name,
					                      'emulator_platform': inferred_emulator_platform, 'updated_on': updated_on,
					                      'machine_url': inferred_machine_url})

	return  emulator_list