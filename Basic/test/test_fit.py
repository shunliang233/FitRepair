import fitparse

# Load the FIT file
fitfile = fitparse.FitFile("./2024-07-06 CA759(北京首都PEK - 名古屋中部NGO)/strava-iphone.fit")

# Iterate over all messages of type "record"
# (other types include "device_info", "file_creator", "event", etc)
for record in fitfile.get_messages("record"):
    output = False
    # Records can contain multiple pieces of data (ex: timestamp, latitude, longitude, etc)
    for data in record:
        if data.name == 'gps_accuracy' and (data.value == None or data.value >= 1):
            # Print the name and value of the data (and the units if it has any)
            output = True
    
    for data in record:
        if output == True:
            if data.units:
                if data.name == 'position_long' or data.name == 'position_lat':
                    print(" * {}: {} ({})".format(data.name, data.value * ( 180.0 / 2**31 ), 'degree'))
                else:
                    print(" * {}: {} ({})".format(data.name, data.value, data.units))
            else:
                print(" * {}: {}".format(data.name, data.value))
    if output == True:
        print("---")