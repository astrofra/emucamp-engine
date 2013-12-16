import os
import time
import logging
import urllib2
import urlparse
import mimetypes
import xml.etree.ElementTree as ET

from utils import *
from data_extraction import *
from bs4 import BeautifulSoup

def ComputeMetaRatings(object_common_name = 'MAME', topic_keyword_array = ['arcade', 'emulator']):
	print('ComputeMetaRatings() object_common_name = ' + object_common_name)
	seach_string = object_common_name
	for s_keyword in topic_keyword_array:
		seach_string = seach_string + ' ' + s_keyword

ComputeMetaRatings('MAME', ['arcade', 'emulator'])
