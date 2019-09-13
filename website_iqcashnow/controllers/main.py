# coding: utf-8
# Copyright 2019 Callino - Pichler Wolfgang, Gerhard Baumgartner
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import http, _
from odoo.http import request
import logging
import pprint
import json

_logger = logging.getLogger(__name__)


class IQCNController(http.Controller):
    _callback_url = '/payment/iqcn/callback'

    # failure/success calls are not handled here because these will lead to default controllers

    @http.route([_callback_url,], type='json', auth='none', csrf=False, methods=['GET', 'POST'], website=True)
    def iqcn_callback(self, **kwargs):
        _logger.debug('IQCN Payment failure: entering form_feedback with post data %s', pprint.pformat(kwargs))
        _logger.debug('IQCN Post Data: %s', request.httprequest.get_data())
        data = json.loads(request.httprequest.get_data())
        payment_transaction = request.env['payment.transaction'].sudo().search([('reference', '=', data['reference'])])
        # call to default payment.acquirer form_feedback - this will then call specific methods for iqcn
        res = request.env['payment.transaction'].sudo().form_feedback(data, 'iqcn')
        if not res:
            payment_transaction.sudo()._set_transaction_error('Validation error occured. Please contact your administrator.')
        return res

    @http.route('/shop/payment/iqcn/validate/<int:transaction_id>', type='http', auth="public", website=True)
    def payment_validate(self, transaction_id=None, **post):
        tx = request.env['payment.transaction'].sudo().browse(transaction_id)
        # Get current sale.order
        order = request.website.sale_get_order()
        # Transaction must be part of current order
        assert tx.id in order.transaction_ids.ids
        # Check status of transaction
        status = tx.s2s_get_tx_status()
        status['reference'] = tx.acquirer_reference
        res = request.env['payment.transaction'].sudo().form_feedback(status, 'iqcn')
        if not res:
            tx.sudo()._set_transaction_error('Validation error occured. Please contact your administrator.')
            return request.redirect('/shop/payment')
        order.message_post(body="IQCN Payment validated !")
        return request.redirect('/shop/payment/validate')



