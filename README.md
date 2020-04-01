# sandiego-covid-data
Tools for tracking / visualizing COVID-19 in San Diego

## scrape_sdcounty_status.py 
Python script that scrapes latest numbers for San Diego county and presents a JSON file. Includes lambda task handler for AWS (in process).

Visualization is currently available at:

https://observablehq.com/@nikolajbaer/san-diego-corona-virus-detail

## scrape_sd_county_daily_summary.py
Python script which scrapes the daily pdf updates from San Diego county and outputs it to a csv file. 
Additionally it will download the most recent pdfs and store them in sd_daily_city_pdfs

