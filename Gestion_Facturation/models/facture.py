from odoo import fields,api,models,tools,_
import string
from datetime import datetime,date
import pdb,re
import calendar
from calendar import monthrange
from odoo.exceptions import UserError,ValidationError
from dateutil.relativedelta import relativedelta
import html
from num2words import num2words


#Faire une nouvelle facture
class FactureFacture(models.Model):
    _name = 'facture_facture'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Facture'
    _order = "create_date desc, id desc"
    sequence = fields.Integer(help="Gives the sequence when displaying a list of facture.", default=10)

    _rec_name = 'x_concat_fields'
    x_concat_fields = fields.Char(compute = 'action_concat_code_fact',store = True,string = 'N° Facture')
    name = fields.Char(string = 'N° Facture',readonly = False)
    x_client = fields.Many2one('facture_client',string = 'Client',required = True)
    x_adress = fields.Char(string="Adresse", readonly=True)
    x_objet = fields.Char(string = 'Objet',required = True)

    x_annee_en_cours = fields.Integer('Année', readonly=True)

    active = fields.Boolean(string="Etat", default=True)
    current_users = fields.Many2one('res.users', 'Agent', default=lambda self: self.env.user,readonly=True)
    date_operation = fields.Date(string='Date facture', default=fields.Date.context_today, required=True)
    company_id = fields.Many2one('res.company', string="Structure", default=lambda self: self.env.user.company_id.id,readonly=True)
    state = fields.Selection([
        ('Nouvelle facture', 'Nouvelle'),
        ('Approuvée', 'Approuvée'),
        ('Liquidation partielle', 'En cours'),
        ('Liquidation totale', "Soldée"),
    ], 'Etat', default='Nouvelle facture', index=True, required=False, copy=False, track_visibility='always')
    x_total_facture = fields.Float(compute = '_calcul_total_fact',store = True,string = 'Montant Total')
    x_total_facture_reel = fields.Float(compute = '_calcul_total_fact',store = True,string = 'Montant réel')
    x_total_encaisse = fields.Float(string='Montant Encaissé',readonly = True,default = 0)
    x_total_reste = fields.Float(compute = '_calcul_total_fact',store = True,string='Reste à payer')
    x_total_perte = fields.Float(compute = '_calcul_total_fact',store = True,string='Perte totale')
    x_taux = fields.Float("Taux", readonly=True)
    x_mnt_deduit = fields.Float(compute = '_calcul_total_fact',store = True,string='Montant déduit')

    x_etat_facture = fields.Char('Etat facture',default = 'Nouvelle facture')

    x_line_ids = fields.One2many('facture_facture_line','x_fact_id',string = 'Ligne facture')
    x_mnt_lettre = fields.Char(string = 'Montant en lettre')
    x_signataire_id = fields.Many2one('res.users', 'Signataire',required=True)

    @api.constrains('x_client')
    def _recup_annee(self):
        for record in self:
            annee = date.today().year
            record.x_annee_en_cours = annee
    
    @api.onchange('x_client')
    def taux(self):
        self.x_taux = self.env['taux'].search([('active', '=', True)]).name


    @api.depends('name', 'x_client')
    def action_concat_code_fact(self):
        for record in self:
            if record.name and record.x_client:
                record.x_concat_fields = record.name + '/' + record.x_client.x_designation_client

    @api.depends('x_line_ids.x_mt_ligne','x_line_ids.x_mnt_perte')
    def _calcul_total_fact(self):
        for record in self:
            text = ''
            record.x_mnt_deduit = (sum(line.x_mt_ligne_reel for line in record.x_line_ids) * record.x_taux) / 100.00
            
            record.x_total_facture_reel = sum(line.x_mt_ligne_reel for line in record.x_line_ids)
            
            
            record.x_total_perte = sum(line.x_mnt_perte for line in record.x_line_ids)

            record.x_total_facture = record.x_total_facture_reel - record.x_mnt_deduit - record.x_total_perte
            record.x_total_reste = record.x_total_facture

            text+=num2words(record.x_total_facture_reel,lang='fr')
            record.x_mnt_lettre = text

    @api.onchange('x_client')
    def _affiche_infos(self):
        for vals in self:
            vals.x_adress = vals.x_client.x_adress

    def action_approuver(self):
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
                self.name = 'FACT'+'/'+ok+'/'+ str(x_annee)
                vals = c1
                self.env.cr.execute("INSERT INTO facture_code(company_id,no_code,x_annee)  VALUES(%d,%d,%d)" % (x_struct_id, vals,x_annee))
                self.env.cr.execute("INSERT INTO facture_facture_stats(name,x_ca_annuel,x_dep_annuel,x_ma_annuel,company_id)  VALUES(%d,%d,%d,%d,%d)" % (x_annee,x_total_facture,0,0,x_struct_id))
                record.write({'state': 'Approuvée','x_etat_facture': 'Approuvée'})
            else:
                c1 = int(no_lo) + 1
                c = str(no_lo)
                ok = str(c1).zfill(4)
                self.name = 'FACT'+'/'+ok+'/'+ str(x_annee)
                vals = c1
                self.env.cr.execute("UPDATE facture_code SET no_code = %d  WHERE company_id = %d and x_annee = %d" % (vals, x_struct_id,x_annee))
                self.env.cr.execute("UPDATE facture_facture_stats SET name = %d,x_ca_annuel = x_ca_annuel + %d WHERE company_id = %d and name = %d" % (x_annee,x_total_facture,x_struct_id,x_annee))
                record.write({'state': 'Approuvée','x_etat_facture': 'Approuvée'})


    def fonction_maj(self):

        pour_maj = self.env['facture_facture'].search(
                [('state', '=', 'Approuvée'), ('company_id', '=', self.company_id.id)])
        for p in pour_maj:
            p.update({'x_mnt_deduit' : sum(line.x_mt_ligne_reel for line in p.x_line_ids) * 0.05,
                    'x_total_facture' : sum(line.x_mt_ligne_reel for line in p.x_line_ids) - p.x_mnt_deduit - p.x_total_perte,
                    'x_total_reste' : sum(line.x_mt_ligne_reel for line in p.x_line_ids) - p.x_mnt_deduit - p.x_total_perte, 'x_taux':5})

