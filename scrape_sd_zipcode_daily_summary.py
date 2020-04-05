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
    pdf_list = tabula.read_pdf(filename, pages = "all", multiple_tables = True)[0]
    
    #Splitting data into proper format 
    pdf_df = pd.DataFrame(pdf_list)
    pdf_df1 = pd.DataFrame(pdf_df.iloc[:,0:2])
    pdf_df1.columns = columns
    pdf_df2 = pd.DataFrame(pdf_df.iloc[:,2:4])
    pdf_df2.columns = columns
    pdf_df = pd.concat([pdf_df1,pdf_df2])
    pdf_df.reset_index(drop=True, inplace=True)
    
    #Determine date through time. This is the date that the sum goes until found 
    #in the PDF
    text = pdf_df.loc[0,"zipcode"]
    month = 1
    match = re.search(r'\d{1}/\d{1}/\d{4}', text)
    if match == None:    
        match = re.search(r'\d{1}/\d{2}/\d{4}', text)
    elif match == None:
        match = re.search(r'\d{2}/\d{2}/\d{4}', text)
        
    date_through = datetime.strptime(match.group(), "%m/%d/%Y")
    pdf_df.drop(0,axis=0,inplace=True)
        
    #Add updated and date through columns
    pdf_df.insert(0,'updated', date.today())
    pdf_df.insert(1,'date through', date_through)
    
    #Find names Zip Code and remove
    zipcode_index = pdf_df[pdf_df["zipcode"] == "Zip Code"].index
    for zi in zipcode_index:
        pdf_df.drop(zi, axis=0, inplace=True)
    
    #Find total and append to bottom of dataframe
    total_line = pdf_df[pdf_df["zipcode"] == "TOTAL"]
    pdf_df.drop(total_line.index,inplace=True)
    pdf_df = pdf_df.append(total_line)
    
    #drop nan values
    pdf_df.dropna(inplace=True)

    return pdf_df


if __name__=="__main__":
    
    yesterdate = str(date.today() - timedelta(days=1)) 
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

