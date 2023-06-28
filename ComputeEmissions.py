from pandas import DataFrame, Series
import pandas as pd
import csv
import datetime
import os
import constants
import common
import avistaconstants

nl = "\n"
elecCO2Lookup = dict()
elecCO2Default = 0.0


# Calculate the metric tons of CO2 equivalent given a data row with yearmonth and kwh values
def compute_mtco2e(in_row):
    tYear = in_row['yearmonth'] // 100
    if tYear in elecCO2Lookup:
        lbPerMwh = elecCO2Lookup[tYear]
    else:
        lbPerMwh = elecCO2Default
    mtco2e = ((in_row['units'] / constants.mwh_per_kwh) * lbPerMwh) / constants.lb_per_mt
    return mtco2e


def elect_emissions(log_file):
    log_file.write("Computing emissions for electrical sources" + nl)
    log_file.write("Loading electrical constants from " + constants.ELECTRICAL_CONSTANTS + nl)
    with open(constants.ELECTRICAL_CONSTANTS, mode="r") as elect_file:
        csv_reader = csv.reader(elect_file)
        highYear = 0
        ref_count = 0
        for row in csv_reader:
            ref_count += 1
            if ref_count > 1:
                yearmon = int(row[0])
                co2factor = float(row[1])
                elecCO2Lookup.setdefault(yearmon, co2factor)
                if yearmon > highYear:
                    highYear = yearmon
    # Use the latest available figure as the default calculation constant value
    elecCO2Default = elecCO2Lookup[highYear]
    in_dir = constants.PERM_DIR + constants.PACIFIC_POWER
    # Concatenate all electrical data files into a single dataframe
    col_names = ["meter", "yearmonth", "days", "units", "cost"]
    allFrame = pd.DataFrame(columns=col_names)
    for in_fname in os.listdir(in_dir):
        log_file.write("Reading data file " + in_fname + nl)
        tFrame = pd.read_csv(in_dir + "\\" + in_fname)
        allFrame = pd.concat([allFrame, tFrame], axis=0)
    # Only keep the dataframe rows from baseline year forward
    yearmonth_comp = constants.baseline_year * 100
    allFrame = allFrame[allFrame['yearmonth'] > yearmonth_comp]
    # Add columns for operation and sub-operation from master reference file
    refFrame = pd.read_csv(constants.PACIFIC_POWER_MASTER)
    allFrame = pd.merge(allFrame, refFrame, on='meter')
    # Remove unneeded columns from dataframe
    to_drop = ["days", "address", 'meter']
    allFrame.drop(to_drop, axis=1, inplace=True)
    # Compute metric tons of CO2 equivalent and add as a new column to dataframe
    allFrame['mtco2e'] = allFrame.apply(compute_mtco2e, axis=1)
    # Consolidate rows by operation, sub-operation, and yearmonth, summing numerical columns
    elecResult = allFrame.groupby(['yearmonth', 'operation', 'suboperation']).sum()
    elecResult['source'] = "Electricity"
    return elecResult


def natgas_emissions(log_file):
    log_file.write("Computing emissions for natural gas sources" + nl)
    in_dir = constants.PERM_DIR + constants.AVISTA
    # Concatenate all electrical data files into a single dataframe
    col_names = ["address", "yearmonth", "days", "units", "cost"]
    allFrame = pd.DataFrame(columns=col_names)
    for in_fname in os.listdir(in_dir):
        log_file.write("Reading data file " + in_fname + nl)
        tFrame = pd.read_csv(in_dir + "\\" + in_fname)
        allFrame = pd.concat([allFrame, tFrame], axis=0)
    # Only keep the dataframe rows from baseline year forward
    yearmonth_comp = constants.baseline_year * 100
    allFrame = allFrame[allFrame['yearmonth'] > yearmonth_comp]
    # Add columns for operation and sub-operation from master reference file
    refFrame = pd.read_csv(constants.AVISTA_MASTER)
    allFrame = pd.merge(allFrame, refFrame, on='address')
    # Remove unneeded columns from dataframe
    to_drop = ["days", "address"]
    allFrame.drop(to_drop, axis=1, inplace=True)
    # Convert therms to cfm (thousand cubic feet)
    allFrame['units'] = allFrame['units'] * constants.cfm_per_therm
    # Compute metric tons of CO2 equivalent and add as a new column to dataframe
    allFrame['mtco2e'] = allFrame['units'] * constants.mtco2_per_cfm
    # Consolidate rows by operation, sub-operation, and yearmonth, summing numerical columns
    natgasResult = allFrame.groupby(['yearmonth', 'operation', 'suboperation']).sum()
    natgasResult['source'] = "Natural Gas"
    return natgasResult


now = datetime.datetime.now()
fnamenow = now.strftime("%Y-%m-%d T %H%M%S")
logfname = constants.LOG_DIR + constants.CALC_EMISSIONS + "\\" + "Log " + fnamenow + ".txt"
print("Processing now.  Log file " + logfname)
with open(logfname, mode="w") as log_file:
    emitDF = elect_emissions(log_file)
    log_file.write("Electrical emissions calculation completed." + nl)
    natgasDF = natgas_emissions(log_file)
    log_file.write("Natural gas emissions calculation completed." + nl)
    emitDF = pd.concat([emitDF, natgasDF], axis=0)
    emitDF.to_csv(constants.DASHBOARD_DATA)
print("Processing completed.")

