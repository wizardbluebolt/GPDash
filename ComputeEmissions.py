import pandas as pd
import numpy as np
import csv
import datetime
import os
import constants


nl = "\n"
elecCO2Lookup = dict()
elecCO2Default = 0.0


class VehicleMaster(object):
    vehicle_id = ""
    op_yearmonth = ""
    operation = ""
    suboperation = ""
    model_year = ""
    description = ""
    category = ""
    purpose = ""
    fuel_type = ""

    def __init__(self, p_row):
        self.vehicle_id = p_row[0]
        self.op_yearmonth = int(p_row[1])
        self.operation = p_row[2]
        self.suboperation = p_row[3]
        self.model_year = p_row[4]
        self.description = p_row[5]
        self.category = p_row[6]
        self.purpose = p_row[7]
        self.fuel_type = p_row[8]


def vehicle_sort_key(p_vehicle_master):
    return p_vehicle_master.op_yearmonth


# Calculate the metric tons of CO2 equivalent given a data row with yearmonth and kwh values
def compute_electric_mtco2e(in_row):
    tYear = in_row['yearmonth'] // 100
    if tYear in elecCO2Lookup:
        lbPerMwh = elecCO2Lookup[tYear]
    else:
        lbPerMwh = elecCO2Default
    mtco2e = ((in_row['units'] / constants.mwh_per_kwh) * lbPerMwh) / constants.lb_per_mt
    return mtco2e


def elect_emissions(p_log_file):
    global elecCO2Default
    p_log_file.write("Computing emissions for electrical sources" + nl)
    p_log_file.write("Loading electrical constants from " + constants.ELECTRICAL_CONSTANTS + nl)
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
        p_log_file.write("Reading data file " + in_fname + nl)
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
    allFrame['mtco2e'] = allFrame.apply(compute_electric_mtco2e, axis=1)
    allFrame['source'] = "Electricity"
    # Consolidate rows by operation, sub-operation, and yearmonth, summing numerical columns
    elecResult = allFrame.groupby(['yearmonth', 'operation', 'suboperation', 'source']).sum()
    return elecResult


def natgas_emissions(p_log_file):
    p_log_file.write("Computing emissions for natural gas sources" + nl)
    in_dir = constants.PERM_DIR + constants.AVISTA
    # Concatenate all electrical data files into a single dataframe
    col_names = ["address", "yearmonth", "days", "units", "cost"]
    allFrame = pd.DataFrame(columns=col_names)
    for in_fname in os.listdir(in_dir):
        p_log_file.write("Reading data file " + in_fname + nl)
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
    allFrame['source'] = "Natural Gas"
    # Consolidate rows by operation, sub-operation, and yearmonth, summing numerical columns
    natgasResult = allFrame.groupby(['yearmonth', 'operation', 'suboperation', 'source']).sum()
    return natgasResult


