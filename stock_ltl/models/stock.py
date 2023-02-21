from odoo import fields, models, api, _
from datetime import date
from odoo.exceptions import ValidationError


class StockEntree(models.Model):
    _name = 'stock.entree'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Permet d enregistrer le stock des différents articles'

    name = fields.Char("N° d'entrée", readonly=True)
    dte_entree = fields.Date("Date d'entrée", required=True)
    magasin_id = fields.Many2one("stock.magasin", "Magasin", required=True)
    total = fields.Float("Montant total", compute='_total')
    state = fields.Selection([('draft', 'Brouillon'), ('V', 'Validée')],
                             default='draft', string="Etat")
    stock_ids = fields.One2many("stock.entree.line", "entree_id")

    @api.constrains('stock_ids')
    def _check_exist_article_in_line(self):
        for entree in self:
            article_in_lines = entree.mapped('stock_ids.article_id')
            for article in article_in_lines:
                lines_count = len(entree.stock_ids.filtered(lambda line: line.article_id == article))
                if lines_count > 1:
                    raise ValidationError(_("Un article a ajouté plus d\'une fois dans la liste."))
        return True

    @api.depends('stock_ids.prix_total')
    def _total(self):
        for entree in self:
            entree.total = sum(item.prix_total for item in entree.stock_ids)

    """enregistrement dans la table suivi.stock"""
    def act_valider(self):
        ligne_entree = self.env['stock.entree.line'].search([('entree_id', '=', self.id)])
        for val in ligne_entree:
            article = val.article_id.id
            qte = val.quantite
            unite = val.unite_id.id
            qte_en_stock = self.env['stock.suivi'].search([
                ('article_id', '=', article), ('magasin_id', '=', self.magasin_id.id)])
            qte_en_stock_existance = qte_en_stock.qte_stock
            inital = qte_en_stock.stock_inital
            existe = self.env['stock.suivi'].search_count([
                ('article_id', '=', article), ('magasin_id', '=', self.magasin_id.id)])
            if existe == 0:
                self.sudo().env['stock.suivi'].create({
                    'article_id': article,
                    'magasin_id': self.magasin_id.id,
                    'unite_id': unite,
                    'stock_inital': inital + qte,
                    'qte_stock': qte_en_stock_existance + qte,
                })
            else:
                qte_en_stock.update({'qte_stock': qte_en_stock_existance + qte})

        self.write({'state': 'V'})
        self.act_numero()
        return self.create_rainbow_man("Stock enregistré avec succès !")

    def create_rainbow_man(self, message):
        return {
            'effect': {
                'fadeout': 'slow',
                'message': message,
                'type': 'rainbow_man'
            }
        }

    def act_numero(self):
        annee = date.today()
        val_annee = annee.year
        for val in self:
            resultat = self.sudo().env['stock.compteur'].search(
                [('annee', '=', val_annee)])
            numero = 1
            if resultat:
                numero = resultat.nombre + 1
                resultat.nombre = numero
                numero = str(numero).zfill(6)
            else:
                self.env['stock.compteur'].create({
                    'nombre': 1,
                    'annee': val_annee})
                numero = str(numero).zfill(6)
            val.name = "Stock N°" + "/" + str(val_annee) + "/" + numero


class StockEntreeLine(models.Model):
    _name = 'stock.entree.line'
    _description = 'Permet d enregistrer les lignes du stock des différents articles'

    entree_id = fields.Many2one("stock.entree", ondelete='cascade')
    article_id = fields.Many2one("stock.article", "Désignation", required=True)
    unite_id = fields.Many2one("stock.unite", "Unité", related='article_id.unite_id')
    quantite = fields.Float("Quantité", required=True, default=1)
    prix_unitaire = fields.Float("P.U", required=True)
    prix_total = fields.Float("Total", compute='_sous_total')

    @api.depends('prix_unitaire', 'quantite')
    def _sous_total(self):
        for line in self:
            line.prix_total = line.prix_unitaire * line.quantite


