#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import json
import requests
import pandas as pd
from difflib import get_close_matches
import openai
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import spacy
import pandas as pd
pd.set_option('display.max_colwidth', 30)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)
import uuid
from urllib.parse import urlparse
import utils as ut
from datamule import Portfolio, Config
import xml.etree.ElementTree as ET

nlp = spacy.load("en_core_web_sm")
MAX_WORKERS = 1
MAX_DOWNLOADS = 10



def categorize_job_title(job_title):
    executive_titles = ["CEO", "Managing Partner", "Chairman","Chief Executive Officer"]
    investor_titles = ["Investor", "LP", "GP", "Fund Manager"]

    doc = nlp(job_title.lower())
    if any(word.lower() in doc.text for word in executive_titles):
        return "Executive"
    elif any(word in doc.text for word in investor_titles):
        return "Investor"
    return "Other"


def extract_company_domain(url: str) -> str:
    """
    Extract the clean company domain from a given website URL.
    Removes protocol (http/https) and 'www.' prefix.

    Example:
    Input:  'http://www.example.com'
    Output: 'example.com'
    """
    try:
        # Extract domain part (e.g., 'www.example.com')
        netloc = urlparse(url).netloc

        # Convert to lowercase and remove 'www.' prefix if present
        domain = netloc.lower().replace("www.", "")

        return domain
    except Exception as e:
        # Handle invalid URLs gracefully
        print(f"Error parsing URL '{url}': {e}")
        return ""


def extract_geographic_focus(sec_10k_text):
    """Extracts geographic investment allocation from SEC 10-K filings."""
    focus_areas = {"North America": 0, "Europe": 0, "Asia": 0, "Global": 0}

    if "north america" in sec_10k_text.lower():
        focus_areas["North America"] = 70
    if "europe" in sec_10k_text.lower():
        focus_areas["Europe"] = 30
    if "asia" in sec_10k_text.lower():
        focus_areas["Asia"] = 10
    if "global" in sec_10k_text.lower():
        focus_areas["Global"] = 100

    return json.dumps({k: f"{v}%" for k, v in focus_areas.items() if v > 0})


def extract_funding_stage(form_d_text):
    """Extracts funding stage from SEC Form D offering type descriptions."""
    funding_stages = {
    "Seed": ["seed", "early stage"],
    "Series A": ["series a"],
    "Series B": ["series b"],
    "Series C": ["series c"],
    "Growth": ["growth", "expansion"],
    "Private Equity": ["private equity"]
    }
    
    form_d_text_lower = form_d_text.lower()
    for stage, keywords in funding_stages.items():
        if any(keyword in form_d_text_lower for keyword in keywords):
            return stage
    return "Unknown"

def get_value_for_issuer(xml_string: str, issuer_name: str = "APPLE INC") -> str:
    """
    Parse the XML string and return the <value> for the given <nameOfIssuer>.

    Parameters:
        xml_string (str): The XML content as a string.
        issuer_name (str): The name of the issuer to search for (default is "APPLE INC").

    Returns:
        str: The <value> of the first matching issuer, or None if not found.
    """
    ns = {'ns': 'http://www.sec.gov/edgar/document/thirteenf/informationtable'}
    root = ET.fromstring(xml_string)

    for info in root.findall("ns:infoTable", ns):
        name = info.find("ns:nameOfIssuer", ns).text.strip()
        if name.upper() == issuer_name.upper():
            value = info.find("ns:value", ns).text
            return value  # Return the first match

    return None

portfolio_path_13F_HR_path = "/Users/zealot/Documents/SEC_13F-HR/portfolio_output_dir"

portfolio = Portfolio(portfolio_path_13F_HR_path)


def sum_issuer_value(text_query: str) -> int:
    """
    Search documents for a text query, filter by issuer name, and return the sum of <value> fields.

    Parameters:
        text_query (str): The string to search for in each document.
        issuer_name (str): The issuer name to look for in the XML content.

    Returns:
        int: The sum of <value> fields for matching documents.
    """

    def callback_function(document):
        try:
            if document.contains_string(text_query):
                return document.content
        except Exception as e:
            print(f"Error processing document: {e}")
        return None

    # Run the document processing with the callback
    ret = portfolio.process_documents(callback=callback_function)

    # Filter out None results
    filtered_ret = [item for item in ret if item is not None]

    total = 0
    for i, item in enumerate(filtered_ret):
        try:
            value = get_value_for_issuer(item, issuer_name=text_query)
            if value is not None:
                total += int(value)
                # print(f"[{i}] Value for {text_query}:", value)
        except Exception as e:
            print(f"[{i}] Error processing item: {e}")

    return total




