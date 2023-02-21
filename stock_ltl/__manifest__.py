{
    "name": "LTL STOCK",
    "Summary": "Gestion de stock LTL",
    "sequence": 1,
    "version": "1.0",
    "author": "OURNO Mohamed Kabir",
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
