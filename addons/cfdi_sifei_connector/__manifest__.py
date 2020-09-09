# -*- coding: utf-8 -*-

# This code is part of Odoo/Tekniu project.
# Development by:
# Salvador Daniel Pelayo <daniel@tekniu.mx>

{
    'name': 'Sifei  Connector CFDI 3.3',
    'version': '0.1',
    'description': '''
    Factura Electronica para Mexico (CFDI 3.3): Conector con SIFEI.
    ''',
    'category': 'Accounting',
    'author': 'Salvador Daniel Pelayo Gómez tekniu',
    'website': 'https://tekniu.mx',
    'depends': [
        'cfdi_invoice'
    ],
    'external_dependencies': {
    },
    'data': [
        'views/pac_config_view.xml',
    ],
    'application': False,
    'installable': True,
}
