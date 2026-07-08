from odoo import fields, models


class ItAssetCategory(models.Model):
    _name = 'it.asset.category'
    _description = 'Categoría de activo IT'
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
        help='Nombre descriptivo de la categoría (ej: Laptops, Monitores).',
    )
    code = fields.Char(
        string='Código',
        required=True,
        help='Código único de identificación (ej: LTP, MON).',
    )
