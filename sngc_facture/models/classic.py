from odoo import fields, models, api
from datetime import date


class SngcFactureClassic(models.Model):
    _name = "sngc.facture.classic"

    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Facture Classic"

    name = fields.Char("FACTURE PROFORMA", readonly=True)
    dte = fields.Date("Date", default=date.today(), required=True)
    doit = fields.Char("Doit :", required=True)
    total = fields.Float("Total", store=True, compute="_total")
    total_tonne = fields.Float("Total tonnes", store=True, compute="_total")
    manut_existe = fields.Float("Manutention ?", default=False)
    frais_manut_total = fields.Float('Frais manutention', compute="_total")
    frais_manut = fields.Float('Montant/Tonne')
    objet = fields.Text("Objet", required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('FP', 'Facture Proforma'), ('V', 'Validé'), ('A', 'Annulé')],
                             default='draft', string="Etat")
    facture_ids = fields.One2many("sngc.facture.classic.line", "facture_id")

    def confirmer(self):
        self.state = 'FP'

    def annuler(self):
        self.state = 'A'

    @api.depends('manut_existe', 'facture_ids.montant_ttc', 'facture_ids.qte')
    def _total(self):
        for facture in self:
            facture.total_tonne = sum(item.qte for item in facture.facture_ids)
            if facture.manut_existe is False:
                facture.total = sum(item.montant_ttc for item in facture.facture_ids)
            else:
                facture.frais_manut_total = facture.frais_manut * facture.total_tonne
                facture.total = sum(item.montant_ttc for item in facture.facture_ids) + facture.frais_manut_total


class SngcFactureClassicLine(models.Model):
    _name = "sngc.facture.classic.line"

    facture_id = fields.Many2one("sngc.facture.classic", ondelete="cascade")
    designation_id = fields.Many2one("sngc.article", "Désignation", required=True)
    qte = fields.Float("Qté(Tonnes)", required=True)
    prix = fields.Float("Prix (HTVA)", required=True)
    montant_ht = fields.Float("Montant HTVA", store=True, compute='_calcul')
    montant_ttc = fields.Float("Montant TTC", store=True, compute='_calcul')

    @api.depends('qte',  'prix')
    def _calcul(self):
        for vals in self:
            vals.montant_ht = vals.qte * vals.prix
            vals.montant_ttc = vals.montant_ht


class SngcCompteurClassic(models.Model):
    _name = "sngc.compteur.classic"

    annee = fields.Integer()
    nombre = fields.Integer()