import os
import plaid
import json
import datetime

def lambda_handler(event, context):
    PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
    PLAID_SECRET = os.getenv('PLAID_SECRET')
    PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
    
    access_token = event["queryStringParameters"]["access_token"]

    plaid_client = plaid.Client(
	    client_id=PLAID_CLIENT_ID, 
	    secret=PLAID_SECRET, 
	    environment=PLAID_ENV,
        api_version='2019-05-29'
	)
    try:
        start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-30))
        end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
        plaid_response = plaid_client.Transactions.get(access_token, start_date, end_date)        
    except plaid.errors.PlaidError as e:
        return create_response_obj(format_error(e))

    response = {}
    all_accounts = {}

    for account in plaid_response['accounts']:
        if account["type"] in all_accounts:
            all_accounts[account["type"]]["AccountList"].append(account)
            all_accounts[account["type"]]["total"] += account["balances"]["current"]
        else:
            all_accounts[account["type"]] = {"AccountList":[account]}
            all_accounts[account["type"]]["total"] = account["balances"]["current"]

    response["Accounts"] = all_accounts
    response["Transactions"] = []
    base = datetime.datetime.today()
    response["MonthlySpending"] = {(base - datetime.timedelta(days=x)).strftime("%Y-%m-%d"):0 for x in range(31)}
    
    for transaction in plaid_response["transactions"]:
        transaction["accountname"] = find_account_name(transaction["account_id"], response["Accounts"])
        response["Transactions"].append(transaction)
        if transaction["amount"] > 0:
            response["MonthlySpending"][transaction["date"]] = response["MonthlySpending"][transaction["date"]] + transaction["amount"]
    
    currAmountSpent = 0
    for date in reversed(response["MonthlySpending"].keys()):
        currAmountSpent = currAmountSpent + response["MonthlySpending"][date]
        response["MonthlySpending"][date] = currAmountSpent
            
    return create_response_obj(response)

def find_account_name(account_id, all_accounts):
    for account_subtype_info in all_accounts.values():
        account_list = account_subtype_info["AccountList"]
        for account in account_list:
            if account["account_id"]==account_id:
                return account["name"]
            
    return ""

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