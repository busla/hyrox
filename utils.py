from typing import Dict


def fix_wrong_category(value: Dict) -> Dict:
    if "Hreindýrabollan".lower() in value["Team"].lower():
        print(f"Fixing wrong category {value['Category']} for {value['Team']}")
        value["Category"] = value["Category"].replace("OPEN", "PRO")
        print(f"Fixed category: {value['Category']}")
    return value
