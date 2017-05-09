# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo Addon, Open Source Management Solution
#    Copyright (C) 2014-now Equitania Software GmbH(<http://www.equitania.de>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import tools
from openerp.osv import osv, fields

class eq_pentaho_mail_compose_message(osv.TransientModel):
    _inherit = 'mail.compose.message'


    def default_get(self, cr, uid, fields, context=None):
        """ Überschreibung der default_get aus email_template, sodass kein onchange-Ereignis mehr ausgelöst wird, siehe Auskommentierung"""
        if context is None:
            context = {}
        res = super(eq_pentaho_mail_compose_message, self).default_get(cr, uid, fields, context=context)
        if res.get('composition_mode') != 'mass_mail' and context.get('default_template_id') and res.get('model') and res.get('res_id'):
            res.update(
                #### Workaround: auskommentiert bezüglich Ticket 4067, Angebotsversand von Pentaho-Reports.
                # Problematik: onchange_template_id wird 2-Mal ausgeführt, beim 1. Mal sind Werte wie template_id und Model noch enthalten,
                # beim 2. Aufruf der onchange_template_id-Methode jedoch, sind diese Werte nicht mehr enthalten.
                # Dies führt dazu, das weder der Empfänger noch die Vorlage mehr ausgewählt werden können.
                # self.onchange_template_id(
                #     cr, uid, [], context['default_template_id'], res.get('composition_mode'),
                #     res.get('model'), res.get('res_id'), context=context
                # )['value']
                self.change_id(
                    cr, uid, [], context['default_template_id'], res.get('composition_mode'),
                    res.get('model'), res.get('res_id'), context=context
                )['value']
            )
        if fields is not None:
            [res.pop(field, None) for field in res.keys() if field not in fields]
        return res


    def change_id(self, cr, uid, ids, template_id, composition_mode, model, res_id, context=None):
        """ Implementierung einer change_id Funktion, um die onchange_template_id-Funktion umgehen zu können"""
        if template_id and composition_mode == 'mass_mail':
            fields = ['subject', 'body_html', 'email_from', 'reply_to', 'mail_server_id']
            template = self.pool['email.template'].browse(cr, uid, template_id, context=context)
            values = dict((field, getattr(template, field)) for field in fields if getattr(template, field))
            if template.attachment_ids:
                values['attachment_ids'] = [att.id for att in template.attachment_ids]
            if template.mail_server_id:
                values['mail_server_id'] = template.mail_server_id.id
            if template.user_signature and 'body_html' in values:
                signature = self.pool.get('res.users').browse(cr, uid, uid, context).signature
                values['body_html'] = tools.append_content_to_html(values['body_html'], signature, plaintext=False)
        elif template_id:
            values = self.generate_email_for_composer_batch(cr, uid, template_id, [res_id], context=context)[res_id]
            # transform attachments into attachment_ids; not attached to the document because this will
            # be done further in the posting process, allowing to clean database if email not send
            ir_attach_obj = self.pool.get('ir.attachment')
            for attach_fname, attach_datas in values.pop('attachments', []):
                data_attach = {
                    'name': attach_fname,
                    'datas': attach_datas,
                    'datas_fname': attach_fname,
                    'res_model': 'mail.compose.message',
                    'res_id': 0,
                    'type': 'binary',  # override default_type from context, possibly meant for another model!
                }
                values.setdefault('attachment_ids', list()).append(ir_attach_obj.create(cr, uid, data_attach, context=context))
        else:
            default_context = dict(context, default_composition_mode=composition_mode, default_model=model, default_res_id=res_id)
            default_values = self.default_get(cr, uid, ['composition_mode', 'model', 'res_id', 'parent_id', 'partner_ids', 'subject', 'body', 'email_from', 'reply_to', 'attachment_ids', 'mail_server_id'], context=default_context)
            values = dict((key, default_values[key]) for key in ['subject', 'body', 'partner_ids', 'email_from', 'reply_to', 'attachment_ids', 'mail_server_id'] if key in default_values)

        if values.get('body_html'):
            values['body'] = values.pop('body_html')
        return {'value': values}

    def change_template(self, cr, uid, ids, context=None):
        """ change_template-Funktion wird durch den entsprechenden Button ausgelöst und führt durch den Klick ein Wechsel zu dem ausgewählten Template aus.
        Danach wird die Anzeige neu gerendert"""
        m_m_compose_obj = self.browse(cr,uid,ids)
        default_res_id = context['active_ids'][0]
        ir_model_data = self.pool.get('ir.model.data')
        compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]

        ctx = context
        ctx.update({
            'default_model': 'sale.order',
            'default_res_id': default_res_id,
            'default_use_template': bool(m_m_compose_obj.template_id.id),
            'default_template_id': m_m_compose_obj.template_id.id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }