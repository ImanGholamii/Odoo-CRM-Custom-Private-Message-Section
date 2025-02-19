# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import UserError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    custom_message_ids = fields.One2many(
        'crm.lead.custom.private.message', 'lead_id', string='Opportunity Commercial Private Chat'
    )

    @api.model
    def create(self, vals):
        lead = super(CrmLead, self).create(vals)
        lead._log_expected_revenue_change(False, lead.expected_revenue)
        return lead

    def write(self, vals):
        for lead in self:
            old_value = lead.expected_revenue
            res = super(CrmLead, lead).write(vals)
            new_value = vals.get('expected_revenue', old_value)

            if 'expected_revenue' in vals and old_value != new_value:
                lead._log_expected_revenue_change(old_value, new_value)

        return res

    def _log_expected_revenue_change(self, old_value, new_value):
        """ Tracking of expected_revenue """
        if old_value != new_value:
            user_name = self.env.user.name
            message = f"{user_name} changed Expected Revenue from {old_value} to ➣➣➣ {new_value}"

            self.env['crm.lead.custom.private.message'].create({
                'lead_id': self.id,
                'message': message,
                'user_id': self.env.user.id,
                'is_system_generated_message': True
            })


class CrmLeadCustomMessage(models.Model):
    _name = 'crm.lead.custom.private.message'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    lead_id = fields.Many2one('crm.lead', string='Lead', required=True, ondelete='cascade')
    message = fields.Text('Message', tracking=True)
    create_date = fields.Datetime('Created On', default=lambda self: fields.Datetime.now())
    user_id = fields.Many2one('res.users', string='Author', default=lambda self: self.env.user, required=True)
    mentioned_user_ids = fields.Many2many('res.users', string='Mentioned Users')

    attachment_ids = fields.Many2many(
        'ir.attachment', 'crm_custom_message_attachment_rel', 'message_id', 'attachment_id',
        string="Attachments",
        help="Attachments related to this message"
    )

    is_system_generated_message = fields.Boolean(default=False)

    @api.model
    def create(self, vals):
        if "changed Expected Revenue from" in vals.get('message', ''):
            vals['is_system_generated_message'] = True

        record = super(CrmLeadCustomMessage, self).create(vals)

        for attachment in record.attachment_ids:
            attachment.write({'public': True})

        record._send_mention_notifications()
        return record

    def _send_mention_notifications(self):
        """Sends notification emails to mentioned users"""

        for record in self:
            lead_url = f"{record.get_base_url()}/web#id={record.lead_id.id}&model=crm.lead&view_type=form"

            for user in record.mentioned_user_ids:
                mail_values = {
                    'email_to': user.email,
                    'subject': f"You were mentioned in a message",
                    'body_html': f"<p>{record.user_id.name} mentioned you in a message:</p><p>{record.message}</p>"
                                 f"<p><a href={lead_url}>Click here to view the message</a></p>",
                }
                mail = self.env['mail.mail'].create(mail_values)
                mail.send()

    def unlink(self):
        for record in self:
            if record.is_system_generated_message or "changed Expected Revenue from" in record.message:
                raise UserError(f"❌\nYou cannot delete this system-generated message. 💻⚙️")
        return super(CrmLeadCustomMessage, self).unlink()

    def write(self, vals):
        for record in self:
            if record.is_system_generated_message or "changed Expected Revenue from" in record.message:
                raise UserError(f"❌\nYou cannot edit this System-generated message. 💻⚙️")
        return super(CrmLeadCustomMessage, self).write(vals)
