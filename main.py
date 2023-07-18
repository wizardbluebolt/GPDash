import consolemenu as cm


choice1 = "Normalize Electrical Utility Data (Pacific Power)"
choice2 = "Normalize Natural Gas Utility Data (Avista)"
choice3 = "Normalize Vehicle Fuel Data (Pacific Pride)"
choice4 = "Generate Emissions Data (Dashboard Data file)"
choices = [choice1, choice2, choice3, choice4]
menu = cm.SelectionMenu(choices)

tfname = "go"
while tfname != "stop":
    menu.show()
    selection = menu.selected_item.text
    if selection == choice1:
        tfname = 'NormPacificPower.py'
    elif selection == choice2:
        tfname = 'NormAvista.py'
    elif selection == choice3:
        tfname = 'NormPacificPride.py'
    elif selection == choice4:
        tfname = 'ComputeEmissions.py'
    else:
        tfname = "stop"
    if tfname != "stop":
        with open(tfname, mode="r") as subfile:
            exec(subfile.read())
