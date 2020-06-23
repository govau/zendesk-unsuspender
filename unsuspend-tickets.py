# Create Zendesk tickets from those in the suspended queue
#
# See https://support.zendesk.com/hc/en-us/articles/360040599713-Upcoming-changes-to-email-behavior
#
# Requires Python 3.x

import os
import time
import requests
import json
import re

ZENDESK_LISTENING_MAILBOX = os.getenv('ZENDESK_LISTENING_MAILBOX') if 'ZENDESK_LISTENING_MAILBOX' in os.environ else ''
ZENDESK_EMAIL = os.getenv('ZENDESK_EMAIL') if 'ZENDESK_EMAIL' in os.environ else ''
ZENDESK_TOKEN = os.getenv('ZENDESK_TOKEN') if 'ZENDESK_TOKEN' in os.environ else ''
ZENDESK_API_ENDPOINT = os.getenv('ZENDESK_API_ENDPOINT') if 'ZENDESK_API_ENDPOINT' in os.environ else ''
ZENDESK_SCHEDULE = os.getenv('ZENDESK_SCHEDULE') if 'ZENDESK_SCHEDULE' in os.environ else 600

if not isinstance(ZENDESK_SCHEDULE, int):
	if not ZENDESK_SCHEDULE.isdigit():
		ZENDESK_SCHEDULE = 600
	else:
		ZENDESK_SCHEDULE = int(ZENDESK_SCHEDULE)

if ZENDESK_SCHEDULE > 3600:
	ZENDESK_SCHEDULE = 600


class ZendeskItem:
	def __init__(self, id, subject, from_name, from_email, content, created_at, recipient, brand_id):
		self.id         = id
		self.subject    = subject
		self.from_name  = from_name
		self.from_email = from_email
		self.content    = content
		self.created_at = created_at
		self.recipient  = recipient
		self.brand_id   = brand_id

		if re.search(r'@govcms\.gov\.au$', self.from_email):
			applicant_email = re.search(r'(Account\/Registrant\ Email\:|Applicant\ Email\:)\n?(.*)$', self.content, re.I|re.M)
			if applicant_email:
				self.from_email = applicant_email.group(2).strip()

	def  __repr__(self):
		return "\nZendeskItem(id: %d, subject: %s, from_name: %s, from_email: %s)" % (self.id, self.subject, self.from_name, self.from_email)
	
	def to_ticket_json(self):
		return json.dumps(
{
	"ticket": { 
		"subject": self.subject,
		"comment": {
			"body": self.content
		},
		"requester": {
			"name": self.from_name,
			"email": self.from_email
		},
		"recipient": self.recipient,
		"brand_id": self.brand_id,
		"created_at": self.created_at
	}
})


def send_batch(zendesk_items=[]):
	if len(zendesk_items) > 0:
		# the following unsuspends
		#ids = ",".join(str(x.id) for x in zendesk_items)
		#r = requests.put(ZENDESK_API_ENDPOINT + 'suspended_tickets/recover_many.json?ids=' + ids, auth=(ZENDESK_EMAIL + '/token', ZENDESK_TOKEN), data={}, headers={'Content-Type': 'application/json'})
		

		# instead of unsuspending, we now create a new ticket with data from the suspended ticket
		for item in zendesk_items:
			payload = ''
			payload = item.to_ticket_json()

			r = requests.post(ZENDESK_API_ENDPOINT + 'tickets.json', auth=(ZENDESK_EMAIL + '/token', ZENDESK_TOKEN), data=payload, headers={'Content-Type': 'application/json'})
			if r.status_code == 201:
				# success, let's delete the ticket from the suspended queue
				r = requests.delete(ZENDESK_API_ENDPOINT + 'suspended_tickets/' + str(item.id) + '.json', auth=(ZENDESK_EMAIL + '/token', ZENDESK_TOKEN), data={}, headers={'Content-Type': 'application/json'})

			else:
				print(f'API error - status code: {r.status_code!s}')
				print(f'API error - body: {r.content!s}')
				print(f'Attempted ticket creation with payload: {payload!s}')

		print("Done")
	return


if ZENDESK_LISTENING_MAILBOX and ZENDESK_EMAIL and ZENDESK_TOKEN and ZENDESK_API_ENDPOINT:

	# convert the ZENDESK_LISTENING_MAILBOX into a list so we can provide multiple mailboxes to look over
	ZENDESK_LISTENING_MAILBOX = [x.strip() for x in ZENDESK_LISTENING_MAILBOX.split(',')]

	while True:
		print("Running")

		url = ZENDESK_API_ENDPOINT + 'suspended_tickets.json'
		unsuspend_tickets = []

		# get a list of suspended tickets
		# Zendesk provides 100 per request then paginates remaining items
		while url is not None:
			print(url)
			r = requests.get(url, auth=(ZENDESK_EMAIL + '/token', ZENDESK_TOKEN))
			tickets = r.json()

			if tickets.get('suspended_tickets'):
				for ticket in tickets['suspended_tickets']:
					if ticket.get('recipient') in ZENDESK_LISTENING_MAILBOX:
						if ticket.get('cause').lower() != 'detected as spam':
							unsuspend_tickets.append(ZendeskItem(
								ticket.get('id'), 
								ticket.get('subject'), 
								ticket['via']['source']['from']['name'],
								ticket['via']['source']['from']['address'],
								ticket.get('content'), 
								ticket.get('created_at'),
								ticket.get('recipient'),
								ticket.get('brand_id')
							))

			url = tickets.get('next_page')

		# unsuspend the tickets
		if len(unsuspend_tickets) > 0:
			print(unsuspend_tickets)

			batch_tickets = []
			for i, zendesk_item in enumerate(unsuspend_tickets):
				# zendesk can only do 100 at a time
				if len(batch_tickets) == 100:
					send_batch(batch_tickets)
					batch_tickets = []
				batch_tickets.append(zendesk_item)
			if len(batch_tickets) > 0:
				send_batch(batch_tickets)


		time.sleep(ZENDESK_SCHEDULE - time.time() % ZENDESK_SCHEDULE)
else:
	if not ZENDESK_LISTENING_MAILBOX: print('ZENDESK_LISTENING_MAILBOX not set')
	if not ZENDESK_EMAIL: print('ZENDESK_EMAIL not set')
	if not ZENDESK_TOKEN: print('ZENDESK_TOKEN not set')
	if not ZENDESK_API_ENDPOINT: print('ZENDESK_API_ENDPOINT not set')
	exit(1)