class OkiraSuiviStock(models.Model):
    _name = 'stock.suivi'
    _description = 'Modele de suivi de stock'

    magasin_id = fields.Many2one("stock.magasin", "Magasin", readonly=True)
    article_id = fields.Many2one("stock.article", "Article", readonly=True)
    unite_id = fields.Many2one("stock.unite", "Unité", readonly=True)
    stock_inital = fields.Float("Stock initial", readonly=True)
    qte_stock = fields.Float("En stock", readonly=True)
    qte_sortie = fields.Float("Sortie", readonly=True)
    qte_rebut = fields.Float("Rébut", readonly=True)
    qte_retour = fields.Float("Retour", readonly=True)


class StockRebut(models.Model):
    _name = 'stock.rebut'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'définition de la table de rebut'

    name = fields.Char("N° Rébut", readonly=True)
    magasin_id = fields.Many2one("stock.marche.line", "Magasin", required=True)
    marche_id = fields.Many2one("stock.marche", "Marché", domain=[('state', '=', 'E')], required=True)
    article_id = fields.Many2one("stock.article", "Article", required=True)
    unite_id = fields.Many2one("stock.unite", "Unité", related='article_id.unite_id')
    dte_op = fields.Date("Date opération", default=date.today(), required=True)
    quantite = fields.Float("Quantité à détruire", required=True)
    qte_dispo = fields.Float("Quantité disponible", readonly=True)
    commentaire = fields.Text('Motif de rebut', required=True)
    prix_unitaire = fields.Float("Prix unitaire", required=True)
    total =fields.Float("Mt Total", compute='_sous_total', store=True)
    state = fields.Selection([('draft', 'Brouillon'), ('V', 'Fait')],
                             default='draft', string="Etat")

    @api.depends('prix_unitaire', 'quantite')
    def _sous_total(self):
        for line in self:
            line.total = line.prix_unitaire * line.quantite

    @api.onchange('magasin_id', 'article_id')
    def dispo(self):
        mag = int(self.magasin_id.magasin_id.id)
        for val in self:
            en_stock = self.env['stock.suivi'].search([('article_id', '=', val.article_id.id),
                                                       ('magasin_id', '=', mag)])
            val.qte_dispo = en_stock.qte_stock
            print("disp", )

    def act_rebut(self):
        magasin = int(self.magasin_id.magasin_id.id)
        for val in self:
            qte = val.quantite
            rebut = self.env['stock.suivi'].search([('article_id', '=', val.article_id.id),
                                                    ('magasin_id', '=', magasin)])
            reb = rebut.qte_rebut

            rebut.update({'qte_rebut': reb + qte})

        self.act_numero()
        self.state = 'V'

    def act_numero(self):
        annee = date.today()
        val_annee = annee.year
        for val in self:
            resultat = self.sudo().env['stock.compteur.rebut'].search([('annee', '=', val_annee)])
            numero = 1
            if resultat:
                numero = resultat.nombre + 1
                resultat.nombre = numero
                numero = str(numero).zfill(6)
            else:
                self.env['stock.compteur.rebut'].create({
                    'nombre': 1,
                    'annee': val_annee})
                numero = str(numero).zfill(6)
            val.name = "Ordre de rebut N°" + "/" + str(val_annee) + "/" + str(numero)

