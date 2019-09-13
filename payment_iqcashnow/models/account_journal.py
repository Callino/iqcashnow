# coding: utf-8
# Copyright 2019 Callino - Pichler Wolfgang, Gerhard Baumgartner
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models, _
from ..iqcashnow.iqcashnow import api as iqcnapi


class IQCashNowJournal(models.Model):
    _inherit = 'account.journal'

    @api.onchange('iqcn_host', 'iqcn_key', 'iqcn_secret')
    def onchange_credentials(self):
        self.iqcn_connection_confirmed = False

    is_iqcn_journal = fields.Boolean(string="IQ Cashnow Journal", default=False)
    iqcn_connection_confirmed = fields.Boolean(string="Connection", default=False)
    iqcn_host = fields.Char(string="Host", default="https://api.iqcashnow.com/")
    iqcn_key = fields.Char(string="Key")
    iqcn_secret = fields.Char(string="Secret")

    def test_iqcn_connection(self):
        self.ensure_one()
        try:
            iq_api = iqcnapi.IQCashNow(key=self.iqcn_key, secret=self.iqcn_secret, host=self.iqcn_host)
            iq_api.get_deposit_balance(self.company_id.currency_id.name)
            self.iqcn_connection_confirmed = True
        except:
            self.iqcn_connection_confirmed = False
