#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import json
import requests
import pandas as pd
from difflib import get_close_matches
from datamule import Portfolio
import time
from concurrent.futures import ProcessPoolExecutor, as_completed


# Global constants
SEC_HEADERS = {
    "User-Agent": "Individual/tyzttzzz@gmail.com"  # Required to avoid being blocked
}
SEC_CIK_MAPPING_URL = "https://www.sec.gov/files/company_tickers.json"
LIST1_CSV_FILE_PATH = "apollo-contacts-export.csv"
output_dir_base = "/Users/zealot/Documents/SECv3"
MAX_WORKERS = 6


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


def download_sec_filings(cik: str, company_ticker: str, submission_type: str = "10-K"):
    """Download and save SEC filings for a given CIK and company ticker."""
    output_dir = f"{output_dir_base}/output/result_{submission_type}_{cik}_{company_ticker}"
    print("output_dir: ", output_dir)
    os.makedirs(output_dir, exist_ok=True)
    portfolio_path=f"{output_dir_base}/output_dir/{cik}_{company_ticker}"
    print("portfolio_path: ", portfolio_path)
    portfolio = Portfolio(portfolio_path)
    portfolio.download_submissions(submission_type=[submission_type], cik=cik)

    for doc in portfolio.document_type(submission_type):
        try:
            doc.parse()
            filing_date = doc.filing_date
            output_file = os.path.join(output_dir, f"{filing_date}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json_string = json.dumps(doc.data, ensure_ascii=False, indent=4)
                f.write(json_string + "\n\n")
        except Exception as e:
            print(f"Failed to parse document for CIK {cik}: {e}")


def main_(csv_path: str, max_downloads: int = 1):
    """Main execution flow."""
    cik_mapping = fetch_cik_mapping()
    list1_df = pd.read_csv(csv_path)
    company_list = list1_df["Company"].dropna().unique().tolist()

    download_count = 0
    for company_name in company_list:
        closest_match, cik = find_closest_cik(company_name, cik_mapping)
        if cik is None:
            print(f"Not found CIK: {company_name}")
            continue

        print(f"Matched: Closest: {closest_match} | Original: {company_name} | CIK: {cik}")
        # download_sec_filings(cik, company_name + "_" + closest_match)
        # download_sec_filings(cik, company_name)

        download_count += 1
        if download_count >= max_downloads:
            break


def main(csv_path: str, max_downloads: int = 1):
    cik_mapping = fetch_cik_mapping()
    list1_df = pd.read_csv(csv_path)
    company_list = list1_df["Company"].dropna().unique().tolist()

    download_tasks = []
    download_count = 0
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for company_name in company_list:
            if download_count >= max_downloads:
                break

            closest_match, cik = find_closest_cik(company_name, cik_mapping)
            if cik is None:
                print(f"Not found CIK: {company_name}")
                continue

            print(f"Matched: Closest: {closest_match} | Original: {company_name} | CIK: {cik}")
            future = executor.submit(download_sec_filings, cik, company_name + "_" + closest_match)
            download_tasks.append(future)
            download_count += 1

        for future in as_completed(download_tasks):
            try:
                future.result()
            except Exception as e:
                print(f"Download failed with exception: {e}")
def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

if __name__ == '__main__':
    start_time = time.time()
    max_downloads = 1000
    main(LIST1_CSV_FILE_PATH, max_downloads)
    end_time = time.time()
    elapsed_time = end_time - start_time
    formatted_time = format_time(elapsed_time)
    print(f"Elapsed time: {formatted_time}")
