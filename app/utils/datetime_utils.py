from datetime import date, datetime
import calendar

def get_first_day_of_month(date: date) -> date:
    """获取指定日期所在月份的第一天"""
    return date.replace(day=1)

def get_last_day_of_month(date: date) -> date:
    """获取指定日期所在月份的最后一天"""
    return date.replace(day=calendar.monthrange(date.year, date.month)[1])