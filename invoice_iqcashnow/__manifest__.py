{
    'name': 'IQ Cashnow Invoice',
    'summary': """
        Invoices with IQ Cashnow Payment
        """,

    'description': u"""
IQ Cashnow Invoice
========================================

    Invoices with IQ Cashnow Payment

        Version 1.0

    """,
    'version': '12.0.1.0.0',
    'author': "Callino",
    'maintainer': 'Callino',
    'website': 'http://www.callino.at',
    'license': 'AGPL-3',
    'category': 'Account',
    'depends': [
        'account', 'payment_iqcashnow'
    ],
    'data': [
        'data/cron.xml',
        'views/account_invoice.xml',
        'views/res_partner.xml',
        'reports/invoice_report_document.xml',
    ],
    "external_dependencies": {

    },
    'installable': True,
    'license': 'AGPL-3',
}
