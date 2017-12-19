# zendesk-unsuspender

Regularly interfaces with the Zendesk API to release specifically branded items in the suspended queue. This was required as Zendesk considers all emails sent from GovCMS as system generated and places the ticket into the suspended queue.

Couldn't use Zendesk triggers as they do not apply to the suspended queue.

This app runs on cloud.gov.au.

## Requirements
Requires Python 3.x

## Configuration
| Environment variable | Notes |
| -------------------- | ----- |
| ZENDESK_LISTENING_MAILBOX | The mailbox that Zendesk is setup to monitor for email traffic, eg `support@domainnames.zendesk.com` |
| ZENDESK_EMAIL | Visit Zendesk as an agent, go to settings > API. Enable Token Access, create a new token. |
| ZENDESK_TOKEN | As above |
| ZENDESK_API_ENDPOINT | `https://{subdomain}.zendesk.com/api/v2/` eg `https://domainnames.zendesk.com/api/v2/` |
| ZENDESK_SCHEDULE | Run every x seconds. Eg 1200 = run every 20 minutes at 00, 20, and 40 minutes past the hour. Cannot be above 3600. Defaults to 600 (10min). |
