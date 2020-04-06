# sandiego-covid-data
Tools for tracking / visualizing COVID-19 in San Diego

## scrape_sdcounty_status.py 
Python script that scrapes latest numbers for San Diego county and presents a JSON file. Includes lambda task handler for AWS (in process).

Visualization is currently available at:

https://observablehq.com/@nikolajbaer/san-diego-corona-virus-detail

## scrape_sd_county_daily_summary.py
Python script which scrapes the daily county pdf updates from San Diego county and outputs it to the sd_daily_city_summary.csv file. . 
Additionally it will download the most recent pdfs and store them in sd_daily_city_pdfs.


## scrape_sd_zipcode_daily_summary.py
Python script which scrapes the zipcode daily pdf updates from San Diego county and outputs it to the sd_daily_zipcode_summary.csv file. Additional it will download the most recent pdfs and store them in sd_daily_zipcode_pdfs.

