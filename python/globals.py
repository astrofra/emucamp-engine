source_root			= 'sources/'
site_root			= '../www/'
machine_list		= sorted(['pc_ms-dos', 'nec_pc_engine', 'arcade', 'vectrex' ,'sega_gamegear', 'sinclair_spectrum', 'snk_neogeo', 'cbm_amiga', 'cbm_64', 'amstrad_cpc', 'atari_st', 'sega_megadrive', 'nintendo_nes'])
resources_root		= 'resources'
resources_folders	= ['assets', 'extern']

g_test_mode			= False
g_create_index		= False

input_pages			= {'machine':'template_machine.html', 'index':'template_index.html'	}
output_pages		= {'machine':{}	}

quik_interface		= {	'machine_name':None, 'machine_filename':None, 'machine_type':None, 'machine_description_source_url':None, 'machine_description_source':None,
						'emulator_list':[], 'machine_list':{'computer':[], 'console':[], 'arcade':[], 'environment':[]}
						
						}