# -*- coding: utf-8 -*-
{
    'name': 'Add image to sale report',
    'summary': """
            Agrega imagen de art{iculo a pdf de venta
    """,
    'description': """ 
            Agrega imagen de art{iculo a pdf de venta
    """,
    'author': "Marco",
    'website': "https://tekniu.mx",

    'category': 'Other',
    'version': '0.1',
    'application': False,
    'external_dependencies': {
        'python': [
        ],
    },
    'depends': [
        'base','sale'
    ],
    # always loaded
    'data': [
        'views/image_sale_format_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
