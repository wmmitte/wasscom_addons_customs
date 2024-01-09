from odoo import fields,api,models,tools,_
import string
from datetime import datetime,date
import pdb
import calendar
from calendar import monthrange
from odoo.exceptions import UserError,ValidationError
from dateutil.relativedelta import relativedelta
from num2words import num2words


class ChiffreAffaire(models.TransientModel):
    _name = 'chiffre.affaire'

    name = fields.Char(default="Chiffre d'affaire")
    dte_deb = fields.Date("Date debut", required=True)
    dte_fin = fields.Date("Date fin", required=True)
    chiffre_ids = fields.One2many("chiffre.affaire.line", "chiffre_id")

    def afficher(self):
        self.chiffre_ids.unlink()
        self.afficherfn()
        self.afficherft()

    def afficherfn(self):
        for va in self:
            lines = va.env['ligne.facture'].search([('dte', '>=', self.dte_deb),('dte', '<=', self.dte_fin), ('type', '=', 'Normale')])
            for li in lines:
                self.sudo().env['chiffre.affaire.line'].create({
                    'brut_fn': li.total_a_payer,
                    'retenue_fn': li.mnt_deduit,
                    'manquant_fn': li.mnt_perte,
                    'net_fn': li.total_reel,
                    'chiffre_id': self.id
                })
    
    def afficherft(self):
        for va in self:
            lines = va.env['ligne.facture'].search([('dte', '>=', self.dte_deb),('dte', '<=', self.dte_fin), ('type', '=', 'Transit')])
            for li in lines:
                self.sudo().env['chiffre.affaire.line'].create({
                    'brut_ft': li.total_a_payer,
                    'chiffre_id': self.id
                })

    def imprimer(self):
        return self.env.ref('Gestion_Facturation.report_chiffre').report_action(self)

class ChiffreAffaireLine(models.TransientModel):
    _name = "chiffre.affaire.line"

    chiffre_id = fields.Many2one("chiffre.affaire")
    brut_fn = fields.Float("Brute F.N")
    net_fn = fields.Float("Net F.N")
    retenue_fn = fields.Float("Retenue F.N")
    manquant_fn = fields.Float("Manquant F.N")
    brut_ft = fields.Float("Brute F.T")
    dep_chauffeur = fields.Float("Dépense Chauffeur")
    dep_camion = fields.Float("Dépense camion")


class EtatChauffeurDef(models.TransientModel):
    _name = "etat.chauffeur.def"

    name = fields.Char(default="Etat chauffeur")
    personnel_id = fields.Many2one("facture_conducteur_camion", "Chauffeur")
    dte_deb = fields.Date("Date de début", required=True)
    dte_fin = fields.Date("Date de fin", required=True)
    chauffeur_ids = fields.One2many("etat.chauffeur.def.line", "chauffeur_id")

    def afficher(self):
        return True

    def imprimer(self):
        return self.env.ref('Gestion_Facturation.report_chauffre').report_action(self)

class EtatChauffeurDefLine(models.TransientModel):
    _name = "etat.chauffeur.def.line"

    chauffeur_id = fields.Many2one("etat.chauffeur.def")
    brut_fn = fields.Float("Brute F.N")
    retenue_fn = fields.Float("Retenue F.N")
    manquant_fn = fields.Float("Manquant F.N")
    dep_chauffeur = fields.Float("Dépense Chauffeur")

### RAS ###
class EtatCamionDef(models.TransientModel):
    _name = "etat.camion.def"

    name = fields.Char(default="Etat camion")
    camion = fields.Many2one("facture_camion", "Camion")
    dte_deb = fields.Date("Date de début", required=True)
    dte_fin = fields.Date("Date de fin", required=True)
    camion_ids = fields.One2many("etat.camion.def.line", "camion_id")

    def afficher(self):
        self.env.cr.execute("select sum(t.x_mnt_ligne + n.)")

    def imprimer(self):
        return self.env.ref('Gestion_Facturation.report_camion').report_action(self)

class EtatCamionDefLine(models.TransientModel):
    _name = "etat.camion.def.line"

    camion_id = fields.Many2one("etat.camion.def")
    brut = fields.Float("Brute")
    retenue = fields.Float("Retenue")
    net = fields.Float("Net")
    dep_camion = fields.Float("Dépense Camion")


class EtatFactureNormale(models.TransientModel):
    _name = "etat.facture.normale"

    name = fields.Char(default="Etat Facture")
    dte_deb = fields.Date("Date de début", required=True)
    dte_fin = fields.Date("Date de fin", required=True)
    facture_ids = fields.One2many("etat.facture.normale.line", "facture_id")

    def afficher(self):
        for va in self:
            va.facture_ids.unlink()
            lines = va.env['ligne.facture'].search([('dte', '>=', self.dte_deb),('dte', '<=', self.dte_fin), ('type', '=', 'Normale')])
            for li in lines:
                self.sudo().env['etat.facture.normale.line'].create({
                    'brut_fn': li.total_a_payer,
                    'num_fact': li.num_fact,
                    'retenue_fn': li.mnt_deduit,
                    'manquant_fn': li.mnt_perte,
                    'net_fn': li.total_reel,
                    'facture_id': self.id
                })

    def imprimer(self):
        #return self.env.ref('Gestion_Facturation.report_facture').report_action(self)
        return True

