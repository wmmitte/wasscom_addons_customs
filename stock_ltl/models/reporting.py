from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EtatDepense(models.TransientModel):
    _name = 'etat.depense'

    name = fields.Char(default="Etat synthétique de gestion")
    dte_deb = fields.Date("Date debut", required=True)
    dte_fin = fields.Date("Date fin", required=True)
    marche_id = fields.Many2one("stock.marche", "Marché", required=True)
    total_materiel = fields.Float("Matériaux utilisés", readonly=True)
    total_rebut = fields.Float("Destockage / Rébut", readonly=True)
    total_depense = fields.Float("Transferts d'argent", readonly=True)
    total = fields.Float("Total Charges", compute='_total')
    montant_marche = fields.Float("Montant du marché", related='marche_id.mnt_ttc', store=True)
    resultat = fields.Float("Résultat", compute='_total')

    def etat(self):
        marche = int(self.marche_id.id)
        depenses = self.env['stock.envoi'].search(
            [('marche_id.id', '=', marche), ('dte', '>=', self.dte_deb),
             ('dte', '<=', self.dte_fin), ('state', '!=', 'A')])
        montant_depense = 0
        for e in depenses:
            montant_depense = montant_depense + e.montant_envoi
            self.total_depense = montant_depense

        retour = self.env['stock.retour'].search(
            [('marche_id.id', '=', marche), ('dte_retour', '>=', self.dte_deb),
             ('dte_retour', '<=', self.dte_fin), ('state', '!=', 'A')])
        montant_retour = retour.total

        materiel = self.env['stock.sortie'].search(
            [('marche_id.id', '=', marche), ('dte_sortie', '>=', self.dte_deb),
             ('dte_sortie', '<=', self.dte_fin), ('state', '!=', 'A')])
        montant_materiel = 0

        for m in materiel:
            montant_materiel = montant_materiel + m.total
            self.total_materiel = montant_materiel - montant_retour

        rebut = self.env['stock.rebut'].search(
            [('marche_id.id', '=', marche), ('dte_op', '>=', self.dte_deb),
             ('dte_op', '<=', self.dte_fin), ('state', '=', 'V')])
        montant_rebut = 0
        for r in rebut:
            montant_rebut = montant_rebut + r.total
            self.total_rebut = montant_rebut

    @api.depends('total_materiel', 'total_depense')
    def _total(self):
        for va in self:
            va.total = va.total_materiel + va.total_depense
            va.resultat = va.montant_marche - va.total - va.total_rebut

    def print_dep(self):
        return self.env.ref('stock_ltl.report_dep_view').report_action(self)


class EtatStock(models.TransientModel):
    _name = "etat.stock"

    name = fields.Char(default="Etat des stocks")
    par = fields.Selection([('1', 'Par magasin'), ('2', 'Tous les magasins')],
                           required=True, string="Rechercher par", default='1')
    magasin_id = fields.Many2one("stock.magasin", "Magasin", required=True)
    etat_ids = fields.One2many("etat.stock.line", "etat_id")

    def etat(self):
        for va in self:
            va.etat_ids.unlink()
            if va.par == '1':
                lines = va.env['stock.suivi'].search([('magasin_id.id', '=', self.magasin_id.id)])
                for li in lines:
                    self.sudo().env['etat.stock.line'].create({
                        'article_id': li.article_id.id,
                        'initial': li.stock_inital,
                        'en_stock': li.qte_stock,
                        'sortie': li.qte_sortie,
                        'qte_stock': li.qte_stock - li.qte_sortie,
                        'etat_id': self.id
                    })

    def print_stock(self):
        return self.env.ref('stock_ltl.report_etat_stock_view').report_action(self)


class EtatStockLine(models.TransientModel):
    _name = "etat.stock.line"

    etat_id = fields.Many2one("etat.stock")
    article_id = fields.Many2one("stock.article", "Désignation")
    initial = fields.Float("Stock initial")
    en_stock = fields.Float("Entrée")
    sortie = fields.Float("Sortie")
    qte_stock = fields.Float('Quantité en stock', readonly=True)




