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
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    This program is distributed in the hope that it will be useful,
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp import models, fields
import html2text


class eq_account_invoice(models.Model):
    """
    Diese Erweiterung der Tabelle sale.order dient als Workaround für das Problem mit HTML-Fields im Pentaho.
    Es ist nicht möglich die Styles bei HTML-Fields zu ändern. Aus diesem Grund müssen wir immer mit Plaintext arbeiten.
    """

    _inherit = "account.invoice"

    # HTML Felder als Plaintext
    eq_head_text_plaintext = fields.Char(compute = '_set_plain_text')
    eq_comment_plaintext = fields.Char(compute = '_set_plain_text')


    def _remove_wrong_chars(self, input):
        """
        Entfernt ** und _ aus dem Plaintext und Liefert den String zurück.
        Das ** und _ bleibt im String nach dem Aufruf der Funktion html2text.
        :param input: Plaintext
        :return: Plaintext ohne ** und _ Zeichen
        """
        input = input.replace("**", "")
        input = input.replace("_", "")
        return input

    def _set_plain_text(self):
        """
        Wandelt ein HTML-Text in Plaintext um und liefert das Ergebins zurück
        :return: Plaintext
        """
        for rec in self:
            rec.eq_head_text_plaintext = self._remove_wrong_chars(html2text.html2text(rec.eq_head_text))
            rec.eq_comment_plaintext = self._remove_wrong_chars(html2text.html2text(rec.comment))