# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class pos_config(models.Model):
    _name = 'pos.config'
    _inherit = 'pos.config'

    auto_icqn_payment = fields.Boolean(string="ICQN Transaktion automatisch", default=True)
