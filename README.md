# zendesk-unsuspender

[![CircleCI](https://circleci.com/gh/govau/zendesk-unsuspender/tree/master.svg?style=svg)](https://circleci.com/gh/govau/zendesk-unsuspender/tree/master)

Regularly interfaces with the Zendesk API to release specifically branded items from the suspended queue. This was required as Zendesk considers emails sent from GovCMS as system generated and places the ticket into the suspended queue. Check out `Detected email as being from a system user` from https://support.zendesk.com/hc/en-us/articles/115009659807

Couldn't use Zendesk triggers as they do not apply to the suspended queue.

This app runs on cloud.gov.au.

## May 2020 Update
Due to https://support.zendesk.com/hc/en-us/articles/360040599713-Upcoming-changes-to-email-behavior suspended tickets are no longer unsuspended as they do not trigger email notifications to end users. Instead, new tickets are created with data found in the suspended tickets. On success, the suspended ticket is tidied up and removed.

## Requirements
Requires Python 3.x

## Configuration
| Environment variable | Notes |
| -------------------- | ----- |
| ZENDESK_LISTENING_MAILBOX | The mailbox that Zendesk is setup to monitor for email traffic, eg `support@domainnames.zendesk.com`. Separate multiple mailboxes with a comma. |
| ZENDESK_EMAIL | Visit Zendesk as an agent, go to settings > API. Enable Token Access, create a new token. |
| ZENDESK_TOKEN | As above |
| ZENDESK_API_ENDPOINT | `https://{subdomain}.zendesk.com/api/v2/` eg `https://domainnames.zendesk.com/api/v2/` |
| ZENDESK_SCHEDULE | Run every x seconds. Eg 1200 = run every 20 minutes at 00, 20, and 40 minutes past the hour. Cannot be above 3600. Defaults to 600 (10min). |

## Running locally
If you don't have an instance on cloud.gov.au, you can run locally:

```
# export ZENDESK_LISTENING_MAILBOX="support@domainnames.zendesk.com, webmaster@domainnames.zendesk.com"
# export ZENDESK_EMAIL="agent@test.gov.au"
# export ZENDESK_TOKEN="1234"
# export ZENDESK_API_ENDPOINT="https://domainnames.zendesk.com/api/v2/"
# python3 unsuspend-tickets.py
```

## Deploying to Prod
All changes to master will initiate a CircleCI pipeline to production. For development changes, run them locally as per instructions above.

Note: due to running one instance of Zendesk, we only need to run one instance of this app in production. Furthermore, items will remain in the suspended queue on availability issues. 

## Updating Python modules
As per [Python buildpack doco](https://docs.cloudfoundry.org/buildpacks/python/index.html#-vendor-app-dependencies):
```
YOUR-APP-DIR# pip install --download vendor -r requirements.txt --no-binary :all:
```
