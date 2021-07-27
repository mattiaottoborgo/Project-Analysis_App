import datetime
#function that make some checks about the sense of the dates inserted
def checkDate(firstDate,secondDate):
    if firstDate>=secondDate:
        return"Error: dates not in the right order!"
    if secondDate>datetime.datetime.now().timestamp():
        return "Error: date must be before "+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return True