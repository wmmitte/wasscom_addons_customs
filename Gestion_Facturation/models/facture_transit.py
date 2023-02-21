from odoo import fields,api,models,tools,_
import string
from datetime import datetime,date
import pdb
import calendar
from calendar import monthrange
from odoo.exceptions import UserError,ValidationError
from dateutil.relativedelta import relativedelta
from num2words import num2words




#classe facture transit
class FactureTransit(models.Model):
    _name = 'facture_transit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Facture Transit'
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of facture transit.", default=10)

    _rec_name = 'x_num_fact'
    x_num_fact = fields.Char(string = "N° Facture Transit", readonly=True)
    name = fields.Many2one('facture_client',string = 'Client',required = True)
    x_adress = fields.Char(string="Adresse", readonly=True)
    x_echeance_facture = fields.Date(string = 'Echéance')
    active = fields.Boolean(string="Etat", default=True)
    current_users = fields.Many2one('res.users', 'Agent', default=lambda self: self.env.user, readonly=True)
    date_operation = fields.Date(string='Date facture', default=fields.Date.context_today, readonly=True)
    company_id = fields.Many2one('res.company', string="Structure", default=lambda self: self.env.user.company_id.id,readonly=True)
    state = fields.Selection([
        ('Nouvelle', 'Nouvelle'),
        ('Approuvée', 'Approuvée'),
        ('En cours Liquidation', 'En cours Liquidation'),
        ('Liquidée', "Liquidée"),
    ], 'Statut', default='Nouvelle', index=True, required=False, copy=False, track_visibility='always')
    x_total_facture = fields.Float(compute = '_calcul_total_fact',store = True,string='Total Facture')
    x_total_encaisse = fields.Float(string='Total Encaissé', readonly=True, default=0)
    x_total_reste = fields.Float(compute = '_calcul_total_fact',store = True,string='Reste à payer')

    x_etat_facture = fields.Char('Etat facture', default='Nouvelle')
    x_line_ids = fields.One2many('facture_transit_line','x_fact_id',string = 'Ligne facture')
    x_mnt_lettre = fields.Char(string='Montant en lettre')
    x_signataire_id = fields.Many2one('res.users', 'Sigantaire', required=True)

    @api.depends('x_line_ids.x_mt_ligne')
    def _calcul_total_fact(self):
        text = ''
        self.x_total_facture = sum(line.x_mt_ligne for line in self.x_line_ids)
        self.x_total_reste = self.x_total_facture
        text += num2words(self.x_total_facture, lang='fr')
        self.x_mnt_lettre = text

    @api.onchange('name')
    def act_remplir_champs(self):
        for record in self:
            record.x_adress = record.name.x_adress

    def action_approuver_facture(self):
        for record in self:
            x_struct_id = int(record.company_id)
            x_annee = date.today().year
            print('année en cours',x_annee)
            x_total_facture = record.x_total_facture

            self.env.cr.execute("select no_code from facture_code where company_id = %d and x_annee = %d" % (x_struct_id,x_annee))
            lo = self.env.cr.fetchone()
            no_lo = lo and lo[0] or 0
            c1 = int(no_lo) + 1
            c = str(no_lo)
            if c == "0":
                ok = str(c1).zfill(4)
                self.x_num_fact = 'FACT'+'/'+ok+'/'+ str(x_annee)
                vals = c1
                self.env.cr.execute("INSERT INTO facture_code(company_id,no_code,x_annee)  VALUES(%d,%d,%d)" % (x_struct_id, vals,x_annee))
                self.env.cr.execute("INSERT INTO facture_facture_stats(name,x_ca_annuel,company_id)  VALUES(%d,%d,%d)" % (x_annee,x_total_facture,x_struct_id))
                self.write({'state': 'Approuvée','x_etat_facture': 'Approuvée'})
            else:
                c1 = int(no_lo) + 1
                c = str(no_lo)
                ok = str(c1).zfill(4)
                self.x_num_fact = 'FACT'+'/'+ok+'/'+ str(x_annee)
                vals = c1
                self.env.cr.execute("UPDATE facture_code SET no_code = %d  WHERE company_id = %d and x_annee = %d" % (vals, x_struct_id,x_annee))
                self.env.cr.execute("UPDATE facture_facture_stats SET name = %d,x_ca_annuel = x_ca_annuel + %d  WHERE company_id = %d and name = %d" % (x_annee,x_total_facture,x_struct_id,x_annee))
                self.write({'state': 'Approuvée','x_etat_facture': 'Approuvée'})


