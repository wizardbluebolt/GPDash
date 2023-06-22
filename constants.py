BASE_DIR = "D:\\Task Force\\Dashboard\\Base\\"
IN_DIR = BASE_DIR + "UtilityIn\\"
OUT_DIR = BASE_DIR + "UtilityOut\\"
LOG_DIR = BASE_DIR + "Logs\\"
REF_DIR = BASE_DIR + "MasterReference\\"
PERM_DIR = BASE_DIR + "PermanentData\\"
DASHBOARD_DIR = BASE_DIR + "DashboardData\\"

PACIFIC_POWER = "PacificPower"
AVISTA = "Avista"
PACIFIC_PRIDE = "PacificPride"
SOLID_WASTE = "SolidWaste"

AVISTA_MASTER = REF_DIR + "AvistaMaster.csv"
PACIFIC_POWER_MASTER = REF_DIR + "PacificPowerMaster.csv"
VEHICLES_MASTER = REF_DIR + "VehiclesMaster.csv"

DIESEL_CONSTANTS = REF_DIR + "DieselConstants.csv"
GASOLINE_CONSTANTS = REF_DIR + "GasolineConstants.csv"
ELECTRICAL_CONSTANTS = REF_DIR + "ElectricalConstants.csv"
EMPLOYEE_COMMUTE_CONSTANTS = REF_DIR + "EmployeeCommuteConstants.csv"
FOREST_SEQ_CONSTANTS = REF_DIR + "ForestSequestrationConstants.csv"
SOLID_WASTE_CONSTANTS = REF_DIR + "SolidWasteConstants.csv"
WATER_RESTORE_CONSTANTS = REF_DIR + "WaterRestorationConstants.csv"

# Calculation Constants - The values below are HIGHLY UNLIKELY TO CHANGE!
mwh_per_kwh = 1000      # Megawatt hours per kilowatt hour
lb_per_mt = 2204.62     # Pounds per metric ton

cfm_per_therm = 0.0973  # Thousand cubic feet (cfm) per therm of natural gas
mtco2_per_cfm = 0.05486 # Metric tons of CO2 equivalent per CFM of consumed natural gas

kg_per_mt = 1000            # Kilograms per metric ton
m3_per_ft3 = 0.028316847    # Cubic meters per cubic foot
days_per_year = 365.25      # Average days per year
mt_per_gram = 0.000001      # Metric tons per gram

# Water Restoration Calculation Constants
digester_ch4_density = 662      # Grams per cubic meter
digester_ch4_destruct = 0.01    # Methane destruction efficiency from flaring or burning
ch4_gwp = 25                    # Methane global warming multiplier (impact vs CO2)

# Forest Sequestration Calculation Constants
forest_seq_factor = -2.23       # Removal in metric tons of carbon per hectare per year
aw_co2 = 44                     # Atomic weight of CO2
aw_c = 12                       # Atomic weight of Carbon
hectare_per_km2 = 100           # Hectares per square kilometer



