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
import utils as ut


# Global constants
SEC_HEADERS = {
    "User-Agent": "Individual/tyzttzzz@gmail.com"  # Required to avoid being blocked
}
SEC_CIK_MAPPING_URL = "https://www.sec.gov/files/company_tickers.json"
LIST1_CSV_FILE_PATH = "generate_silver_data/apollo-contacts-export.csv"
submission_type = "10-K"
submission_type = "8-K"
submission_type = "D"
submission_type = ["13F-HR"]
# submission_type = "ADV"
output_dir_base = "/Users/zealot/Documents/SEC_"+str(submission_type)
MAX_WORKERS = 1
MAX_DOWNLOADS = 1000


def download_sec_filings(cik: str, company_ticker: str, submission_type: str = "10-K"):
    """Download and save SEC filings for a given CIK and company ticker."""
    output_dir = f"{output_dir_base}/output/result_{submission_type}_{cik}_{company_ticker}"
    print("output_dir: ", output_dir)
    os.makedirs(output_dir, exist_ok=True)
    portfolio_path=f"{output_dir_base}/output_dir/{cik}_{company_ticker}"
    print("portfolio_path: ", portfolio_path)
    portfolio = Portfolio(portfolio_path)
    # portfolio.download_submissions(submission_type=[submission_type], cik=cik)
    # portfolio.download_submissions(submission_type=[submission_type], cik=cik)
    portfolio.download_submissions(submission_type=[submission_type])

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


def download_sec_filings_13f(submission_type, filing_date=('2024-01-01', '2024-03-31')):
    if isinstance(submission_type, list):
        submission_type = submission_type[0]  # transform to list
    date_range_str = f"{filing_date[0]}_to_{filing_date[1]}"
    output_dir = f"{output_dir_base}/output/result_{submission_type}_{date_range_str}"
    print("output_dir:", output_dir)
    os.makedirs(output_dir, exist_ok=True)

    portfolio_path = f"{output_dir_base}/portfolio_output_dir"
    print("portfolio_path:", portfolio_path)

    portfolio = Portfolio(portfolio_path)

    # download sec data
    portfolio.download_submissions(submission_type=[submission_type], filing_date=filing_date)

    for doc in portfolio.document_type(submission_type):
        try:
            doc.parse()
            filing_date_val = doc.filing_date
            output_file = os.path.join(output_dir, f"{filing_date_val}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json_string = json.dumps(doc.data, ensure_ascii=False, indent=4)
                f.write(json_string + "\n\n")
        except Exception as e:
            print(f"Failed to parse document: {e}")


def download_sec_filings_v2(
    cik: str,
    company_ticker: str,
    submission_type: "10-K",
    filing_date=('2023-01-01', '2023-01-03')
):
    """Download and save SEC filings for a given CIK and company ticker, with date range support."""

    if isinstance(submission_type, str):
        submission_type = [submission_type]  # transform to list

    for sub_type in submission_type:
        date_range_str = f"{filing_date[0]}_to_{filing_date[1]}"
        output_dir = f"{output_dir_base}/output/result_{sub_type}_{cik}_{company_ticker}_{date_range_str}"
        print("output_dir:", output_dir)
        os.makedirs(output_dir, exist_ok=True)

        portfolio_path = f"{output_dir_base}/portfolio_output_dir/{cik}_{company_ticker}"
        print("portfolio_path:", portfolio_path)

        portfolio = Portfolio(portfolio_path)

        # download sec data
        portfolio.download_submissions(submission_type=[sub_type], cik=cik, filing_date=filing_date)

        for doc in portfolio.document_type(sub_type):
            try:
                doc.parse()
                filing_date_val = doc.filing_date
                output_file = os.path.join(output_dir, f"{filing_date_val}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json_string = json.dumps(doc.data, ensure_ascii=False, indent=4)
                    f.write(json_string + "\n\n")
            except Exception as e:
                print(f"Failed to parse document for CIK {cik}: {e}")



def main(csv_path: str, max_downloads: int = 1):
    cik_mapping = ut.fetch_cik_mapping()
    list1_df = pd.read_csv(csv_path)
    company_list = list1_df["Company"].dropna().unique().tolist()

    download_tasks = []
    download_count = 0

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        if '13F-HR' in submission_type:
            future = executor.submit(download_sec_filings_13f, submission_type='13F-HR')
            download_tasks.append(future)
        else:
            for company_name in company_list:
                if download_count >= max_downloads:
                    break

                closest_match, cik = ut.find_closest_cik(company_name, cik_mapping)
                if cik is None:
                    print(f"Not found CIK: {company_name}")
                    continue

                print(f"Matched: Closest: {closest_match} | Original: {company_name} | CIK: {cik}")

                future = executor.submit(download_sec_filings_v2, cik, company_name + "_" + closest_match, submission_type)
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

    main(LIST1_CSV_FILE_PATH, MAX_DOWNLOADS)
    end_time = time.time()
    elapsed_time = end_time - start_time
    formatted_time = format_time(elapsed_time)
    print(f"Elapsed time: {formatted_time}")
