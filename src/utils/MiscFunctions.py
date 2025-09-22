import datetime

def ConvertStringToDateTimeOne(date_str):
    ''' Converts 20240502 to 02 May 2024 '''
    date_obj = datetime.datetime.strptime(date_str, "%Y%m%d")
    formatted_date = date_obj.strftime("%d %B %Y")
    return formatted_date