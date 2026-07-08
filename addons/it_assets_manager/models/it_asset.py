from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ItAsset(models.Model):
    _name = 'it.asset'
    _description = 'Activo IT'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    asset_type = fields.Selection(
        selection=[
            ('laptop', 'Laptop'),
            ('monitor', 'Monitor'),
            ('licencia', 'Licencia'),
            ('periferico', 'Periférico'),
            ('otro', 'Otro'),
        ],
        string='Tipo de activo',
        default='otro',
        required=True,
    )
    serial_number = fields.Char(string='Número de serie')
    category_id = fields.Many2one(
        comodel_name='it.asset.category',
        string='Categoría',
    )
    purchase_date = fields.Date(string='Fecha de compra')
    warranty_end_date = fields.Date(string='Fin de garantía')
    warranty_expiring_soon = fields.Boolean(
        string='Garantía por vencer',
        compute='_compute_warranty_expiring_soon',
    )
    state = fields.Selection(
        selection=[
            ('disponible', 'Disponible'),
            ('asignado', 'Asignado'),
            ('mantenimiento', 'Mantenimiento'),
            ('baja', 'Baja'),
        ],
        string='Estado',
        default='disponible',
        required=True,
    )
    assignment_ids = fields.One2many(
        comodel_name='it.asset.assignment',
        inverse_name='asset_id',
        string='Historial de asignaciones',
    )
    current_employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Empleado actual',
        compute='_compute_current_employee_id',
        store=True,
    )

    def _get_open_assignment(self):
        self.ensure_one()
        open_assignments = self.assignment_ids.filtered(lambda assignment: not assignment.returned_date)
        if len(open_assignments) > 1:
            raise ValidationError(_("El activo tiene más de una asignación abierta. Revisa el historial antes de continuar."))
        return open_assignments[:1]

    def action_assign(self):
        self.ensure_one()
        if self.state != 'disponible':
            raise ValidationError(_("Solo se puede asignar un activo que esté disponible."))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Nueva asignación'),
            'res_model': 'it.asset.assignment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_asset_id': self.id,
            },
        }

    def action_return(self):
        self.ensure_one()
        if self.state not in ('asignado', 'mantenimiento'):
            raise ValidationError(_("Solo se puede devolver un activo asignado o en mantenimiento."))

        open_assignment = self._get_open_assignment()
        if self.state == 'asignado' and open_assignment:
            open_assignment.returned_date = fields.Date.context_today(self)

        self.state = 'disponible'

    def action_send_maintenance(self):
        self.ensure_one()
        if self.state == 'baja':
            raise ValidationError(_("No se puede enviar a mantenimiento un activo dado de baja."))
        if self.state == 'mantenimiento':
            raise ValidationError(_("El activo ya está en mantenimiento."))

        open_assignment = self._get_open_assignment()
        if open_assignment:
            open_assignment.returned_date = fields.Date.context_today(self)

        self.state = 'mantenimiento'

    def action_retire(self):
        self.ensure_one()
        if self.state == 'asignado' and self._get_open_assignment():
            raise ValidationError(_("No se puede dar de baja un activo con una asignación activa."))
        if self.state == 'baja':
            raise ValidationError(_("El activo ya está dado de baja."))

        self.state = 'baja'

    @api.constrains('state')
    def _check_state_consistency(self):
        for asset in self:
            open_assignments = asset.assignment_ids.filtered(lambda assignment: not assignment.returned_date)
            if asset.state == 'asignado' and not open_assignments:
                raise ValidationError(_("Un activo asignado debe tener una asignación activa."))
            if asset.state != 'asignado' and open_assignments:
                raise ValidationError(_("Un activo fuera de estado asignado no puede tener asignaciones abiertas."))

    @api.depends('warranty_end_date')
    def _compute_warranty_expiring_soon(self):
        today = fields.Date.context_today(self)
        limit_date = today + timedelta(days=30)
        for asset in self:
            asset.warranty_expiring_soon = bool(
                asset.warranty_end_date and today <= asset.warranty_end_date <= limit_date
            )

    @api.depends('assignment_ids.employee_id', 'assignment_ids.returned_date')
    def _compute_current_employee_id(self):
        for asset in self:
            open_assignment = asset.assignment_ids.filtered(lambda assignment: not assignment.returned_date)[:1]
            asset.current_employee_id = open_assignment.employee_id if open_assignment else False
