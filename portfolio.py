#!/usr/bin/python
# -*- coding: UTF-8 -*-
from datamule import Portfolio

# Create a Portfolio object
portfolio = Portfolio('APPL10K') # can be an existing directory or a new one

# Download submissions
portfolio.download_submissions(
   submission_type=['10-K'],
    # cik='320193',
    ticker='AAPL'
)

# Iterate through documents by document type
print(type(portfolio.document_type('10-K')))
for ten_k in portfolio.document_type('10-K'):
   ten_k.parse()
   data = ten_k.data
   # print(ten_k.data['document']['partii']['item7'])
   print(ten_k.filing_date)
   print(ten_k.data['document'])


# 打开输出文件
with open('data/result_10-K.txt', 'w', encoding='utf-8') as f:
    for ten_k in portfolio.document_type('10-K'):
        ten_k.parse()
        content = ten_k.data['document']['partii']['item7']
        print(content)
        f.write(content + "\n\n")