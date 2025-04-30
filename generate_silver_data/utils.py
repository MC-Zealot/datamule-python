#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
from difflib import get_close_matches
import openai


# Set your OpenAI API key
openai.api_key = "your_openai_api_key"
# Global constants
SEC_HEADERS = {
    "User-Agent": "Individual/tyzttzzz@gmail.com"  # Required to avoid being blocked
}

SEC_CIK_MAPPING_URL = "https://www.sec.gov/files/company_tickers.json"
LIST1_CSV_FILE_PATH = "apollo-contacts-export.csv"
output_dir_base = "/Users/zealot/Documents/SEC_8K"


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
    closest_matches = get_close_matches(company_name_lower, normalized_mapping.keys(), n=1, cutoff=0.85)

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