
from datetime import time
from django.utils import timezone


WINDOWS = {
    "Breakfast": {
        "today":    (time(0, 0, 0),  time(0, 0, 1)),      
        "tomorrow": (time(14, 0), time(23, 59)),    
    },
    "Lunch": {
        "today":    (time(0, 0),  time(9, 0)),     
        "tomorrow": (time(17, 0), time(23, 59)),     
    },
    "Dinner": {
        "today":    (time(0, 0),  time(16, 0)),     
        "tomorrow": (time(22, 0), time(23, 59)),     
    },
}

def capitalize_first_letter(text):
    return text.capitalize()

def is_window_open(meal_name, which_day):

    meal_name = capitalize_first_letter(meal_name)
    
    if meal_name not in WINDOWS or which_day not in WINDOWS[meal_name]:
        return False

    start, end = WINDOWS[meal_name][which_day]
    now = timezone.localtime().time()

    
    return start <= now <= end

SHOW_CUTOFF_TIMES = {
    "Breakfast": [time(0, 0, 1), time(9, 30, 0)],
    "Lunch":     [time(9, 0),    time(14, 30)],
    "Dinner":    [time(16, 0),   time(21, 30)]
}

def is_qr_visible_for_meal(meal_name):
    meal_name = capitalize_first_letter(meal_name)
    
    if meal_name not in SHOW_CUTOFF_TIMES:
        raise KeyError(f"{meal_name} is not a valid meal name.")
    
    now = timezone.localtime().time()
    start, end = SHOW_CUTOFF_TIMES[meal_name]
    return start <= now <= end


# Special Order booking window opening times
SPECIAL_ORDER_OPEN_TIMES = {
    "Breakfast": [time(7, 0), time(9, 30, 0)],
    "Lunch":     [time(12, 0),    time(14, 30)],
    "Dinner":    [time(19, 0),   time(21, 30)]
}

def is_special_order_window_open(meal_name):
    meal_name = capitalize_first_letter(meal_name)
    
    if meal_name not in SPECIAL_ORDER_OPEN_TIMES:
        return False

    open_time, close_time = SPECIAL_ORDER_OPEN_TIMES[meal_name]
    now = timezone.localtime().time()

    if open_time <= now < close_time:
        return True
    return False

