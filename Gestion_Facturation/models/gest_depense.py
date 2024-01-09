from odoo import fields,api,models,tools,_
import string
from datetime import datetime,date
import pdb
import calendar
from calendar import monthrange
from odoo.exceptions import UserError,ValidationError
from dateutil.relativedelta import relativedelta


#classe depense
class GestDepense(models.Model):
    _name = 'gest_depense'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Dépense'
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of depense.", default=10) 

    name = fields.Many2one('facture_camion',string = 'Camion',required=False)
    x_type_depense = fields.Selection([
        ('Voyage', 'Voyage'),
        ('Autre', 'Autre'),
    ], 'Type dépense', default='', index=True, required=False, copy=False, track_visibility='always')
    x_immatricul_id = fields.Many2one('facture_camion', string='Camion', readonly=True)
    x_trajet_id = fields.Many2one('facture_trajet', string='Trajet', readonly=True)
    x_distance = fields.Integer(string='Distance (km)', readonly=True)
    x_produit_id = fields.Many2one('facture_produit', string='Produit', readonly=True)
    x_capacite = fields.Integer(string='Capacité', readonly=True)
    objet_dep = fields.Text(string = "Objet", required = True,states={'Validé': [('readonly', True)]})
    x_personnel_id = fields.Many2one('facture_conducteur_camion',string = 'Personnel',required = False)

    mt = fields.Integer('Montant depensé',required = True,states={'Validé': [('readonly', True)]})
    date_op = fields.Date(string = 'Date opération',default=fields.Date.context_today)

    company_id = fields.Many2one('res.company',string = "Société", default=lambda self: self.env.user.company_id.id)
    active = fields.Boolean(string = "Etat", default=True) 
    currents_users = fields.Many2one('res.users','Agent', default=lambda self: self.env.user,readonly=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('Validé', 'Validé'),
        ], 'Etat', default='draft', index=True,readonly=True, copy=False, track_visibility='always')
    x_num_facture = fields.Char(string = 'Dépense N°',readonly=True)


    @api.constrains('name')
    def action_valider(self):
        for record in self:
            x_struct_id = int(record.company_id)
            x_annee = date.today().year
            print('année en cours', x_annee)

            mt = record.mt

            self.env.cr.execute("select no_code from depense_code where company_id = %d and x_annee = %d" % (x_struct_id, x_annee))
            lo = self.env.cr.fetchone()
            no_lo = lo and lo[0] or 0
            c1 = int(no_lo) + 1
            c = str(no_lo)
            if c == "0":
                ok = str(c1).zfill(4)
                self.x_num_facture = 'DEP' + '/' + ok + '/' + str(x_annee)
                vals = c1
                self.env.cr.execute("INSERT INTO depense_code(company_id,no_code,x_annee)  VALUES(%d,%d,%d)" % (x_struct_id, vals, x_annee))
                self.env.cr.execute("UPDATE facture_facture_stats SET x_dep_annuel = x_dep_annuel + %d  WHERE company_id = %d and name = %d" % (mt,x_struct_id,x_annee))
                record.write({'state': 'Validé'})
            else:
                c1 = int(no_lo) + 1
                c = str(no_lo)
                ok = str(c1).zfill(4)
                self.x_num_facture = 'DEP' + '/' + ok + '/' + str(x_annee)
                vals = c1
                self.env.cr.execute("UPDATE depense_code SET no_code = %d  WHERE company_id = %d and x_annee = %d" % (vals, x_struct_id, x_annee))
                self.env.cr.execute("UPDATE facture_facture_stats SET x_dep_annuel = x_dep_annuel + %d  WHERE company_id = %d and name = %d" % (mt,x_struct_id,x_annee))
                record.write({'state': 'Validé'})

#Classe pour gerer le compteur pour le code des dépenses
class Compteur_Code_Depense(models.Model):
    _name = "depense_code"
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    x_annee = fields.Integer('année')
    no_code = fields.Integer()



class LigneFacture(models.Model):
    _name = "ligne.facture"

    num_fact = fields.Char()
    dte = fields.Date()
    total_reel = fields.Float()
    total_a_payer = fields.Float()
    mnt_manquant = fields.Float()
    mnt_deduit = fields.Float()
    mnt_perte = fields.Float()
    mnt_depense = fields.Float()
    type = fields.Char()
