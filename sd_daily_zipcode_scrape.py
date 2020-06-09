#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 17:44:13 2020

@author: tstone
"""

import arcgis
from arcgis.gis import GIS
from arcgis import geometry
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from arcgis.features import FeatureLayerCollection
import pandas as pd

from datetime import datetime, date

gis = GIS()

sd_dashboard_service = 'https://services1.arcgis.com/1vIhDJwtG5eNmiqX/ArcGIS/rest/services/CovidDashUpdate/FeatureServer'
file_name = "sd_daily_zipcode_summary.csv"

db_item = FeatureLayerCollection(sd_dashboard_service)

zipcodes_df = pd.DataFrame.spatial.from_layer(db_item.layers[0])
ConfirmHopsitalICuDeaths_df = pd.DataFrame.spatial.from_layer(db_item.layers[1])
AgeGenderPoints_df = pd.DataFrame.spatial.from_layer(db_item.layers[2])
CompiledCopyDashUpdate_df = pd.DataFrame.spatial.from_layer(db_item.layers[3])

zipcode_summary = pd.read_csv(file_name)

#Determine last entry added to summary file
last_summary = zipcode_summary['date through'].iloc[-1]
last_summary_dt = datetime.strptime(last_summary, "%Y-%m-%d").date()

#Determine last entry added to arcgis
newest_entry_value = zipcodes_df['UpdateDate'].iloc[-1]
newest_entry_dt = zipcodes_df['UpdateDate'].tail(1).values[0]
newest_entry_dt = datetime.utcfromtimestamp((newest_entry_dt.tolist()/1e9))
newest_entry_dt = newest_entry_dt.date()

def update_summary(zp_df, summary_df, newest_entry):
    zipcodes_df['Case_Count'].fillna(0,inplace=True)
    
    keep_columns = ['UpdateDate','ZipText','Case_Count' ]
    rename_columns = ['updated','date through','zipcode','confirmed_cases']
    
    #Convert information to proper format
    new_entries = zipcodes_df[zipcodes_df['UpdateDate'] == newest_entry].loc[:, keep_columns]
    new_entries['Case_Count'].fillna(0,inplace=True)
    new_entries['Case_Count'] = new_entries['Case_Count'].astype('int64')
    
    #Create new column with updated information
    new_entries.insert(0,"updated",date.today())
    
    #rename columns
    new_entries.columns = rename_columns
    
    #Update date through so it only returns YYYY-mm-dd
    prev_date = new_entries['date through'].tail(1).values[0]
    new_date = datetime.utcfromtimestamp((prev_date.tolist()/1e9))
    new_entries['date through'] = new_date.date()
    
    
    return new_entries


if newest_entry_dt > last_summary_dt:
    df = update_summary(zipcodes_df, zipcode_summary, newest_entry_value)
    df.to_csv(file_name,mode = 'a', header = False, index = False)
else:
    print(date.today(),": No newer data to record")

    