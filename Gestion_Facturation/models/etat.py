from odoo import fields,api,models,tools,_
from datetime import datetime,date
from odoo.exceptions import UserError,ValidationError
from num2words import num2words

class EtatCamion(models.TransientModel):
    _name = 'etat.camion'
    _rec_name = 'camion_id'

    camion_id = fields.Many2one("facture_camion", "Camion", required=True)
    dt_deb = fields.Date("Date de début", required=True)
    dt_fin = fields.Date("Date de fin", required=True)
    recette = fields.Float("Recette", readonly=True)
    depense = fields.Float("Dépense", readonly=True)

        
    def etatCamionDepRec(self):
        came = int(self.camion_id.id)
        depenses = self.env['gest_depense'].search(
            [('name.id', '=', came), ('date_op', '>=', self.dt_deb),
             ('date_op', '<=', self.dt_fin), ('state', '=', 'Validé')])
        montant_depense = 0
        for e in depenses:
            montant_depense = montant_depense + e.mt
        self.depense = montant_depense
        

        recettes = self.env['facture_facture_line'].search(
            [('x_immatricul_id.id', '=', came), ('x_fact_id.date_operation', '>=', self.dt_deb),
             ('x_fact_id.date_operation', '<=', self.dt_fin), ('x_fact_id.state', 'in', ['Nouvelle', 'Approuvée', 'Liquidation partielle', 'Liquidation totale'])])
        montant_recette = 0
        for r in recettes:
            montant_recette = montant_recette + r.x_mt_ligne
        recette1 = montant_recette
        
        recettest = self.env['facture_transit_line'].search(
            [('x_immatricul_id.id', '=', came), ('x_fact_id.date_operation', '>=', self.dt_deb),
             ('x_fact_id.date_operation', '<=', self.dt_fin), ('x_fact_id.state', 'in', ['Nouvelle', 'Approuvée', 'En cours liquidation', 'Liquidée'])])
        montant_recettet = 0
        for rt in recettest:
            montant_recettet = montant_recettet + rt.x_mt_ligne
        recette2 = montant_recettet
        
        self.recette = recette1 + recette2
    
    def print_camion(self):
        return self.env.ref('Gestion_Facturation.report_etat_camion').report_action(self)



class EtatChauffeur(models.TransientModel):
    _name = 'etat.chauffeur'
    _rec_name = 'personnel_id'

    personnel_id = fields.Many2one("facture_conducteur_camion", "Personnel", required=True)
    dt_deb = fields.Date("Date de début", required=True)
    dt_fin = fields.Date("Date de fin", required=True)
    recette = fields.Float("Recette", readonly=True)
    depense = fields.Float("Dépense", readonly=True)
    

    def etatChauffeurDepRec(self):
        pers = int(self.personnel_id.id)
        depenses = self.env['gest_depense'].search(
            [('x_personnel_id.id', '=', pers), ('date_op', '>=', self.dt_deb),
             ('date_op', '<=', self.dt_fin), ('state', '=', 'Validé')])
        montant_depense = 0
        for e in depenses:
            montant_depense = montant_depense + e.mt
        self.depense = montant_depense
        

        recettes = self.env['facture_facture_line'].search(
            [('x_immatricul_id.x_conducteur_id.id', '=', pers), ('x_fact_id.date_operation', '>=', self.dt_deb),
             ('x_fact_id.date_operation', '<=', self.dt_fin), ('x_fact_id.state', 'in', ['Nouvelle', 'Approuvée', 'Liquidation partielle', 'Liquidation totale'])])
        montant_recette = 0
        for r in recettes:
            montant_recette = montant_recette + r.x_mt_ligne
        recette1 = montant_recette
        
        recettest = self.env['facture_transit_line'].search(
            [('x_immatricul_id.x_conducteur_id.id', '=', pers), ('x_fact_id.date_operation', '>=', self.dt_deb),
             ('x_fact_id.date_operation', '<=', self.dt_fin), ('x_fact_id.state', 'in', ['Nouvelle', 'Approuvée', 'En cours liquidation', 'Liquidée'])])
        montant_recettet = 0
        for rt in recettest:
            montant_recettet = montant_recettet + rt.x_mt_ligne
        recette2 = montant_recette
        
        self.recette = recette1 + recette2
    

    def print_chauffeur(self):
        return self.env.ref('Gestion_Facturation.report_etat_chauffeur').report_action(self)

