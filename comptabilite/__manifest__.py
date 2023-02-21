{
    "name": "COMPTABILITE",
    "version": "1.0",
    "author": "OURNO Mohamed Kabir",
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
