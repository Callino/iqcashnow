# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class IQCNCallbackController(http.Controller):

    @http.route('/invoice/iqcn/<token>', type='http', auth='public', website=True)
    def iqcn_callback(self, token):
        return