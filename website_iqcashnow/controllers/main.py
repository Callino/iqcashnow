# coding: utf-8
# Copyright 2019 Callino - Pichler Wolfgang, Gerhard Baumgartner
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment.controllers.portal import PaymentProcessing
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


class IQCashnowTransaction(WebsiteSale):

    @http.route('/shop/payment/iqcn_transaction/<string:currency>', type='json', auth='public', website=True)
    def iqcn_transaction(self, currency, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        # Ensure a payment acquirer is selected
        if not acquirer_id:
            return False

        try:
            acquirer_id = int(acquirer_id)
        except:
            return False

        # Retrieve the sale order
        if so_id:
            env = request.env['sale.order']
            domain = [('id', '=', so_id)]
            if access_token:
                env = env.sudo()
                domain.append(('access_token', '=', access_token))
            order = env.search(domain, limit=1)
        else:
            order = request.website.sale_get_order()

        # Ensure there is something to proceed
        if not order or (order and not order.order_line):
            return False

        assert order.partner_id.id != request.website.partner_id.id

        # Create transaction
        vals = {'acquirer_id': acquirer_id,
                'return_url': '/shop/payment/validate'}

        if save_token:
            vals['type'] = 'form_save'
        if token:
            vals['payment_token_id'] = int(token)

        transaction = order._create_payment_transaction(vals)

        # store the new transaction into the transaction list and if there's an old one, we remove it
        # until the day the ecommerce supports multiple orders at the same time
        last_tx_id = request.session.get('__website_sale_last_tx_id')
        last_tx = request.env['payment.transaction'].browse(last_tx_id).sudo().exists()
        if last_tx:
            PaymentProcessing.remove_payment_transaction(last_tx)
        PaymentProcessing.add_payment_transaction(transaction)
        request.session['__website_sale_last_tx_id'] = transaction.id
        return transaction.with_context(crypto_currency=currency).render_sale_button(order)
