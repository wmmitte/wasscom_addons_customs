from odoo import fields, models, api
from datetime import date
from num2words import num2words


class SngcFactureSonagess(models.Model):
    _name = "sngc.facture.sonagess"

    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Facture SONAGESS"

    name = fields.Char("FACTURE PROFORMA", readonly=True)
    namef = fields.Char("FACTURE", readonly=True)
    dte = fields.Date("Date", default=date.today(), required=True, states={'V': [('readonly', True)]})
    region_id = fields.Many2one("sngc.region", "Région", required=True, states={'V': [('readonly', True)]})
    province_id = fields.Many2one("sngc.province", "Départ", required=True, states={'V': [('readonly', True)]})
    doit = fields.Char("Doit :", default='Société Nationale de Gestion de Stock et de Sécurité Alimentaire (SONAGESS)')
    total = fields.Float("Total",digits=(12,3), store=True, compute="_total")
    total_tonne = fields.Float("Total tonnes",digits=(12,3), store=True, compute="_total")
    manut_existe = fields.Boolean("Manutention ?", default=False, states={'V': [('readonly', True)]})
    frais_manut = fields.Float('Montant/Tonne',digits=(12,3), states={'V': [('readonly', True)]})
    objet = fields.Text("Objet", required=True, states={'V': [('readonly', True)]})
    company_id = fields.Many2one('res.company', readonly=True,
                                 default=lambda self: self.env.user.company_id.id)
    mnt_lettre = fields.Char(string='Montant en lettre')
    state = fields.Selection([('draft', 'Brouillon'), ('FP', 'Facture Proforma'), ('V', 'Validé'), ('A', 'Annulé')],
                             default='draft', string="Etat")
    facture_ids = fields.One2many("sngc.facture.sonagess.line", "facture_id", states={'V': [('readonly', True)]})

    def confirmer(self):
        self.act_numero()
        self.state = 'FP'

    def valider(self):
        self.act_numerof()
        self.state = 'V'

    def act_numero(self):
        annee = date.today()
        val_annee = annee.year
        struct = self.company_id.name
        for val in self:
            resultat = self.sudo().env['sngc.compteur.sonagess'].search(
                [('annee', '=', val_annee), ('company_id', '=', val.company_id.id)])
            numero = 1
            if resultat:
                numero = resultat.nombre + 1
                resultat.nombre = numero
                numero = str(numero).zfill(3)
            else:
                self.env['sngc.compteur.sonagess'].create({
                    'nombre': 1,
                    'annee': val_annee,
                    'company_id': val.company_id.id})
                numero = str(numero).zfill(3)
            val.name = "N°" + numero + "/" + str(struct) + "/" + str(val_annee)

    def act_numerof(self):
        annee = date.today()
        val_annee = annee.year
        struct = self.company_id.name
        for val in self:
            resultat = self.sudo().env['sngc.compteur.sonagess'].search(
                [('annee', '=', val_annee), ('company_id', '=', val.company_id.id)])
            numero = 1
            if resultat:
                numero = resultat.nombref + 1
                resultat.nombref = numero
                numero = str(numero).zfill(3)
            else:
                self.env['sngc.compteur.sonagess'].create({
                    'nombref': 1,
                    'annee': val_annee,
                    'company_id': val.company_id.id})
                numero = str(numero).zfill(3)
            val.namef = "N°" + numero + "/" + str(struct) + "/" + str(val_annee)

    def annuler(self):
        self.state = 'A'

    @api.depends('manut_existe', 'facture_ids.montant_ttc', 'facture_ids.qte', 'frais_manut')
    def _total(self):
        for facture in self:
            text = ''
            facture.total_tonne = sum(item.qte for item in facture.facture_ids)
            if facture.manut_existe is False:
                facture.total = sum(item.montant_ttc for item in facture.facture_ids)
                text += num2words(self.total, lang='fr')
                self.mnt_lettre = text
            else:
                facture.total = sum(item.montant_ttc for item in facture.facture_ids) + (facture.frais_manut * facture.total_tonne)
                text += num2words(self.total, lang='fr')
                self.mnt_lettre = text


class SngcFactureSonagessLine(models.Model):
    _name = "sngc.facture.sonagess.line"

    facture_id = fields.Many2one("sngc.facture.sonagess", ondelete="cascade")
    ville_id = fields.Many2one("sngc.ville", "Ville/Localité", required=True)
    boutique = fields.Integer("Boutique", required=True)
    designation_id = fields.Many2one("sngc.article", "Article", required=True)
    qte = fields.Float("Qté (Tonnes)",digits=(12,3), required=True)
    prix = fields.Float("Prix/TK (HTVA)",digits=(12,3), required=True)
    montant_ht = fields.Float("Montant HTVA",digits=(12,3), store=True, compute='_calcul')
    montant_ttc = fields.Float("Montant TTC",digits=(12,3), store=True, compute='_calcul')
    distance = fields.Float("Distance (Km)")

    @api.depends('qte', 'distance', 'prix')
    def _calcul(self):
        for vals in self:
            if vals.distance <= 100:
                vals.montant_ht = vals.qte * vals.prix
                vals.montant_ttc = vals.montant_ht
            else:
                vals.montant_ht = vals.qte * vals.prix * vals.distance
                vals.montant_ttc = vals.montant_ht


class SngcCompteurSonagess(models.Model):
    _name = "sngc.compteur.sonagess"

    annee = fields.Integer()
    nombre = fields.Integer()
    nombref = fields.Integer()
    company_id = fields.Many2one("res.company")
