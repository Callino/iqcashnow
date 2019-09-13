To configure this module, you need to:

* Register within https://www.iqcashnow.com/ for an account. You will receive a key / secret pair

* Go to Invoicing > Configuration > Journals - there is a new journal called "IQ Cashnow". Do configure this journal with your credentials from the first step.

.. figure:: https://raw.githubusercontent.com/Callino/iqcashnow/12.0/payment_iqcashnow/static/screenshots/account_journal.png
   :alt: Odoo Journal configuration
   :width: 80 %
   :align: center

* Go to Invoicing -> Configuration -> Payment Acquirers - Open the payment acquirer IQCashnow. Switch to the Configuration tab, and select the IQCashnow journal. Do activate the payment aqcuirer and disable the test mode.

.. figure:: https://raw.githubusercontent.com/Callino/iqcashnow/12.0/website_iqcashnow/static/screenshots/payment_acquirer.png
   :alt: Odoo Payment Acquirer Config
   :width: 80 %
   :align: center
