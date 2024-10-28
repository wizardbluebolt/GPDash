import csv
import datetime
import os
import constants
import common

now = datetime.datetime.now()
fnamenow = now.strftime("%Y-%m-%d T %H%M%S")
logfname = constants.LOG_DIR + constants.PACIFIC_PRIDE + "\\" + "Log " + fnamenow + ".txt"
nl = "\n"
print("Processing now.  Log file " + logfname)
with open(logfname, mode="w") as log_file:
    log_file.write("Reading vehicle master from " + constants.VEHICLES_MASTER + nl)
    vehicles = dict()
    ref_in = 0
    with open(constants.VEHICLES_MASTER, mode="r") as ref_file:
        csv_reader = csv.reader(ref_file)
        for row in csv_reader:
            ref_in += 1
            if ref_in > 1:
                trow = row[0]
                vehicles.setdefault(trow.replace("-", ""), 0)
    log_file.write("Read " + str(ref_in) + " rows from vehicle master file." + nl)
    in_dir = constants.IN_DIR + constants.PACIFIC_PRIDE
    out_dir = constants.OUT_DIR + constants.PACIFIC_PRIDE
    for in_fname in os.listdir(in_dir):
        log_file.write("Reading data input from " + in_fname + nl)
        with open(in_dir + "\\" + in_fname, mode="r") as in_file:
            csv_reader = csv.reader(in_file)
            in_count = 0
            out_count = 0
            noVehicle = dict()
            out_fname = out_dir + "\\Temp " + fnamenow + ".csv"
            low_yearmonth = ""
            high_yearmonth = ""
            log_file.write("Writing temporary data to " + out_fname + nl)
            with open(out_fname, mode="w", newline="") as out_file:
                csv_writer = csv.writer(out_file)
                csv_writer.writerow(["vehicle_id", "date", "gallons", "price"])
                for row in csv_reader:
                    in_count += 1
                    # Skip header row, and blank rows or grand total row if present
                    if (in_count > 1) & (row[0] != "") & (row[1] != "") & (row[0] != "Grand Total"):
                        vehicle_id = row[0].strip().replace("-", "")
                        fuel_date = datetime.datetime.strptime(row[1], "%m/%d/%Y")
                        yearmonth = str(fuel_date.year) + '{:02d}'.format(fuel_date.month)
                        fuel_date = fuel_date.strftime("%m/%d/%Y")
                        gallons = row[2]
                        price = row[3].replace("$", "")
                        csv_writer.writerow([vehicle_id, fuel_date, gallons, price])
                        out_count += 1
                        if vehicle_id in vehicles:
                            vehicles[vehicle_id] = vehicles[vehicle_id] + 1
                        elif vehicle_id in noVehicle:
                            noVehicle[vehicle_id] = noVehicle[vehicle_id] + 1
                        else:
                            noVehicle.setdefault(vehicle_id, 1)
                        if low_yearmonth == "":
                            low_yearmonth = yearmonth
                            high_yearmonth = yearmonth
                        else:
                            if yearmonth < low_yearmonth:
                                low_yearmonth = yearmonth
                            if yearmonth > high_yearmonth:
                                high_yearmonth = yearmonth
        log_file.write("Read " + str(in_count) + " rows from input file" + nl)
        log_file.write("Wrote " + str(out_count) + " rows to output file" + nl)
        if len(noVehicle) == 0:
            log_file.write("All vehicles in data file have descriptions (no new vehicles)" + nl)
        else:
            log_file.write("The following vehicles have no description entries (new vehicles):" + nl)
            for vehicle_key in noVehicle:
                log_file.write(vehicle_key + " has " + str(noVehicle[vehicle_key]) + " data file entries" + nl)
        target_out = out_dir + "\\" + constants.PACIFIC_PRIDE + " " + \
                     common.comp_mon_range(low_yearmonth, high_yearmonth) + ".csv"
        os.rename(out_fname, target_out)
        log_file.write("Renamed temporary file to " + target_out + nl)
        log_file.write("Remember to move data file to archive folder to avoid duplicates!" + nl)
    noData = False
    log_file.write("The following vehicle IDs have no data (warning only):" + nl)
    for vehicle_key in vehicles:
        if vehicles[vehicle_key] == 0:
            noData = True
            log_file.write(vehicle_key + nl)
    if not noData:
        log_file.write("None" + nl)
print("Processing complete")
