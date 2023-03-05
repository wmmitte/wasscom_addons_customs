from odoo import fields, models, api
from datetime import date
from num2words import num2words


class SngcFacturePam(models.Model):
    _name = "sngc.facture.pam"

    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Facture PAM"
    _rec_name = "namef"

    name = fields.Char("FACTURE PROFORMA", readonly=True)
    namef = fields.Char("FACTURE", readonly=True)
    dte = fields.Date("Date", default=date.today(), required=True, states={'V': [('readonly', True)]})
    vendor = fields.Integer("N° Vendor", required=True, default=50085944)
    doit = fields.Char("Doit :", default='Programme Alimentaire Mondial', required=True, states={'V': [('readonly', True)]})
    total = fields.Float("Total", store=True, compute="_total")
    objet = fields.Text("Objet", required=True, states={'V': [('readonly', True)]})
    mnt_lettre = fields.Char(string='Montant en lettre')
    state = fields.Selection([('draft', 'Brouillon'), ('FP', 'Facture Proforma'), ('V', 'Validé'), ('A', 'Annulé')],
                             default='draft', string="Etat")
    company_id = fields.Many2one('res.company', readonly=True,
                                 default=lambda self: self.env.user.company_id.id)
    facture_ids = fields.One2many("sngc.facture.pam.line", "facture_id", states={'V': [('readonly', True)]})

    def confirmer(self):
        self.act_numero()
        self.state = 'FP'

    def valider(self):
        self.act_numerof()
        self.state = 'V'

    def annuler(self):
        self.state = 'A'

    def act_numero(self):
        annee = date.today()
        val_annee = annee.year
        struct = self.company_id.name
        for val in self:
            resultat = self.sudo().env['sngc.compteur.pam'].search(
                [('annee', '=', val_annee), ('company_id', '=', val.company_id.id)])
            numero = 1
            if resultat:
                numero = resultat.nombre + 1
                resultat.nombre = numero
                numero = str(numero).zfill(3)
            else:
                self.env['sngc.compteur.pam'].create({
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
            resultat = self.sudo().env['sngc.compteur.pam'].search(
                [('annee', '=', val_annee), ('company_id', '=', val.company_id.id)])
            numero = 1
            if resultat:
                numero = resultat.nombref + 1
                resultat.nombref = numero
                numero = str(numero).zfill(3)
            else:
                self.env['sngc.compteur.pam'].create({
                    'nombref': 1,
                    'annee': val_annee,
                    'company_id': val.company_id.id})
                numero = str(numero).zfill(3)
            val.namef = "N°" + numero + "/" + str(struct) + "/" + str(val_annee)


    @api.depends('facture_ids.montant', 'facture_ids.qte')
    def _total(self):
        for facture in self:
            text = ''
            facture.total = sum(item.montant for item in facture.facture_ids)
            text += num2words(self.total, lang='fr')
            self.mnt_lettre = text



class SngcFacturePamLine(models.Model):
    _name = "sngc.facture.pam.line"

    facture_id = fields.Many2one("sngc.facture.pam", ondelete="cascade")
    manut_id = fields.Many2one("sngc.manutention")
    tpo = fields.Integer("N° TPO", required=True)
    sto = fields.Integer("N° STO", required=True)
    designation = fields.Char("Désignation", required=True)
    qte = fields.Float("Quantité", required=True)
    prix = fields.Float("Prix unitaire", required=True)
    prix_manut = fields.Float("Prix unitaire")
    manut_total = fields.Float("Montant", store=True, compute='_calcul_manut')
    montant = fields.Float("Montant", store=True, compute='_calcul')

    @api.depends('qte', 'prix')
    def _calcul(self):
        for vals in self:
            vals.montant = vals.qte * vals.prix

    @api.depends('qte', 'prix_manut')
    def _calcul_manut(self):
        for vals in self:
            vals.manut_total = vals.qte * vals.prix_manut


class SngcCompteurPam(models.Model):
    _name = "sngc.compteur.pam"

    annee = fields.Integer()
    nombre = fields.Integer()
    nombref = fields.Integer()
    nombrep = fields.Integer()
    company_id = fields.Many2one("res.company")


class SngcManutention(models.Model):
    _name = 'sngc.manutention'

    facture_id = fields.Many2one("sngc.facture.pam", "Facture", required=True, domain=[('state', '=', 'V')])
    dte = fields.Date("Date", readonly=True)
    name = fields.Char("N° Facture", readonly=True)
    vendor = fields.Integer("N° Vendor", readonly=True, default=50085944)
    doit = fields.Char("Doit :", default='Programme Alimentaire Mondial', readonly=True)
    total = fields.Float("Total", store=True, compute='_sum_total')
    objet = fields.Text("Objet", required=True, states={'V': [('readonly', True)]})
    state = fields.Selection([('draft', 'Brouillon'), ('V', 'Validé')],
                             default='draft', string="Etat")
    mnt_lettre = fields.Char(string='Montant en lettre')
    manutention_ids = fields.One2many("sngc.facture.pam.line", "manut_id", states={'V': [('readonly', True)]})
    company_id = fields.Many2one('res.company', readonly=True,
                                 default=lambda self: self.env.user.company_id.id)

    @api.depends('manutention_ids.montant', 'manutention_ids.qte')
    def _sum_total(self):
        for facture in self:
            text = ''
            facture.total = sum(item.manut_total for item in facture.manutention_ids)
            text += num2words(self.x_total_facture, lang='fr')
            self.mnt_lettre = text


    @api.onchange('facture_id')
    def val_ids(self):
        for va in self:
            if va.facture_id:
                va.dte = va.facture_id.dte
                va.doit = va.facture_id.doit
                va.manutention_ids = va.facture_id.facture_ids


    def valider(self):
        self.act_numerop()
        self.state = 'V'

    def act_numerop(self):
        annee = date.today()
        val_annee = annee.year
        struct = self.company_id.name
        for val in self:
            resultat = self.sudo().env['sngc.compteur.pam'].search(
                [('annee', '=', val_annee), ('company_id', '=', val.company_id.id)])
            numero = 1
            if resultat:
                numero = resultat.nombrep + 1
                resultat.nombrep = numero
                numero = str(numero).zfill(3)
            else:
                self.env['sngc.compteur.pam'].create({
                    'nombref': 1,
                    'annee': val_annee,
                    'company_id': val.company_id.id})
                numero = str(numero).zfill(3)
            val.name = "N°" + numero + "/" + str(struct) + "/" + str(val_annee)

