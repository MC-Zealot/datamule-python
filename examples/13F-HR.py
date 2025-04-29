# Get Insider Trading Data for Q1 2024

from datamule import Submission,Portfolio, PremiumDownloader
import pandas as pd
from tqdm import tqdm


# I set my api_key using the environment variable 'DATAMULE_API_KEY'
downloader = PremiumDownloader()

# Downloads for me in about 45 seconds (200/sec)
#downloader.download_submissions(filing_date=('2024-01-01','2024-03-31'),submission_type='13F-HR',output_dir='q1_24')
portfolio = Portfolio('q1_24')


# This is not optimized for speed, but it's a good example of how to iterate over the portfolio. Takes about 10 minutes to run all.
info_table_dict_list = []


# Just using the first 100 submissions for this example, feel free to remove this line to get all submissions
portfolio.submissions = portfolio.submissions[:10]

total_submissions = len(portfolio.submissions)
# Using tqdm to create a progress bar
df_list = []
for submission in tqdm(portfolio, total=total_submissions, desc="Processing submissions"):
    for info_table in submission.document_type('INFORMATION TABLE'):
        df_list.append(pd.DataFrame(info_table))

pd.concat(df_list).to_csv('q1_24_info_table.csv',index=False)