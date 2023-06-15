from odoo import fields,api,models,tools,_
from dateutil.relativedelta import relativedelta
from datetime import datetime


class FleetTypePermis(models.Model):
    _name = 'fleet.type.permis'

    name = fields.Char("Categorie de permis", required=True)
    description = fields.Text(string='Description')


class FleetChauffeur(models.Model):
    _name = 'fleet.chauffeur'

    name = fields.Char(string='Nom chauffeur', required=True)
    date_naissance = fields.Date(string='Date Naissance')
    numero_identite = fields.Char(string='N° Document Identité / Passeport')
    date_expiration_identite = fields.Date(string='Date expiration Document Identité')
    telephone = fields.Char(string='Telephone')
    email = fields.Char(string='Email')
    adresse = fields.Text(string='Adresse')
    permis = fields.Char(string='N° permis', required=True)
    date_expiration_permis = fields.Date("Date d'expiration")
    type_permis = fields.Many2one('fleet.type.permis', 'Catégorie de permis', required=True)


class FleetEmployee(models.Model):
    _inherit = 'hr.employee'

    def hasVehicle(self):
        print("checker voir si l'employe a un véhicule")
