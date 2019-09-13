# -*- coding: utf-8 -*-
{
    'name': 'Webshop IQ Cashnow Integration',
    'version': '12.0.0.1',
    'category': 'ECommerce',
    'sequence': 6,
    'summary': 'Webshop IQ Cashnow Integration',
    'website': 'https://github.com/Odoo-Austria',
    'author': 'Wolfgang Pichler (Callino), Gerhard Baumgartner (Callino)',
    'license': "Other proprietary",
    'description': """
Webshop IQ Cashnow Integration
=============================

""",
    'depends': ['website_sale', 'payment_iqcashnow'],
    'test': [
    ],
    'data': [
        'views/payment_iqcn_templates.xml',
        'data/payment_acquirer.xml',
    ],
    'installable': True,
    'auto_install': False,
}