class EtatDetaille(models.Model):
    _name = "etat.detaille"

    name = fields.Char(default="Etat détaillé des opérations")
    par = fields.Selection([('1', 'Par marché'), ('2', 'Tous les marchés')],
                           string="Par", required=True)
    marche_id = fields.Many2one("stock.marche", "Marché")
    dte_deb = fields.Date("Date debut", required=True)
    dte_fin = fields.Date("Date fin", required=True)
    etat_ids = fields.One2many("etat.detaille.line", "etat_id")

    def etat(self):
        for va in self:
            print("--marche--", va.marche_id)
            va.etat_ids.unlink()
            if va.par == '1' and va.marche_id.id is not False:
                lines = va.env['stock.envoi'].search([('marche_id.id', '=', self.marche_id.id),
                                                      ('dte', '>=', self.dte_deb),
                                                      ('dte', '<=', self.dte_fin), ('state', '=', 'V')
                                                      ])
                for li in lines:
                    self.sudo().env['etat.detaille.line'].create({
                        'dte': li.dte,
                        'marche_id': li.marche_id.id,
                        'responsable_id': li.personnel_id.id,
                        'en_cours': li.en_cours,
                        'mode_id': li.mode_id.id,
                        'reference': li.reference,
                        'montant': li.montant_envoi,
                        'objet': li.objet,
                        'etat_id': self.id
                    })


            elif va.par == '1' and va.marche_id.id is False:
                raise ValidationError(_("Choisissez au moins un marché"))
            else:
                lines = va.env['stock.envoi'].search([('dte', '>=', self.dte_deb),
                                                      ('dte', '<=', self.dte_fin), ('state', '=', 'V')
                                                      ])
                for li in lines:
                    self.sudo().env['etat.detaille.line'].create({
                        'dte': li.dte,
                        'marche_id': li.marche_id.id,
                        'responsable_id': li.personnel_id.id,
                        'en_cours': li.en_cours,
                        'mode_id': li.mode_id.id,
                        'reference': li.reference,
                        'montant': li.montant_envoi,
                        'objet': li.objet,
                        'etat_id': self.id
                    })

    def print_det(self):
        return self.env.ref('stock_ltl.report_etat_detaille_view').report_action(self)


class EtatDetailleLine(models.Model):
    _name = "etat.detaille.line"

    etat_id = fields.Many2one("etat.detaille")
    dte = fields.Date("Date")
    marche_id = fields.Many2one("stock.marche", "Marché")
    responsable_id = fields.Many2one("stock.personnel", "Responsable")
    en_cours = fields.Float("En cours")
    montant = fields.Float("Montant")
    mode_id = fields.Many2one("stock.mode", "Mode de règlement")
    reference = fields.Char("Référence")
    objet = fields.Text("Objet")


class EtatDetStock(models.TransientModel):
    _name = "etat.det.stock"

    dte_deb = fields.Date("Date debut", required=True)
    dte_fin = fields.Date("Date fin", required=True)
    etat_ids = fields.One2many("etat.det.stock.line", "etat_id")
    etat_sortie_ids = fields.One2many("etat.det.sortie.stock.line", "etat_id")

    def etat(self):
        for va in self:
            va.etat_ids.unlink()
            entres = va.env['stock.entree.line'].search([('entree_id.dte_entree', '>=', self.dte_deb),
                                                         ('entree_id.dte_entree', '<=', self.dte_fin),
                                                         ('entree_id.state', '=', 'V')])
            for en in entres:
                self.sudo().env['etat.det.stock.line'].create({
                    'dte_entree': en.entree_id.dte_entree,
                    'article_id': en.article_id.id,
                    'unite_id': en.unite_id.id,
                    'qte': en.quantite,
                    'etat_id': self.id
                })

            sorties = va.env['stock.sortie.line'].search([('sortie_id.dte_sortie', '>=', self.dte_deb),
                                                         ('sortie_id.dte_sortie', '<=', self.dte_fin),
                                                         ('sortie_id.state', '=', 'V')])
            for so in sorties:
                self.sudo().env['etat.det.sortie.stock.line'].create({
                    'dte_sortie': so.sortie_id.dte_sortie,
                    'article_id': so.article_id.id,
                    'unite_id': so.unite_id.id,
                    'qte': so.qte_dmde,
                    'etat_id': self.id
                })

    def print_entree_sortie(self):
        return self.env.ref('stock_ltl.report_etat_entree_sortie_view').report_action(self)


class EtatDetStockLine(models.TransientModel):
    _name = "etat.det.stock.line"

    etat_id = fields.Many2one("etat.det.stock")
    dte_entree = fields.Date("Date entrée")
    article_id = fields.Many2one("stock.article", "Désignation")
    unite_id = fields.Many2one("stock.unite", "Unité")
    qte = fields.Float("Qté")


class EtatDetSortieStockLine(models.TransientModel):
    _name = "etat.det.sortie.stock.line"

    etat_id = fields.Many2one("etat.det.stock")
    dte_sortie = fields.Date("Date sortie")
    article_id = fields.Many2one("stock.article", "Désignation")
    unite_id = fields.Many2one("stock.unite", "Unité")
    qte = fields.Float("Qté")
