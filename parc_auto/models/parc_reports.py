from odoo import fields,api,models,tools,_
from dateutil.relativedelta import relativedelta
from datetime import datetime


class ParcReportVehiculeList(models.TransientModel):
    _name = 'parc.report.vehicule.list'

    name = fields.Char(default ='Etat des véhicules du parc')

    model_id = fields.Many2one("fleet.vehicle.model", "Modèle")
    marque_id = fields.Many2one("fleet.vehicle.model.brand", "Constructeur")
    annee_model = fields.Char("Année Model")
    numero_Chassis = fields.Char("N° Chassis")
    type_carburant = fields.Selection([
        ('gasoline', 'Essence (super 91)'),
        ('diesel', 'Diesel'),
        ('lpg', 'Gaz'),
        ('electric', 'Electrique'),
        ('hybrid', 'Hybride')
        ], 'Type Carburant')
    puissance = fields.Float("Puissance (kW)")
    nombre_place = fields.Integer("Nombre place")
    couleur = fields.Char("Couleur")

