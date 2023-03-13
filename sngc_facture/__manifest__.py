{
    "name": "TRANSPORT SONAGES/PAM - SOTEC",
    "Summary": "SNGC FACTURATION",
    "sequence": 1,
    "version": "1.0",
    "author": "Songo Technonogies (SOTEC)",
    "depends": ["base", "mail"],
    'images': ['static/description/sngc.jpg'],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml", "views/donnee.xml",
        "views/pam.xml", "views/sonagess.xml",
        "views/classic.xml", "report/report.xml",
"report/report_comm.xml",
        ],
    "category": "ENTREPRISE PRIVEE",
    "installable": True,
    "auto_install": False,
}