#Classe pour gerer le compteur pour le code des factures
class Compteur_Code_Facture(models.Model):
    _name = "facture_code"
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    x_annee = fields.Integer('année')
    no_code = fields.Integer()


#Faire une nouvelle facture line
class FactureFactureLine(models.Model):
    _name = 'facture_facture_line'

    x_fact_id = fields.Many2one('facture_facture')
    _rec_name = 'x_concat'
    x_concat = fields.Char(compute = 'action_concat_element',store = True,string = 'Trajet')
    x_date_be = fields.Date(string = 'Date BE',required = True)
    x_num_be = fields.Char(string = 'N° BE',required = True)
    x_date_bl = fields.Date(string = 'Date BL',required = True)
    x_num_bl = fields.Char(string = 'N° BL',required = True)
    x_immatricul_id = fields.Many2one('facture_camion',string = 'Immatriculation',required = True)
    x_trajet_id = fields.Many2one('facture_trajet',string = 'Trajet',required = True)
    x_distance = fields.Float(string = 'Distance (km)',readonly = True)
    x_produit_id = fields.Many2one('facture_produit',string = 'Produit',required = True)
    x_capacite = fields.Float(string='Capacité',digits=(15,5),required = True)
    x_taux = fields.Float(string='Taux',required = True)
    x_mt_ligne = fields.Float(compute = '_mnt_ligne', store = True,string='Mnt réel payé', readonly=True)
    x_echeance_facture = fields.Date(string = 'Echéance')
    x_manquant = fields.Integer(string = 'Capacité manquante',digits=(15,5),default = 0)
    x_capacite_net = fields.Float(compute = '_calcul_cap_net', store = True,string = 'Capacité finale')
    x_mnt_perte = fields.Float(compute = '_mnt_ligne', store = True,string = 'Perte')
    x_mt_ligne_reel = fields.Float(compute = '_mnt_ligne', store = True,string='Mnt Ligne sans perte', readonly=True)
    mnt_manquant = fields.Float("Montant manquant")

    @api.depends('x_capacite','x_manquant')
    def _calcul_cap_net(self):
        for record in self:
            record.x_capacite_net = record.x_capacite - record.x_manquant

    @api.depends('x_date_be', 'x_num_be','x_date_bl','x_num_bl','x_immatricul_id')
    def action_concat_element(self):
        for record in self:
            if record.x_date_be and record.x_num_be and record.x_date_bl and record.x_num_bl and record.x_immatricul_id:
                record.x_concat =  record.x_num_be + '/' + record.x_num_bl + '/' + record.x_immatricul_id.name


    @api.onchange('x_trajet_id')
    def remplir_distance(self):
        for vals in self:
            vals.x_distance = vals.x_trajet_id.x_distance


    @api.depends('x_capacite_net','x_capacite','x_taux','x_manquant')
    def _mnt_ligne(self):
        for vals in self:
            vals.x_mt_ligne = round(vals.x_capacite_net * vals.x_taux)
            vals.x_mnt_perte = round(vals.x_manquant * vals.x_taux)
            vals.x_mt_ligne_reel = round(vals.x_capacite * vals.x_taux)



