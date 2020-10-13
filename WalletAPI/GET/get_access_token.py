import os
import plaid
import json

def lambda_handler(event, context):

    PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
    PLAID_SECRET = os.getenv('PLAID_SECRET')
    PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
    
    public_token = event["queryStringParameters"]["public_token"]

    plaid_client = plaid.Client(
	    client_id=PLAID_CLIENT_ID, 
	    secret=PLAID_SECRET, 
	    environment=PLAID_ENV,
        api_version='2019-05-29'
	)

    try:
        exchange_response = plaid_client.Item.public_token.exchange(public_token)
    except plaid.errors.PlaidError as e:
        return create_response_obj(format_error(e))
    
    
    return create_response_obj(exchange_response)

def format_error(e):
  return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type, 'error_message': e.message } }
    
def create_response_obj(data):
    responseObject = {}
    responseObject['statusCode'] = 200
    responseObject['headers'] = {
        "Access-Control-Allow-Origin" : "*", 
        "Access-Control-Allow-Credentials" : True 
    }
    responseObject['headers']['Content-Type'] = 'application/json'
    responseObject['body'] = json.dumps(data)
    return responseObject