{
    "name": "xml_data_generator",
    "license": "GPL-3",
    "summary": """Module to export records as XML.""",
    "author": "Vauxoo",
    "website": "https://www.yourcompany.com",
    "category": "Uncategorized",
    "version": "16.0.0.0.1",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/xml_data_generator_views.xml",
    ],
    "demo": [
        "demo/res_partner.xml",
        "demo/res_currency.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "xml_data_generator/static/src/views/form_controller.js",
        ],
    },
}
