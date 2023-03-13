{
    "name": "COMPTABILITE - SOTEC",
    "version": "1.0",
    "author": "Songo Technonogies (SOTEC)",
    "sequence": 1,
    "category": "Comptabilité",
    "Summary": "Gestion de la comptabilité",
    "depends": ["base", "om_account_accountant"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/view.xml",
        ],
    "installable": True,
    "auto_install": False,
}
