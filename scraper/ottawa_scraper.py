import requests
from bs4 import BeautifulSoup
from utils.help_functions import *
import json
import pandas as pd

OTTAWA_URL = "https://ottawa.ca/en/city-hall/mayor-and-city-councillors"
ROOT_URL = "https://ottawa.ca"

def scraper():
    initial_members_dicts = get_initial_members_dicts()
    members_dicts = []
    for member_dict in initial_members_dicts:
        member_dict = fill_missing_info_into_member_dict(member_dict)
        members_dicts.append(member_dict)
    # Write to json file
    with open("data/json/ottawa_council.json", "w") as f:
        json.dump(members_dicts, f, indent=2)
    # Write to excel file
    df = pd.DataFrame(members_dicts)
    df.to_excel("data/excel/ottawa_council.xlsx", index=False)

def fill_missing_info_into_member_dict(member_dict):
    member_url = member_dict["quick_links"][0]["url"]
    html = requests.get(member_url).text
    soup = BeautifulSoup(html, "html.parser")
    member_dict["photo_url"] = ROOT_URL + soup.find("img", class_="img-fluid w-100")["src"]
    address = soup.find("p", class_="address").text.strip()
    member_dict["offices"][0]["address"] = address
    member_dict["bio"] = soup.find("div", class_="clearfix text-formatted field field--name-field-about field--type-text-long field--label-above").text.strip()
    return member_dict

def get_initial_members_dicts():
    """
        Scrape initial members info from the Ottawa website
        Returns:
            list of dict: list of all the members dicts
    """
    html = requests.get(OTTAWA_URL).text
    soup = BeautifulSoup(html, "html.parser")
    memeber_cards = soup.find_all("div", class_="card-body p-0")
    member_initial_dicts_list = []
    for member_card in memeber_cards:
        member_dict = create_politician_dict()
        member_dict["name"] = member_card.find("h3").text.strip()
        member_dict["first_name"] = member_dict["name"].split(" ")[0]
        member_dict["last_name"] = member_dict["name"].split(" ")[-1]
        member_dict["quick_links"].append({"url": ROOT_URL + member_card.find("a")["href"], "type": "Offical Website"})
        member_dict["elected_office"] = member_card.find("h4").text.strip().title()
        member_dict["elected_office"] = "Councillor" if "Councillor" in member_dict["elected_office"] else member_dict["elected_office"]
        if member_dict["elected_office"] == "Mayor":
            member_dict["district_name"] = "Ottawa"
        else:
            member_dict["district_name"] = "Ottawa/" + member_card.find("div", class_="mb-2").text.strip().title()
        contact = member_card.find("div", class_="item-list").text.strip()
        email_link = member_card.find("a", href=lambda href: href and "mailto:" in href)["href"].replace("mailto:", "")
        member_dict["email"] = email_link
        member_dict["offices"].append({"type": "Office", "contact": contact})
        member_initial_dicts_list.append(member_dict)
    return member_initial_dicts_list

def main():
    scraper()

if __name__ == "__main__":
    main()