def vehicle_emissions(p_log_file):
    p_log_file.write("Computing emissions for vehicle sources" + nl)
    p_log_file.write("Loading vehicle master information from " + constants.VEHICLES_MASTER + nl)
    master_count = 0
    # vehicles is a dictionary keyed by vehicle_id
    # Dictionary entry for each key is a list of master entries for that vehicle sorted by yearmonth
    # This allows the operational department for a vehicle to change over time.  Emissions will be
    # counted against the vehicle's assigned department as of the time of each fueling event.
    vehicles = dict()
    with open(constants.VEHICLES_MASTER, mode="r") as vehicle_file:
        csv_reader = csv.reader(vehicle_file)
        for row in csv_reader:
            master_count += 1
            if master_count > 1:
                master_entry = VehicleMaster(row)
                if not (master_entry.vehicle_id in vehicles):
                    vehicles.setdefault(master_entry.vehicle_id, [])
                vehicles[master_entry.vehicle_id].append(master_entry)
    for entry in vehicles.values():
        entry.sort(key=vehicle_sort_key, reverse=True)
    p_log_file.write("Completed loading " + str(master_count - 1) + " vehicle master entries." + nl)
    gasoline_factors = dict()
    highest_year = ""
    with open(constants.GASOLINE_CONSTANTS, mode="r") as gasoline_file:
        csv_reader = csv.reader(gasoline_file)
        gasoline_count = 0
        for row in csv_reader:
            gasoline_count += 1
            if gasoline_count > 1:
                if row[0] > highest_year:
                    highest_year = row[0]
                gasoline_factors.setdefault(row[0], float(row[1]))
    gasoline_factor_default = gasoline_factors[highest_year]
    p_log_file.write("Completed loading " + str(gasoline_count - 1) + " gasoline conversion factors" + nl)
    diesel_factors = dict()
    highest_year = ""
    with open(constants.DIESEL_CONSTANTS, mode="r") as diesel_file:
        csv_reader = csv.reader(diesel_file)
        diesel_count = 0
        for row in csv_reader:
            diesel_count += 1
            if diesel_count > 1:
                if row[0] > highest_year:
                    highest_year = row[0]
                diesel_factors.setdefault(row[0], float(row[1]))
    diesel_factor_default = diesel_factors[highest_year]
    p_log_file.write("Completed loading " + str(diesel_count - 1) + " diesel conversion factors" + nl)
    column_names = ["yearmonth", "operation", "suboperation", "units", "cost", "mtco2e", "source"]
    vehFrame = pd.DataFrame(columns=column_names)
    in_dir = constants.PERM_DIR + constants.PACIFIC_PRIDE
    baseline_comp = str(constants.baseline_year)
    for in_fname in os.listdir(in_dir):
        p_log_file.write("Reading data file " + in_fname + nl)
        with open(constants.PERM_DIR + constants.PACIFIC_PRIDE + "\\" + in_fname, mode="r") as in_file:
            csv_reader = csv.reader(in_file)
            in_count = 0
            for row in csv_reader:
                in_count += 1
                # Skip heading row
                if in_count > 1:
                    vehicle_id = row[0]
                    tDateParts = row[1].split("/")
                    tYear = tDateParts[2]
                    units = float(row[2])
                    price = float(row[3])
                    cost = units * price
                    # Ignore entries before the baseline
                    if tYear >= baseline_comp:
                        yearmonth = int(tYear + '{:02d}'.format(int(tDateParts[0])))
                        if vehicle_id in vehicles:
                            for entry in vehicles[vehicle_id]:
                                if entry.op_yearmonth <= yearmonth:
                                    vme = entry
                                    break
                            if vme.fuel_type == constants.gasoline:
                                source = constants.gasoline
                                if tYear in gasoline_factors:
                                    factor = gasoline_factors[tYear]
                                else:
                                    factor = gasoline_factor_default
                            elif vme.fuel_type == constants.diesel:
                                source = constants.diesel
                                if tYear in diesel_factors:
                                    factor = diesel_factors[tYear]
                                else:
                                    factor = diesel_factor_default
                            elif vme.fuel_type == constants.electricity:
                                source = constants.electricity
                                factor = 0.0
                            else:
                                p_log_file.write("Error: Unknown fuel type for vehicle " + vehicle_id +
                                               ".  Entry skipped" + nl)
                                continue
                            tEvent = pd.DataFrame({'yearmonth': [yearmonth],
                                      'operation': [vme.operation],
                                      'suboperation': [vme.suboperation],
                                      'units': [units],
                                      'cost': [cost],
                                      'mtco2e': [(units * factor) / constants.kg_per_mt],
                                      'source': [source]})
                            vehFrame = pd.concat([vehFrame, tEvent])
                        else:
                            p_log_file.write("Error: Missing master entry for vehicle: " + vehicle_id +
                                           ".  Entry skipped" + nl)
    vehicleResult = vehFrame.groupby(['yearmonth', 'operation', 'suboperation', 'source']).sum()
    return vehicleResult


