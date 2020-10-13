import os
import plaid
import json

def lambda_handler(event, context):
  PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
  PLAID_SECRET = os.getenv('PLAID_SECRET')
  PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
  PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions').split(',')
  PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US').split(',')

  plaid_client = plaid.Client(
	  client_id=PLAID_CLIENT_ID, 
	  secret=PLAID_SECRET, 
	  environment=PLAID_ENV,
    api_version='2019-05-29'
	)
  
  response = plaid_client.LinkToken.create(
    {
      'user': {
         # This should correspond to a unique id for the current user.
         'client_user_id': 'user-id',
      },
      'client_name': "Plaid Quickstart",
      'products': PLAID_PRODUCTS,
      'country_codes': PLAID_COUNTRY_CODES,
      'language': "en",
      }
    )

  responseObject = {}
  responseObject['statusCode'] = 200
  responseObject['headers'] = {}
  responseObject['headers']['Content-Type'] = 'application/json'
  responseObject['body'] = response

  return responseObject
