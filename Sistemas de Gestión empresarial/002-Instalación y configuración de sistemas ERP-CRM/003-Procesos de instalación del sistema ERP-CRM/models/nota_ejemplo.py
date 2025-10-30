from odoo import models, fields, api

class NotaEjemplo(models.Model):
    _name = 'mi.modulo.ejemplo' 
    _description = 'Nota de Mi Módulo Ejemplo'
    _order = 'fecha desc, name asc'
    
    name = fields.Char(
        string='Título', 
        required=True, 
        help='Título principal de la nota'
    )
    
    description = fields.Text(
        string='Descripción',
        help='Descripción detallada de la nota'
    )
    
    fecha = fields.Date(
        string='Fecha', 
        default=fields.Date.context_today,
        help='Fecha de creación de la nota'
    )
    
    active = fields.Boolean(
        string='Activo', 
        default=True,
        help='Indica si la nota está activa'
    )