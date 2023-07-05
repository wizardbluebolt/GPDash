# GPDash

Sustainable energy tracking dashboard for City of Grants Pass, Oregon USA

## Description

A set of scripts to:
* Process energy utility billing files to standardize and format for processing
* Compute greenhouse gas emissions using the Local Government Operations Protocol standards and EPA provided parameters
* Summarize energy costs and emissions by city operational departments, year / month, and emissions source
* Provide a simple graphical dashboard display for the web using Data Driven Documents (D3)

## Getting Started

TBD

### Dependencies

* Python3, pandas, D3
* Windows 10

### Installing

* Install Python3 and pip following standard instructions for target host environment.
* Create top level directory to host project data files and note full absolute file path.
* Clone this repository (typically to a different location from above data directory tree).
* Expand zip file under installation / Base Folders and Files.zip and move all folders and files under Base folder to data directory above.
* Modify first line of project file constants.py so that BASE_DIR variable references the top level data directory.
* Complete the following steps in a command shell (i.e. cmd in Windows):
* Change the current directory to the repository location (cd <repository location>)
* Create Python virtual environment by executing "python -m venv /path/to/directory", where /path/to/directory is relative to the current directory.  Use "." to create the virtual environment directory under the current directory.  A virtual environment will be created under a folder titled "venv" within the designated directory.  All python scripts will be executed using this virtual environment.
* Activate the virtual directory by executing "venv\Scripts\activate.bat" (on Windows)
* Install project dependencies by executing "pip install -r requirements.txt"

### Executing program

* Complete the following steps in a command shell (i.e. cmd in Windows):
* Change the current directory to the repository location (cd <repository location>)
* Activate the virtual directory by executing "venv\Scripts\activate.bat" (on Windows)
* Run the desired script by "python <script name>", for example "python ComputeEmissions.py".  See project documentation for specific instructions for data maintenance, preparation, and manual steps.

## Help

* See project documentation

## Authors

Provided to the City of Grants Pass by the volunteers of the [Sustainable Energy Action Task Force](https://www.grantspassoregon.gov/1449/Sustainability-Energy-Action-Taskforce)

Matt Rosen [@wizardbluebolt]

## Version History

* 0.1
    * In development

## License

This project is licensed under the [GNU Public] License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
* [Sustainable Energy Action Plan](https://www.grantspassoregon.gov/DocumentCenter/View/27647/Sustainability-and-Energy-Action-Plan)
