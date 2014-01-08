SOURCE_ROOT			= 'sources/'
SITE_ROOT			= '../www/'

machine_list		= sorted([	'oric','google_android', 'amstrad_cpc', 'nintendo_snes', 'pc_ms-dos', 'nintendo_gameboy', 'sega_mastersystem-gamegear',
								'atari_lynx', 'msx', 'thomson_mo_to', 'atari_800xl', 'nec_pc_engine', 'arcade', 'vectrex', 'sinclair_ql',
								'nintendo_nes', 'sinclair_spectrum', 'snk_neogeo', 'acorn_archimedes', 'cbm_64', 'cbm_amiga', 'sega_megadrive', 'atari_st'
								])

machine_update_only = ['arcade']

RESOURCES_ROOT		= 'resources'
RESOURCES_FOLDERS	= ['assets', 'extern']

G_TEST_MODE			= False
G_CREATE_INDEX		= True

INPUT_PAGES			= {'machine':'template_machine.html', 'index':'template_index.html', 'about':'about.html'	}
OUTPUT_PAGES		= {'machine':{}	}

quik_interface		= {	'machine_name':None, 'machine_filename':None, 'machine_type':None, 'machine_description_source_url':None, 'machine_description_source':None,
						'emulator_list':[], 'machine_list':{'computer':[], 'console':[], 'arcade':[], 'environment':[]},
						'emulator_update_list': []
						}
