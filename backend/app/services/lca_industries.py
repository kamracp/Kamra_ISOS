"""Industry (product family) register for the LCA / PCF Studio (LCA session 5).

The engine is industry-agnostic; this key only selects which published benchmarks, distribution
presets and inventory templates are offered. An industry with no sourced benchmark shows
'no published benchmark loaded' - nothing is guessed.
"""
INDUSTRIES: list[dict] = [
    {"key": "ceramic_tiles",  "label": "Ceramic / vitrified tiles",        "typical_fu": "m2"},
    {"key": "cement_clinker", "label": "Cement and clinker",               "typical_fu": "tonne"},
    {"key": "steel",          "label": "Iron and steel",                   "typical_fu": "tonne"},
    {"key": "aluminium",      "label": "Aluminium",                        "typical_fu": "tonne"},
    {"key": "glass",          "label": "Glass",                            "typical_fu": "tonne"},
    {"key": "bricks",         "label": "Bricks and clay building products", "typical_fu": "tonne"},
    {"key": "paper_pulp",     "label": "Pulp and paper",                   "typical_fu": "tonne"},
    {"key": "textiles",       "label": "Textiles",                         "typical_fu": "kg"},
    {"key": "chemicals",      "label": "Chemicals and fertilisers",        "typical_fu": "tonne"},
    {"key": "carbon_black",   "label": "Carbon black",                     "typical_fu": "tonne"},
    {"key": "generic",        "label": "Other / generic product",          "typical_fu": ""},
]
INDUSTRY_KEYS = {i["key"] for i in INDUSTRIES}
