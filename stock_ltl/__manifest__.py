{
    "name": "STOCK CHANTIER - SOTEC",
    "Summary": "Gestion de stock chantier",
    "sequence": 1,
    "version": "1.0",
    "author": "Songo Technonogies (SOTEC)",
    "depends": ["base", "mail"],
    'images': ['static/description/production.jpg'],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml", "views/donnee.xml",
        "views/stock.xml", "views/reporting.xml",
        "views/depense.xml", "report/report.xml",
        "data/data.xml",
        ],
    "category": "ENTREPRISE PRIVEE",
    "installable": True,
    "auto_install": False,
}
