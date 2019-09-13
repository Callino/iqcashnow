# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _payment_fields(self, ui_paymentline):
        values = super(PosOrder, self)._payment_fields(ui_paymentline)
        _logger.info("got payment line values %r", ui_paymentline)
        values['iqcn_payment_id'] = (ui_paymentline['iqcn_payment_id'] if 'iqcn_payment_id' in ui_paymentline else None)
        values['iqcn_status_id'] = (ui_paymentline['iqcn_status_id'] if 'iqcn_status_id' in ui_paymentline else None)
        values['iqcn_status_text'] = (ui_paymentline['iqcn_status_text'] if 'iqcn_status_text' in ui_paymentline else None)
        values['iqcn_payment_currency'] = (ui_paymentline['iqcn_payment_currency'] if 'iqcn_payment_currency' in ui_paymentline else None)
        values['iqcn_payment_amount'] = (ui_paymentline['iqcn_payment_amount'] if 'iqcn_payment_amount' in ui_paymentline else None)
        values['iqcn_payment_url'] = (ui_paymentline['iqcn_payment_url'] if 'iqcn_payment_url' in ui_paymentline else None)
        values['iqcn_valid_until'] = (ui_paymentline['iqcn_valid_until'] if 'iqcn_valid_until' in ui_paymentline else None)
        values['iqcn_payment_address'] = (ui_paymentline['iqcn_payment_address'] if 'iqcn_payment_address' in ui_paymentline else None)
        return values

    @api.model
    def add_payment(self, data):
        _logger.info("add payment got called with data %r", data)
        orig_payment_name = None
        if 'iqcn_payment_id' in data and data['iqcn_payment_id']:
            orig_payment_name = (data['payment_name'] if 'payment_name' in data else None)
            data['payment_name'] = data['iqcn_payment_id']
        statement_id = super(PosOrder, self).add_payment(data)
        # Here do update the statement - include iqcn data
        if 'iqcn_payment_id' in data and data['iqcn_payment_id']:
            name = self.name + ': ' + (data.get('payment_name', '') or '')
            statement_line_obj = self.env['account.bank.statement.line']
            line_statement_id = statement_line_obj.search([('name', '=', name),('statement_id','=',statement_id)])
            # do write iqcn ref number - and bring back old name
            line_statement_id.write({
                'iqcn_payment_id': data['iqcn_payment_id'],
                'iqcn_status_id': data['iqcn_status_id'],
                'iqcn_status_text': data['iqcn_status_text'],
                'iqcn_payment_currency': data['iqcn_payment_currency'],
                'iqcn_payment_amount': data['iqcn_payment_amount'],
                'iqcn_payment_url': data['iqcn_payment_url'],
                'iqcn_valid_until': data['iqcn_valid_until'],
                'iqcn_payment_address': data['iqcn_payment_address'],
                'name': self.name + ': ' + (orig_payment_name or ''),
            })
        return statement_id
