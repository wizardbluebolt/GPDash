import csv
import datetime
import os
import constants
import avistaconstants as aconstants
import common


class FileLine(object):
    lineParts = []
    isSkipLine = False
    isAddressLine = False
    isMeterLine = False
    isDataLine = False
    address = ""
    meter = "None"
    month = ""
    year = ""
    days = 0
    therms = 0.0
    cost = 0.0

    def __init__(self, p_prior_address, p_prior_meter):
        self.address = p_prior_address
        self.meter = p_prior_meter

    def check_skip_line(self):
        line1 = self.lineParts[0]
        if len(line1) == 0:
            self.isSkipLine = True
        else:
            self.isSkipLine = any(line1.startswith(elem) for elem in aconstants.SKIP_INDICATORS)

    def check_address(self):
        line1 = self.lineParts[0]
        if line1.startswith(aconstants.ADDR_INDICATOR):
            self.isAddressLine = True
            taddr = line1.replace(aconstants.ADDR_INDICATOR, "")
            taddr = taddr.replace(aconstants.ADDR_SUFFIX, "")
            self.address = taddr.strip()

    def check_data(self):
        line1 = self.lineParts[0]
        self.isDataLine = any(line1.startswith(elem) for elem in aconstants.MONTHS)
        if self.isDataLine:
            tline = line1.split(" ")
            tmonName = tline[0]
            self.month = '{:02d}'.format(aconstants.MONTHS.index(tmonName) + 1)
            self.year = tline[2]
            self.days = int(self.lineParts[1])
            self.therms = float(self.lineParts[3].replace(",", ""))
            self.cost = float(self.lineParts[7].replace(",", ""))

    def check_meter(self):
        line1 = self.lineParts[0]
        if not self.isDataLine:
            self.isMeterLine = True
            self.meter = line1.split(", ")[1]

    def set_line_parts(self, parts):
        self.lineParts = parts
        self.check_skip_line()
        if not self.isSkipLine:
            self.check_address()
            if not self.isAddressLine:
                self.check_data()
                self.check_meter()


now = datetime.datetime.now()
fnamenow = now.strftime("%Y-%m-%d T %H%M%S")
logfname = constants.LOG_DIR + constants.AVISTA + "\\" + "Log " + fnamenow + ".txt"
nl = "\n"
print("Processing now.  Log file " + logfname)
with open(logfname, mode="w") as log_file:
    log_file.write("Reading address master from " + constants.AVISTA + nl)
    addresses = dict()
    ref_in = 0
    with open(constants.AVISTA_MASTER, mode="r") as ref_file:
        csv_reader = csv.reader(ref_file)
        for row in csv_reader:
            ref_in += 1
            if ref_in > 1:
                addresses.setdefault(row[0], 0)
    log_file.write("Read " + str(ref_in) + " rows from address master file." + nl)
    in_dir = constants.IN_DIR + constants.AVISTA
    out_dir = constants.OUT_DIR + constants.AVISTA
    for in_fname in os.listdir(in_dir):
        log_file.write("Reading data input from " + in_fname + nl)
        with open(in_dir + "\\" + in_fname, mode="r") as in_file:
            csv_reader = csv.reader(in_file)
            in_count = 0
            out_count = 0
            noAddress = dict()
            out_fname = out_dir + "\\Temp " + fnamenow + ".csv"
            low_yearmonth = ""
            high_yearmonth = ""
            prior_address = ""
            prior_meter = ""
            log_file.write("Writing temporary data to " + out_fname + nl)
            with open(out_fname, mode="w", newline="") as out_file:
                csv_writer = csv.writer(out_file)
                csv_writer.writerow(["address", "yearmonth", "days", "units", "cost"])
                for row in csv_reader:
                    in_count += 1
                    fl = FileLine(prior_address, prior_meter)
                    fl.set_line_parts(row)
                    if not fl.isSkipLine:
                        if fl.isAddressLine:
                            prior_address = fl.address
                            prior_meter = "None"
                            if fl.address in addresses:
                                addresses[fl.address] = addresses[fl.address] + 1
                            elif fl.address in noAddress:
                                noAddress[fl.address] = noAddress[fl.address] + 1
                            else:
                                noAddress.setdefault(fl.address, 1)
                        elif fl.isMeterLine:
                            prior_meter = fl.meter
                        elif fl.isDataLine:
                            yearmonth = fl.year + fl.month
                            csv_writer.writerow([fl.address, yearmonth, fl.days, fl.therms, fl.cost])
                            out_count += 1
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
        if len(noAddress) == 0:
            log_file.write("All addresses in data file have master address entries (no new addresses)" + nl)
        else:
            log_file.write("The following addresses have no entry in Avista master address file (new):" + nl)
            for address in noAddress:
                log_file.write(address + " has " + str(noAddress[address]) + " data file entries" + nl)
        target_out = out_dir + "\\" + constants.AVISTA + " " + \
                        common.comp_mon_range(low_yearmonth, high_yearmonth) + ".csv"
        os.rename(out_fname, target_out)
        log_file.write("Renamed temporary file to " + target_out + nl)
        log_file.write("Remember to move data file to archive folder to avoid duplicates!" + nl)
    noData = False
    log_file.write("The following addresses have no data (warning only):" + nl)
    for address in addresses:
        if addresses[address] == 0:
            noData = True
            log_file.write(address + nl)
    if not noData:
        log_file.write("None" + nl)
print("Processing complete")