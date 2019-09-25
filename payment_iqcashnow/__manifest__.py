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
* Invoicing (in the next weeks)

At time Bitcoin and Dash are supported.
More to come like Bitcoin Cash, Ethereum, Litecoin, Monero
    """,
    'version': '12.0.1.0.0',
    'author': 'Wolfgang Pichler (Callino), Gerhard Baumgartner (Callino)',
    'maintainer': 'Callino',
    'development_status': 'stable',
    'website': 'https://github.com/Callino/iqcashnow',
    'license': 'AGPL-3',
    'category': 'Payment',
    'depends': [
        'account', 'payment'
    ],
    'data': [
        'data/account_journal.xml',
        'views/account_journal.xml',
    ],
    "external_dependencies": {

    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'license': 'AGPL-3',
}
