# -*- coding: utf-8 -*-
{
    'name': 'POS IQ Cashnow Integration',
    'version': '12.0.0.1',
    'category': 'Point of Sale',
    'sequence': 6,
    'summary': 'POS IQ Cashnow Integration',
    'website': 'https://github.com/Odoo-Austria',
    'author': 'Wolfgang Pichler (Callino), Gerhard Baumgartner (Callino), WT-IO-IT GmbH, Wolfgang Taferner',
    'license': "Other proprietary",
    'description': """
POS IQ Cashnow Integration
=============================

""",
    'depends': ['point_of_sale', 'payment_iqcashnow'],
    'test': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/pos_order.xml',
        'views/pos_config.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'application': False,
    'installable': True,
    'auto_install': True,
}
