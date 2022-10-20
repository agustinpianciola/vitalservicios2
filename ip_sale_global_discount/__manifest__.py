# -*- coding: utf-8 -*-
{
    'name': 'Global Discount on Sale Order & Invoice',
    'summary': "Add option to give global dicount on sale order and Invoice by fix amount or by percentage",
    'description': "Add option to give global dicount on sale order and Invoice by fix amount or by percentage",

    'author': 'iPredict IT Solutions Pvt. Ltd.',
    'website': 'http://ipredictitsolutions.com',
    'support': 'ipredictitsolutions@gmail.com',

    'category': 'Sales',
    'version': '15.0.0.1.0',
    'depends': ['sale_management'],

    'data': [
        'report/sale_report_views.xml',
        'views/sale_discount_views.xml',
        'views/account_move_view.xml',
    ],

    'license': "OPL-1",
    'price': 10,
    'currency': "EUR",

    'auto_install': False,
    'installable': True,

    'images': ['static/description/banner.png'],
    'pre_init_hook': 'pre_init_check',
}
