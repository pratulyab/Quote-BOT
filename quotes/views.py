from django.shortcuts import render, get_object_or_404

# Create your views here.
from .models import Author, Keyword, Topic, Quote
from .scraper import Scraper

def render_quote(request, qid):
	quote = get_object_or_404(Quote, pk=int(qid))
	return render(request, 'quotes/quote.html', context={'quote':quote})

# These functions are not intended to be mapped to a url
# To be called as and when required, to scrape and update DB
def save_db(result, aut=''):
	for quote in result:
		try:
			author = Author.objects.get_or_create(name=quote['author'])[0]
		except KeyError:
			author = Author.objects.get_or_create(name=aut)[0]
		topics = set()
		keywords = set()
		for t in quote['topics']:
			t = t.title()
			t = Topic.objects.get_or_create(name=t)[0]
			topics.add(t)
		for k in quote['keywords']:
			k = k.title()
			k = Keyword.objects.get_or_create(name=k)[0]
			keywords.add(k)
		quote = Quote.objects.get_or_create(text=quote['text'], author=author)[0]
		for t in topics:
			quote.topics.add(t)
		for k in keywords:
			quote.keywords.add(k)
		quote.save()

def topic():
	s = Scraper()
	for topic in ['motivational', 'love', 'funny', 'life', 'success', 'positive']:
		result = s.topic_quotes(topic, num_of_pages=2)
		save_db(result)

def author():
	s = Scraper()
	for author in ['Albert Einstein', 'Buddha', 'Socrates', 'Mark Twain', 'Winston Churchill']:
		result = s.author_quotes(author, num_of_pages=2)
		save_db(result, aut=author)
		author = Author.objects.get(name=author)
		author.is_popular = True
		author.save()

