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
    personnel_id = fields.Many2one("facture_conducteur_camion", "Chauffeur", required=True)
    dte_deb = fields.Date("Date de début", required=True)
    dte_fin = fields.Date("Date de fin", required=True)
    chauffeur_ids = fields.One2many("etat.chauffeur.def.line", "chauffeur_id")

    def afficher(self):
        for va in self:
            va.chauffeur_ids.unlink()
            lines = va.env['facture_facture_line'].search([('x_fact_id.date_operation', '>=', self.dte_deb),('x_fact_id.date_operation', '<=', self.dte_fin), 
                                                           ('x_immatricul_id.x_conducteur_id','=', self.personnel_id.id)])
            for li in lines:
                self.sudo().env['etat.chauffeur.def.line'].create({
                    'brut_fn': li.x_mt_ligne_reel,
                    'manquant_fn': li.x_mnt_perte,
                    'dte': li.x_fact_id.date_operation,
                    'net_fn': li.x_mt_ligne,
                    'chauffeur_id': self.id
                })
            
            liness = va.env['gest_depense'].search([('date_op', '>=', self.dte_deb),('date_op', '<=', self.dte_fin), 
                                                           ('x_personnel_id','=', self.personnel_id.id)])
            for lis in liness:
                self.sudo().env['etat.chauffeur.def.line'].create({
                    'dep_chauffeur': lis.mt,
                    'dte': lis.date_op,
                    'chauffeur_id': self.id
                })

    def imprimer(self):
        return self.env.ref('Gestion_Facturation.report_chauff_etat').report_action(self)

class EtatChauffeurDefLine(models.TransientModel):
    _name = "etat.chauffeur.def.line"

    chauffeur_id = fields.Many2one("etat.chauffeur.def")
    dte= fields.Date("Date")
    brut_fn = fields.Float("Brute")
    net_fn = fields.Float("Net")
    manquant_fn = fields.Float("Manquant")
    dep_chauffeur = fields.Float("Dépense Chauffeur")

### RAS ###
class EtatCamionDef(models.TransientModel):
    _name = "etat.camion.def"

    name = fields.Char(default="Etat camion")
    camion = fields.Many2one("facture_camion", "Camion", required=False)
    dte_deb = fields.Date("Date de début", required=True)
    dte_fin = fields.Date("Date de fin", required=True)
    nbre = fields.Integer("Nbre de voyage")
    camion_ids = fields.One2many("etat.camion.def.line", "camion_id")

    def afficher(self):
        for va in self:
            nb = va.env['facture_facture_line'].search_count([('x_fact_id.date_operation', '>=', self.dte_deb),('x_fact_id.date_operation', '<=', self.dte_fin), 
                                                           ('x_immatricul_id.name','=', self.camion.name)])
            self.nbre = nb
            va.camion_ids.unlink()
            lines = va.env['facture_facture_line'].search([('x_fact_id.date_operation', '>=', self.dte_deb),('x_fact_id.date_operation', '<=', self.dte_fin), 
                                                           ('x_immatricul_id.name','=', self.camion.name)])
            for li in lines:
                self.sudo().env['etat.camion.def.line'].create({
                    'brut': li.x_mt_ligne_reel,
                    'manquant': li.x_mnt_perte,
                    'dte': li.x_fact_id.date_operation,
                    'net': li.x_mt_ligne,
                    'camion_id': self.id
                })
            
            liness = va.env['gest_depense'].search([('date_op', '>=', self.dte_deb),('date_op', '<=', self.dte_fin), 
                                                           ('name.name','=', self.camion.name)])
            for lis in liness:
                self.sudo().env['etat.camion.def.line'].create({
                    'dep_camion': lis.mt,
                    'dte': lis.date_op,
                    'camion_id': self.id
                })

    def imprimer(self):
        return self.env.ref('Gestion_Facturation.report_camion_etat').report_action(self)

class EtatCamionDefLine(models.TransientModel):
    _name = "etat.camion.def.line"

    camion_id = fields.Many2one("etat.camion.def")
    dte = fields.Date("Date de début")
    brut = fields.Float("Brute")
    net = fields.Float("Net")
    manquant = fields.Float("Manquant")
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

class Nombre(models.TransientModel):
    _name = "nombre"

    dte_deb = fields.Date("Date de début", required=True)
    dte_fin = fields.Date("Date de fin", required=False)
    facture_ids = fields.One2many("nombre.line", "nombre_id")


    def afficher(self):
        for vals in self:
            if self.dte_fin:
                vals.env.cr.execute("""select d.name as chauffeur, c.name as camion, count(*) as voyages from facture_facture_line fl
                inner join facture_camion c on c.id=fl.x_immatricul_id 
                inner join facture_conducteur_camion d on d.id=c.x_conducteur_id
                where fl.x_date_bl between %s and %s
                group by c.name, d.name order by voyages desc;""",(self.dte_deb, self.dte_fin))
            else:
                vals.env.cr.execute("""select d.name as chauffeur, c.name as camion, count(*) as voyages from facture_facture_line fl
                inner join facture_camion c on c.id=fl.x_immatricul_id 
                inner join facture_conducteur_camion d on d.id=c.x_conducteur_id
                where fl.x_date_bl = %s
                group by c.name, d.name order by voyages desc;""",(self.dte_deb,))

            rows = vals.env.cr.dictfetchall()
            result = []
            vals.facture_ids.unlink()
            for line in rows:
                result.append((0,0, {'chauffeur' : line['chauffeur'], 'camion': line['camion'], 'voyage': line['voyages']}))
            self.facture_ids = result

    def imprimer(self):
        return self.env.ref('Gestion_Facturation.report_nombre_etat').report_action(self)

