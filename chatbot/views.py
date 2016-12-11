from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt

from pprint import pprint
from quotes.models import Author, Keyword, Topic, Quote

from .utils import *

# Create your views here.

class QuoteBotView(View):
	standard_reply = "Oops. I don't know how to handle that. Please type 'help' to see how can I serve you."
	
	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return View.dispatch(self, request, *args, **kwargs)

	def get(self, request, *args, **kwargs):
		if request.GET.get('hub.verify_token', None) == settings.VERIFY_TOKEN:
			return HttpResponse(request.GET.get('hub.challenge'))
		else:
			raise Http404('Invalid token')

	def handle_postbacks_qr(self, uid, quotes, data, what, name, *args, **kwargs):

		"""
			Payload Structure
			topic/author_Full Name!=1,4,7,3,9
								  | Pks sent | Therefore, choose random other than these
								  --> Newest to Oldest
		"""

		payload = {
			"recipient":{"id" : uid},
			"message": {
				"attachment": {
					"type": "template",
					"payload": {
						"template_type": "list",
						"top_element_style": "compact",
						"buttons": [
							{
								"title": "View More",
								"type": "postback",
							}
						]
			}}}}
		elements = []
		new_pks = []
		for quote in quotes:
			title = quote.text
			author = quote.author
			subtitle = author.name
			el = {'title' : title, 'subtitle' : subtitle}
			if author.photo:
				el['image_url'] = author.photo
			default_action = {
				"type" : "web_url",
				"messenger_extensions": True,
				"webview_height_ratio" : "tall",
				"fallback_url" : "https://www.google.com/"
			}
			buttons = {
				"title" : "View",
				"type" : "web_url",
				"messenger_extensions": True,
				"webview_height_ratio" : "tall",
				"fallback_url" : "https://www.google.com/"
			}
			buttons['url'] = default_action['url'] = "https://quotechatbot.herokuapp.com/quotes/%s" % quote.pk
			el['default_action'] = default_action
			el['buttons'] = [buttons]
			elements.append(el)
			new_pks.append(quote.pk)
	# Removing last 4 pks
		length = len(data)
		if length == 12:
			for i in range(4):
				try:
					data.pop(length-i-1)
				except:
					pass
		data = new_pks + data
		data = [str(i) for i in data]
		updated_payload_string = what + '_' + name + '!=' + ','.join(data)
		payload['message']['attachment']['payload']['elements'] = elements
		payload['message']['attachment']['payload']['buttons'][0]['payload'] = updated_payload_string
		send_message(payload)

	def enlighten_user(self, uid, *args, **kwargs):
		random_quote = Quote.objects.random_popular()
		author = random_quote.author
		text = "Here's a quote:\n\n🗣 %s\n- %s" % (random_quote.text, author.name)
		payload = {"recipient" : {"id" : uid } , "message" : {"text" : text}}
		photo = author.photo
		if photo:
			payload['message']['attachment']['payload']['elements']['image_url'] = photo
		send_message(payload)

	def send_instructions(self, uid):
		recipient = {"id" : uid}
		send_message({"recipient" : recipient, "message" : {"text" : "To read a random quote, send 'quote'\n\nTo choose from topics, send 'topics'\n\nTo get enlightened by popular authors' quotes, send 'authors'"}})


	def send_topics(self, uid, *args, **kwargs):
		payload = {
			"recipient":{
				"id": uid
			},
			"message":{
				"text":"Choose a topic:",
				"quick_replies":[
					{
						"content_type":"text",
						"title":"Motivational 😀 ",
						"payload": "topic_Motivational!="
					},
					{
						"content_type":"text",
						"title":"Life 😇 ",
						"payload":"topic_Life!="
					},
					{
						"content_type":"text",
						"title":"Success 😎 ",
						"payload": "topic_Success!="
					},
					{
						"content_type":"text",
						"title":"Positive 😊 ",
						"payload": "topic_Positive!="
					},
					{
						"content_type":"text",
						"title":"Funny 😂 ",
						"payload": "topic_Funny!="
					},
					{
						"content_type":"text",
						"title":"Love 😍 ",
						"payload": "topic_Love!="
					},
				]
			}
		}
		send_quickreplies(payload)

	def send_authors(self, uid, *args, **kwargs):
		payload = {
			"recipient":{
				"id": uid
			},
			"message":{
				"text":"Choose an author:"
			}
		}
		quick_replies = []
		popular_authors = Author.objects.random_popular(how_many=6)
		for author in popular_authors:
			title = author.name
			payload_string = "author_" + title + "!="
			quick_replies.append({"content_type":"text", "title":title, "payload":payload_string})
		payload['message']['quick_replies'] = quick_replies
		send_quickreplies(payload)

	def post(self, request, *args, **kwargs):
		response = json.loads(request.body.decode('utf-8'))
		try:
			for entry in response['entry']:
				for message in entry['messaging']:
					uid = message['sender']['id']
				# Typing On
					send_action(uid, "typing_on")
					
				# Recipient's details
					first_name = get_user_details(uid, params=['first_name'])['first_name']
					recipient = {"id" : uid}
				# Handling Postback
					if 'postback' in message or 'quick_reply' in message['message']:
						data = message.get('postback', {}).get('payload', None) or message['message']['quick_reply']['payload']
						data = data.split('_')
						what = data[0]
						data = data[1]
						data = data.split('!=')
						name = data[0]
						already_sent = data[1].split(',')
						already_sent = [i for i in already_sent if i]
						already_sent = [int(i) for i in already_sent]
						if what == 'topic':
							topic = Topic.objects.get(name=name)
							quotes = topic.quotes.random_but(already_sent, how_many=4)
							self.handle_postbacks_qr(uid, quotes, already_sent, what, name)
						elif what == 'author':
							author = Author.objects.get(name=name)
							quotes = author.quotes.random_but(already_sent, how_many=4)
							self.handle_postbacks_qr(uid, quotes, already_sent, what, name)
						else:
							payload = {"recipient" : recipient, "message" : {"text" : self.standard_reply}}
							send_message(payload)
				# Handling attachments, if sent
					elif 'attachment' in message['message']:
						payload = {"recipient" : recipient, "message" : {"text" : self.standard_reply}}
						send_message(payload)
				# Handling Random Texts
					else:
						text = message['message']['text'].lower()
						if 'topic' in text:
							self.send_topics(uid)
						elif 'author' in text:
							self.send_authors(uid)
						else:
							text = text.split()
						# Checking for relevant words
							oops = True
							for token in text:
								if token == 'help':
									self.send_instructions(uid)
									oops = False
									break
								elif token in ['quote', 'quotes', 'send', 'go', 'start', 'enlighten']:
									self.enlighten_user(uid)
									oops = False
									break
								else:
									greetings = ['hiiii', 'hellooo', 'yooooo', 'heyyy']
									for word in greetings:
										if word.startswith(token):
											oops = False
											payload = {"recipient":recipient, "message" : {"text" : "Hey %s!\nI'm a ChatBot 🤖  who is here to enlighten you with quotes.\n\nSend 'help' to see how can I be of service to you! ^_^" % (first_name, )}}
											send_message(payload)
											break
							if oops:
								payload = {"recipient" : recipient, "message" : {"text" : self.standard_reply}}
								send_message(payload)
		except Exception as e:
			print(e)
		
		return HttpResponse()

