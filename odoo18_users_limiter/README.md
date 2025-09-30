# Odoo Users Limiter - Odoo 17

[![Odoo Apps](https://img.shields.io/badge/Odoo-Apps%20Store-brightgreen)](https://apps.odoo.com/apps/modules/)

## Overview

The **Odoo Users Limiter** module allows Odoo administrators to set a limit on the number of internal users that can be created in the system. This helps organizations maintain control over user management by preventing the creation of more users once the predefined limit is reached.

This module is compatible with **Odoo 17** and is designed for both Community and Enterprise editions.

---

## Key Features

- **Set User Limits**: Administrators can define a limit for internal user creation.
- **Error Handling**: Displays an error message when the user limit is exceeded, preventing further user creation.
- **Admin Control**: Easy setup via the admin interface.
- **Configurable Limits**: Limits can be set based on your organization’s needs.
- **Portal/Public User Exemption**: Limits apply only to internal users, allowing portal and public users to be created without restrictions.

---

## How It Works

1. **Login as Admin**: You must be logged in as an admin user to set and manage user limits.
2. **Navigate to Users**: Go to `Settings > Users` and configure the `Set User Limit` field.
3. **Set the User Limit**: Define the maximum number of internal users that can be created.
4. **Error Handling**: Once the limit is reached, the system will block the creation of new internal users and raise an error message: 
   `"Maximum number of users created. Please contact your system administrator!"`

---

## Installation

1. Download or clone this module into your Odoo’s addons directory:
   ```bash
   git clone https://github.com/iifast2/Odoo_Users_Limiter
   ```

2. Update the app list by navigating to **Apps** -> **Update App List** in the Odoo interface.
   
3. Search for **Odoo Users Limiter** and install the module.

---

## Technical Information

- **Version**: 17.0.0.0
- **Author**: Ben Taieb Med Amine
- **License**: AGPL-3
- **Website**: [Ben Taieb Med Amine](http://medaminebt.com)
- **Odoo Apps URL**: [Odoo Users Limiter on Odoo Apps](https://apps.odoo.com/apps/modules/)

---

## Screenshots

<p align="center">
  <img src="https://i.imgur.com/hn3yr12.png" alt="Odoo Users Limiter Screenshot 1"/>
  <br/>
  <img src="https://i.imgur.com/q0RYvWu.png" alt="Odoo Users Limiter Screenshot 2"/>
  <br/>
  <img src="https://i.imgur.com/tVn1GF8.png" alt="Odoo Users Limiter Screenshot 3"/>
</p>

---

## Support & Contact

For any support or queries, please contact **Ben Taieb Med Amine**:

- **Website**: [http://medaminebt.com](http://medaminebt.com)
- **Email**: contact@medaminebt.com
