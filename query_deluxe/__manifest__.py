{
        'name': 'Requête de luxe PostgreSQL',
        'description': 'Requettage sur postgreSQL à partir de l\'interface de ODOO',
        'author': 'SOTEC',
        'depends': ['base', 'mail'],
        'application': True,
        'version': '14.0.1.0.4',
        'license': 'AGPL-3',
        'support': 'wmyameogo@songo-technologie.com',
        'website': 'https://songotechnologies.com',
        'installable': True,

        'data': [
            'security/security.xml',
            'security/ir.model.access.csv',

            'views/query_deluxe_views.xml',

            'wizard/pdforientation.xml',

            'report/print_pdf.xml',

            'datas/data.xml'
            ],

        'images': ['static/description/banner.gif']
}

