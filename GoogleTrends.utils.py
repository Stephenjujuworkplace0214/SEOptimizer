import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random as random
from typing import Optional, Any, Union
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from pytrends.request import TrendReq
import json



def Create_Google_trends_hunter(
    hl: str, # The host language you want to search.
)-> TrendReq:
    """
    Create Google Trends hunter object.

    Args:
        geo (str, optional): The geo lozation you want to search. Defaults to "zh-TW".

    Returns:
        TrendReq: Google Trends hunter object
    """
    return TrendReq(hl=hl, tz=360)
    


# 取時間
def __get_Converted_WholeTime_str(whole_type: str, whole_period: Union[int,list[int]])-> str:
    """
    使用者選擇某個全時段，如全年、全月等等，則用到此轉換。

    Args:
        whole_type (str): 類別，如years or months
        whole_period (Union[int, str]): 時間區間，年如2023、月如2022-9

    Returns:
        str: Valid date string in Google Trends
    """    

    # try:
    if whole_type == 'years':
        start_date = f"{whole_period}-01-01"
        end_date = f"{whole_period}-12-31"
        return f"{start_date} {end_date}"
    elif whole_type == 'months':
        try:
            start_datetime = datetime(year=whole_period[0], month=whole_period[1], day=1)
            end_date = start_datetime.strftime('%Y-%m-%d')
            start_date = (start_datetime - relativedelta(months=1)).strftime('%Y-%m-%d')
            return f"{start_date} {end_date}"
        except ValueError as e:
            print(f"Error in whole_period, the error is:{e}.")
    else:
        return "Invalid input in get_Converted_WholeTime_str. Please enter a valid one."

    # except Exception as e:
    #     print(f"Error in get_Converted_WholeTime_str, the error is:{e}.")


def __get_Converted_fromToday_str(
    fromToday_interval_unit: str, 
    fromToday_interval_value: int,
)-> str | None:
    """
    使用者選擇某個從今天到某個時間之前，如全年、全月等等，則用到此轉換。

    Args:
        fromToday_interval_unit (str): 類別，如年、月、時
        fromToday_interval_value (Union[int, str]): 時間區間，年如2023、月如2022-9

    Returns:
        str: Valid date string in Google Trends
    """    
    current_time = datetime.now()
    current_datetime = current_time.strftime("%Y-%m-%d")
    
    # try:
    match fromToday_interval_unit:
        # case 'hours':
        #     base_hr = 16 # 台灣時區24:00為16hr
        #     interval_timedelta = timedelta(hours=fromToday_interval_value)
        #     current_datetime = f"{current_time.strftime('%Y-%m-%d')}T{base_hr + current_time.hour}"
        #     start_time = current_time - interval_timedelta
        #     start_datetime = f"{start_time.strftime('%Y-%m-%d')}T{base_hr + start_time.hour}"
        case 'days': # 幾天前
            start_datetime = (current_time - relativedelta(days=fromToday_interval_value)).strftime("%Y-%m-%d")
        case 'weeks': # 幾週前
            start_datetime = (current_time - relativedelta(weeks=fromToday_interval_value)).strftime("%Y-%m-%d")
        case 'months': # 幾月前
            start_datetime = (current_time - relativedelta(months=fromToday_interval_value)).strftime("%Y-%m-%d")
        case 'years': # 幾年前
            start_datetime = (current_time - relativedelta(years=fromToday_interval_value)).strftime("%Y-%m-%d")
        case _:
            print(f"Invalid input in fromToday_period_type:{fromToday_interval_unit}，因此回傳近一個月")
            start_datetime = (current_time - relativedelta(months=1)).strftime("%Y-%m-%d")
        
    print(f"start_datetime: {start_datetime}")
    return f"{start_datetime} {current_datetime}"

    # except ValueError as e:
    #     print(f"ValueError in __get_Converted_fromToday_str, the error is:{e}.")
    #     return None

    # except Exception as e:
    #     print(f"Error in __get_Converted_fromToday_str, the error is:{e}.")
    #     return None


    
