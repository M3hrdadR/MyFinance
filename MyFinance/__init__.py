import MetaTrader5 as mt5
import datetime
from MyFinance.Constants import *
import pandas as pd


def start(path=""):
    """
    Tries to connect to MetaTrader5
    :param [path : "path to mt5"]
    :return: Boolean
    """

    if path:
        result = mt5.initialize(path)
    else:
        result = mt5.initialize()
    assert result, "Failed to Connect to MT5"
    return result


def end():
    """
    Disconnecting
    :return: None
    """

    return mt5.shutdown()


def login(account_number, server="", password=""):
    """
    Logging into MT5 account
    :param account_number: Account Number(Int)
    :param server: "Server Name"(Str)
    :param password: "Password"(Str)
    :return: Boolean
    """
    assert (server == "" and password == "") or (server != "" and password != ""), "You must enter password " \
                                                     "and server both or do not enter any of them."
    result = False
    if server and password:
        result = mt5.login(account_number, password=password, server=server)
    elif not server and not password:
        result = mt5.login(account_number, password=password, server=server)
    assert result, "Login Failed!"
    return result


def modify_market_watch(symbol_name, enable=True):
    """
    Adding or removing a symbol of market watch.
    :param symbol_name: (Str)
    :param enable: True= adding to MW |False= removing of MW (Boolean)
    :return: Boolean
    """
    result = mt5.symbol_select(symbol_name, enable)
    assert result, "Error in modifying Market Watch"
    return result


def get_symbols(MT5_regex=""):
    """
    Used to get symbols and their INFOs.
    https://www.mql5.com/en/docs/integration/python_metatrader5/mt5symbolsget_py
    further information in get_symbol()
    :param MT5_regex: "MT5 Regex"(Str)
    :return: List of Symbols (List) or Error
    """
    if MT5_regex:
        result = mt5.symbols_get(MT5_regex)
    else:
        result = mt5.symbols_get()

    if result is None:
        error = mt5.last_error()
        if error[0] != 1:
            return error
        else:
            return list(result)
    else:
        return list(result)


def get_symbol(symbol_name):
    """
    information about a symbol name, Structure is available here:
    https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants#enum_symbol_info_string
    :param symbol_name: (Str)
    :return: information about symbol (Dict) or Error
    """
    result = mt5.symbol_info(symbol_name)
    if result is None:
        error = mt5.last_error()
        if error[0] != 1:
            return error
        else:
            return result
    else:
        return result._asdict()


def get_last_tick(symbol_name):
    """
    getting last thing happened in symbol
    :param symbol_name: (Str)
    :return: information of last tick (Dict)  or Error
    """
    modify_market_watch(symbol_name, enable=True)
    result = mt5.symbol_info_tick(symbol_name)
    if result is None:
        error = mt5.last_error()
        if error[0] != 1:
            return error
        else:
            return result
    else:
        dct = result._asdict()
        dct['time'] = pd.to_datetime(dct['time'], unit='s').to_pydatetime()
        dct['bid'] = round(dct['bid'], 5)
        dct['ask'] = round(dct['ask'], 5)
        del dct['time_msc']
        del dct['volume_real']
        del dct['flags']
    return dct


def get_data(symbol_name, time_frame, start, count=None, end_date=None):
    """
    getting data for a symbol.
    ! You are not allowed to use both of "count" and "end_date" arguments.

    :param symbol_name: (Str)
    :param time_frame: Constant (ex: mt5.TIMEFRAME.D1)
    :param start: index of a bar you want start from our date (Int, DateTime, Pandas.TimeStamps)
    :param count: number of bars you want to have (Int)
    :param end_date: datetime of last data you want (Datetime, Pandas.TimeStamps)
    :return: requested data (Pandas DataFrame)
    """
    assert not count or not end_date, "You must provide either number of bars you want or date you want data up to it."
    assert count or end_date, "You must provide just one of end_date or count."
    assert type(start) is datetime.datetime or type(start) is int or type(start) is pd.Timestamp, "Your start type is" \
                                            " not True, It must one of Pandas.Timestamps or datetime.datetime or Int."
    date_to = None
    date_from = None
    start_position = None

    if type(start) is pd.Timestamp or type(start) is datetime.datetime:
        if type(start) is pd.Timestamp:
            try:
                end_date = pd.to_datetime(start, unit='D').to_pydatetime()
            except:
                try:
                    end_date = pd.to_datetime(start, unit='s').to_pydatetime()
                except:
                    print("Your timestamp doesn't seem to be valid for end_date.")
                    quit()
        elif type(start) is datetime.datetime:
            try:
                end_date = pd.to_datetime(start).to_pydatetime()
            except:
                print("Your datetime input for end_date doesn't seem to be valid.")
                quit()
        date_from = start
    elif type(start) is int:
        start_position = start

    if end_date is not None:
        assert type(end_date) is datetime.datetime or type(end_date) is pd.Timestamp, "Your end_date type is not True" \
                                                        ", It must be either Pandas.Timestamps or datetime.datetime"
        if type(end_date) is pd.Timestamp:
            try:
                end_date = pd.to_datetime(end_date, unit='D').to_pydatetime()
            except:
                try:
                    end_date = pd.to_datetime(end_date, unit='s').to_pydatetime()
                except:
                    print("Your timestamp doesn't seem to be valid for end_date.")
                    quit()
        elif type(end_date) is datetime.datetime:
            try:
                end_date = pd.to_datetime(end_date).to_pydatetime()
            except:
                print("Your datetime input for end_date doesn't seem to be valid.")
                quit()
        date_to = end_date
    result = None
    if date_from is not None and count is not None:
        print("ok")
        result = mt5.copy_rates_from(symbol_name, time_frame, date_from, count)

    elif start_position is not None and count is not None:
        print("dokay")
        result = mt5.copy_rates_from_pos(symbol_name, time_frame, start_position, count)

    elif date_from is not None and date_to is not None:
        print("sokay")
        result = mt5.copy_rates_range(symbol_name, time_frame, date_from, date_to)
    if result is None:
        error = mt5.last_error()
        if error[0] != 1:
            return error
        else:
            return result
    else:
        result = pd.DataFrame(result)
        result['time'] = pd.to_datetime(result['time'], unit='s')
        return result

# to place an order, first we should add symbol to market watch
# A market order is an order to buy or sell a security immediately.
# A limit order is an order to buy or sell a security at a specific price or better