# For educational purposes

import requests
from bs4 import BeautifulSoup

class Scraper:
	base_url = "https://www.brainyquote.com"
	headers = {"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36", "accept-language":"en-US,en;q=0.8"}
	max_page_limit = 1 # Max pages avail for current url

	def extract_quotes(self, url, extract_author=True):
		"""
			Requires a 'brainyquote domain' webpage url. Returns a list of quotes extracted from that page, if any.
			Format:
				[{"text": <quote_text>, "author": <author's name>, "topics": [], "keywords": []}]
			If a particular author's quotes are requested, then:
				[{"text": <quote_text>, "topics": [], "keywords": []}]
		"""
		
		quotes = []
		r = requests.get(url, headers=self.headers)
		
		try:
			r.raise_for_status()
		except requests.exceptions.HTTPError as e:
			print(e)
			return quotes
		
		soup = BeautifulSoup(r.text, "html.parser")
		
		# Pagination
		ul = soup.find('ul', {'class': 'pagination'})
		li = ul.find_all('li')[-2].text
		self.max_page_limit = int(li)
		
		cards = soup.find_all("div", {"class": "masonryitem boxy bqQt bqShare"})
		if not cards and 'search_results' in url:
			cards = soup.find_all("div", {"class": "bq_list_i boxy bqQt bqShare bqSearchResultQt bqcpx"})
		
		for card in cards:
			
			# Quote + Author
			quothor_div = card.select_one('div.boxyPaddingBig')
			quote = quothor_div.select_one('span.bqQuoteLink > a').text
			
			# Tags
			tags_div = card.find("div", {"class": "bq_q_nav boxyBottom boxyPaddingSmall"})
			tags = tags_div.find("div", {"class": "body bq_boxyRelatedLeft bqBlackLink"}).find_all('a')
			topics = []
			keywords = []
			for a in tags:
				word = a['href'].split('/')[2]
				if word == 'topics':
					topics.append(a.text)
				elif word == 'keywords':
					keywords.append(a.text)
			
			quotes.append({'text': quote, 'topics': topics, 'keywords': keywords})
			
			# Add 'author' only if required i.e. not when a particular author's quotes are requested
			if extract_author:
				quotes[-1]['author'] = quothor_div.select_one('div.bq-aut > a').text.title()
			
		return quotes

	def topic_quotes(self, topic, num_of_pages=1):
		"""
			Requires <topic name> and optional <num_of_pages=1> (to be scraped)
			Returns list of quotes in format
				[{"text": <quote_text>, "author": <author's name>, "topics": [], "keywords": []}]
		"""
		quotes = []
		if not topic:
			return quotes
		for i in range(num_of_pages):
			topic = topic.lower().replace(' ', '').replace('\'','')			
			url = self.base_url + "/quotes/topics/topic_" + topic
			if i+1 != 1:
				url = url + str(i+1) + '.html' # .html is required, otherwise the site redirects twice!
			result = self.extract_quotes(url)
			if not result:
				return quotes
			quotes += result
			if i+1 == self.max_page_limit:
				break
		return quotes

	def author_quotes(self, author, num_of_pages=1):
		"""
			Requires <author's name> and optional <num_of_pages=1> (to be scraped)
			Returns, format:
				[{"text": <quote_text>, "topics": [], "keywords": []}]
		"""
		quotes = []
		if not author:
			return quotes
		for i in range(num_of_pages):
			author = author.lower().replace(' ','_').replace('-', '').replace(',', '').replace('.', '')
			url = self.base_url + "/quotes/authors/%s/%s" % (author[0], author)
			if i+1 != 1:
				url = url + '_' + str(i+1) + '.html'
			result = self.extract_quotes(url, extract_author=False)
			if not result:
				return quotes
			quotes += result
			if i+1 == self.max_page_limit:
				break
		return quotes

	def popular_author_quotes(self, limit_to=5, num_of_pages=1):
		"""
			Requires 2 optional arguments: limit_to=5 (limit scraping to this many number of popular authors)
										   num_of_pages=1 (scrape only this many pages of author's quotes.. One page usually has 26 quotes)
			Return dictionary of author and his list of quotes
		"""
		quotes = {}
		url = self.base_url + '/quotes/favorites.html'
		r = requests.get(url, headers=self.headers)
		soup = BeautifulSoup(r.text, "html.parser")
		pin_icons = soup.select('img.bqPinIcon') # Icon next to popular authors
		pin_icons = pin_icons[:limit_to]
		for count, img in enumerate(pin_icons):
			a = img.find_previous_sibling()
			author = a.text
			href = a['href']
			for i in range(num_of_pages):
				url = self.base_url + href
				if i+1 != 1:
					url = url.split('.html')[0]
					url = url + '_' + str(i+1) + '.html'
				result = self.extract_quotes(url)
				if not result:
					break
				quotes[author] = quotes.get(author, []) + result
				if i+1 == self.max_page_limit:
					break
		return quotes

	def search_quotes(self, query, num_of_pages=1):
		"""
			Requires a <search query> argument
			Optional argument num_of_pages=1 (scrape only this many pages of author's quotes.. One page usually has 26 quotes)
		"""
		quotes = []
		if not query:
			return quotes
		for i in range(num_of_pages):
			url = self.base_url + "/search_results.html?q=%s" % (query, )
			if i+1 != 1:
				url = url + '&pg=' + str(i+1)
			result = self.extract_quotes(url)
			if not result:
				return quotes
			quotes += result
			if i+1 == self.max_page_limit:
				break
		return quotes
