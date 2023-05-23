from odoo import fields,api,models,tools,_


class FleetTypePermis(models.Model):
    _name = 'fleet.type.permis'

    name = fields.Char("Libellé", required=True)
    description = fields.Text(string='Description')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    permis = fields.Char(string='N permis', required=True)
    dte_expire = fields.Date("Date d'expiration")
    type_permis = fields.Many2one('fleet.type.permis', 'Catégorie de permis', required=True)


class FleetFuel(models.Model):
    _name = 'fleet.fuel'

    vehicle_id = fields.Many2one("fleet.vehicle", "Véhicule", required=True)
    prix = fields.Float("Prix du litre", required=True)
    quantite = fields.Float("Quantité", required=True)
    conducteur = fields.Many2one("res.partner", "Conducteur", related='vehicle_id.driver_id')
    license_plate = fields.Char("Immatriculation", related='vehicle_id.license_plate')
    total = fields.Float("Prix total", compute='_mnt_total')
    dte = fields.Date("Date", required=True)
    kilometre = fields.Float("Kilométrage")
    reference = fields.Char("Référence facture")
    observation = fields.Text("Autres informations")
    
    @api.depends('prix', 'quantite')
    def _mnt_total(self):
        for vals in self:
            vals.total = vals.prix * vals.quantite