#Effectuer le paiement d'une facture en attente
class FactureFacturePaiement(models.Model):
    _name = 'facture_facture_paiement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Paiement Facture'
    _order = "create_date desc, id desc"
    sequence = fields.Integer(help="Gives the sequence when displaying a list of paiement facture.", default=10)


    name = fields.Many2one('facture_facture',string = 'N° Facture',required = True,domain = ('|',['state','in',('Approuvée','Liquidation partielle')],['x_etat_facture','in',('Approuvée','Liquidation partielle')]))
    x_client = fields.Many2one('facture_client',string = 'Client',readonly = True)
    x_adress = fields.Char(string="Adresse", readonly=True)
    x_objet = fields.Char(string = 'Objet',readonly = True)

    active = fields.Boolean(string="Etat", default=True)
    current_users = fields.Many2one('res.users', 'Agent', default=lambda self: self.env.user,readonly=True)
    date_operation = fields.Date(string='Date paiement', default=fields.Date.context_today, readonly=True)
    company_id = fields.Many2one('res.company', string="Structure", default=lambda self: self.env.user.company_id.id,readonly=True)
    state = fields.Selection([
        ('Nouveau paiement', 'Non Validé'),
        ('Paiement effectuée', 'Validé'),
    ], 'Statut', default='Nouveau paiement', index=True, required=False, copy=False, track_visibility='always')
    x_total_facture = fields.Float(compute = '_calcul_total_fact',store = True,string = 'Total Facture')
    x_total_encaisse = fields.Float(string='Total Encaissé',readonly = True)
    x_total_reste = fields.Float(string='Reste à payer',readonly = True)
    x_mt_encaisse = fields.Float(string='Somme versée', required=True)
    x_total_reste_apr = fields.Float(compute = '_calcul_rest_mnt', store = True,string='Reste après opération', readonly=True)

    taux5 = fields.Float("Taux(%)", default=5)
    mnt_manquant = fields.Float('Total manquants', store=True)
    ligne_facture = fields.One2many("facture_facture_line", "x_fact_id")



    @api.depends('x_mt_encaisse')
    def _calcul_rest_mnt(self):
        for record in self:
            record.x_total_reste_apr = record.x_total_reste - record.x_mt_encaisse
            print("========== TOTAL RESTE AVT =",record.x_total_reste_apr)
        print("========== TOTAL RESTE APR =",self.x_total_reste_apr)

    @api.onchange('name')
    def act_remplir_champs(self):
        for record in self:
            record.x_client = record.name.x_client
            record.x_adress = record.name.x_adress
            record.x_objet = record.name.x_objet
            record.x_total_facture = record.name.x_total_facture
            record.x_total_encaisse = record.name.x_total_encaisse

            record.x_total_reste = record.name.x_total_reste
    

    def action_valider(self):
        for record in self:
            id_fact = int(record.name.id)
            x_mt_encaisse = float(record.x_mt_encaisse)
            x_total_reste = record.x_total_reste - record.x_mt_encaisse

            if x_mt_encaisse <= 0:
                raise ValidationError(_("Montant %d saisi invalide") % (record.x_mt_encaisse))
            elif record.x_mt_encaisse > record.x_total_reste:
                raise ValidationError(_("Montant %d saisi est supérieur au reste qui est de %d") % (record.x_mt_encaisse,record.x_total_reste))
            elif record.x_total_reste_apr > 0:
                record.env.cr.execute("UPDATE facture_facture SET x_total_encaisse = x_total_encaisse + %d, x_total_reste = x_total_reste - %d,state = 'Liquidation partielle',x_etat_facture = 'Liquidation partielle'  WHERE id = %d" %(record.x_mt_encaisse,x_mt_encaisse,id_fact))
                record.write({'state': 'Paiement effectuée'})
            elif record.x_total_reste_apr == 0:
                record.env.cr.execute("UPDATE facture_facture SET x_total_encaisse = x_total_encaisse + %d, x_total_reste =  %d,state = 'Liquidation totale',x_etat_facture = 'Liquidation totale'  WHERE id = %d" %(record.x_mt_encaisse,x_total_reste,id_fact))
                record.write({'state': 'Paiement effectuée'})
    

    #@api.constrains('x_mt_encaisse')
    @api.constrains('x_total_reste','x_mt_encaisse')
    def _check_montant(self):
        if self.x_total_reste < self.x_mt_encaisse:
            raise ValidationError(_("A-Le montant a encaissé est supérieur au reste à payer."))
        else:
            facture = self.env['facture_facture_paiement'].search([('name','=',self.name.id)])
            print("--facture--", facture)
            montant = 0.0
            for m in facture:
                montant = montant + m.x_mt_encaisse
                print("-----montant : %d, encaissé : %d" % (montant, m.x_mt_encaisse))
                if self.x_total_facture < montant:
                    raise ValidationError(_("B-Le montant a encaissé sera supérieur au montant de la facture : montant encaissé= %d > total facture=%d") % (montant,self.x_total_facture ))
                else:
                    print("Ok")