#classe facture transit line
class FactureTransitLine(models.Model):
    _name = 'facture_transit_line'
    x_fact_id = fields.Many2one('facture_transit')

    x_date_be = fields.Date(string='Date BE', required=True)
    x_num_be = fields.Char(string='N° BE', required=True)
    x_date_bl = fields.Date(string='Date BL', required=True)
    x_num_bl = fields.Char(string='N° BL', required=True)
    x_immatricul_id = fields.Many2one('facture_camion', string='Immatriculation', required=True)
    x_trajet_id = fields.Many2one('facture_trajet', string='Trajet', required=True)
    x_produit_id = fields.Many2one('facture_produit', string='Produit', required=True)
    x_mt_ligne = fields.Float(string='Mnt Ligne', required=True)

    """name = fields.Many2one('facture_facture',string = 'N° Facture',required=True)
    date_facture = fields.Date(string='Date facture', default=fields.Date.context_today, readonly=True)
    x_objet = fields.Char(string = 'Objet',readonly = True)
    x_ht = fields.Float(string='Mnt HT',required = True)
    x_tva = fields.Float(string = 'TVA')
    x_mnt_tva = fields.Float(compute = '_calcul_mnt_tva',store = True,string = 'Mnt TVA', readonly=True)
    x_bic = fields.Float(string = 'BIC')
    x_mnt_bic = fields.Float(compute = '_calcul_mnt_bic',store = True,string = 'Mnt BIC', readonly=True)
    x_mnt_ttc = fields.Float(compute = '_calcul_mnt_tva',store = True,string = 'Montant TTC')
    x_mnt_net = fields.Float(compute = '_calcul_mnt_bic',store = True,string = 'Montant NET')"""
    x_annee_en_cours = fields.Integer('Année', readonly=True)

    @api.onchange('x_immatricul_id')
    def _act_rempl_champ(self):
        for record in self:
            annee = date.today().year
            record.x_annee_en_cours = annee

    """@api.depends('x_ht','x_tva')
    def _calcul_mnt_tva(self):
        for record in self:
            record.x_mnt_tva = round((record.x_ht * record.x_tva) / 100)
            record.x_mnt_ttc = record.x_ht + record.x_mnt_tva


    @api.depends('x_mnt_ttc', 'x_bic')
    def _calcul_mnt_bic(self):
        for record in self:
            record.x_mnt_bic = round((record.x_mnt_ttc * record.x_bic) / 100)
            record.x_mnt_net = record.x_ht + record.x_mnt_bic + record.x_mnt_tva"""


