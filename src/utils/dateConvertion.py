
from datetime import datetime


class DateConvertion:
    def __init__(self):
        self.date_format = '%Y/%m/%d %H:%M:%S'
        self.string_formart = '%d/%m/%Y - %H:%M:%S'

    def toString(self, date):
        return datetime.strftime(date, self.string_format)

    def toDatetime(self, string):
        return datetime.strptime(string, self.date_formart)