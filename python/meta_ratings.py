import logging
from duckduckgo_search import DDGS


def ComputeMetaRatings(object_common_name='MAME', topic_keyword_array=None, max_results=5):
	if topic_keyword_array is None:
		topic_keyword_array = ['arcade', 'emulator']

	print('ComputeMetaRatings() object_common_name = ' + object_common_name)
	search_string = ' '.join([object_common_name] + topic_keyword_array)
	print('search_string = ' + search_string)

	results = []
	try:
		with DDGS() as ddgs:
			for result in ddgs.text(search_string, max_results=max_results):
				results.append(result)
	except Exception as exc:
		logging.warning("DuckDuckGo search failed: %s", exc)
		return []

	for result in results:
		url = result.get('href') or result.get('url') or ''
		if url:
			print('url found : ' + url)

	return results


# If the script is not imported, execute the main function
if __name__ == "__main__":
	ComputeMetaRatings('what is the best', ['arcade', 'emulator', '?'])
