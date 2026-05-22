{
    'name': 'Garage Management System',
    'version': '16.0.1.0.0',
    'category': 'Services/Garage',
    'summary': 'AI-powered Garage & Vehicle Service Management',
    'description': """
        Complete Garage Management Solution for Sri Lanka
        - Vehicle & Customer Management
        - Job Cards / Service Orders
        - Parts Inventory
        - AI Service Reminders
        - WhatsApp Notifications
        - Revenue Dashboard
    """,
    'author': 'Manoja Somarathna',
    'website': 'https://github.com/manojasomarathna/AI-Garage-Management-System',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'product', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/vehicle_views.xml',
        'views/service_order_views.xml',
        'views/service_history_views.xml',
        'views/reminder_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}
