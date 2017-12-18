# Unsuspend Zendesk tickets
# Requires Python 3.x

import os
import time
import requests
import json

ZENDESK_LISTENING_MAILBOX = os.getenv('ZENDESK_LISTENING_MAILBOX') if 'ZENDESK_LISTENING_MAILBOX' in os.environ else ''
ZENDESK_EMAIL = os.getenv('ZENDESK_EMAIL') if 'ZENDESK_EMAIL' in os.environ else ''
ZENDESK_TOKEN = os.getenv('ZENDESK_TOKEN') if 'ZENDESK_TOKEN' in os.environ else '' 
ZENDESK_API_ENDPOINT = os.getenv('ZENDESK_API_ENDPOINT') if 'ZENDESK_API_ENDPOINT' in os.environ else ''


def send_batch(ticket_ids = []):
	if len(ticket_ids) > 0:
		print('Unsuspending: ' + str(ticket_ids))
		ids = ",".join(str(x) for x in ticket_ids)
		
		r = requests.put(ZENDESK_API_ENDPOINT + 'suspended_tickets/recover_many.json?ids=' + ids, auth=(ZENDESK_EMAIL + '/token', ZENDESK_TOKEN), data={}, headers={'Content-Type': 'application/json'})
		print("Done")

	return



if ZENDESK_LISTENING_MAILBOX and ZENDESK_EMAIL and ZENDESK_TOKEN and ZENDESK_API_ENDPOINT:
#	while True:
		# get a list of suspended tickets
		r = requests.get(ZENDESK_API_ENDPOINT + 'suspended_tickets.json', auth=(ZENDESK_EMAIL + '/token', ZENDESK_TOKEN))
		tickets = r.json()
		unsuspend_tickets = []

		if tickets.get('suspended_tickets'):	
			for ticket in tickets['suspended_tickets']:
				if ticket.get('recipient') == ZENDESK_LISTENING_MAILBOX:
					unsuspend_tickets.append(ticket.get('id'))

		# unsuspend the tickets
		if len(unsuspend_tickets) > 0:
			batch_tickets = []
			for i, id in enumerate(unsuspend_tickets):
				# zendesk can only do 100 at a time
				if len(batch_tickets) == 100:
					send_batch(batch_tickets)
					batch_tickets = []
				batch_tickets.append(id)
			if len(batch_tickets) > 0:
				send_batch(batch_tickets)


#		time.sleep(60 - time.time() % 60)
else:
	if not ZENDESK_LISTENING_MAILBOX: print('ZENDESK_LISTENING_MAILBOX not set')
	if not ZENDESK_EMAIL: print('ZENDESK_EMAIL not set')
	if not ZENDESK_TOKEN: print('ZENDESK_TOKEN not set')
	if not ZENDESK_API_ENDPOINT: print('ZENDESK_API_ENDPOINT not set')
	exit(1)