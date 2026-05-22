{
    'name': 'Garage WhatsApp Notifications',
    'version': '16.0.1.0.0',
    'category': 'Services/Garage',
    'summary': 'WhatsApp notifications for Garage Management via Twilio',
    'author': 'Manoja Somarathna',
    'license': 'LGPL-3',
    'depends': ['garage_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/whatsapp_config_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
