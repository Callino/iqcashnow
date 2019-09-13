# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ABStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    iqcn_payment_id = fields.Char('IQCN Payment ID')
    iqcn_status_id = fields.Char('IQCN Status ID')
    iqcn_status_text = fields.Char('IQCN Status Text')
    iqcn_payment_currency = fields.Char('IQCN Payment Currency')
    iqcn_payment_amount = fields.Char('IQCN Payment Amount')
    iqcn_payment_url = fields.Char('IQCN Payment URL')
    iqcn_valid_until = fields.Char('IQCN Valid Until')
    iqcn_payment_address = fields.Char('IQCN Payment Address')
