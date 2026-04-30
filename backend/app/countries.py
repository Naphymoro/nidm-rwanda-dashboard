COUNTRY_CONFIG = {
    "Rwanda": {
        "admin_levels": ["province", "district", "sector"],
    },
    "Kenya": {
        "admin_levels": ["county", "subcounty", "ward"],
    },
    "Nigeria": {
        "admin_levels": ["state", "lga", "ward"],
    },
}


def get_admin_levels(country: str):
    return COUNTRY_CONFIG.get(country, {}).get("admin_levels", [])
