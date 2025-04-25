#!/usr/bin/python
# -*- coding: UTF-8 -*-

from datamule import Downloader, Filing, DatasetBuilder
import pandas as pd
import os

# setup
os.makedirs('data', exist_ok=True)

# Download
downloader = Downloader()
downloader.download(ticker='MSFT',form='8-K',file_types='8-K',items=['5.02'],output_dir='msft_eod')

# Parse
data = []
# get all files in the directory
filepaths = os.listdir('msft_eod')
for filepath in filepaths:
    accession_number = filepath.split('_')[0]
    filepath = os.path.join('msft_eod', filepath)
    filing = Filing(filepath, filing_type='8-K')
    parsed_data = filing.parse_filing()
    # extract item 5.02
    text = [d['text'] for d in parsed_data['content'] if d['title'] == 'ITEM 5.02']
    # Save to csv with column accension number and text
    data.append({'accession_number': accession_number, 'text': text[0] if text else ''})

df = pd.DataFrame(data)
# remove rows with empty text (failed to extract item 5.02)
df = df[df['text'] != '']
df.to_csv('data/msft_item_502.csv', index=False)