#Effectuer le paiement d'une facture transit en attente
class FactureFacturePaiementTransit(models.Model):
    _name = 'facture_facture_paiement_transit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Paiement Facture Transit'
    _order = "create_date desc, id desc"
    sequence = fields.Integer(help="Gives the sequence when displaying a list of paiement facture transit.", default=10)


    name = fields.Many2one('facture_transit',string = 'N° Facture',required = True,domain = ('|',['state','in',('Approuvée','En cours Liquidation')],['x_etat_facture','in',('Approuvée','En cours Liquidation')]))
    x_client = fields.Many2one('facture_client',string = 'Client',readonly = True)
    x_adress = fields.Char(string="Adresse", readonly=True)
    x_objet = fields.Char(string = 'Objet',readonly = True)

    active = fields.Boolean(string="Etat", default=True)
    current_users = fields.Many2one('res.users', 'Agent', default=lambda self: self.env.user,readonly=True)
    date_operation = fields.Date(string='Date paiement', default=fields.Date.context_today, readonly=True)
    company_id = fields.Many2one('res.company', string="Structure", default=lambda self: self.env.user.company_id.id,readonly=True)
    state = fields.Selection([
        ('Nouveau paiement', 'Nouveau paiement'),
        ('Paiement effectuée', 'Paiement effectuée'),
    ], 'Statut', default='Nouveau paiement', index=True, required=False, copy=False, track_visibility='always')
    x_total_facture = fields.Float(compute = '_calcul_total_fact',store = True,string = 'Total Facture')
    x_total_encaisse = fields.Float(string='Total Encaissé',readonly = True)
    x_total_reste = fields.Float(compute = '_calcul_total_fact',store = True,string='Reste à payer',readonly = True)
    x_mt_encaisse = fields.Float(string='Somme versée', required=True)
    x_total_reste_apr = fields.Float(compute = '_calcul_rest_mnt', store = True,string='Reste après opération', readonly=True)

    @api.depends('x_mt_encaisse')
    def _calcul_rest_mnt(self):
        for record in self:
            record.x_total_reste_apr = record.x_total_reste - record.x_mt_encaisse

    @api.onchange('name')
    def act_remplir_champs(self):
        for record in self:
            record.x_client = record.name.name
            record.x_adress = record.name.x_adress
            record.x_total_facture = record.name.x_total_facture
            record.x_total_encaisse = record.name.x_total_encaisse
            record.x_total_reste = record.name.x_total_reste

    def action_valider(self):
        for record in self:
            id_fact = int(record.name.id)
            print('id_fact',id_fact)
            x_mt_encaisse = float(record.x_mt_encaisse)
            x_total_reste = record.x_total_reste - record.x_mt_encaisse

            if x_mt_encaisse <= 0:
                raise ValidationError(_("Montant %d saisi invalide") % (record.x_mt_encaisse))
            elif record.x_mt_encaisse > record.x_total_reste:
                raise ValidationError(_("Montant %d saisi est supérieur au reste qui est de %d") % (record.x_mt_encaisse,record.x_total_reste))
            elif record.x_total_reste_apr > 0:
                record.env.cr.execute("UPDATE facture_transit SET x_total_encaisse = x_total_encaisse + %d, x_total_reste =  %d,state = 'En cours Liquidation',x_etat_facture = 'En cours Liquidation'  WHERE id = %d" %(record.x_mt_encaisse,x_total_reste,id_fact))
                record.write({'state': 'Paiement effectuée'})
            elif record.x_total_reste_apr == 0:
                record.env.cr.execute("UPDATE facture_transit SET x_total_encaisse = x_total_encaisse + %d, x_total_reste =  %d,state = 'Liquidée',x_etat_facture = 'Liquidée'  WHERE id = %d" %(record.x_mt_encaisse,x_total_reste,id_fact))
                record.write({'state': 'Paiement effectuée'})



#Table de recuperation des stats ( CA)
class FactureFacturePaiementStats(models.Model):
    _name = 'facture_facture_stats'
    name = fields.Integer('Année')
    x_ca_annuel = fields.Float("Chiffre d'Affaire Annuel",default = 0)
    x_dep_annuel = fields.Float("Dépenses Annuelles",default = 0)
    x_ma_annuel = fields.Float(string = "Marge Annuelle",default = 0)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


#Affichage du chiffre d'affaire sur l'ecran de stats
class FactureFactureStats(models.Model):
    _name = 'facture_stats_ca'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'CA'
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of depense.", default=10)


    name = fields.Date(string='Date opération', default=fields.Date.context_today, readonly=True)
    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.user.company_id.id)
    active = fields.Boolean(string="Etat", default=True)
    currents_users = fields.Many2one('res.users', 'Agent', default=lambda self: self.env.user, readonly=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('Validé', 'Validé'),
    ], 'Etat', default='draft', index=True, readonly=True, copy=False, track_visibility='always')
    x_line_ids = fields.One2many('facture_stats_ca_line','x_fact_stat_ca_id',string = 'Lignes', readonly=True)

    def action_afficher(self):
        for vals in self:
            vals.env.cr.execute("SELECT * FROM facture_facture_stats")
            rows = vals.env.cr.dictfetchall()
            print('Liste CA', rows)
            result = []
            if rows:
                # delete old details transactions lines
                vals.x_line_ids.unlink()
                for line in rows:
                    result.append((0, 0, {
                        'name': line['name'],
                        'x_ca_annuel': line['x_ca_annuel'],
                        'x_dep_annuel': line['x_dep_annuel'],
                        'x_ma_annuel': line['x_ca_annuel'] - line['x_dep_annuel'],
                    }))
                vals.x_line_ids = result


# Affichage du chiffre d'affaire sur l'ecran de stats line
class FactureFactureStatsLine(models.Model):
    _name = 'facture_stats_ca_line'

    x_fact_stat_ca_id = fields.Many2one('facture_stats_ca')
    name = fields.Integer('Année')
    x_ca_annuel = fields.Float("Chiffre d'Affaire Annuel",default = 0)
    x_dep_annuel = fields.Float("Dépenses Annuelles",default = 0)
    x_ma_annuel = fields.Float(string = "Marge Annuelle",default = 0)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)