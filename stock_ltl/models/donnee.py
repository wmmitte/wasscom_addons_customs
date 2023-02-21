from odoo import fields, models


class StockUnite(models.Model):
    _name = "stock.unite"
    _description = 'Modele des unités'

    name = fields.Char("Libellé", required=True)
    description = fields.Text("Description")
    active = fields.Boolean("Actif", default=True)


class StockMode(models.Model):
    _name = "stock.mode"
    _description = 'Modele des mode envoi'

    name = fields.Char("Libellé", required=True)
    description = fields.Text("Description")
    active = fields.Boolean("Actif", default=True)

class StockPersonnel(models.Model):
    _name = "stock.personnel"
    _description = 'Modele personnel'

    name = fields.Char("NOM-PRENOM", required=True)
    cnib = fields.Char("N°CNIB", required=True)
    montant = fields.Float("En cours", readonly=True)
    active = fields.Boolean("Actif", default=True)

class StockArticle(models.Model):
    _name = "stock.article"
    _description = 'Modele des articles'

    name = fields.Char("Article", required=True)
    description = fields.Text("Description")
    active = fields.Boolean("Actif", default=True)
    unite_id = fields.Many2one("stock.unite", "Unité")


class StockMagasin(models.Model):
    _name = "stock.magasin"
    _description = 'Modele des magasins'

    name = fields.Char("Libellé", required=True)
    central = fields.Boolean("Central ?", default=True)
    description = fields.Text("Description")
    active = fields.Boolean("Actif", default=True)
    responsable = fields.Many2one("stock.personnel", "Responsable", required=True)
