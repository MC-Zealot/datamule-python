#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from datamule import Portfolio
import requests
import json
from difflib import get_close_matches
import pandas as pd

SEC_HEADERS = {
    "User-Agent": "Individual/tyzttzzz@gmail.com"  # Required to avoid being blocked
}


# Fetch and store CIK-Ticker mapping
def get_cik_mapping():
    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=SEC_HEADERS)
    if response.status_code == 200:
        cik_data = response.json()
        cik_mapping = {entry["ticker"].upper(): str(entry["cik_str"]).zfill(10) for entry in cik_data.values()}
        return cik_mapping
    else:
        raise Exception(f"Failed to fetch CIK mapping. Status code: {response.status_code}")


def download_and_save_filings(filing_date=('2023-01-01', '2023-01-03'), submission_type='10-K', cik='',
                              company_ticker='None'):
    # Ensure the output directory exists
    os.makedirs('data', exist_ok=True)

    # Create a Portfolio object
    portfolio = Portfolio('output_dir/'+str(cik)+"_"+str(company_ticker))  # Can be an existing or new directory

    # Download submissions based on given date range and submission type
    portfolio.download_submissions(
        # filing_date=filing_date,
        submission_type=[submission_type],
        cik=cik
    )

    # Define output file path


    # Open the output file and write parsed data

    for doc in portfolio.document_type(submission_type):
        filing_date = doc.filing_date
        os.makedirs(f'data/result_{submission_type}_{cik}_{company_ticker}', exist_ok=True)
        output_file = f'data/result_{submission_type}_{cik}_{company_ticker}/{filing_date}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            try:
                doc.parse()
                # content = doc.data['document']['partii']['item7']
                content = str(doc.data)
                # print()
                # print(content)
                f.write(content + "\n\n")
            except Exception as e:
                print(f"Failed to parse document: {e}")


cik_mapping = get_cik_mapping()
keys = cik_mapping.keys()


def get_cik_from_redis(company_name):
    """
    Searches Redis for a fuzzy and case-insensitive match and returns the CIK number.
    """
    if not company_name:
        return None  # Ensure input is valid

    company_name = company_name.strip().lower()

    # Fetch all keys from Redis (Company Names)
    normalized_keys = {key.strip().lower(): cik_mapping[key] for key in keys}  # Store original names for lookup

    # Use fuzzy matching to find the closest match
    closest_match = get_close_matches(company_name, normalized_keys.keys(), n=1, cutoff=0.6)

    if closest_match:
        best_match_cik = normalized_keys[closest_match[0]]  # Get the original stored key
        return closest_match[0], best_match_cik  # Return the corresponding CIK

    return None, None


# Example usage
if __name__ == '__main__':
    df = pd.read_csv("apollo-contacts-export.csv")

    company_list = df["Company"].dropna().unique().tolist()
    index = 0
    for company_name in company_list:
        closest_match, cik = get_cik_from_redis(company_name)

        if cik is None:
            print("not find cik: ", company_name)
            continue

        print("matched: ",[closest_match, company_name, cik])

        download_and_save_filings(
            # filing_date=('2023-01-01', '2023-01-02'),
            submission_type='10-K',
            cik=cik,
            company_ticker=company_name
        )
        index += 1
        if index == 3: break
