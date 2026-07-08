from odoo import fields, models


class ItAssetCategory(models.Model):
    _name = 'it.asset.category'
    _description = 'Categoría de activo IT'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código', required=True)
