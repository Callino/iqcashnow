# -*- coding: utf-8 -*-
{
    'name': 'POS IQ Cashnow Integration',
    'version': '12.0.1.0',
    'category': 'Point of Sale',
    'summary': 'POS IQ Cashnow Integration',
    'website': 'https://github.com/Callino/iqcashnow',
    'author': 'Wolfgang Pichler (Callino), Gerhard Baumgartner (Callino)',
    'license': 'AGPL-3',
    'description': """
POS IQ Cashnow Integration
=============================
Customer can pay using crypto currency on your pos
""",
    'depends': ['point_of_sale', 'payment_iqcashnow'],
    'test': [
    ],
    'data': [
        'views/templates.xml',
        'views/pos_order.xml',
        'views/pos_config.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'application': False,
    'installable': True,
    'auto_install': True,
}
