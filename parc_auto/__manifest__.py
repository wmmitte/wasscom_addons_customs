{
    'name': 'PARC AUTO - SOTEC',
    'version': '1.0',
    'website': '',
    'category': 'Logiciel Parc Auto',
    'summary': "Ce logiciel est conçu pour faciliter la gestion de parc automobile",
    'author': 'Songo Technonogies (SOTEC)',
    'depends': ['base', 'fleet', "mail"],
    'images': ['static/description/auto.jpg'],
    'data': [
        'security/ir.model.access.csv',
        'views/vue_parc.xml',
    ],
    'installable': True,
    'auto_install': False,
}
