# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    custom_message_ids = fields.One2many(
        'crm.lead.custom.private.message', 'lead_id', string='Commercial Team Messages'
    )


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

    @api.model
    def create(self, vals):
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
