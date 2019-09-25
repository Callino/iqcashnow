odoo.define('website_iqcashnow.payment_form', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var Dialog = require('web.Dialog');
    var PaymentForm = require('payment.payment_form');

    var _t = core._t;

    PaymentForm.include({
        init: function(parent, options) {
            this.events['click .iqcashnow-checkbox'] = 'selectCryptoCurrency';
            this._super.apply(this, arguments);
        },

        selectCryptoCurrency: function(el) {
            this.$('.iqcashnow-checkbox').prop("checked", false);
            this.$('#'+el.target.id).prop("checked", true);
            this.$el.find('input[name="prepare_tx_url"]').val('/shop/payment/iqcn_transaction/'+el.target.dataset['currency']);
            this.preventDefault();
        },

    });
});