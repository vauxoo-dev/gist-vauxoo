import html
import unicodedata
from xml.etree import ElementTree as ET

from odoo.exceptions import AccessError
from odoo.tests import Form, TransactionCase, tagged

from odoo.addons.xml_data_generator.wizard.xml_data_generator import (
    RECURSIVE_DEPTH_STATES,
)


@tagged("test_xml_data_generator")
class TestXMLDataGenerator(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.xml_wizard = cls.env["xml.data.generator"]

    def get_xml_trees(self, data):
        # Manage encoding
        res = unicodedata.normalize("NFKD", data)
        res = html.unescape(res)
        # Rearrange tag order to account for <?xml version="1.0" ?> tag not having a closing tag
        res = (
            res.replace("<br>", "")
            .replace('<div><?xml version="1.0" ?>', '<?xml version="1.0" ?>')
            .replace("</div></odoo></div>", "</div></odoo>")
        )
        res = res.split('<?xml version="1.0" ?>')[1:]
        return [ET.ElementTree(ET.fromstring('<?xml version="1.0" ?>%s' % record)) for record in res]

    def check_node(self, xml_wizard, field_node, field_object_map, target_record):
        node_items = field_node.items()
        node_name = node_items[0][1]
        node_value = field_node.text
        if len(node_items) == 2:
            node_value = node_items[1][1]
        self.assertTrue(node_name in field_object_map)
        field_object = field_object_map[node_name]
        expected_field_value = xml_wizard._xml_data_generator_get_field_data(target_record, field_object)[node_name][
            "value"
        ]
        # Test primary typed fields
        if field_object.type not in ["one2many", "many2many", "many2one"]:
            self.assertEqual(node_value, str(expected_field_value))
        if field_object.type == "many2one":
            # Verify real external ID is the same as in the row
            model_name = expected_field_value._name
            res_id = expected_field_value.id
            external_id = xml_wizard._prepare_external_id(model_name, res_id)
            self.assertEqual(node_value, external_id)
        if field_object.type == "many2many":
            # Verify all real external IDs are in the XMl row
            for record in expected_field_value:
                model_name = record._name
                res_id = record.id
                external_id = xml_wizard._prepare_external_id(model_name, res_id)
                self.assertTrue(external_id in node_value)

    def test_01_export_partner_by_external_id(self):
        """Export a partner to XML, search it by external ID"""
        partner_external_id = "xml_data_generator.res_partner_auto_1"
        partner = self.env.ref(partner_external_id)
        field_objects = self.xml_wizard._get_field_objects(partner._name)
        field_object_map = {field_object.name: field_object for field_object in field_objects}
        partner_context = {"active_model": partner._name, "active_id": partner.id}
        xml_wizard_form = Form(self.xml_wizard.with_context(**partner_context))
        xml_wizard_form.search_by_external_id = partner_external_id
        self.assertEqual(xml_wizard_form.res_id, partner.id)
        xml_wizard = xml_wizard_form.save()
        # Export XML for a single partner
        xml_wizard.action_export_to_xml()
        xml_tree = self.get_xml_trees(xml_wizard.fetched_data)[0]
        parent_node = xml_tree.find(".//record")
        # Ensure a record was found
        self.assertTrue(bool(parent_node))

        field_nodes = parent_node.findall("./field")
        for field_node in field_nodes:
            self.check_node(xml_wizard, field_node, field_object_map, partner)

    def test_02_export_partner_by_model_and_id(self):
        """Export a partner to XML, search it by model and id."""
        partner = self.env.ref("xml_data_generator.res_partner_auto_1")
        field_objects = self.xml_wizard._get_field_objects(partner._name)
        field_object_map = {field_object.name: field_object for field_object in field_objects}
        partner_context = {"active_model": partner._name, "active_id": partner.id}
        xml_wizard_form = Form(self.xml_wizard.with_context(**partner_context))
        self.assertEqual(xml_wizard_form.res_id, partner.id)
        xml_wizard = xml_wizard_form.save()
        # Export XML for a single partner
        xml_wizard.action_export_to_xml()
        xml_tree = self.get_xml_trees(xml_wizard.fetched_data)[0]
        parent_node = xml_tree.find(".//record")
        # Ensure a record was found
        self.assertTrue(bool(parent_node))

        field_nodes = parent_node.findall("./field")
        for field_node in field_nodes:
            self.check_node(xml_wizard, field_node, field_object_map, partner)

    def test_03_export_partner_dummy_string_data(self):
        """Export a partner to XML, but fetch demo data from model using defined methods for it, if any."""
        partner = self.env.ref("xml_data_generator.res_partner_auto_3")
        field_objects = self.xml_wizard._get_field_objects(partner._name)
        field_object_map = {field_object.name: field_object for field_object in field_objects}
        partner_context = {"active_model": partner._name, "active_id": partner.id}
        xml_wizard_form = Form(self.xml_wizard.with_context(**partner_context))
        xml_wizard_form.mode = "demo"
        self.assertEqual(xml_wizard_form.res_id, partner.id)
        xml_wizard = xml_wizard_form.save()
        # Export XML for a single partner
        xml_wizard.action_export_to_xml()
        xml_tree = self.get_xml_trees(xml_wizard.fetched_data)[0]
        parent_node = xml_tree.find(".//record")
        # Ensure a record was found
        self.assertTrue(bool(parent_node))
        field_nodes = parent_node.findall("./field")
        for field_node in field_nodes:
            self.check_node(xml_wizard, field_node, field_object_map, partner)

    def test_04_export_partner_company_dummy_string_data(self):
        """Export a partner company to XML, but fetch demo data from model using defined methods for it, if any."""
        partner = self.env.ref("xml_data_generator.res_partner_auto_1")
        field_objects = self.xml_wizard._get_field_objects(partner._name)
        field_object_map = {field_object.name: field_object for field_object in field_objects}
        partner_context = {"active_model": partner._name, "active_id": partner.id}
        xml_wizard_form = Form(self.xml_wizard.with_context(**partner_context))
        xml_wizard_form.mode = "demo"
        self.assertEqual(xml_wizard_form.res_id, partner.id)
        xml_wizard = xml_wizard_form.save()
        # Export XML for a single partner
        xml_wizard.action_export_to_xml()
        xml_tree = self.get_xml_trees(xml_wizard.fetched_data)[0]
        parent_node = xml_tree.find(".//record")
        # Ensure a record was found
        self.assertTrue(bool(parent_node))
        field_nodes = parent_node.findall("./field")
        for field_node in field_nodes:
            self.check_node(xml_wizard, field_node, field_object_map, partner)

    def test_05_export_partner_depth_1(self):
        """Export a partner to XML, set recursive depth = 1 to trigger methods that compute dependencies.
        This test deals with many2many and many2one fields.
        """
        partner = self.env.ref("xml_data_generator.res_partner_auto_1")
        field_objects = self.xml_wizard._get_field_objects(partner._name)
        field_object_map = {field_object.name: field_object for field_object in field_objects}
        partner_context = {"active_model": partner._name, "active_id": partner.id}
        xml_wizard_form = Form(self.xml_wizard.with_context(**partner_context))
        xml_wizard_form.recursive_depth = RECURSIVE_DEPTH_STATES[1][0]
        self.assertEqual(xml_wizard_form.res_id, partner.id)
        xml_wizard = xml_wizard_form.save()
        # Export XML for a single partner
        xml_wizard.action_export_to_xml()
        xml_tree = self.get_xml_trees(xml_wizard.fetched_data)[0]
        parent_node = xml_tree.find(".//record")
        # Ensure a record was found
        self.assertTrue(bool(parent_node))
        field_nodes = parent_node.findall("./field")
        for field_node in field_nodes:
            self.check_node(xml_wizard, field_node, field_object_map, partner)

    def test_06_export_currency_depth_2(self):
        """Export a currency to XML, set recursive depth = 2 to trigger methods that compute dependencies.
        This test deals with one2many fields.
        """
        currency = self.env.ref("xml_data_generator.res_currency_auto_1")
        field_objects = self.xml_wizard._get_field_objects(currency._name)
        field_object_map = {field_object.name: field_object for field_object in field_objects}
        currency_context = {"active_model": currency._name, "active_id": currency.id}
        xml_wizard_form = Form(self.xml_wizard.with_context(**currency_context))
        xml_wizard_form.recursive_depth = RECURSIVE_DEPTH_STATES[2][0]
        xml_wizard_form.avoid_duplicates = False
        self.assertEqual(xml_wizard_form.res_id, currency.id)
        xml_wizard = xml_wizard_form.save()
        # Export XML for a single currency
        xml_wizard.action_export_to_xml()
        xml_trees = self.get_xml_trees(xml_wizard.fetched_data)
        for xml_tree in xml_trees:
            parent_node = xml_tree.find(".//record")
            # Only check main record fields
            if not parent_node.attrib["model"] == currency._name:
                continue
            # Ensure a record was found
            self.assertTrue(bool(parent_node))
            field_nodes = parent_node.findall("./field")
            for field_node in field_nodes:
                self.check_node(xml_wizard, field_node, field_object_map, currency)

    def test_07_export_user_raise_access_error(self):
        """Export a user to XML, but raise AccessError with totp_secret field."""
        user = self.env.ref("base.user_admin")
        self.xml_wizard._get_field_objects(user._name)
        user_context = {"active_model": user._name, "active_id": user.id}
        xml_wizard_form = Form(self.xml_wizard.with_context(**user_context))
        xml_wizard_form.recursive_depth = RECURSIVE_DEPTH_STATES[1][0]
        self.assertEqual(xml_wizard_form.res_id, user.id)
        xml_wizard = xml_wizard_form.save()
        # Export XML for a single user
        with self.assertRaises(AccessError):
            xml_wizard.with_user(2).action_export_to_xml()

    def test_08_export_user_not_raise_access_error(self):
        """Export a user to XML, but do not raise AccessError with totp_secret field."""
        user = self.env.ref("base.user_admin")
        field_objects = self.xml_wizard._get_field_objects(user._name)
        field_object_map = {field_object.name: field_object for field_object in field_objects}
        self.xml_wizard._get_field_objects(user._name)
        user_context = {"active_model": user._name, "active_id": user.id}
        xml_wizard_form = Form(self.xml_wizard.with_context(**user_context))
        xml_wizard_form.recursive_depth = RECURSIVE_DEPTH_STATES[1][0]
        xml_wizard_form.ignore_access = True
        self.assertEqual(xml_wizard_form.res_id, user.id)
        xml_wizard = xml_wizard_form.save()
        # Export XML for a single user
        xml_wizard.action_export_to_xml()
        xml_tree = self.get_xml_trees(xml_wizard.fetched_data)[0]
        parent_node = xml_tree.find(".//record")
        # Ensure a record was found
        self.assertTrue(bool(parent_node))
        field_nodes = parent_node.findall("./field")
        for field_node in field_nodes:
            self.check_node(xml_wizard, field_node, field_object_map, user)
