import csv
import datetime
import os
import constants
import common

now = datetime.datetime.now()
fnamenow = now.strftime("%Y-%m-%d T %H%M%S")
logfname = constants.LOG_DIR + constants.PACIFIC_POWER + "\\" + "Log " + fnamenow + ".txt"
nl = "\n"
print("Processing now.  Log file " + logfname)
with open(logfname, mode="w") as log_file:
    log_file.write("Reading meter master from " + constants.PACIFIC_POWER_MASTER + nl)
    meters = dict()
    ref_in = 0
    with open(constants.PACIFIC_POWER_MASTER, mode="r") as ref_file:
        csv_reader = csv.reader(ref_file)
        for row in csv_reader:
            ref_in += 1
            if ref_in > 1:
                meters.setdefault(row[1], 0)
    log_file.write("Read " + str(ref_in) + " rows from meter master file." + nl)
    in_dir = constants.IN_DIR + constants.PACIFIC_POWER
    out_dir = constants.OUT_DIR + constants.PACIFIC_POWER
    for in_fname in os.listdir(in_dir):
        log_file.write("Reading data input from " + in_fname + nl)
        with open(in_dir + "\\" + in_fname, mode="r") as in_file:
            csv_reader = csv.reader(in_file)
            in_count = 0
            out_count = 0
            no_meter_num = 0
            noMeter = dict()
            out_fname = out_dir + "\\Temp " + fnamenow + ".csv"
            low_yearmonth = ""
            high_yearmonth = ""
            log_file.write("Writing temporary data to " + out_fname + nl)
            with open(out_fname, mode="w", newline="") as out_file:
                csv_writer = csv.writer(out_file)
                csv_writer.writerow(["meter", "yearmonth", "days", "units", "cost"])
                for row in csv_reader:
                    in_count += 1
                    # Skip header row
                    if in_count > 1:
                        cust_id = row[0]
                        acct_num = row[1]
                        agreement = row[2]
                        cust_name = row[3]
                        address = row[4]
                        csz = row[5]
                        meter_num = row[6].strip()
                        year_mon = row[7]
                        days = row[8]
                        on_kwh = row[9]
                        off_kwh = row[10]
                        kwh = row[11].replace(",", "")
                        on_kw = row[12]
                        off_kw = row[13]
                        kw = row[14]
                        kvar = row[15]
                        invoice = row[16].replace("$", "").replace(",", "")
                        if meter_num == "":
                            no_meter_num += 1
                        else:
                            csv_writer.writerow([meter_num, year_mon, days, kwh, invoice])
                            out_count += 1
                            if meter_num in meters:
                                meters[meter_num] = meters[meter_num] + 1
                            elif meter_num in noMeter:
                                noMeter[meter_num] = noMeter[meter_num] + 1
                            else:
                                noMeter.setdefault(meter_num, 1)
                        if low_yearmonth == "":
                            low_yearmonth = year_mon
                            high_yearmonth = year_mon
                        else:
                            if year_mon < low_yearmonth:
                                low_yearmonth = year_mon
                            if year_mon > high_yearmonth:
                                high_yearmonth = year_mon
        log_file.write("Read " + str(in_count) + " rows from input file" + nl)
        log_file.write("Wrote " + str(out_count) + " rows to output file" + nl)
        log_file.write("Number of entries with no meter number " + str(no_meter_num) + nl)
        if len(noMeter) == 0:
            log_file.write("All meters in data file have descriptions (no new meters)" + nl)
        else:
            log_file.write("The following meters have no description entries (new meters):" + nl)
            for meter_key in noMeter:
                log_file.write(meter_key + " has " + str(noMeter[meter_key]) + " data file entries" + nl)
        target_out = out_dir + "\\" + constants.PACIFIC_POWER + " " + \
                     common.comp_mon_range(low_yearmonth, high_yearmonth) + ".csv"
        os.rename(out_fname, target_out)
        log_file.write("Renamed temporary file to " + target_out + nl)
        log_file.write("Remember to move data file to archive folder to avoid duplicates!" + nl)
    noData = False
    log_file.write("The following meters have no data (warning only):" + nl)
    for meter_key in meters:
        if meters[meter_key] == 0:
            noData = True
            log_file.write(meter_key + nl)
    if not noData:
        log_file.write("None" + nl)
print("Processing complete")
