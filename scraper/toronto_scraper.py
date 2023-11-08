from utils.help_functions import *
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
import pandas as pd


WEB_SITE_URL = "https://www.toronto.ca/city-government/council/members-of-council/"
ROOT_URL = "https://www.toronto.ca/city-government"

def scrapper():
    """
    Function to scrape all the Toronto councillors information
    """
    # councillor_test_link = "https://www.toronto.ca/city-government/council/members-of-council/councillor-ward-1/"
    # process_details_page(councillor_test_link)
    members_list = []
    member_links = get_initial_member_links()
    for member_link in member_links:
        councillor = process_details_page(member_link)
        if councillor is not None:
            members_list.append(councillor)
    # Add mayor information
    members_list.append(get_mayor_information())
    # Write the members_list to a json file
    with open("data/json/toronto_councillors.json", "w") as f:
        json.dump(members_list, f, indent=2)
    # Write the members_list to a excel file
    df = pd.DataFrame(members_list)
    df.to_excel("data/excel/toronto_councillors.xlsx", index=False)

def get_mayor_information():
    url = "https://www.toronto.ca/city-government/council/office-of-the-mayor/about-mayor/"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    mayor = create_politician_dict()
    mayor["elected_office"] = "Mayor"
    mayor["province"] = "Ontario"
    mayor["gov_level"] = "municipal"
    mayor["district_name"] = "Toronto"
    mayor["name"] = soup.find("h1", id="page-header--title").text.replace("About Mayor ", "")
    mayor["first_name"] = mayor["name"].split(" ")[0]
    mayor["last_name"] = mayor["name"].split(" ")[-1]
    mayor["photo_url"] = soup.find("img", class_="alignright wp-image-786980 size-thumbnail")["src"]
    mayor["bio"] = soup.find("div", id="page-content").text
    # Contact information need use Selenium to render the JavaScript
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--user-agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options) # See
    driver.get(url)
    driver.implicitly_wait(5)
    email = None
    office = ""
    try:
        email = driver.find_element(By.XPATH, "/html/body/section/div/div[4]/aside/div[4]/div[1]/div/p[1]/a[2]").text
    except Exception as e:
        pass
    try:
        office = driver.find_element(By.XPATH, "/html/body/section/div/div[4]/aside/div[4]/div[1]/div/p[2]").text
    except Exception as e:
        pass
    mayor["email"] = email
    mayor["offices"].append({"type": "Office ", "address": office})
    return mayor


def process_details_page(councillor_link):
    """
    Function to process the details page of a councillor
    Parameters:
        councillor_link (string): the link to the councillor details page
    Returns:
        dict: the councillor information
    """
    html = requests.get(councillor_link).text
    soup = BeautifulSoup(html, "html.parser")
    # Get the councillor name
    councillor_name = soup.find("h1", id="page-header--title").text
    if "ward" in councillor_name.lower(): # There is a vacancy seat in Toronto council
        return
    # Initalize the councillor dictionary object from the helper function
    councillor = create_politician_dict()
    councillor["elected_office"] = "Councillor"
    councillor["province"] = "Ontario"
    councillor["gov_level"] = "municipal"
    # Remove the "Councillor" prefix
    councillor_name = councillor_name.replace("Councillor ", "")
    councillor["name"] = councillor_name
    councillor["first_name"] = councillor_name.split(" ")[0]
    councillor["last_name"] = councillor_name.split(" ")[-1]
    # Get the councillor district name
    councillor["district_name"] = "Toronto/"+soup.find("div", id="page-content").find("h2").text
    bio_element = soup.find("div", id="accordion-profile")
    councillor["bio"] = bio_element.text if bio_element is not None else ""
    # Get the councillor photo url
    councillor["photo_url"] = soup.find("img", class_="alignnone")["src"]
    # Add the official profile link
    councillor["quick_links"].append({"url": councillor_link, "title": "Official Profile"})
    # Get the councillor contact information since this part need JavaScript to render, we need to use Selenium
    # Initialize the selenium driver
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--user-agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options) # See https://github.com/SergeyPirogov/webdriver_manager
    driver.get(councillor_link)
    driver.implicitly_wait(5)
    email = None
    try:
        city_hall_contact_element = driver.find_element(By.XPATH, "/html/body/section/div/div[4]/aside/div[4]/div[1]/div/p[1]")
        city_hall_contact_info = city_hall_contact_element.text
        try:
            email = city_hall_contact_element.find_element(By.TAG_NAME, "a").text
        except Exception as e:
            pass
    except Exception as e:
        city_hall_contact_info = ""
    try:
        constituency_contact_info = driver.find_element(By.XPATH, "/html/body/section/div/div[4]/aside/div[4]/div[1]/div/p[2]").text
    except Exception as e:
        constituency_contact_info = ""
    driver.close()
    councillor["email"] = email
    councillor["offices"].append({"type": "Office ", "address": city_hall_contact_info})
    councillor["offices"].append({"type": "Constituency ", "address": constituency_contact_info})
    return councillor

def get_initial_member_links():
    """
    Function to get all the member links from the official Toronto website
    Returns:
        list of string: list of all the member links
    """
    html = requests.get(WEB_SITE_URL).text
    soup = BeautifulSoup(html, "html.parser")
    councillors_table = soup.find("table", id="js_map--data")
    councillors_a_tags = councillors_table.find_all("a")
    # Get the links for each councillor a tag, and add the base url
    councillors_links = [ROOT_URL + a_tag["href"] for a_tag in councillors_a_tags]
    return councillors_links

def main():
    scrapper()


if __name__ == "__main__":
    main()