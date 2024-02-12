from read_emails import *
import datetime


def prev_weekday(adate):
    while adate.weekday() > 4: # Mon-Fri are 0-4
        adate -= datetime.timedelta(days=1)
    return adate.strftime('%Y/%m/%#d')


today = prev_weekday(datetime.datetime.now())
emails = getEmails()
body = emails[0]['decoded']
soup = BeautifulSoup(body, 'html.parser')
