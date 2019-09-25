# coding: utf-8
# Copyright 2019 Callino - Pichler Wolfgang, Gerhard Baumgartner
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import logging
import werkzeug
from werkzeug import urls
import traceback

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.payment_iqcashnow.iqcashnow.iqcashnow import api as iqcnapi

_logger = logging.getLogger(__name__)


class PaymentAcquirerIQCN(models.Model):
    _inherit = 'payment.acquirer'

    iqcn_host = fields.Char(string="IQ Cashnow Host", related='journal_id.iqcn_host')
    iqcn_key = fields.Char(string="IQ Cashnow Key", related='journal_id.iqcn_key')
    iqcn_secret = fields.Char(string="IQ Cashnow Secret", related='journal_id.iqcn_secret')
    provider = fields.Selection(selection_add=[('iqcn', _('IQ Cashnow'))])

    @api.multi
    def iqcn_get_form_action_url(self):
        # We do inject the tx_url in the context in the render function
        return None

    @api.multi
    def render(self, reference, amount, currency_id, partner_id=False, values=None):
        if not self.provider == 'iqcn':
            return super(PaymentAcquirerIQCN, self).render(reference, amount, currency_id, partner_id, values)
        currency_record = self.env['res.currency'].browse(currency_id)
        callback_url = urls.url_join(self.env['ir.config_parameter'].sudo().get_param('web.base.url'), "/payment/iqcn/callback")
        success_url = urls.url_join(self.env['ir.config_parameter'].sudo().get_param('web.base.url'), "/shop/payment/validate")
        cancel_url = urls.url_join(self.env['ir.config_parameter'].sudo().get_param('web.base.url'), "/shop/payment")
        try:
            payment_data = self.iqcn_transaction(
                name=reference,
                amount=amount,
                reference=reference,
                currency=currency_record.name,
                target_currency=self.env.context.get('crypto_currency'),
                description=reference,
                callback_url=callback_url,
                success_url=success_url,
                cancel_url=cancel_url,
            )
        except Exception as e:
            traceback.print_exc()
            raise UserError("Error while creating IQCashnow Payment: %r" % e)
        # Inject tx_url here in the context
        res = super(PaymentAcquirerIQCN, self.with_context({'tx_url': payment_data['invoice_url']})).render(reference, amount, currency_id, partner_id, values)
        return res

    @api.multi
    def iqcn_form_generate_values(self, tx_values):
        # Dummy function - because we did the work already in the render function
        return tx_values

    def test_connection(self):
        return

    def iqcn_transaction(self, name, amount, reference, currency, target_currency="", description="", callback_url="", success_url="", cancel_url=""):
        iq_api = iqcnapi.IQCashNow(key=self.iqcn_key, secret=self.iqcn_secret, host=self.iqcn_host)
        response = iq_api.payment_request(name=str(name), price=str(amount), reference=str(reference), currency=str(currency), target_currency=target_currency, description=description, callback_url=callback_url, success_url=success_url, cancel_url=cancel_url)
        return response

    def invoice_payment(self, data):
        iq_api = iqcnapi.IQCashNow(key=self.iqcn_key, secret=self.iqcn_secret, host=self.iqcn_host)
        response = iq_api.invoice_payment_request(data)
        return response

    def create_payment(self, currency, price):
        iq_api = iqcnapi.IQCashNow(key=self.iqcn_key, secret=self.iqcn_secret, host=self.iqcn_host)
        response = iq_api.create_payment(currency=str(currency), price=str(price))
        return response

    def payment_status(self, payment_id):
        iq_api = iqcnapi.IQCashNow(key=self.iqcn_key, secret=self.iqcn_secret, host=self.iqcn_host)
        response = iq_api.payment_status(payment_id=str(payment_id))
        return response