class FactureQuantite(models.Model):
    _name = 'facture.quantite'
    _rec_name = 'camion_id'

    camion_id = fields.Many2one('facture_camion', 'Camion', required=True)
    chauffeur = fields.Many2one('facture_conducteur_camion', string='Chauffeur', related='camion_id.x_conducteur_id')
    date_operation = fields.Date(string='Date opération', default=fields.Date.context_today, required=True)
    x_date_be = fields.Date(string = 'Date BE',required = True)
    x_num_be = fields.Char(string = 'N° BE',required = True)
    x_date_bl = fields.Date(string = 'Date BL',required = True)
    x_num_bl = fields.Char(string = 'N° BL',required = True)
    quantite = fields.Float(string='Quantité perdue',required = True)
    state = fields.Selection([('1', 'Nouveau'), ('2', 'Validé')], string='Etat', default='1')
    company_id = fields.Many2one('res.company', string="Structure", default=lambda self: self.env.user.company_id.id,readonly=True)

    def valider(self):
        self.state = '2'
        mnqt = self.quantite
        lines_manquant = self.env['facture_facture_line'].search([('x_immatricul_id.id', '=', self.camion_id.id),
                                                      ('x_num_bl', '=', self.x_num_bl),
                                                      ('x_date_bl', '=', self.x_date_bl), 
                                                      ('x_num_be', '=', self.x_num_be),
                                                      ('x_date_bl', '=', self.x_date_bl),
                                                      ])
        for val in lines_manquant:
            val.update({'x_manquant': mnqt, 'x_mnt_perte': mnqt * lines_manquant.x_taux})


class FactureEtatQuantite(models.TransientModel):
    _name = 'facture.etat.quantite'

    name = fields.Char(default="Etat quantité perdue", readonly=True)
    camion_id = fields.Many2one('facture_camion', 'Camion', required=True)
    chauffeur = fields.Many2one('facture_conducteur_camion', string='Chauffeur', related='camion_id.x_conducteur_id')
    dte_deb = fields.Date('Date de début', required=True)
    dte_fin = fields.Date('Date de fin', required=True)
    total = fields.Float('Qté totale perdue', store=True, compute='_total')
    lines_ids = fields.One2many('facture.etat.quantite.line', 'etat_id', readonly=True)


    @api.depends('lines_ids.quantite')
    def _total(self):
        for depense in self:
            depense.total = sum(item.quantite for item in depense.lines_ids)


    def action_afficher(self):
        for va in self:
            va.lines_ids.unlink()
            if va.camion_id:
                lines = va.env['facture.quantite'].search([('camion_id.id', '=', self.camion_id.id),
                                                      ('date_operation', '>=', self.dte_deb),
                                                      ('date_operation', '<=', self.dte_fin), ('state', '=', '2')
                                                      ])
                for li in lines:
                    self.sudo().env['facture.etat.quantite.line'].create({
                        'x_date_be': li.x_date_be,
                        'x_num_be': li.x_num_be,
                        'x_date_bl': li.x_date_bl,
                        'x_num_bl': li.x_num_bl,
                        'quantite': li.quantite,
                        'etat_id': self.id
                    })


class FactureEtatQuantiteLine(models.TransientModel):
    _name = 'facture.etat.quantite.line'

    etat_id = fields.Many2one('facture.etat.quantite')
    x_date_be = fields.Date(string = 'Date BE')
    x_num_be = fields.Char(string = 'N° BE')
    x_date_bl = fields.Date(string = 'Date BL')
    x_num_bl = fields.Char(string = 'N° BL')
    quantite = fields.Float(string='Quantité perdue')


"""
select id, name,state, x_total_facture,x_total_encaisse,x_total_reste,x_mt_encaisse,x_total_reste_apr from facture_facture_paiement;
update facture_facture set x_total_encaisse=0,x_total_reste=x_total_facture;
delete from facture_facture_paiement;
"""