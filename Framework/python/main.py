from optparse import Values
from pandas import read_csv as reader
from datetime import date
import re
import telepot
import configparser
import sys, os

def execute(path_to_config, path_to_download_folder, token, receiver_id) -> str:   
    try:
        global report_table
        report_table = reader(path_to_download_folder)
        message = define_message(path_to_config)
        send_to_telegram(message, token, receiver_id)
        return 'Success'
    except Exception as e:
        return str(e)


#Define the message to be send to a group of people
def define_message(path_to_config) -> str:
    try:
        config = read_config(path_to_config)
        global row_name
        row_name = config["Config"]["name_row"]
        price_column = config["Config"]["price_column"]
        value_column = config["Config"]["value_column"]
        diff_today_yesterday = config["Config"]["diff_today_yesterday"] + "%"
        tmk_name = config["Config"]["tmk_name"]
        brent_name = config["Config"]["brent_name"]
        wti_name = config["Config"]["wti_name"]
        rts_name = config["Config"]["rts_name"]
        usd_rub_name = config["Config"]["usd_rub_name"]
        eur_rub_name = config["Config"]["eur_rub_name"]
        message = config["Config"]["message"]
        count_shares_TMK = config["Config"]["count_shares_TMK"]
        time_column_name = config["Config"]["time_column_name"]
        today = date.today().strftime("%d.%m.%Y")

        #Define market is open or not 
        #Check date of last transaction sale of TMK. If the date has formal like HH:MM:SS then market was open 
        sale_date = report_table.loc[report_table[row_name] == tmk_name][time_column_name].values[0]
        if not re.search("\d{2}:\d{2}:\d{2}", sale_date):
            raise SystemExit

        share_price_TMK = get_value(tmk_name, price_column)
        value_TMK = get_value(tmk_name, value_column)
        diff_today_yesterday_tmk = get_value(tmk_name, diff_today_yesterday)
        value_traded = int(value_TMK.replace('.', '')) * float(share_price_TMK) / 1000000
        #round to 2 decimals
        value_traded = str(round(value_traded, 2))
        mcap = float(share_price_TMK) * int(count_shares_TMK) / 1000000000
        #round to 2 decimals
        mcap = str(round(mcap, 2))
        brant_oil_price = get_value(brent_name, price_column)
        diff_today_yesterday_brant = get_value(brent_name, diff_today_yesterday)
        wti_oil_price = get_value(wti_name, price_column)
        diff_today_yesterday_wti = get_value(wti_name, diff_today_yesterday)
        rtc_price = get_value(rts_name, price_column)
        if len(re.findall("\.", rtc_price)) == 2:
            rtc_price = rtc_price.replace(".", ",", 1)

        diff_today_yesterday_rtc = get_value(rts_name, diff_today_yesterday)
        usd_rub = get_value(usd_rub_name, price_column)
        diff_today_yesterday_usd_rub = get_value(usd_rub_name, diff_today_yesterday)
        eur_rub = get_value(eur_rub_name, price_column)
        diff_today_yesterday_eur_rub = get_value(eur_rub_name, diff_today_yesterday)

        return message.format(today, share_price_TMK, diff_today_yesterday_tmk, value_traded, mcap, brant_oil_price, 
                            diff_today_yesterday_brant, wti_oil_price, diff_today_yesterday_wti, 
                            rtc_price, diff_today_yesterday_rtc, round(float(eur_rub.replace(',','.')), 2), 
                            diff_today_yesterday_eur_rub, round(float(usd_rub.replace(',','.')), 2), 
                            diff_today_yesterday_usd_rub)   
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        raise Exception("Error occures during form the message - {} in line - {}".format(exc_type, exc_tb.tb_lineno))
    except SystemExit:
        raise Exception("Market is close!")


#read config file
def read_config(path_to_config):
    config = configparser.ConfigParser()
    config.read(path_to_config, encoding='utf-8')
    return config


def get_value(val_name, col_name) -> str:
    return str(report_table.loc[report_table[row_name] == val_name][col_name].values[0]).replace(',', '.')


def send_to_telegram(text, token, receiver_id):
    try:
        bot = telepot.Bot(token)
        bot.sendMessage(receiver_id, text)
    except:
        raise Exception("Error occures during sent the message")


