import os
import time
import logging
import ddg3
import string

from utils import *


def ComputeMetaRatings(object_common_name = 'MAME', topic_keyword_array = ['arcade', 'emulator']):
	print(('ComputeMetaRatings() object_common_name = ' + object_common_name))
	seach_string = object_common_name
	for s_keyword in topic_keyword_array:
		seach_string = seach_string + ' ' + s_keyword

	##seach_string = seach_string.replace(' ', ',')

	print(('seach_string = ' + seach_string))

	r = ddg3.query(seach_string)
	print((r.type))
	print((r.answer.text))

	if (r.type == 'answer'):
		for result in r.results:
			print(('url found : ' + result.url))


# If the script is not imported, execute the main function
if __name__ == "__main__":
	ComputeMetaRatings('what is the best', ['arcade', 'emulator', '?'])
