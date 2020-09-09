# -*- encoding: utf-8 -*-
{
    'name': "Feedback de usuario",
    'version': "1.0",
    'description': u"Módulo de gestión del feedback de usuario",
    'author': "Tekniu, S.A. de C.V.",
    'website': 'https://tekniu.mx',
    'application': True,
    'installable': True,
    'depends': ['base', 'mail'],
    'data': [
        'security/account_security.xml',
        'security/ir.model.access.csv',
        'views/css_template.xml',
        'views/feedback_view.xml',
    ]
}