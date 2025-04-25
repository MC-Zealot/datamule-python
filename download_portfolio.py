#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from datamule import Portfolio
import requests
import json


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



def download_and_save_filings(filing_date=('2023-01-01', '2023-01-03'), submission_type='10-K',cik = '', company_ticker='None'):
    # Ensure the output directory exists
    os.makedirs('data', exist_ok=True)

    # Create a Portfolio object
    portfolio = Portfolio('output_dir')  # Can be an existing or new directory

    # Download submissions based on given date range and submission type
    portfolio.download_submissions(
        # filing_date=filing_date,
        submission_type=[submission_type],
        cik=cik
    )

    # Define output file path
    output_file = f'data/result_{submission_type}_{cik}_{company_ticker}.json'

    # Open the output file and write parsed data
    with open(output_file, 'w', encoding='utf-8') as f:
        for doc in portfolio.document_type(submission_type):
            try:
                doc.parse()
                # content = doc.data['document']['partii']['item7']
                content = str(doc.data)
                # print(content)
                f.write(content + "\n\n")
            except Exception as e:
                print(f"Failed to parse document: {e}")

cik_mapping = get_cik_mapping()
# Example usage
if __name__ == '__main__':
    index = 0
    for key in cik_mapping:
        company_ticker=key
        cik = cik_mapping[key]
        download_and_save_filings(
            # filing_date=('2023-01-01', '2023-01-02'),
            submission_type='10-K',
            cik=cik,
            company_ticker=company_ticker
        )
        index+=1
        if index==5: break