class NombreLine(models.TransientModel):
    _name = "nombre.line"

    nombre_id = fields.Many2one("nombre")
    chauffeur = fields.Char("Chauffeur")
    camion = fields.Char("Camion")
    voyage = fields.Integer("Voyage")


class VoyageChauffeur(models.TransientModel):
    _name = "voyage.chauffeur"

    dte_deb = fields.Date("Date de début", required=True)
    dte_fin = fields.Date("Date de fin", required=False)
    donnees_ids = fields.One2many("voyage.chauffeur.line", "voyage_chauffeur_id")


    def afficher(self):
        for vals in self:
            if self.dte_fin:
                vals.env.cr.execute("""select d.name as chauffeur,d.x_tel as telephone, count(*) as voyages from facture_facture_line fl
                inner join facture_camion c on c.id=fl.x_immatricul_id 
                inner join facture_conducteur_camion d on d.id=c.x_conducteur_id
                where fl.x_date_bl between %s and %s
                group by d.name,d.x_tel order by voyages desc, chauffeur asc;""",(self.dte_deb, self.dte_fin))
            else:
                vals.env.cr.execute("""select d.name as chauffeur,d.x_tel as telephone, count(*) as voyages from facture_facture_line fl
                inner join facture_camion c on c.id=fl.x_immatricul_id 
                inner join facture_conducteur_camion d on d.id=c.x_conducteur_id
                where fl.x_date_bl = %s
                group by d.name,d.x_tel order by voyages desc, chauffeur asc;""",(self.dte_deb,))

            rows = vals.env.cr.dictfetchall()
            result = []
            vals.donnees_ids.unlink()
            for line in rows:
                result.append((0,0, {'chauffeur' : line['chauffeur'], 'telephone': line['telephone'], 'voyage': line['voyages']}))
            self.donnees_ids = result

    def imprimer(self):
        return self.env.ref('Gestion_Facturation.report_voyage_chauffeur_etat').report_action(self)

class VoyageChauffeurLine(models.TransientModel):
    _name = "voyage.chauffeur.line"

    voyage_chauffeur_id = fields.Many2one("voyage.chauffeur")
    chauffeur = fields.Char("Chauffeur")
    telephone = fields.Char("Telephone")
    voyage = fields.Integer("Voyage")


class VoyageChauffeurDetail(models.TransientModel):
    _name = "voyage.chauffeur.detail"

    dte_deb = fields.Date("Date de début", required=True)
    dte_fin = fields.Date("Date de fin", required=False)
    donnees_ids = fields.One2many("voyage.chauffeur.detail.line", "voyage_chauffeur_detail_id")


    def afficher(self):
        for vals in self:
            if self.dte_fin:
                vals.env.cr.execute("""select d.name as chauffeur,fl.x_date_be as date_be,fl.x_date_bl as date_bl,
                                     fl.x_num_be as be, fl.x_num_bl as bl,
                                    fl.x_capacite as capacite,ft.name as trajet,
                                    fp.name as produit
                                     from facture_facture_line fl
                inner join facture_camion c on c.id=fl.x_immatricul_id 
                inner join facture_conducteur_camion d on d.id=c.x_conducteur_id
                inner join facture_trajet ft on ft.id=fl.x_trajet_id
                inner join facture_produit fp on fp.id=fl.x_produit_id
                where fl.x_date_bl between %s and %s
                order by be asc, chauffeur asc;""",(self.dte_deb, self.dte_fin))
            else:
                vals.env.cr.execute("""select d.name as chauffeur,fl.x_date_be as date_be,fl.x_date_bl as date_bl,
                                     fl.x_num_be as be, fl.x_num_bl as bl,
                                    fl.x_capacite as capacite,ft.name as trajet,
                                    fp.name as produit
                                     from facture_facture_line fl
                inner join facture_camion c on c.id=fl.x_immatricul_id 
                inner join facture_conducteur_camion d on d.id=c.x_conducteur_id
                inner join facture_trajet ft on ft.id=fl.x_trajet_id
                inner join facture_produit fp on fp.id=fl.x_produit_id
                where fl.x_date_bl  = %s
                order by be asc, chauffeur asc;""",(self.dte_deb,))

            rows = vals.env.cr.dictfetchall()
            result = []
            vals.donnees_ids.unlink()
            for line in rows:
                result.append((0,0, {'chauffeur' : line['chauffeur'], 
                                     'date_be': line['date_be'], 
                                     'date_bl': line['date_bl'], 
                                     'be': line['be'], 
                                     'bl': line['bl'], 
                                     'capacite': line['capacite'], 
                                     'trajet': line['trajet'], 
                                     'produit': line['produit']}))
            self.donnees_ids = result

    def imprimer(self):
        return self.env.ref('Gestion_Facturation.report_voyage_chauffeur_detail_etat').report_action(self)

class VoyageChauffeurDetailLine(models.TransientModel):
    _name = "voyage.chauffeur.detail.line"

    voyage_chauffeur_detail_id = fields.Many2one("voyage.chauffeur.detail")
    date_be = fields.Date("Date BE")
    date_bl = fields.Date("Date BL")
    chauffeur = fields.Char("Chauffeur")
    be = fields.Char("N° BE")
    bl = fields.Char("N° BL")
    trajet = fields.Char("Trajet")
    produit = fields.Char("Produit")
    capacite = fields.Float("Capacite")