class EtatFactureNormaleLine(models.TransientModel):
    _name = "etat.facture.normale.line"

    facture_id = fields.Many2one("etat.facture.normale")
    brut_fn = fields.Float("Mnt Brut")
    num_fact = fields.Char("N° Facture")
    retenue_fn = fields.Float("Mnt Retenu")
    manquant_fn = fields.Float("Mnt Manquant")
    net_fn = fields.Float("Mnt Net")
    state = fields.Selection([
        ('Nouvelle facture', 'Nouvelle'),
        ('Approuvée', 'Approuvée'),
        ('Liquidation partielle', 'En cours'),
        ('Liquidation totale', "Soldée"),
    ], 'Etat')


class EtatFactureTransit(models.TransientModel):
    _name = "etat.facture.transit"

    name = fields.Char(default="Etat facture transit")
    dte_deb = fields.Date("Date de début", required=True)
    dte_fin = fields.Date("Date de fin", required=True)
    facture_ids = fields.One2many("etat.facture.transit.line", "facture_id")

    def afficher(self):
        for va in self:
            va.facture_ids.unlink()
            lines = va.env['ligne.facture'].search([('dte', '>=', self.dte_deb),('dte', '<=', self.dte_fin), ('type', '=', 'Transit')])
            for li in lines:
                self.sudo().env['etat.facture.transit.line'].create({
                    'num_fact': li.num_fact,
                    'montant': li.total_a_payer,
                    'dte': li.dte,
                    'facture_id': self.id
                })

    def imprimer(self):
        return self.env.ref('Gestion_Facturation.report_facture_transite').report_action(self)

class EtatFactureTransitLine(models.TransientModel):
    _name = "etat.facture.transit.line"

    facture_id = fields.Many2one("etat.facture.transit")
    num_fact = fields.Char("N° Facture")
    montant = fields.Float("Montant")
    dte = fields.Date("Date")


class EtatPaiement(models.TransientModel):
    _name = "etat.paiement"

    name = fields.Char(default="Etat paiement")
    dte_deb = fields.Date("Date de début", required=True)
    dte_fin = fields.Date("Date de fin", required=True)
    facture_ids = fields.One2many("etat.paiement.line", "paiement_id")

    def afficher(self):
        for va in self:
            va.facture_ids.unlink()
            lines = va.env['facture_facture_paiement'].search([('date_operation', '>=', self.dte_deb),('date_operation', '<=', self.dte_fin), ('state', '=', 'Paiement effectuée')])
            for li in lines:
                self.sudo().env['etat.paiement.line'].create({
                    'dte': li.date_operation,
                    'numero': li.name.name,
                    'montant': li.x_mt_encaisse,
                    'paiement_id': self.id
                })

    def imprimer(self):
        return self.env.ref('Gestion_Facturation.report_paiement').report_action(self)

class EtatPaiementLine(models.TransientModel):
    _name = "etat.paiement.line"

    paiement_id = fields.Many2one("etat.paiement")
    dte = fields.Date("Date paiement")
    numero = fields.Char("N° Facture")
    montant = fields.Float("Montant")


class EtatPaiementTransit(models.TransientModel):
    _name = "etat.paiement.transit"

    name = fields.Char(default="Etat paiement")
    dte_deb = fields.Date("Date de début", required=True)
    dte_fin = fields.Date("Date de fin", required=True)
    facture_ids = fields.One2many("etat.paiement.line", "paiement_id")

    def afficher(self):
        for va in self:
            va.facture_ids.unlink()
            lines = va.env['facture_facture_paiement_transit'].search([('date_operation', '>=', self.dte_deb),('date_operation', '<=', self.dte_fin), ('state', '=', 'Paiement effectuée')])
            for li in lines:
                self.sudo().env['etat.paiement.transit.line'].create({
                    'dte': li.date_operation,
                    'numero': li.name.name,
                    'montant': li.x_mnt_encaisse,
                    'paiement_id': self.id
                })

    def imprimer(self):
        return self.env.ref('Gestion_Facturation.report_paiement').report_action(self)

class EtatPaiementTransitLine(models.TransientModel):
    _name = "etat.paiement.transit.line"

    paiement_id = fields.Many2one("etat.paiement.transit")
    dte = fields.Date("Date paiement")
    numero = fields.Char("N° Facture")
    montant = fields.Float("Montant")
