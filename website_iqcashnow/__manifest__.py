# -*- coding: utf-8 -*-
{
    'name': 'Webshop IQ Cashnow Integration',
    'version': '12.0.0.1',
    'category': 'ECommerce',
    'sequence': 6,
    'summary': 'Webshop IQ Cashnow Integration',
    'website': 'https://github.com/Odoo-Austria',
    'author': 'Wolfgang Pichler (Callino), Gerhard Baumgartner (Callino)',
    'license': 'AGPL-3',
    'description': """
Webshop IQ Cashnow Integration
=============================
Accept crypto currency payments in your webshop
""",
    'depends': ['website_sale', 'payment_iqcashnow'],
    'test': [
    ],
    'data': [
        'views/payment_iqcn_templates.xml',
        'views/payment_acquirer.xml',
        'data/payment_acquirer.xml',
    ],
    'installable': True,
    'auto_install': False,
}
