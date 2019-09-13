# coding: utf-8
# Copyright 2019 Callino - Pichler Wolfgang, Gerhard Baumgartner
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import logging

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError

_logger = logging.getLogger(__name__)


class PaymentTransactionIQCN(models.Model):
    _inherit = 'payment.transaction'

    iqcn_invoice_url = fields.Char('IQCN Url')
    iqcn_id = fields.Integer('IQCN ID')
    iqcn_address = fields.Char('IQCN Address')
    iqcn_valid_until_time = fields.Datetime('IQCN valid until')

    @api.model
    def _iqcn_form_get_tx_from_data(self, data):
        reference = data.get('payment_id')
        if not reference:
            error_msg = _('ICQN: received data with missing reference (%s)') % (reference, )
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        txs = self.env['payment.transaction'].search([('acquirer_reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'ICQN: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no transaction found'
            else:
                error_msg += '; multiple transactions found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    @api.multi
    def _iqcn_s2s_get_tx_status(self):
        result = self.acquirer_id.iqcn_payment_status(self.acquirer_reference)
        return result

    @api.multi
    def _iqcn_form_validate(self, data):
        status_id = data.get('status_id')
        res = {
        }
        # Callback will be triggered after payment procedure - so there should only be 2 states
        # payment success
        if status_id == '1':
            _logger.info('Validated ICQN payment for tx %s: set as done' % (self.reference))
            date = fields.Datetime.now()
            res.update(date=date)
            self._set_transaction_done()
            self.write(res)
            return True
        # payment failure
        else:
            error = 'Received unrecognized status for Paypal payment %s: %s, set as error' % (self.reference, status_id)
            _logger.info(error)
            res.update(state_message=error)
            self._set_transaction_cancel()
            self.write(res)
            return False
