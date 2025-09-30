# -*- coding: utf-8 -*-

from . import controllers
from . import models

from odoo.addons.payment import setup_provider, reset_payment_provider

# from odoo.addons.payment.models.payment_acquirer import create_missing_journal_for_acquirers