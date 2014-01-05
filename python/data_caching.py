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
				inferred_emulator_platform = inferred_emulator_platform[0].upper() + inferred_emulator_platform[1:]

				inferred_emulator_name = string.replace(root, '\\', '/').split('/')[-2]
				inferred_emulator_name = string.replace(inferred_emulator_name, '_', ' ')
				inferred_emulator_name = inferred_emulator_name[0].upper() + inferred_emulator_name[1:]

				emulator_list.append({'emulator_name': inferred_emulator_name, 'emulator_platform': inferred_emulator_platform, 'updated_on': updated_on})

	return  emulator_list