#!/usr/bin/python
# -*- coding: UTF-8 -*-
from datamule import Portfolio

# Create a Portfolio object
portfolio = Portfolio('output_dir') # can be an existing directory or a new one

# Download submissions
portfolio.download_submissions(
   filing_date=('2023-01-01','2023-01-03'),
   submission_type=['10-K'],
)

# Iterate through documents by document type
for ten_k in portfolio.document_type('10-K'):
   ten_k.parse()
   print(ten_k.data['document']['partii']['item7'])
   # print(ten_k.data['document'])


# 打开输出文件
with open('data/result_10-K.txt', 'w', encoding='utf-8') as f:
    for ten_k in portfolio.document_type('10-K'):
        ten_k.parse()
        content = ten_k.data['document']['partii']['item7']
        print(content)
        f.write(content + "\n\n")