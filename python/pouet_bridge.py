
from bs4 import BeautifulSoup


pouet_machine_dict = {'cbm_amiga':['Amiga+OCS%2FECS'],
                      'cbm_64':['Commodore+64']
                      }


def machine_get_pouet_prods(machine):
	print('machine_get_pouet_prods() machine = ' + machine)
	# if machine in pouet_machine_dict:
	# 	pouet_url = 'http://www.pouet.net' ## 'http://www.pouet.net/prodlist.php?platform[]=' + pouet_machine_dict[machine][0] + '&page=1&order=thumbup'
	# 	print('url = ' + pouet_url)
		
	# 	print(data)

	# 	return []


	return None

# If the script is not imported, execute the main function
if __name__ == "__main__":
	machine_get_pouet_prods('cbm_64')