# def callback_function(document):
#     try:
#         if document.contains_string(text_query):
#             return document.content
#     except Exception as e:
#         print(f"Error processing document: {e}")
#
# # Process submissions - note that filters are applied here
# ret = portfolio.process_documents(callback=callback_function)
# filtered_ret = [item for item in ret if item is not None]
#
# print(len(filtered_ret))

# sum=0
# for i, item in enumerate(filtered_ret):
#     if item is not None:
#         try:
#             value = get_value_for_issuer(item, issuer_name="APPLE INC")
#             if value is not None:
#                 sum+= int(value)
#                 print(f"[{i}] Value for APPLE INC:", value)
#         except Exception as e:
#             print(f"[{i}] Error processing item: {e}")


# Step 1: Read the CSV file
csv_file_path = 'generate_silver_data/apollo-contacts-export.csv'
apollo_lead_df = pd.read_csv(csv_file_path)
cik_mapping = ut.fetch_cik_mapping()
# Step 2: Display the loaded data
print("Data read from CSV:")
print(apollo_lead_df.head())  # Print only the first 5 rows to quickly check the content

portfolio_path_13F_HR_path = ""

portfolio = Portfolio(portfolio_path_13F_HR_path)
for document in portfolio.contains_string(r'(?i)APPLE INC'):
    doc_type = document.type



for index, row in apollo_lead_df.iterrows():
    random_uuid = uuid.uuid4()
    first_name = row['First Name']
    last_name = row['Last Name']
    full_name = str(first_name) + " " + str(first_name)
    title = row['Title']
    job_title_category = categorize_job_title(title)
    company_name = row['Company']
    website = row['Website']
    company_domain = extract_company_domain(website)
    company_email_name = row['Company Name for Emails']
    email = row['Email']

    person_linkedin_url = row['Person Linkedin Url']
    company_linkedin_url = row['Company Linkedin Url']
    # home_phone = row['Home Phone']
    # mobile_phone = row['Mobile Phone']
    phone_number = row['Corporate Phone']

    text_query = "APPLE INC"
    # prompt = f"Give a one-line description of the company named '{company_name}'."
    # print("job_title_category: ", job_title_category)
    # print("company_domain: ", company_domain)

    closest_match, cik = ut.find_closest_cik(company_name, cik_mapping)
    if cik is None:
        # print(f"Not found CIK: {company_name}")
        continue

    print(f"Matched: Closest: {closest_match} | Original: {company_name} | CIK: {cik}")
    aum = sum_issuer_value(text_query)
    # get form d
    # gpt_summary = call_chatgpt(prompt)

    # email_status = row['Email Status']
    # primary_email_source = row['Primary Email Source']
    # email_confidence = row['Email Confidence']
    # primary_email_catch_all_status = row['Primary Email Catch-all Status']
    # primary_email_last_verified_at = row['Primary Email Last Verified At']
    # seniority = row['Seniority']
    # departments = row['Departments']
    # contact_owner = row['Contact Owner']
    # work_direct_phone = row['Work Direct Phone']
    # corporate_phone = row['Corporate Phone']
    # other_phone = row['Other Phone']
    # stage = row['Stage']
    # lists = row['Lists']
    # last_contacted = row['Last Contacted']
    # account_owner = row['Account Owner']
    # num_employees = row['# Employees']
    # industry = row['Industry']
    # keywords = row['Keywords']
    # facebook_url = row['Facebook Url']
    # twitter_url = row['Twitter Url']
    # city = row['City']
    # state = row['State']
    # country = row['Country']
    # company_address = row['Company Address']
    # company_city = row['Company City']
    # company_state = row['Company State']
    # company_country = row['Company Country']
    # company_phone = row['Company Phone']
    # seo_description = row['SEO Description']
    # technologies = row['Technologies']
    # annual_revenue = row['Annual Revenue']
    # total_funding = row['Total Funding']
    # latest_funding = row['Latest Funding']
    # latest_funding_amount = row['Latest Funding Amount']
    # last_raised_at = row['Last Raised At']
    # email_sent = row['Email Sent']
    # email_open = row['Email Open']
    # email_bounced = row['Email Bounced']
    # replied = row['Replied']
    # demoed = row['Demoed']
    # num_retail_locations = row['Number of Retail Locations']
    # apollo_contact_id = row['Apollo Contact Id']
    # apollo_account_id = row['Apollo Account Id']
    # secondary_email = row['Secondary Email']
    # secondary_email_source = row['Secondary Email Source']
    # tertiary_email = row['Tertiary Email']
    # tertiary_email_source = row['Tertiary Email Source']
    # primary_intent_topic = row['Primary Intent Topic']
    # primary_intent_score = row['Primary Intent Score']
    # secondary_intent_topic = row['Secondary Intent Topic']
    # secondary_intent_score = row['Secondary Intent Score']
