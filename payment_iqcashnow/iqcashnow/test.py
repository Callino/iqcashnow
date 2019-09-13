from iqcashnow import api
import logging

_logger = logging.getLogger(__name__)

host = ""
key = ""
secret = ""

iq_api = api.IQCashNow(key=key, secret=secret, host=host)
# test connection
# iq_api.test_connection()
print(iq_api.get_deposit_address("BTC"))
print(iq_api.get_deposit_balance("BTC"))
print(iq_api.get_exchange_rates("EUR", "BTC"))
print(iq_api.payment_request(currency='EUR', price="21.6", name="4", description='', reference="4", callback_url='', success_url='', cancel_url=''))
print(iq_api.create_payment(currency='EUR', price="21.6"))