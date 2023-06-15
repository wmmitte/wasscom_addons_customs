from odoo import fields,api,models,tools,_
from dateutil.relativedelta import relativedelta
from datetime import datetime


class FleetVehicleParcAssuranceHistory(models.Model):
    _name = 'fleet.vehicle.parc.assurance.history'
    _order = 'id desc'

    # Historique - Assurance
    vehicule_id = fields.Many2one('fleet.vehicle', 'Véhicule')
    assureur_id = fields.Many2one('res.partner', 'Assurance/Assureur')
    date_souscription = fields.Date('Date Souscription')
    montant_souscription = fields.Float('Montant')
    duree_souscription = fields.Integer('Durée (En Mois)')
    date_expiration = fields.Date('Date Expiration')
    couverture_assurance = fields.Text('Couverture')

class FleetVehicleParcVisiteTechniqueHistory(models.Model):
    _name = 'fleet.vehicle.parc.visite.technique.history'
    _order = 'id desc'

    # Historique - Visite technique
    vehicule_id = fields.Many2one('fleet.vehicle', 'Véhicule')
    centre_controle_id = fields.Many2one('res.partner', 'Centre de controle')
    date_visite_technique = fields.Date('Date Visite')
    montant_visite = fields.Float('Montant')
    duree_visite = fields.Integer('Durée (En mois)')
    date_expiration_visite_technique = fields.Date('Date Expiration')


class FleetVehicleParcTaxeHistory(models.Model):
    _name = 'fleet.vehicle.parc.taxe.history'
    _order = 'id desc'

    # Historique - Taxes
    vehicule_id = fields.Many2one('fleet.vehicle', 'Véhicule')
    annee_paiement = fields.Integer('Annnée')
    montant_taxe = fields.Float('Montant')
    date_paiement_taxe = fields.Date('Date paiement')
