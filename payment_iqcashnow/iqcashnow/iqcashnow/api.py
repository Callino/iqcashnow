# coding: utf-8
# Copyright 2019 Callino - Pichler Wolfgang, Gerhard Baumgartner
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import hashlib
import hmac
import time
import requests
import json
from urllib.parse import urljoin


class IQCashNow:

    def __init__(self, key, secret, host):
        self.key = key
        self.secret = secret
        self.host = host
        self.signature = ""
        self.nonce = ""

    def generate_signature(self, path, nonce, request_data=''):
        msg = path + str(nonce) + hashlib.sha256(json.dumps(request_data).encode('utf-8')).hexdigest()
        signature = hmac.new(self.secret.encode('utf-8'), msg=msg.encode('utf-8'), digestmod=hashlib.sha512).hexdigest()
        self.signature = signature

    def get_nonce(self):
        return str(round(time.time() * 1000))

    def get_headers(self):
        return {'Content-Type': 'multipart/form-data',
                'Accept': 'multipart/form-data',
                'X-IQCashNow-Key': self.key,
                'X-IQCashNow-Nonce': self.nonce,
                'X-IQCashNow-Signature': self.signature,
                }

    def prepare_values(self, location, payload):
        self.nonce = self.get_nonce()
        self.generate_signature(location, self.nonce, payload)
        headers = self.get_headers()
        api_url = urljoin(self.host, location)
        return headers, api_url

    def payment_request(self, name, price, reference, currency, target_currency="", description="", callback_url="", success_url="", cancel_url=""):
        location = "/v2/?a=WebPaymentRequest"
        payload = {
            "currency": currency,
            "price": price,
            "name": name,
            "description": description,
            "reference": reference,
            "callback_url": callback_url,
            "success_url": success_url,
            "cancel_url": cancel_url
        }
        if target_currency:
            payload.update({
                'target_currency': target_currency
            })
        return self.send_request(location, payload)

    def invoice_payment_request(self, data):
        location = "/v2/?a=InvoicePaymentRequest"
        payload = data
        return self.send_request(location, payload)

    def create_payment(self, currency, price):
        location = "/v2/?a=createPayment"
        payload = {
            "currency": currency, "price": price
        }
        return self.send_request(location, payload)

    def payment_status(self, payment_id):
        location = "/v2/?a=getStatus"
        payload = {
            "payment_id": payment_id,
        }
        return self.send_request(location, payload)

    def get_deposit_address(self, currency):
        location = "/v2/?a=getDepositAddress"
        payload = {
            'currency': currency
        }
        return self.send_request(location, payload)

    def get_deposit_balance(self, currency):
        location = "/v2/?a=getDepositBalance"
        payload = {
            'currency': currency
        }
        return self.send_request(location, payload)

    def get_deposit_status(self, payment_id):
        location = "/v2/?a=getDepositStatus"
        payload = {
            'payment_id': payment_id
        }
        return self.send_request(location, payload)

    def withdraw_fiat(self, currency, amount):
        location = "/v2/?a=withdrawal"
        payload = {
            'currency': currency,
            'amount': amount
        }
        return self.send_request(location, payload)

    def withdraw_crypto(self, currency, amount, address):
        location = "/v2/?a=withdrawal"
        payload = {
            'currency': currency,
            'amount': amount,
            'address': address
        }
        return self.send_request(location, payload)

    def get_exchange_rates(self, fiat_currency, crypto_currency):
        location = "/v2/?a=getRates"
        payload = {
            'fiat_currency': fiat_currency,
            'crypto_currency': crypto_currency,
        }
        return self.send_request(location, payload)

    def exchange_from_currency(self, from_currency, to_currency, from_amount, send=False):
        if send:
            location = "/v2/?a=exchangeSend"
        else:
            location = "/v2/?a=exchange"
        payload = {
            'from_currency': from_currency,
            'to_currency': to_currency,
            'from_amount': from_amount,
        }
        return self.send_request(location, payload)

    def exchange_to_currency(self, from_currency, to_currency, to_amount, send=False):
        if send:
            location = "/v2/?a=exchangeSend"
        else:
            location = "/v2/?a=exchange"
        payload = {
            'from_currency': from_currency,
            'to_currency': to_currency,
            'to_amount': to_amount,
        }
        return self.send_request(location, payload)

    def exchange_from_currency_crypto(self, from_currency, to_currency, from_amount, send=False, address=False):
        if send:
            if not address:
                raise ValueError("Address must be provided for crypto withdrawal!")
            location = "/v2/?a=exchangeSend"
        else:
            location = "/v2/?a=exchange"
        payload = {
            'from_currency': from_currency,
            'to_currency': to_currency,
            'from_amount': from_amount,
        }
        if send and address:
            payload.update({
                'address': address,
            })
        return self.send_request(location, payload)

    def exchange_to_currency_crypto(self, from_currency, to_currency, to_amount, send=False, address=False):
        if send:
            if not address:
                raise ValueError("Address must be provided for crypto withdrawal!")
            location = "/v2/?a=exchangeSend"
        else:
            location = "/v2/?a=exchange"
        payload = {
            'from_currency': from_currency,
            'to_currency': to_currency,
            'to_amount': to_amount,
        }
        if send and address:
            payload.update({
                'address': address,
            })
        return self.send_request(location, payload)

    def send_request(self, location, payload):
        headers, api_url = self.prepare_values(location, payload)
        response = requests.post(api_url, headers=headers, data=payload)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            raise ValueError(response.reason)
