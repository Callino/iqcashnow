# coding: utf-8
from odoo import api, fields, models, _
from ..iq_cash_now.iq_cash_now import api


class IQCashNowPaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    iqcn_host = fields.Char(string="IQ Cashnow Host")
    iqcn_key = fields.Char(string="IQ Cashnow Key")
    iqcn_secret = fields.Char(string="IQ Cashnow Secret")
    provider = fields.Selection(selection_add=[('iqcn', _('IQ Cashnow'))])

    def test_connection(self):
        return

    def iqcn_transaction(self, name, amount, reference, currency, target_currency="", description="", callback_url="", success_url="", cancel_url=""):
        iq_api = api.IQCashNow(key=self.iqcn_key, secret=self.iqcn_secret, host=self.iqcn_host)
        response = iq_api.payment_request(name=str(name) ,price=str(amount), reference=str(reference), currency=str(currency), target_currency=target_currency, description=description, callback_url=callback_url, success_url=success_url, cancel_url=cancel_url)
        return response

    def invoice_payment(self, data):
        iq_api = api.IQCashNow(key=self.iqcn_key, secret=self.iqcn_secret, host=self.iqcn_host)
        response = iq_api.invoice_payment_request(data)
        return response

    def create_payment(self, currency, price):
        iq_api = api.IQCashNow(key=self.iqcn_key, secret=self.iqcn_secret, host=self.iqcn_host)
        response = iq_api.create_payment(currency=str(currency), price=str(price))
        return response

    def payment_status(self, payment_id):
        iq_api = api.IQCashNow(key=self.iqcn_key, secret=self.iqcn_secret, host=self.iqcn_host)
        response = iq_api.payment_status(payment_id=str(payment_id))
        return response
