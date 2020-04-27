# -*- coding: utf-8 -*-

'''
Code downloads pdf files from SD County website and converts information to 
json output

Website: https://www.sandiegocounty.gov/content/dam/sdc/hhsa/programs/phs/Epidemiology/COVID-19%20Summary%20of%20Cases%20by%20Zip%20Code.pdf
'''

import requests
from datetime import date, timedelta, datetime
import tabula
import pandas as pd
import re

#For testing
import os

#Download PDF locally
def download_pdf(filename,URL):
    myfile = requests.get(URL)
    open(filename,'wb').write(myfile.content)

#Read pdf file and
def convert_pdf(filename, download_date):
    columns = ['zipcode', 'confirmed_cases']
    
    #Loading data from pdf
    pdf_list = tabula.read_pdf(filename, pages = "all", \
                               multiple_tables = True)
    
    #Splitting data into proper format 
    pdf_df1 = pd.DataFrame(pdf_list[1]).iloc[1:,0:2]
    pdf_df2 = pd.DataFrame(pdf_list[2]).iloc[1:,0:2]
    pdf_df1.columns = columns
    pdf_df2.columns = columns
    pdf_df = pd.concat([pdf_df1,pdf_df2])
    pdf_df.reset_index(drop=True, inplace=True)
    
    #Determine date through time. This is the date that the sum goes until found 
    #in the PDF
    pdf_title = pdf_list[0][0][0]
    match = re.search(r'\d{1}/\d{1}/\d{4}', pdf_title)
    if match == None:    
        match = re.search(r'\d{1}/\d{2}/\d{4}', pdf_title)
    elif match == None:
        match = re.search(r'\d{2}/\d{2}/\d{4}', pdf_title)
        
    date_through = datetime.strptime(match.group(), "%m/%d/%Y")
        
    #Add updated and date through columns
    pdf_df.insert(0,'updated', date.today())
    pdf_df.insert(1,'date through', date_through)

    return pdf_df


if __name__=="__main__":
    
    testing = True
    yesterdate = str(date.today() - timedelta(days=1)) 
    
    if testing:
        filename = 'sd_daily_zipcode_pdfs/sd_daily_update_zipcode_2020-04-23.pdf'
    else:
        file = "sd_daily_update_zipcode_" + yesterdate + ".pdf"
        filepath = "sd_daily_zipcode_pdfs/"
        filename = filepath + file
        URL = "https://www.sandiegocounty.gov/content/dam/sdc/hhsa/programs/" +\
            "phs/Epidemiology/COVID-19%20Summary%20of%20Cases%20by%20Zip%20Code.pdf"
    
        #Downloading and converting data
        download_pdf(filename,URL)
   
    df = convert_pdf(filename, yesterdate)
    
    #Writing data
    csv_file = 'sd_daily_zipcode_summary.csv'
    
    
    csv_mode = 'a'
    csv_header = False
    if(not os.path.exists(csv_file)):
        csv_mode = 'w'
        csv_header = True
        
    
    df.to_csv(csv_file,mode=csv_mode,header=csv_header,\
              index=False)

