import datetime
import xmltodict
import os
import codecs
import logging

from globals import *


def build_machine_timeline(_machine_list):

	logging.info('build_machine_timeline() : _machine_list contains ' + str(len(_machine_list)) + ' elements.')

	machine_dict_array = []
	first_release_date = datetime.date.today().year
	last_discontinued_date = 0

	##  Parse the XML file of each machine
	for machine_name in _machine_list:
		machine_desc_filename = SOURCE_ROOT + machine_name + ".xml"
		if os.path.exists(machine_desc_filename):
				f = codecs.open(machine_desc_filename, 'r', encoding = 'utf-8')
				machine_xml_buffer = f.read()
				machine_dict_array.append(xmltodict.parse(machine_xml_buffer))


	# print(machine_dict_array[0])
	for machine_dict in machine_dict_array:
		machine = machine_dict['data']['machine']
		machine_full_name = machine['@name']

		if '@release_date' in machine:
			if first_release_date > int(machine['@release_date']):
				first_release_date = int(machine['@release_date'])

			if '@discontinued' in machine:
				if last_discontinued_date < int(machine['@discontinued']):
					last_discontinued_date = int(machine['@discontinued'])
			else:
				if last_discontinued_date < datetime.date.today().year:
					last_discontinued_date = datetime.date.today().year

	print('build_machine_timeline() : first_release_date = ' + str(first_release_date))
	print('build_machine_timeline() : last_discontinued_date = ' + str(last_discontinued_date))

	# crawl every year and search for a machine introduction / discontinuation

	for _year in range(first_release_date, last_discontinued_date):
		current_row = []
		for machine_dict in machine_dict_array:
			machine = machine_dict['data']['machine']
			# machine_full_name = machine['@name']
			release_date = -1
			discontinued_date = -1
			# if the period of activity is available for this machine
			if '@release_date' in machine:
				release_date = int(machine['@release_date'])
				if '@discontinued' in machine:
					discontinued_date = int(machine['@discontinued'])
				else:
					discontinued_date = datetime.date.today().year

			if discontinued_date > release_date > -1:
				# if this machine was active this year
				if release_date <= _year <= discontinued_date:
					machine_already_in_row = False
					for machine_in_current_row in current_row:
						if machine_dict['data']['machine']['@name'] == machine_in_current_row['data']['machine']['@name']:
							machine_already_in_row = True
							break

					if not machine_already_in_row:
						current_row.append(machine_dict)

		# sum up the selected machines for this year
		_str = ''
		for current_machine in current_row:
			_str += current_machine['data']['machine']['@name'] + ','

		print('Year ' + str(_year) + ' : ' + _str)