def solid_waste_emissions(p_log_file, p_year_min, p_year_max):
    p_log_file.write("Calculating solid waste emissions from " + str(p_year_min) +
                     " to " + str(p_year_max) + nl)
    swc_dict = dict()
    sw_default_year_low = 9999
    sw_default_year_high = 0
    with open(constants.SOLID_WASTE_CONSTANTS) as swc_file:
        p_log_file.write("Reading solid waste constants from " + constants.SOLID_WASTE_CONSTANTS + nl)
        csv_reader = csv.reader(swc_file)
        ref_in = 0
        for row in csv_reader:
            ref_in += 1
            # Skip header row
            if ref_in > 1:
                tyear = int(row[0])
                swc_dict.setdefault(tyear, int(row[1]))
                if tyear < sw_default_year_low:
                    sw_default_year_low = tyear
                if tyear > sw_default_year_high:
                    sw_default_year_high = tyear
        p_log_file.write("Read " + str(ref_in) + " rows from solid waste reference file" + nl)
    # Concatenate all solid waste data files into a single dataframe
    column_names = ["address", "operation", "suboperation", "yearmonth", "units", "cost", "interpolated"]
    swFrame = pd.DataFrame(columns=column_names)
    in_dir = constants.PERM_DIR + constants.SOLID_WASTE
    for in_fname in os.listdir(in_dir):
        p_log_file.write("Reading data file " + in_fname + nl)
        tframe = pd.read_csv(in_dir + "\\" + in_fname)
        swFrame = pd.concat([swFrame, tframe], axis=0)
    # Only keep dataframe rows from baseline year forward
    yearmonthcomp = constants.baseline_year * 100
    swFrame = swFrame[swFrame['yearmonth'] > yearmonthcomp]
    # Remove unneeded columns from dataframe
    to_drop = ["address", "interpolated"]
    swFrame.drop(to_drop, axis=1, inplace=True)
    # Get total cost per year in order to prorate emissions across operations
    totFrame = swFrame.copy()
    totFrame['year'] = totFrame['yearmonth'] // 100
    to_drop = ["yearmonth", "operation", "suboperation", "units"]
    totFrame.drop(to_drop, axis=1, inplace=True)
    totFrame = totFrame.groupby(['year']).sum()
    # Convert total cost dataframe to dictionary keyed by year for convenience
    totDict = dict()
    for index, row in totFrame.iterrows():
        # Expression row.name is the year
        totDict.setdefault(row.name, row['cost'])
    # Compute estimated emissions value for each solid waste entry
    for index, row in swFrame.iterrows():
        tyear = row['yearmonth'] // 100
        if tyear < sw_default_year_low:
            tyear = sw_default_year_low
        elif tyear > sw_default_year_high:
            tyear = sw_default_year_high
        tfactor = row['cost'] / totDict[tyear]
        temit = swc_dict[tyear] * tfactor
        swFrame.loc[index, 'mtco2e'] = temit
        swFrame.loc[index, 'source'] = "Solid Waste"
    # Use groupby function to create the multi-index to correspond to other sources
    swResult = swFrame.groupby(['yearmonth', 'operation', 'suboperation', 'source']).sum()
    return swResult


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
    vehDF = vehicle_emissions(log_file)
    log_file.write("Vehicle fuel emissions calculation completed." + nl)
    emitDF = pd.concat([emitDF, vehDF], axis=0)
    yearmonths = emitDF.index.get_level_values('yearmonth')
    monthyearmax = np.max(yearmonths)
    yearmax = int(monthyearmax // 100)
    monthyearmin = np.min(yearmonths)
    yearmin = int(monthyearmin // 100)
    swDF = solid_waste_emissions(log_file, yearmin, yearmax)
    log_file.write("Solid waste emissions calculation completed." + nl)
    emitDF = pd.concat([emitDF, swDF], axis=0)
    emitDF.to_csv(constants.DASHBOARD_DATA)

print("Processing completed.")

