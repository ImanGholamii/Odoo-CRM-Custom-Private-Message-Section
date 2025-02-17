# Custom Private Messages for CRM

## Overview
This Odoo module extends the `crm.lead` model to enable private commercial team messages within leads. Users can mention others, attach files, and send email notifications when mentioned in a message.

## Features
- Adds a **Commercial Team Messages** tab to CRM leads.
- Enables private messages related to leads.
- Supports mentioning users (`@username`) and sending email notifications.
- Allows attaching files to messages.
- Restricts access to messages through a dedicated user group.

## Installation
1. Copy this module into your Odoo `addons` directory.
2. Restart the Odoo server.
3. Install the module from the Odoo Apps menu.

## Usage
1. Open a lead (`CRM -> Sales -> Leads`).
2. Navigate to the **Commercial Team Messages** tab.
3. Add a message, mention users, and attach files.
4. Mentioned users will receive an email notification.

## Security
- The module introduces a new access group: **Custom Private Message Access for CRM**.
- Users in this group can view, create, and delete messages.

## Technical Details
### Models
- `crm.lead.custom.private.message`
  - Stores private messages linked to CRM leads.
  - Supports tracking messages and mentions.
  - Sends email notifications to mentioned users.

### Views
- Inherits the CRM lead form view to add a **Commercial Team Messages** tab.
- Provides a dedicated form view for creating and editing private messages.

## License
This module is released under the Odoo Proprietary License (OPL-1).

