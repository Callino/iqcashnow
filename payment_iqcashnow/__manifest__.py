# -*- coding: utf-8 -*-
{
    'name': 'IQ Cashnow Payment',
    'summary': """
        Provides basic data and functions for the IQ Cashnow payments
        """,

    'description': u"""
IQ Cashnow
========================================

Does service as base module for the modules which does integrate IQCashnow for
* ECommerce
* POS
* Invoicing
    """,
    'version': '12.0.1.0.0',
    'author': "Callino",
    'maintainer': 'Callino',
    'website': 'https://github.com/Callino/iqcashnow',
    'license': 'AGPL-3',
    'category': 'Payment',
    'depends': [
        'account', 'payment'
    ],
    'data': [
        'data/payment_acquirer.xml',
        'data/account_journal.xml',
        'views/account_journal.xml',
        'views/payment_acquirer.xml',
    ],
    "external_dependencies": {

    },
    'installable': True,
    'license': 'AGPL-3',
}