class StockSortie(models.Model):
    _name = 'stock.sortie'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'définition de la table sortie stock'

    name = fields.Char("N° Sortie", readonly=True)
    magasin_id = fields.Many2one("stock.magasin", "De", required=True)
    marche_id = fields.Many2one("stock.marche", "Marché", domain=[('state', '=', 'E')], required=True)
    magasin_vers = fields.Many2one("stock.marche.line", "Vers", required=True)
    dte_sortie = fields.Date("Date sortie", default=date.today(), required=True)
    total = fields.Float("Montant total", compute='_total', store=True)
    objet = fields.Text("Objet", required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('V', 'Sortie validée'), ('A', 'Annulée sortie')],
                             default='draft', string="Etat")
    sortie_ids = fields.One2many('stock.sortie.line', 'sortie_id')

    @api.constrains('sortie_ids')
    def _verification(self):
        for x in self.sortie_ids:
            if x.qte_dispo < x.qte_dmde:
                raise ValidationError(_("La quantité à servir d'une des désignations" +
                                        " " + "est supérieue à la disponibilité"))

    def act_valider(self):
        self.act_numero()
        self.act_sortie()
        self.state = 'V'

    def act_numero(self):
        marche = int(self.marche_id)
        nom_marche = self.marche_id.name
        for val in self:
            resultat = self.sudo().env['stock.compteur.sortie'].search(
                [('marche_id', '=', marche)])
            numero = 1
            if resultat:
                numero = resultat.nombre + 1
                resultat.nombre = numero
                numero = str(numero).zfill(6)
            else:
                self.env['stock.compteur.sortie'].create({
                    'nombre': 1,
                    'marche_id': marche})
                numero = str(numero).zfill(6)
            val.name = "Sortie N°" + "/" + str(numero) + " " + str(nom_marche)

    def act_annuler(self):
        self.state = 'A'

    def act_sortie(self):
        mag_ver = int(self.magasin_vers.magasin_id.id)
        mag_de = int(self.magasin_id.id)
        for val in self.sortie_ids:
            article = val.article_id.id
            qte = val.qte_dmde
            pour_sortie = self.env['stock.suivi'].search([('article_id', '=', article),
                                                          ('magasin_id', '=', mag_de)])
            for ligne in pour_sortie:
                en_stock = ligne.qte_stock
                sortie = ligne.qte_sortie
                ligne.update({'qte_stock': en_stock - qte, 'qte_sortie': sortie + qte})

            pour_sortie_vers = self.env['stock.suivi'].search(
                [('article_id', '=', article), ('magasin_id', '=', mag_ver)])
            qte_en_stock_existance = pour_sortie_vers.qte_stock
            inital = pour_sortie_vers.stock_inital

            """compteur pour vérifier si existance de ligne 1.si non insert si oui else pour update"""
            pour_appro_cpt = self.env['stock.suivi'].search_count(
                [('article_id', '=', article), ('magasin_id', '=', mag_ver)])
            if pour_appro_cpt == 0:
                self.sudo().env['stock.suivi'].create({
                    'article_id': article,
                    'magasin_id': mag_ver,
                    'qte_stock': qte_en_stock_existance + qte,
                    'stock_inital': inital + qte,
                })
            else:
                pour_appro = self.env['stock.suivi'].search(
                    [('article_id', '=', article), ('magasin_id', '=', mag_ver)])
                for p in pour_appro:
                    en_stock = p.qte_stock
                    p.update({'qte_stock': en_stock + qte})

        self.state = 'V'

    @api.depends('sortie_ids.prix_total')
    def _total(self):
        for sortie in self:
            sortie.total = sum(item.prix_total for item in sortie.sortie_ids)

    @api.onchange('sortie_ids')
    def dispo(self):
        mag = int(self.magasin_id.id)
        for val in self.sortie_ids:
            en_stock = self.env['stock.suivi'].search([('article_id', '=', val.article_id.id),
                                                       ('magasin_id', '=', mag)])
            val.qte_dispo = en_stock.qte_stock


class StockSortieLine(models.Model):
    _name = 'stock.sortie.line'

    sortie_id = fields.Many2one("stock.sortie", ondelete='cascade')
    article_id = fields.Many2one("stock.article", "Article", required=True)
    unite_id = fields.Many2one("stock.unite", "Unité", related='article_id.unite_id')
    qte_dmde = fields.Float("Quantité demandée", required=True)
    qte_dispo = fields.Float("Quantité disponible", readonly=True)
    prix_unitaire = fields.Float("P.U", required=True)
    prix_total = fields.Float("Prix total", compute='_sous_total')

    @api.depends('prix_unitaire', 'qte_dmde')
    def _sous_total(self):
        for line in self:
            line.prix_total = line.prix_unitaire * line.qte_dmde


class StockCompteur(models.Model):
    _name = "stock.compteur"

    annee = fields.Integer()
    nombre = fields.Integer()

class StockCompteurRebut(models.Model):
    _name = "stock.compteur.rebut"

    annee = fields.Integer()
    nombre = fields.Integer()


class StockCompteurSortie(models.Model):
    _name = "stock.compteur.sortie"

    marche_id = fields.Many2one("stock.marche")
    nombre = fields.Integer()


class StockCompteurRetour(models.Model):
    _name = "stock.compteur.retour"

    marche_id = fields.Many2one("stock.marche")
    nombre = fields.Integer()



