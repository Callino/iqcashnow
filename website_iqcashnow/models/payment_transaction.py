# coding: utf-8
# Copyright 2019 Callino - Pichler Wolfgang, Gerhard Baumgartner
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import logging

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError

_logger = logging.getLogger(__name__)


class PaymentTransactionIQCN(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _iqcn_form_get_tx_from_data(self, data):
        reference = data.get('reference')
        if not reference:
            error_msg = _('ICQN: received data with missing reference (%s)') % (reference, )
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
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
    def _iqcn_form_validate(self, data):
        status = data.get('status')
        res = {
            'acquirer_reference': data.get('id'),
        }
        # Callback will be triggered after payment procedure - so there should only be 2 states
        # payment success
        if status in ['completed']:
            _logger.info('Validated ICQN payment for tx %s: set as done' % (self.reference))
            date = fields.Datetime.now()
            res.update(date=date)
            self._set_transaction_done()
            return self.write(res)
        # payment failure
        else:
            error = 'Received unrecognized status for Paypal payment %s: %s, set as error' % (self.reference, status)
            _logger.info(error)
            res.update(state_message=error)
            self._set_transaction_cancel()
            return self.write(res)
