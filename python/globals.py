source_root			= 'sources/'
site_root			= '../www/'
machine_list		= sorted([	'cbm_amiga',
								'google_android', 'amstrad_cpc', 'nintendo_snes', 'pc_ms-dos', 'nintendo_gameboy', 'sega_mastersystem-gamegear', 
								'atari_lynx', 'msx', 'thomson_mo_to', 'atari_800xl', 'nec_pc_engine', 'arcade', 'vectrex', 'sinclair_ql', 
								'sinclair_spectrum', 'snk_neogeo', 'acorn_archimedes', 'cbm_64', 'atari_st', 'sega_megadrive', 'nintendo_nes'
								])

resources_root		= 'resources'
resources_folders	= ['assets', 'extern']

g_test_mode			= False
g_create_index		= True

input_pages			= {'machine':'template_machine.html', 'index':'template_index.html', 'about':'about.html'	}
output_pages		= {'machine':{}	}

quik_interface		= {	'machine_name':None, 'machine_filename':None, 'machine_type':None, 'machine_description_source_url':None, 'machine_description_source':None,
						'emulator_list':[], 'machine_list':{'computer':[], 'console':[], 'arcade':[], 'environment':[]}
						
						}