class StockMarche(models.Model):
    _name = "stock.marche"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Libellé", required=True)
    dte = fields.Date("Date")
    tva_existe = fields.Boolean("TVA existe?")
    mnt_ht = fields.Float("Montant HT", required=True)
    mnt_ttc = fields.Float("Montant TTC", compute='_calcul_ttc')
    state = fields.Selection([('N', 'Nouveau'), ('E', 'En cours'), ('T', 'Terminée')],
                             default='N', string="Etat")
    magasin_ids = fields.One2many("stock.marche.line", "marche_id")
    stock_ids = fields.One2many("stock.stock.line", "marche_id")

    @api.depends('tva_existe')
    def _calcul_ttc(self):
        for val in self:
            if val.tva_existe is False:
                val.mnt_ttc = val.mnt_ht
            else:
                val.mnt_ttc = val.mnt_ht * 1.18

    def act_confirmer(self):
        self.state = 'E'

    def act_cloturer(self):
        self.state = 'T'

    @api.constrains('magasin_ids')
    def _cpte_mag(self):
        for val in self:
            nbre_mag = len(val.magasin_ids)
            if nbre_mag < 1:
                raise ValidationError(_("Veuillez créer au moins un magasin pour ce marché."))
            else:
                pass

class StockMarcheLine(models.Model):
    _name = "stock.marche.line"
    _rec_name = "magasin_id"

    marche_id = fields.Many2one("stock.marche", ondelete='cascade')
    magasin_id = fields.Many2one("stock.magasin", "Magasin", required=True)
    responsable = fields.Many2one("stock.personnel", "Responsable", required=True, related='magasin_id.responsable')
    ouvert = fields.Boolean("Actif", default=True)


class StockStockLine(models.Model):
    _name = "stock.stock.line"

    marche_id = fields.Many2one("stock.marche", ondelete='cascade')
    article_id = fields.Many2one("stock.article", "Désignation", required=True)
    qte = fields.Float("Qté", required=True)
    qte_conso = fields.Float("Qté consommée", readonly=True)
    ecart = fields.Float("Ecart", store=True)

    @api.depends('qte_conso', 'qte')
    def _ecart(self):
        for va in self:
            va.ecart = va.qte - va.qte_conso

class BilanJournee(models.Model):
    _name = "bilan.journee"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Libellé")
    dte = fields.Date("Date",  default=date.today(), required=True)
    marche_id = fields.Many2one("stock.marche", "Marché", domain=[('state','=', 'E')],  required=True)
    magasin_id = fields.Many2one("stock.marche.line", "Magasin", required=True)
    responsable = fields.Many2one("stock.personnel", "Responsable", readonly=True)
    objet = fields.Text("Commentaire")
    state = fields.Selection([('N', 'Nouveau'), ('V', 'Validé')], default='N', string="Etat")
    bilan_ids = fields.One2many("bilan.journee.line", "bilan_id")

    @api.onchange('magasin_id')
    def respo(self):
        for va in self:
            mag = self.env['stock.magasin'].search([('id', '=', va.magasin_id.magasin_id.id)])
            va.responsable = mag.responsable

    @api.onchange('bilan_ids')
    def dispo(self):
        mag = int(self.magasin_id.magasin_id.id)
        for val in self.bilan_ids:
            en_stock = self.env['stock.suivi'].search([('article_id', '=', val.article_id.id),
                                                       ('magasin_id', '=', mag)])
            val.qte_actuel = en_stock.qte_stock

    def act_sortie_mag(self):
        mag = int(self.magasin_id.magasin_id.id)
        for val in self.bilan_ids:
            article = val.article_id.id
            qte = val.qte_conso
            pour_conso = self.env['stock.suivi'].search([('article_id', '=', article), ('magasin_id', '=', mag)])
            for ligne in pour_conso:
                en_stock = ligne.qte_stock
                sortie = ligne.qte_sortie
                ligne.update({'qte_stock': en_stock - qte, 'qte_sortie': sortie + qte})

        self.name = "Bilan" + " "+ "du" + " " + str(self.dte) + "/" + str(self.marche_id.name) + "/" + str(self.magasin_id.magasin_id.name)
        self.state = 'V'