def __get_Converted_selectedTime_str(
    selectedTime_startTime: list[int], 
    selectedTime_endTime: list[int],
)-> str | None:
    """
    使用者選擇某個從特定時間到某個時間，則用到此轉換。

    Args:
        selectedTime_startTime (str): e.g. [2023, 9, 5]
        selectedTime_endTime (str): e.g. [2023, 9, 10]

    Returns:
        str: Valid date string in Google Trends
    """    
    # try: 
    start_date = datetime(selectedTime_startTime[0], selectedTime_startTime[1], selectedTime_startTime[2])
    end_date = datetime(selectedTime_endTime[0], selectedTime_endTime[1], selectedTime_endTime[2])

    if start_date < end_date:
        early_date = start_date
        late_date = end_date
    else:
        early_date = end_date
        late_date = start_date

    early_datetime = early_date.strftime('%Y-%m-%d')
    late_datetime = late_date.strftime('%Y-%m-%d')
    return f"{early_datetime} {late_datetime}"
    
    # except ValueError as e:
    #     print(f"ValueError in __get_Converted_selectedTime_str, the error is:{e}.")
    #     return None

    # except Exception as e:
    #     print(f"Error in __get_Converted_selectedTime_str, the error is:{e}.")
    #     return None
    
        
    

def Mapping_Google_trends_date(
    selectTime_type: int,
    startTime_or_type: Union[list[int], str],
    endTime: Union[list[int], int],
)-> str:
    """
    分為四種：
    - 所有時間 -> 0 
    - 全年 -> 1: slectedTime_period[str: type, int: value]
    - 從今至之前xx -> 2: slectedTime_period[str: type, int: value]
    - 開始時間~結束時間 -> 3: slectedTime_period[list[int]: startTime, list[int]: endTime]
    
    slectedTime_period 
    """
    match selectTime_type:
        case 0: # 所有時間
            return 'all'
        case 1: # 全xx
            return __get_Converted_WholeTime_str(whole_type = startTime_or_type, whole_period = endTime)
        case 2: # 從今至之前xx
            return __get_Converted_fromToday_str(fromToday_interval_unit = startTime_or_type, fromToday_interval_value = endTime)
        case 3: # 開始時間~結束時間
            return __get_Converted_selectedTime_str(selectedTime_startTime = startTime_or_type, selectedTime_endTime = endTime)
        
        

def GET_Google_trends_data(
    selectTime_type: int,
    slectedTime_period: Union[list[list[int]], list[str|int]], # The time spread you want to search.
    kw_list: list, # Max 5 keywords and MIN 1 Keyword you can search.
    hostLanguage: str = 'zh-TW', # The host language you want to search. e.g. zh-TW, en-US, zh-CN, en-AU, 
    categorie_num: int = 0, # We set the default cat is 0, which means find the trends in ALL categories. You can find your own categories you want in this url: https://github.com/pat310/google-trends-api/wiki/Google-Trends-Categories
    geo: str = 'TW', # The geo lozation you want to search. you can change any geos you want. e.g. US, CN....You can find your own two-num geo numbers in this url: https://www.webdesigntooler.com/internet-country-code-table 
    gprop: str = '', # Can be images, news, youtube or froogle (for Google Shopping results), Defaults to web searches
)-> pd.DataFrame:
        
    pytrend = Create_Google_trends_hunter(hl = hostLanguage)
    timeframe = Mapping_Google_trends_date(selectTime_type = selectTime_type, startTime_or_type = slectedTime_period[0], endTime=slectedTime_period[1])
    pytrend.build_payload(kw_list=kw_list, cat=categorie_num, timeframe=timeframe, geo=geo, gprop=gprop)
    preload = json.loads(pytrend.interest_over_time().to_json(orient='table'))['data']
    preload_df = pd.DataFrame.from_dict(preload)

    if preload_df.empty is False:
        preload_df['date'] = pd.to_datetime(preload_df['date'])
        return preload_df
    else:
        print(f"preload_df is None:{preload_df}")
        return None
    
    


if __name__ == '__main__':
    selectTime_type = 1
    slectedTime_period_list = ['months', 'years']
    slectedTime_period = [slectedTime_period_list[0], [2023, 2]]
    slectedTime_period = [slectedTime_period_list[1], 2023]
    
    selectTime_type = 2
    slectedTime_period_list = ['days', 'weeks','months', 'years']
    slectedTime_period = [slectedTime_period_list[0], 10]

    # selectTime_type = 3
    # slectedTime_period = [[2023,8,28], [2023,9,15]]
    
    print(slectedTime_period)
    result_df = GET_Google_trends_data(selectTime_type = selectTime_type,
                           slectedTime_period=slectedTime_period, 
                           kw_list=['木柵', '茶行', '政大','亡者榮耀', 'yahoo'], 
                           hostLanguage='zh-TW', 
                           categorie_num=0, 
                           geo='TW',)
    if result_df is not None:
        print(f"result_df: \n{result_df}")
    