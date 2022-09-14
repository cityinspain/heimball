# convert height formatted as "feet' inches"" to inches
def convert_height_string_to_inches(height_string):

    feet_str = height_string.split("'")[0]

    inches_str = height_string.split("'")[1].split('"')[0]

    feet = int(feet_str)
    inches = int(inches_str)

    return feet * 12 + inches
