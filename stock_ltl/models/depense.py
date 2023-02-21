from odoo import fields, models, api, _
from datetime import date
from odoo.exceptions import ValidationError


class StockEnvoi(models.Model):
    _name = 'stock.envoi'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Enregistrement des diférents envoi argent"

    name = fields.Char("Libellé", default="Dépense Personnel - Autres Dépenses", readonly=True)
    dte = fields.Date("Date", default=date.today(), required=True)
    marche_id = fields.Many2one("stock.marche", "Marché",  domain=[('state', '=', 'E')], required=True)
    mode_id = fields.Many2one("stock.mode", "Mode de règlement", required=True)
    reference = fields.Char("Référence", required=True)
    type_operation = fields.Selection([('1', 'Envoi')],
                                     required=True, string="Type d'opération", default='1', readonly=True)
    personnel_id = fields.Many2one("stock.personnel", "Responsable", required=True)
    en_cours = fields.Float("Montant disponible", readonly=True)
    montant_envoi = fields.Float("Montant", required=True)
    objet = fields.Text("Objet", required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('V', 'Fait'), ('A', 'Annulé')],
                             default='draft', string="Etat")

    @api.constrains('montant_envoi')
    def _ctr_mnt(self):
        for va in self:
            if va.montant_envoi < 0:
                raise ValidationError(_("Le montant doit être supérieur à zéro."))

    @api.onchange('personnel_id')
    def mnt_en_cours(self):
        for va in self:
            va.en_cours = va.personnel_id.montant

    def valider_envoi(self):
        for x in self:
            if x.type_operation == '1':
                mnt = self.montant_envoi
                for va in self:
                    res = va.env['stock.personnel'].search([('id', '=', self.personnel_id.id)])
                    mnt_dispo = res.montant
                    res.update({'montant': mnt_dispo + mnt})
                self.state = 'V'
            else:
                x.state = 'V'

    def act_annuler_envoi(self):
        for x in self:
            if x.type_operation == '1':
                mnt = self.montant_envoi
                for va in self:
                    res = va.env['stock.personnel'].search([('id', '=', self.personnel_id.id)])
                    mnt_dispo = res.montant
                    res.update({'montant': mnt_dispo - mnt})
                x.state = 'A'
            else:
                x.state = 'A'


class StockDepensePersonnel(models.Model):
    _name = "stock.depense.personnel"

    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Enregistrement des diférents envoi argent"

    name = fields.Char("Libellé", default="Dépense du personnel", readonly=True)
    dte = fields.Date("Date", default=date.today(), required=True)
    marche_id = fields.Many2one("stock.marche", "Marché", required=True)
    mode_id = fields.Many2one("stock.mode", "Mode de règlement", required=True)
    reference = fields.Char("Référence", required=True)
    total = fields.Float("Total", store=True, compute="_total")
    objet = fields.Text("Objet", required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('V', 'Fait'), ('A', 'Annulé')],
                             default='draft', string="Etat")
    depense_ids = fields.One2many("stock.depense.personnel.line", "depense_id")

    def valider(self):
        self.state = 'V'

    def annuler(self):
        self.state = 'A'

    @api.depends('depense_ids.montant')
    def _total(self):
        for depense in self:
            depense.total = sum(item.montant for item in depense.depense_ids)


class StockDepensePersonnelLine(models.Model):
    _name = "stock.depense.personnel.line"

    depense_id = fields.Many2one("stock.depense.personnel", ondelete="cascade")
    personnel_id = fields.Many2one("stock.personnel", "Personnel", required=True)
    montant = fields.Float("Montant", required=True)


class StockDepensee(models.Model):
    _name = 'stock.depense'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Enregistrement des autres dépenses"

    name = fields.Char("Libellé", default="Autres dépenses", readonly=True)
    dte = fields.Date("Date", default=date.today(), required=True)
    marche_id = fields.Many2one("stock.marche", "Marché", required=True)
    mode_id = fields.Many2one("stock.mode", "Mode de règlement", required=True)
    reference = fields.Char("Référence", required=True)
    montant = fields.Float("Montant", required=True)
    objet = fields.Text("Objet", required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('V', 'Validé'), ('A', 'Annulé')],
                             default='draft', string="Etat")

    def valider_envoi(self):
        self.state = 'V'

    def act_annuler(self):
        self.state = 'A'


class SuiviDepense(models.Model):
    _name = "suivi.depense"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Enregistrement des diférents envoi argent"

    name = fields.Char("Libellé", default="Dépense Personnel - Autres Dépenses", readonly=True)
    dte = fields.Date("Date", default=date.today(), required=True)
    marche_id = fields.Many2one("stock.marche", "Marché", domain=[('state', '=', 'E')], required=True)
    personnel_id = fields.Many2one("stock.personnel", "Responsable", required=True)
    en_cours = fields.Float("Montant disponible", readonly=True)
    montant_depense = fields.Float("Montant dépensé", compute='_total', store=True)
    nouveau_dispo = fields.Float("Nouveau disponible", compute='_total', store=True)
    state = fields.Selection([('draft', 'Brouillon'), ('V', 'Fait')],
                             default='draft', string="Etat")
    depense_ids = fields.One2many("suivi.depense.line", "suivi_id")

    @api.onchange('personnel_id')
    def mnt_en_cours(self):
        for va in self:
            va.en_cours = va.personnel_id.montant

    @api.depends('depense_ids.montant')
    def _total(self):
        for entree in self:
            entree.montant_depense = sum(item.montant for item in entree.depense_ids)
            entree.nouveau_dispo = entree.en_cours - entree.montant_depense

    def valider(self):
        mnt = self.montant_depense
        for va in self:
            res = va.env['stock.personnel'].search([('id', '=', self.personnel_id.id)])
            mnt_dispo = res.montant
            res.update({'montant': mnt_dispo - mnt})
        self.state = 'V'


class SuiviDepenseLine(models.Model):
    _name = "suivi.depense.line"

    suivi_id = fields.Many2one("suivi.depense", ondelete='cascade')
    libelle = fields.Char("Libellé", required=True)
    montant = fields.Float("Montant", required=True)


