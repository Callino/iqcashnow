# coding: utf-8
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date
import hashlib
import uuid
import json
import werkzeug
from random import randint


class IQCashNowAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def generate_token(self):
        token = hashlib.sha1((str(uuid.uuid4()) + str(self.id)).encode('utf-8')).hexdigest()
        while self.env['account.invoice'].search([('token', '=', token)]):
            token = hashlib.sha1((self.ref + str(randint(0, 999))).encode('utf-8')).hexdigest()
        self.write({'token': token})

    @api.multi
    @api.depends('token')
    def _get_token_url(self):
        for record in self:
            if record.token:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                record.token_url = base_url + "/invoice/iqcn/" + record.token

    @api.onchange('partner_id')
    def onchange_partner_iqcn(self):
        if self.partner_id and self.partner_id.iqcn_payment:
            self.iqcn_payment = True

    @api.onchange('iqcn_payment')
    def onchange_iqcn_payment(self):
        if self.iqcn_payment:
            self.payment_acquirer_id = self.env['payment.acquirer'].search([('provider', '=', 'iqcn'), ('company_id', '=', self.company_id.id)], limit=1).id

    iqcn_payment = fields.Boolean("Use IQCN")
    payment_acquirer_id = fields.Many2one('payment.acquirer', string="IQCN Payment")
    payment_url = fields.Char(string="Payment URL")
    payment_id_iqcn = fields.Char(string="Payment ID")
    payment_address_iqcn = fields.Char(string="Payment Address")
    payment_valid_until_iqcn = fields.Char(string="Payment Valid Until")
    token = fields.Char(string="Token", copy=False)
    token_url = fields.Char(string="Token URL", compute=_get_token_url, store=True, copy=False)

    _sql_constraints = [
        ('token',
         'unique(token)',
         'Token must be unique!')
    ]

    @api.model
    def create(self, vals):
        res = super(IQCashNowAccountInvoice, self).create(vals)
        if res.partner_id.iqcn_payment:
            res.iqcn_payment = True
        res.generate_token()
        return res

    @api.multi
    def action_invoice_open(self):
        res = super(IQCashNowAccountInvoice, self).action_invoice_open()
        for record in self:
            if record.state == 'open' and record.iqcn_payment:
                record.create_icqn_payment()
        return res

    @api.multi
    def create_icqn_payment(self):
        self.ensure_one()
        if not self.payment_acquirer_id:
            raise UserError("This invoices is is missing a payment acquirer.")
        iqcn_pa = self.payment_acquirer_id
        try:
            payment_data = json.loads(iqcn_pa.create_payment(self.currency_id.name, self.amount_total))
            self.message_post(body="IQCN Payment created: \n\n %r" % payment_data)
            self.payment_url = payment_data['qr_code']
            self.payment_id_iqcn = payment_data['id']
            self.payment_address_iqcn = payment_data['address']
            self.payment_valid_until_iqcn = payment_data['valid_until_time']
        except Exception as e:
            raise UserError("Error while creating IQCashNow Payment: %r" % e)
        return

    @api.model
    def build_qr_code_url(self, url):
        qr_code_url = '/report/barcode/?type=%s&value=%s&width=%s&height=%s&humanreadable=1' % (
        'QR', werkzeug.url_quote_plus(url), 256, 256)
        return qr_code_url

    @api.model
    def check_open_iqcn_payments(self):
        invocies = self.env['account.invoice'].search([('state', '=', 'open'), ('iqcn_payment', '=', True)])
        for invoice in invocies:
            invoice.check_payment_status()

    @api.multi
    def check_payment_status(self):
        for record in self:
            if not record.payment_acquirer_id:
                raise UserError("This invoices is is missing a payment acquirer.")
            iqcn_pa = record.payment_acquirer_id
            payment_status = json.loads(iqcn_pa.payment_status(record.payment_id_iqcn))
            self.message_post(body="IQCN Payment status update: \n\n %r" % payment_status)
            if payment_status['status_id'] == 1:
                payment = self.env['account.payment'].create({
                    'journal_id': record.journal_id.id,
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'amount': record.amount_total,
                    'partner_id': record.partner_id.id,
                    'payment_date': date.today(),
                    'communication': payment_status['payment_id'],
                    'invoice_ids': [(6, 0, record.ids)],
                })
                payment.post()