class BilanJourneeLine(models.Model):
    _name = "bilan.journee.line"

    bilan_id = fields.Many2one("bilan.journee", ondelete="cascade")
    article_id = fields.Many2one("stock.article", "Article", required=True)
    unite_id = fields.Many2one("stock.unite", "Unité", related='article_id.unite_id')
    qte_actuel = fields.Float("Quantité actuelle", readonly=True)
    qte_conso = fields.Float("Quantité consommée", required=True)
    reste = fields.Float("Quantité restante", compute="_qte_reste")

    @api.depends('qte_conso')
    def _qte_reste(self):
        for va in self:
            va.reste = va.qte_actuel - va.qte_conso



class StockRetour(models.Model):
    _name = 'stock.retour'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'définition de la table retour stock'

    name = fields.Char("N° Retour", readonly=True)
    magasin_vers = fields.Many2one("stock.magasin", "Vers", required=True)
    marche_id = fields.Many2one("stock.marche", "Marché", domain=[('state', '=', 'E')], required=True)
    magasin_de = fields.Many2one("stock.marche.line", "De", required=True)
    dte_retour = fields.Date("Date retour", default=date.today(), required=True)
    total = fields.Float("Montant total", compute='_total', store=True)
    objet = fields.Text("Objet", required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('V', 'Retour validé')],
                             default='draft', string="Etat")
    retour_ids = fields.One2many('stock.retour.line', 'retour_id')

    @api.constrains('sortie_ids')
    def _verification(self):
        for x in self.sortie_ids:
            if x.qte_dispo < x.qte_dmde:
                raise ValidationError(_("La quantité à servir d'une des désignations" +
                                        " " + "est supérieue à la disponibilité"))

    def act_valider(self):
        self.act_numero()
        self.act_sortie()
        self.state = 'V'

    def act_numero(self):
        marche = int(self.marche_id)
        nom_marche = self.marche_id.name
        for val in self:
            resultat = self.sudo().env['stock.compteur.retour'].search(
                [('marche_id', '=', marche)])
            numero = 1
            if resultat:
                numero = resultat.nombre + 1
                resultat.nombre = numero
                numero = str(numero).zfill(6)
            else:
                self.env['stock.compteur.retour'].create({
                    'nombre': 1,
                    'marche_id': marche})
                numero = str(numero).zfill(6)
            val.name = "Retour N°" + "/" + str(numero) + " " + str(nom_marche)

    def act_sortie(self):
        mag_de = int(self.magasin_de.magasin_id.id)
        mag_ver = int(self.magasin_vers.id)
        for val in self.retour_ids:
            article = val.article_id.id
            qte = val.qte
            pour_retour = self.env['stock.suivi'].search(
                [('article_id', '=', article), ('magasin_id', '=', mag_de)])
            for ligne in pour_retour:
                en_stock = ligne.qte_stock
                retour = ligne.qte_retour
                ligne.update({'qte_stock': en_stock - qte, 'qte_retour': retour + qte})


            pour_appro = self.env['stock.suivi'].search(
                [('article_id', '=', article), ('magasin_id', '=', mag_ver)])
            for p in pour_appro:
                en_stock = p.qte_stock
                retour_p = p.qte_retour
                p.update({'qte_stock': en_stock + qte, 'qte_retour': retour_p + qte})

        self.state = 'V'

    @api.depends('retour_ids.prix_total')
    def _total(self):
        for sortie in self:
            sortie.total = sum(item.prix_total for item in sortie.retour_ids)

class StockRetourLine(models.Model):
    _name = 'stock.retour.line'

    retour_id = fields.Many2one("stock.retour", ondelete='cascade')
    article_id = fields.Many2one("stock.article", "Article", required=True)
    unite_id = fields.Many2one("stock.unite", "Unité", related='article_id.unite_id')
    qte = fields.Float("Quantité", required=True)
    prix_unitaire = fields.Float("P.U", required=True)
    prix_total = fields.Float("Prix total", compute='_sous_total')

    @api.depends('prix_unitaire', 'qte')
    def _sous_total(self):
        for line in self:
            line.prix_total = line.prix_unitaire * line.qte
