from django.utils import timezone
import datetime


def is_peak_hour():
    current_datetime = timezone.now()
    current_time = current_datetime.time()

    is_weekday = current_datetime.weekday() < 5
    morning_peak = datetime.time(6, 0, 0) <= current_time <= datetime.time(11, 59, 59)
    evening_peak = datetime.time(17, 0, 0) <= current_time <= datetime.time(21, 0, 0)

    return (is_weekday and morning_peak) or evening_peak
