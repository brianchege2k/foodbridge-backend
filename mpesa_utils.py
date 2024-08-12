# to handle mpesa API interactions
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
from flask import current_app

def generate_mpesa_access_token():
    url = f"{current_app.config['MPESA_BASE_URL']}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(
        current_app.config['MPESA_CONSUMER_KEY'], 
        current_app.config['MPESA_CONSUMER_SECRET']
    ))
    access_token = response.json()['access_token']
    return access_token

def lipa_na_mpesa_online(phone_number, amount, account_reference, transaction_desc):
    access_token = generate_mpesa_access_token()
    api_url = f"{current_app.config['MPESA_BASE_URL']}/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {access_token}"}

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(
        f"{current_app.config['MPESA_SHORTCODE']}{current_app.config['MPESA_PASSKEY']}{timestamp}".encode()
    ).decode('utf-8')

    payload = {
        "BusinessShortCode": current_app.config['MPESA_SHORTCODE'],
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": current_app.config['MPESA_SHORTCODE'],
        "PhoneNumber": phone_number,
        "CallBackURL": "https://yourdomain.com/mpesa-callback",
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()
