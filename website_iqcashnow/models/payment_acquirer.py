# coding: utf-8

import logging
import werkzeug
from werkzeug import urls
import json
import traceback

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PaymentAcquirerIQCN(models.Model):
    _inherit = 'payment.acquirer'

    @api.multi
    def render(self, reference, amount, currency_id, partner_id=False, values=None):
        if not self._context.get('submit_class', False):
            return super(PaymentAcquirerIQCN, self).render(reference, amount, currency_id, partner_id, values)
        currency_record = self.env['res.currency'].browse(currency_id)
        callback_url = urls.url_join(self.env['ir.config_parameter'].sudo().get_param('web.base.url'), "payment/iqcn/callback")
        success_url = urls.url_join(self.env['ir.config_parameter'].sudo().get_param('web.base.url'), "/shop/payment/validate")
        cancel_url = urls.url_join(self.env['ir.config_parameter'].sudo().get_param('web.base.url'), "shop/payment")
        try:
            payment_data = json.loads(self.iqcn_transaction(
                name=reference,
                amount=amount,
                reference=reference,
                currency=currency_record.name,
                description=reference,
                callback_url=callback_url,
                success_url=success_url,
                cancel_url=cancel_url,
            ))
        except Exception as e:
            traceback.print_exc()
            raise UserError("Error while creating IQCashnow Payment: %r" % e)
        qr_code_url = '/report/barcode/?type=%s&value=%s&width=%s&height=%s&humanreadable=1' % (
            'QR', werkzeug.url_quote_plus(payment_data['invoice_url']), 256, 256)
        if not values:
            values = {}
        values.update({
            'qrcode': qr_code_url,
            'tx_url': payment_data['invoice_url'],
        })
        res = super(PaymentAcquirerIQCN, self).with_context({'tx_url': payment_data['invoice_url']}).render(reference, amount, currency_id, partner_id, values)
        return res
