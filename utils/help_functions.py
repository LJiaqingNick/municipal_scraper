from datetime import datetime
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import json
import pandas as pd

PROVINCE_CENCUS_PREFIX_DICT = {
        "35": "Ontario",
        "24": "Quebec",
        "12": "Nova Scotia",
        "13": "New Brunswick",
        "46": "Manitoba",
        "59": "British Columbia",
        "11": "Prince Edward Island",
        "47": "Saskatchewan",
        "48": "Alberta",
        "10": "Newfoundland and Labrador",
        "61": "Northwest Territories",
        "60": "Yukon",
        "62": "Nunavut"
    }
PROVINCE_CENCUS_PREFIX_DICT_REVERSE = {v: k for k, v in PROVINCE_CENCUS_PREFIX_DICT.items()}

def create_politician_dict():
    return {
        'id': None, # integer
        'politician_id': None, # integer
        'is_primary': True,
        'name': None,
        'first_name': None,
        'last_name': None,
        'gender': None,
        'birth_date': None,
        'birth_date_public': False,
        'email': None,
        'group_email': None,
        'photo_url': None,
        'bio': None,
        'twitter': None,
        'linkedin': None,
        'instagram': None,
        'facebook': None,
        'youtube': None,
        'tiktok': None,
        'fun_facts': [],
        'faq': [],
        'gallery': [],
        'salutation': None,
        'gender_pronouns': None,
        'party_name': None,
        'gov_level': None,
        'province': None,
        'organization': None,
        'district_name': None,
        'boundary': None,
        'offices': [], # [{'fax': '1 416 972-7686', 'type': 'legislature'}, {'tel': '1 416 972-7683', 'type': 'constituency'}]
        'quick_links': [], # [{'url': 'https://ville.montreal.qc.ca/portal/page?_pageid=5798,85809754&_dad=portal&_schema=PORTAL&id=142239476', 'title': 'Official Profile'}]
        'elected_office': None,
        'role_type': None,
        'titles': {}, # {'primary_titles': [], 'additional_titles': 'Minister of Health'}
        'policy_priorities': None,
        'message_to_constituent': None,
        'land_ack': None,
        'update_date': get_current_date(), # 2021-09-07 00:25:00
        'last_request': None, # 2022-12-07 14:59:27
    }
def get_current_date():
    # Get the current date and time
    now = datetime.now()
    # Format it as a string
    date_string = now.strftime("%Y-%m-%d %H:%M:%S")
    return date_string

def get_boundaries_dict():
    """
    Returns a list of dictionary of the form [{(district_name, province): boundary_slug}]
    """

    # Get the boundaries.json file path
    current_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(current_dir, '..', 'data')
    boundaries_path = os.path.join(data_dir, 'boundaries.json')
    # Load the boundaries.json file
    with open(boundaries_path, "r") as f:
        boundaries = json.load(f)
    boundaries = [boundary for boundary in boundaries if boundary["set_id"] == "census-subdivisions"]
    boundaries_dict = {}
    boundary_map = defaultdict(int)
    for boundary in boundaries:
        slug_prefix = boundary["slug"][0:2]
        # Check if the slug prefix is valid
        assert len(slug_prefix) == 2, f"Slug prefix {slug_prefix} is not of length 2"
        assert str(slug_prefix).isdigit(), f"Slug prefix {slug_prefix} is not a digit"
        assert slug_prefix in PROVINCE_CENCUS_PREFIX_DICT.keys(), f"Slug prefix {slug_prefix} is not a valid province"
        key = (boundary["name"], slug_prefix)
        boundary_map[key] += 1
    
    # log directory path
    log_dir = os.path.join(current_dir, '..', 'logs')
    log_path = os.path.join(log_dir, 'same_district_name_same_province.xlsx')
    boundary_set = {key for key, value in boundary_map.items() if value == 1}
    same_district_name_same_province = [(key[0], PROVINCE_CENCUS_PREFIX_DICT[key[1]]) for key, value in boundary_map.items() if value > 1]
    same_district_name_same_province = pd.DataFrame(same_district_name_same_province).to_excel(log_path, index=False)
    

    for boundary in boundaries:
        slug_prefix = boundary["slug"][0:2]
        # Check if the slug prefix is valid
        assert len(slug_prefix) == 2, f"Slug prefix {slug_prefix} is not of length 2"
        assert str(slug_prefix).isdigit(), f"Slug prefix {slug_prefix} is not a digit"
        assert slug_prefix in PROVINCE_CENCUS_PREFIX_DICT.keys(), f"Slug prefix {slug_prefix} is not a valid province"
        key = (boundary["name"], slug_prefix) # Example: ("Toronto", "35") 35 is the province code for Ontario
        if key in boundary_set:
            assert key not in boundaries_dict.keys(), f"Key {key} already exists in boundaries_dict"
            boundaries_dict[key] = f"{boundary['set_id']}/{boundary['slug']}"
    return boundaries_dict

def assign_boundary(district_name, province, boundaries_dict):
    """
        return the boundary string in the form of "census-subdivisions/3520005"
    """
    # Check if the district_name and province are valid
    assert district_name is not None, f"district_name is None"
    assert province is not None, f"province is None"
    assert district_name != "", f"district_name is empty"
    assert province != "", f"province is empty"
    return boundaries_dict[(district_name, PROVINCE_CENCUS_PREFIX_DICT_REVERSE[province])]
