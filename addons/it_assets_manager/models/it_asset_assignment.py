from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ItAssetAssignment(models.Model):
    _name = 'it.asset.assignment'
    _description = 'Asignación de activo IT'
    _order = 'assigned_date desc, id desc'

    asset_id = fields.Many2one(
        comodel_name='it.asset',
        string='Activo',
        required=True,
        ondelete='cascade',
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Empleado',
        required=True,
    )
    assigned_date = fields.Date(
        string='Fecha de asignación',
        default=fields.Date.context_today,
        required=True,
    )
    returned_date = fields.Date(string='Fecha de devolución')
    notes = fields.Text(string='Notas')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            asset = record.asset_id
            if asset.state != 'disponible':
                raise ValidationError(_("Solo se puede asignar un activo que esté disponible."))

            open_assignments = asset.assignment_ids.filtered(
                lambda assignment: assignment.id != record.id and not assignment.returned_date
            )
            if open_assignments:
                raise ValidationError(_("El activo ya tiene una asignación activa."))

            asset.state = 'asignado'
        return records

    @api.constrains('returned_date', 'assigned_date')
    def _check_returned_date(self):
        for record in self:
            if record.returned_date and record.returned_date < record.assigned_date:
                raise ValidationError(_("La fecha de devolución no puede ser anterior a la fecha de asignación."))

    @api.constrains('asset_id')
    def _check_single_open_assignment(self):
        for record in self:
            open_assignments = record.asset_id.assignment_ids.filtered(lambda assignment: not assignment.returned_date)
            if len(open_assignments) > 1:
                raise ValidationError(_("El activo no puede tener más de una asignación activa."))