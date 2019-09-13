odoo.define('pos_iq_cash_now.pos', function (require) {
    "use strict";

    var core = require('web.core');
    var QWeb = core.qweb;
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var chrome = require('point_of_sale.chrome');
    var devices = require('point_of_sale.devices');
    var gui = require('point_of_sale.gui');
    var _t = core._t;

    // Include the iqcn fields on load of account.journal
    models.load_fields("account.journal", ["is_iqcn_journal", "iqcn_key", "iqcn_secret", "iqcn_host"]);

    // Define our own IQCN Class - does provide all IQCN related functions
    var IQCN = core.Class.extend({

        init: function (attributes) {
            this.pos = attributes.pos;
        },

        send_current_iqcn_payment_to_customer_facing_display: function(qr_code) {
            var self = this;
            this.pos.render_html_for_customer_facing_display().then(function (rendered_html) {
                var $rendered_html = $(rendered_html);
                if (qr_code) {
                    var canvas = $('<div class="pos-adv"></div>').qrcode({width: 450, height: 450, text: qr_code});
                    var dataURL = canvas.find("canvas")[0].toDataURL('image/png');
                    var canvas_img = $("<img src='" + dataURL + "' alt='from canvas'/>");
                    $rendered_html.find('.pos-adv').html(canvas_img);
                    $rendered_html.find('.pos-adv').attr("style", "background: #fff;text-align:center;padding-top:25px;")
                }
                rendered_html = _.reduce($rendered_html, function (memory, current_element) {
                    return memory + $(current_element).prop('outerHTML');
                }, "");

                rendered_html = QWeb.render('CustomerFacingDisplayHead', {
                    origin: window.location.origin
                }) + rendered_html;
                self.pos.proxy.update_customer_facing_display(rendered_html);
            });
        },

        iqcn_payment_select_currency: function (line) {
            var self = this;
            this.pos.gui.popup_instances.iqcn_select_currency.show({payment_line: line});
        },

        iqcn_payment_currency_selected: function (line, currency) {
            var self = this;
            this.pos.iqcn.iqcn_payment_start(line, currency);
        },

        iqcn_payment_start: function (line, crypto_currency) {
            var self = this;
            var transaction_amount = line.get_iqcn_transaction_amount();
            if (transaction_amount <= 0) {
                return;
            }
            this.pos.gui.popup_instances.iqcn_idle.show();
            line.iqcn_transaction = true;
            $('.payment-iqcn-transaction-start[data-cid=' + line.id + ']').addClass('oe_hidden');
            var nonce = $.now();
            var form_data = new FormData();
            form_data.append("currency", self.pos.currency.name);
            form_data.append("price", transaction_amount.toString());
            form_data.append("ref", line.order.name);
            form_data.append("target_currency", crypto_currency ? crypto_currency : "BTC");
            form_data.append("sandbox", "0");
            $.ajax({
                url: line.cashregister.journal.iqcn_host + "/v2/?a=createPayment",
                type: 'post',
                data: form_data,
                contentType: false,
                processData: false,
                headers: {
                    'X-IQCashNow-Key': line.cashregister.journal.iqcn_key,
                    'X-IQCashNow-Nonce': nonce,
                    'X-IQCashNow-Signature': CryptoJS.HmacSHA512("/v2/?a=createPayment" + nonce + CryptoJS.SHA256(JSON.stringify(form_data)), line.cashregister.journal.iqcn_secret)
                },
            }).then(
                function done(result) {
                    line.iqcn_transaction = false;
                    if (!result.qr_code) {
                        self.pos.gui.show_popup('error', {
                            'title': _t('Error'),
                            'body': _t('Failed to initialize transaction.'),
                        });
                    }
                    line.set_amount(transaction_amount);
                    line.iqcn_payment_id = result.id;
                    line.iqcn_payment_url = result.qr_code;
                    line.iqcn_payment_address = result.address;
                    line.iqcn_valid_until = result.valid_until_time;
                    line.iqcn_payment_currency = self.pos.currency.name;
                    line.iqcn_payment_amount = transaction_amount;
                    line.order.save_to_db();
                    self.pos.gui.popup_instances.iqcn_idle.hide();
                    self.iqcn_payment_status(line);
                    self.pos.gui.popup_instances.iqcn_qr_code.show({
                        payment_line: line
                    });
                    self.send_current_iqcn_payment_to_customer_facing_display(result.qr_code)
                },
                function failed(result) {
                    self.pos.gui.popup_instances.iqcn_idle.hide();
                    line.iqcn_transaction = false;
                    line.order.remove_paymentline(line);
                    self.pos.gui.show_popup('error', {
                        'title': _t('Error'),
                        'body': _t('Failed to initialize transaction.'),
                    });
                }
            );
        },

        iqcn_payment_abort: function(line) {
            var self = this;
            line.iqcn_status_id = 99;
            line.iqcn_status_text = _t("Payment aborted");
            line.set_amount(0);
            line.set_iqcn_transaction_amount(0);
            self.pos.gui.screen_instances.payment.render_paymentlines();
        },

        iqcn_payment_status: function (line) {
            if (line == null) {
                console.log("Do disable check payment state");
                return;
            }
            if (line.iqcn_status_id == 99) {
                console.log("Do disable check payment state because payment got aborted");
                return;
            }
            if (line.iqcn_status_check_active) {
                return;
            }
            line.iqcn_status_check_active = true;
            var self = this;
            console.log("Checking Payment Status.");
            var nonce = $.now();
            var form_data = new FormData();
            form_data.append("payment_id", line.iqcn_payment_id);
            $.ajax({
                url: line.cashregister.journal.iqcn_host + "/v2/?a=getStatus",
                type: 'post',
                data: form_data,
                contentType: false,
                processData: false,
                headers: {
                    'X-IQCashNow-Key': line.cashregister.journal.iqcn_key,
                    'X-IQCashNow-Nonce': nonce,
                    'X-IQCashNow-Signature': CryptoJS.HmacSHA512("/v2/?a=createPayment" + nonce + CryptoJS.SHA256(JSON.stringify(form_data)), line.cashregister.journal.iqcn_secret),
                    'sandbox': ""
                },
            }).then(
                function done(result) {
                    console.log("Status: " + result['status_text']);
                    switch (result.status_id) {
                        case "1":
                            line.iqcn_status_id = 1;
                            line.iqcn_status_text = "payment done";
                            line.order.save_to_db();
                            self.pos.gui.popup_instances.iqcn_qr_code.payment_success();
                            self.pos.gui.screen_instances.payment.render_paymentlines();
                            self.pos.gui.screen_instances.payment.validate_order();
                            break;
                        case "2":
                            // Waiting for payment
                            if (line.iqcn_status_id == 99) {
                                // Payment got aborted - so do not check again
                                break;
                            }
                            line.iqcn_status_id = 2;
                            line.iqcn_status_text = result['status_text'];
                            self.pos.gui.screen_instances.payment.render_paymentlines();
                            line.iqcn_status_check_active = false;
                            setTimeout(self.iqcn_payment_status(line), 5000);
                            break;
                        case "3":
                            line.iqcn_status_check_active = false;
                            setTimeout(self.iqcn_payment_status(line), 5000);
                            break;
                        case "4":
                            self.pos.gui.show_popup('error',{
                                'title': _t('Invalide Zahlung'),
                                'body': _t('Die Zahlung konnte nicht ordnungsgemäß durchgeführt werden.'),
                            });
                            break;
                        default:
                            break;
                    }
                },
                function failed(result) {
                    if (line) {
                        line.iqcn_status_check_active = false;
                        setTimeout(self.iqcn_payment_status(line), 5000);
                    }
                    self.gui.show_popup('error',{
                        'title': _t('Failure'),
                        'body': _t('Failed to start transaction'),
                    });
                }
            );
        }

    });

    var PosModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            // Call super call
            PosModelSuper.prototype.initialize.apply(this, arguments);
            // Do connect initialize MPD Class
            this.iqcn = new IQCN({'pos': this});
        }
    });

    // Extend PaymentScreenWidget
    screens.PaymentScreenWidget.include({
        render_paymentlines: function () {
            // Supercall using prototype
            this._super();
            var container = this.$('.paymentlines-container');
            // Register gui hooks
            var self = this;
            // Do unbind click events first
            container.off('click', '.payment-icqn-transaction-start');
            container.off('click', '.payment-icqn-transaction-open');
            // Bind on the new icqn payment button
            container.on('click', '.payment-icqn-transaction-start', function (event) {
                var line_cid = $(this).data('cid');
                var order = self.pos.get_order();
                var line = order.paymentlines._byId[line_cid];
                self.pos.iqcn.iqcn_payment_select_currency(line);
            }).on('click', '.payment-icqn-transaction-open', function (event) {
                var line_cid = $(this).data('cid');
                var order = self.pos.get_order();
                var line = order.paymentlines._byId[line_cid];
                self.pos.gui.popup_instances.iqcn_qr_code.show({
                    payment_line: line
                });
            });
            var order = this.pos.get_order();
            if (!order) {
                return;
            }
            // check for open payments open qr_code screen if its the case
            order.paymentlines.each(function (paymentLine) {
                if (paymentLine.iqcn_payment_url && paymentLine.iqcn_status_id != '1') {
                    // Enable payment status check on payment line
                    self.pos.iqcn.iqcn_payment_status(paymentLine);
                }
            });
        },
        payment_input: function (input) {
            var order = this.pos.get_order();
            if ((order.selected_paymentline) && (order.selected_paymentline.iqcn_status_id)) {
                // Do not let the user change the amount on payment lines with a ref_number
                console.log('Do not let the user change the amount on payment lines with a ref_number');
                return;
            }
            this._super.apply(this, arguments);
        }

    });

    // Extend Order Model
    // remove_paymentline: function in Order Model - if there is a ref number attached - then we need to do a reversal
    // add_paymentline: store the amount to pay in transaction_amount - and set paid amount to 0
    var OrderModelParent = models.Order;
    models.Order = models.Order.extend({
        remove_paymentline: function (line) {
            console.log('in remove_paymentline');
            if (line.iqcn_status_id) {
                // Do not remove - there is a payment already on this line
                console.log('do not remove - there is a payment or pending payment already on this line');
                return false;
            }
            // Normal Super Call
            OrderModelParent.prototype.remove_paymentline.apply(this, arguments);
        },
        add_paymentline: function (cashregister) {
            // Get open amount before we add the payment line
            var open_amount = this.get_due();
            // Do make super call
            OrderModelParent.prototype.add_paymentline.apply(this, arguments);
            // Check - if this is a icqn payment line - then set amount to 0 !
            if (cashregister.journal.is_iqcn_journal) {
                this.selected_paymentline.set_iqcn_transaction_amount(open_amount);  // this.selected_paymentline.get_amount()
                this.selected_paymentline.set_amount(0);
                this.pos.gui.screen_instances.payment.render_paymentlines();
                // Check if auto transaction is enabled - if so - then start it here
                if (this.pos.config.auto_icqn_payment) {
                    this.pos.iqcn.iqcn_payment_select_currency(this.selected_paymentline);
                }
            }
        }
    });

    // Extend Paymentline Model
    var PaymentlineModelParent = models.Paymentline;
    models.Paymentline = models.Paymentline.extend({
        // Add iqcn data to json export
        add_iqcn_data_json: function(json) {
            json['iqcn_payment_id'] = this.iqcn_payment_id;
            json['iqcn_payment_url'] = this.iqcn_payment_url;
            json['iqcn_status_id'] = this.iqcn_status_id;
            json['iqcn_status_text'] = this.iqcn_status_text;
            json['iqcn_payment_currency'] = this.iqcn_payment_currency;
            json['iqcn_payment_amount'] = this.iqcn_payment_amount;
            json['iqcn_payment_address'] = this.iqcn_payment_address;
            json['iqcn_valid_until'] = this.iqcn_valid_until;
            json['iqcn_transaction_amount'] = this.iqcn_transaction_amount;
            return json;
        },
        export_as_JSON: function () {
            var json = PaymentlineModelParent.prototype.export_as_JSON.apply(this, arguments);
            return this.add_iqcn_data_json(json);
        },
        init_from_JSON: function (json) {
            PaymentlineModelParent.prototype.init_from_JSON.apply(this, arguments);
            this.iqcn_transaction_amount = json['iqcn_transaction_amount'];
            this.iqcn_payment_id = json['iqcn_payment_id'];
            this.iqcn_status_id = json['iqcn_status_id'];
            this.iqcn_status_text = json['iqcn_status_text'];
            this.iqcn_payment_url = json['iqcn_payment_url'];
            this.iqcn_payment_currency = json['iqcn_payment_currency'];
            this.iqcn_payment_amount = json['iqcn_payment_amount'];
            this.iqcn_payment_address = json['iqcn_payment_address'];
            this.iqcn_valid_until = json['iqcn_valid_until'];
        },
        //sets the amount of money on this payment line for sixx transaction
        set_iqcn_transaction_amount: function (value) {
            this.iqcn_transaction_amount = value;
            this.trigger('change', this);
        },
        // returns the amount of money on this paymentline for transaction
        get_iqcn_transaction_amount: function () {
            return this.iqcn_transaction_amount;
        },
    });

    var ProxyDeviceSuper = devices.ProxyDevice;
    devices.ProxyDevice = devices.ProxyDevice.extend({
        // ask for the cashbox (the physical box where you store the cash) to be opened
        open_cashbox: function (force) {
            if (force) {
                return ProxyDeviceSuper.prototype.open_cashbox.apply(this, arguments);
            }
            // Here - get current order - check payment statements - if there is any statement other than icqn - then open it - else - let it closed
            var currentOrder = this.pos.get('selectedOrder');
            var plines = currentOrder.paymentlines.models;
            if (plines.length == 0) {
                return ProxyDeviceSuper.prototype.open_cashbox.apply(this, arguments);
            }
            var open_cashdrawer = false;
            for (var i = 0; i < plines.length; i++) {
                if (!plines[i].cashregister.journal.is_iqcn_journal) {
                    open_cashdrawer = true;
                    break;
                }
            }
            if (open_cashdrawer) {
                // Super Call
                return ProxyDeviceSuper.prototype.open_cashbox.apply(this, arguments);
            }
        },
    });

    // This is used to show the QR Code containing the payment link
    // Also checks for Status Updates, finalizes payments
    var IQCN_QRCodeWidget = chrome.StatusWidget.extend({
        template: 'IQCN_QRCodeWidget',
        init: function (pos, options) {
            this._super(pos, options);
        },
        installEventHandler: function () {
            var self = this;
            this.$('#iqcn_payment_successful').off();
            this.$('#iqcn_payment_successful').on('click', this.pos, function (event) {
                self.payment_success(this.pos, event)
            });
            this.$('#iqcn_payment_abort').off();
            this.$('#iqcn_payment_abort').on('click', this.pos, function (event) {
                self.payment_abort(this.pos, event)
            });
        },
        show: function (show_options) {
            this._super(show_options);
            this.payment_line = show_options['payment_line'];
            this.installEventHandler();
            this.$el.find('#qrcode').empty();
            this.$el.find('#qrcode').qrcode({width: 512, height: 512, text: this.payment_line.iqcn_payment_url});
        },
        hide: function () {
            if (this.$el) {
                this.$el.addClass('oe_hidden');
            }
        },
        loading: function (message) {
            this.$('.content').addClass('oe_hidden');
            this.$('.loading').removeClass('oe_hidden');
            this.$('.loading').html(message);
        },
        loading_done: function () {
            this.$('.content').removeClass('oe_hidden');
            this.$('.loading').addClass('oe_hidden');
        },
        payment_success: function () {
            this.hide();
        },
        payment_abort: function () {
            this.pos.iqcn.iqcn_payment_abort(this.payment_line);
            this.payment_line = null;
            this.hide();
        },

    });
    gui.define_popup({name: 'iqcn_qr_code', widget: IQCN_QRCodeWidget});

    var IQCN_IdleWidget = chrome.StatusWidget.extend({
        template: 'IQCN_IdleWidget',
        init: function (pos, options) {
            this._super(pos, options);
        },
        show: function (show_options) {
            this._super(show_options);
        },
        hide: function () {
            if (this.$el) {
                this.$el.addClass('oe_hidden');
            }
        },
    });
    gui.define_popup({name: 'iqcn_idle', widget: IQCN_IdleWidget});

    var IQCN_SelectCurrencyWidget = chrome.StatusWidget.extend({
        template: 'IQCN_SelectCurrencyWidget',
        init: function (pos, options) {
            this._super(pos, options);
        },
        installEventHandler: function () {
            var self = this;
            this.$('.crypto-select').off();
            this.$('.crypto-select').on('click', this.pos, function (event) {
                self.currency_selected(event.currentTarget.getAttribute('code'))
            });
            this.$('#iqcn_currency_select_abort').off();
            this.$('#iqcn_currency_select_abort').on('click', this.pos, function (event) {
                self.abort()
            });
        },
        show: function (show_options) {
            this._super(show_options);
            this.payment_line = show_options['payment_line'];
            this.installEventHandler();
        },
        hide: function () {
            if (this.$el) {
                this.$el.addClass('oe_hidden');
            }
        },
        abort: function() {
            this.pos.iqcn.iqcn_payment_abort(this.payment_line);
            this.payment_line = null;
            this.hide();
        },
        currency_selected: function(currency) {
            this.pos.iqcn.iqcn_payment_currency_selected(this.payment_line, currency);
            this.hide();
        }
    });
    gui.define_popup({name: 'iqcn_select_currency', widget: IQCN_SelectCurrencyWidget});

});
