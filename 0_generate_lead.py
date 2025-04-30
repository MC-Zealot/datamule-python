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


# Set your OpenAI API key
openai.api_key = "your_openai_api_key"
# Global constants
SEC_HEADERS = {
    "User-Agent": "Individual/tyzttzzz@gmail.com"  # Required to avoid being blocked
}
nlp = spacy.load("en_core_web_sm")
SEC_CIK_MAPPING_URL = "https://www.sec.gov/files/company_tickers.json"
LIST1_CSV_FILE_PATH = "apollo-contacts-export.csv"
output_dir_base = "/Users/zealot/Documents/SEC_8K"
MAX_WORKERS = 1
MAX_DOWNLOADS = 10

def fetch_cik_mapping() -> dict:
    """Fetch CIK-ticker mapping from SEC."""
    response = requests.get(SEC_CIK_MAPPING_URL, headers=SEC_HEADERS)
    if response.status_code == 200:
        cik_data = response.json()
        # cik_mapping = {entry["ticker"].upper(): str(entry["cik_str"]).zfill(10) for entry in cik_data.values()}
        cik_mapping = {entry["title"].upper(): str(entry["cik_str"]) for entry in cik_data.values()}
        return cik_mapping
    else:
        raise Exception(f"Failed to fetch CIK mapping. Status code: {response.status_code}")


def find_closest_cik(company_name: str, cik_mapping: dict) -> tuple:
    """Find the closest matching CIK using fuzzy matching."""
    if not company_name:
        return None, None

    normalized_mapping = {key.strip().lower(): cik for key, cik in cik_mapping.items()}
    company_name_lower = company_name.strip().lower()
    closest_matches = get_close_matches(company_name_lower, normalized_mapping.keys(), n=1, cutoff=0.6)

    if closest_matches:
        matched_name = closest_matches[0]
        return matched_name, normalized_mapping[matched_name]

    return None, None

def call_chatgpt(prompt: str, model: str = "gpt-3.5-turbo", temperature: float = 0.7) -> str:
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"[Error] {e}"


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


# Step 1: Read the CSV file
csv_file_path = 'apollo-contacts-export.csv'
apollo_lead_df = pd.read_csv(csv_file_path)

# Step 2: Display the loaded data
print("Data read from CSV:")
print(apollo_lead_df.head())  # Print only the first 5 rows to quickly check the content

for index, row in apollo_lead_df.iterrows():
    random_uuid = uuid.uuid4()
    first_name = row['First Name']
    last_name = row['Last Name']
    full_name = str(first_name) + " " + str(first_name)
    title = row['Title']
    job_title_category = categorize_job_title(title)
    company = row['Company']
    website = row['Website']
    company_domain = extract_company_domain(website)
    company_email_name = row['Company Name for Emails']
    email = row['Email']

    person_linkedin_url = row['Person Linkedin Url']
    company_linkedin_url = row['Company Linkedin Url']
    home_phone = row['Home Phone']
    mobile_phone = row['Mobile Phone']
    phone_number = row['Corporate Phone']

    prompt = f"Give a one-line description of the company named '{company}'."
    print("job_title_category: ", job_title_category)
    print("company_domain: ", company_domain)
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
