from django.core import validators
from django.db import models
from django.db.models import Q

import re
from random import randint

# Create your models here.

class RandomAuthorManager(models.Manager):
	def random(self, how_many=1):
		chosen = []
		length = self.count()
		if how_many > length:
			how_many = length
			return self.all()
		
		for _ in range(how_many):
			rindex = randint(0, length - 1)
			while rindex in chosen:
				rindex = randint(0, length - 1)
			chosen.append(rindex)
		return self.filter(Q(pk__in = chosen))

	def random_but(self, not_in, how_many=1):
		chosen = []
		length = self.count()
		if how_many > length:
			return self.all()
		
		for _ in range(how_many):
			rindex = randint(0, length - 1)
			while rindex in chosen or rindex in not_in:
				rindex = randint(0, length - 1)
			chosen.append(rindex)
		return self.filter(Q(pk__in = chosen))

	def random_popular(self, how_many=5):
		chosen = []
		popular_authors = self.filter(is_popular=True)
		length = len(popular_authors)
		if how_many > length:
			return popular_authors
		
		for _ in range(how_many):
			rindex = randint(0, length - 1)
			while rindex in chosen:
				rindex = randint(0, length - 1)
			chosen.append(rindex)
		return self.filter(Q(pk__in=chosen))

class Author(models.Model):
	name = models.CharField(max_length=256, unique=True)
	photo = models.URLField(blank=True)
	is_popular = models.BooleanField(default=False)
	objects = RandomAuthorManager()

	def __str__(self):
		return self.name


class Keyword(models.Model):
	name = models.CharField(max_length=32, unique=True)

	def __str__(self):
		return self.name


class Topic(models.Model):
	name = models.CharField(max_length=32, unique=True)

	def __str__(self):
		return self.name


class RandomQuoteManager(models.Manager):
	def random(self, how_many=1):
		chosen = []
		length = self.count()
		if how_many > length:
			how_many = length
			return self.all()
		actual_quote_pks = [q.pk for q in self.all()]
		for _ in range(how_many):
			rindex = randint(0, length - 1)
			while rindex in chosen:
				rindex = randint(0, length - 1)
			chosen.append(rindex)
		actual_chosen = [actual_quote_pks[i] for i in chosen]
		return self.filter(Q(pk__in = actual_chosen))

	def random_but(self, not_in, how_many=1):
		if not not_in:
			return self.all()[:how_many]
		actual_quote_pks = [q.pk for q in self.all()] # len will be the number of quotes in specific domain of either topic or author
		chosen = [] # will hold indices corresponding to actual_quote_pks list
		length = self.count()
		if how_many > length:
			how_many = length
			return self.all()
		
		for _ in range(how_many):
			rindex = randint(0, length - 1)
			while rindex in chosen or rindex in not_in:
				rindex = randint(0, length - 1)
			chosen.append(rindex)
		actual_chosen = [actual_quote_pks[i] for i in chosen]
		return self.filter(Q(pk__in = actual_chosen)) # filter(Q) will return objects considering whole, rather than the specific domain

	def random_popular(self):
		# Returns one random quote by a popular author
		popular_authors = Author.objects.filter(is_popular=True)
		author = popular_authors[randint(0, len(popular_authors) - 1)]
		quotes = author.quotes.all()
		return quotes[randint(0, len(quotes) - 1)]


class Quote(models.Model):
	text = models.TextField()
	author = models.ForeignKey(Author, related_name="quotes")
	topics = models.ManyToManyField(Topic, related_name="quotes")
	keywords = models.ManyToManyField(Keyword, related_name="quotes")
	objects = RandomQuoteManager()

	def __str__(self):
		return self.author.__str__()

	class Meta:
		unique_together = ["text", "author"]
