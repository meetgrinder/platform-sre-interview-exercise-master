import asyncio
import datetime
from dateutil import tz
from fastapi import FastAPI, HTTPException
from fastapi_utils.tasks import repeat_every
# from http.client import HTTPException
import json
import logging
import os
import pytz
import requests
import sys
import uvicorn

currency_conversions_usd = {}
root_path = os.getenv('CURRENCY_API_PATH_PREFIX', '')
app = FastAPI()

conversion_base_cur = os.getenv('CONVERSION_BASE_CUR', 'usd')
conversion_rate_endpoint = os.getenv('CONVERSION_RATE_ENDPOINT',
                                     f'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{conversion_base_cur}.json')
converter_tz = os.getenv('CONVERTER_TIMEZONE', 'US/Eastern')
endpoint_recheck_period = os.getenv('ENDPOINT_RECHECK_PERIOD', 60)  # secs
serve_port = os.getenv('SERVE_PORT', 8000)

# setup basic stdout logging
allowed_log_levels = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 'WARNING': logging.WARNING, 'ERROR': logging.ERROR, 'CRITICAL': logging.CRITICAL}
logging_level = os.getenv('CURRENCY_API_LOG_LEVEL', logging.INFO)
if logging_level not in allowed_log_levels.keys():
    logging_level = logging.INFO

logger = logging.getLogger(__name__)
logger.setLevel(logging_level)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)


@app.get(root_path + "/v1/currencies")
async def get_currencies():
    print(f'logging_level: {logging_level}')
    print(f'logging.INFO: {logging.INFO}')
    usd_dict = currency_conversions_usd.get(conversion_base_cur)
    if not usd_dict:
        logging.error('get_currencies could not retrieve the base currency dict info')
        raise HTTPException(status_code=404, detail=f"currency conversion is experiencing issues")

    key_list = list(usd_dict.keys())
    logger.info(f'currency_list: {key_list}')
    return {"currency_list":  key_list}


@app.get(root_path + "/v1/rates/direct/{from_currency}/{to_currency}")
async def get_currency_rate(from_currency: str, to_currency: str):
    usd_dict = currency_conversions_usd.get(conversion_base_cur)
    if not usd_dict:
        logger.error('direct conversion could not retrieve the base currency dict')
        raise HTTPException(status_code=404, detail=f"currency conversion is experiencing issues")

    usd_from_currency = usd_dict.get(from_currency)
    if not usd_from_currency:
        logger.info(f'direct conversion from_currency {from_currency} not found')
        raise HTTPException(status_code=404, detail=f"from_currency {from_currency} not found")

    usd_to_currency = usd_dict.get(to_currency)
    if not usd_to_currency:
        logger.info(f'direct conversion to_currency {to_currency} not found')
        raise HTTPException(status_code=404, detail=f"to_currency {to_currency} not found")

    final_rate = usd_to_currency / usd_from_currency
    resp = {'from_currency': from_currency,
            'to_currency': to_currency,
            'rate': final_rate}

    logger.debug(f'sending response: {resp}')
    return resp


@app.get(root_path + "/v1/rates/synthetic/{from_currency}/{to_currency}")
async def get_synthetic_rate(from_currency: str, to_currency: str):
    usd_dict = currency_conversions_usd.get(conversion_base_cur)
    usd_from_currency = usd_dict.get(from_currency)
    usd_to_currency = usd_dict.get(to_currency)

    # TODO - need to refactor the key exist checking logic

    synth_rates = {'from_currency': from_currency,
                   'to_currency': to_currency}
    for thru_key, thru_val in usd_dict.items():
        if thru_key == from_currency or thru_key == to_currency:
            continue

        jump1 = thru_val / usd_from_currency
        jump2 = thru_val / usd_to_currency
        synth_rate = jump1 / jump2
        synth_resp_key = f'thru_{thru_key}'
        synth_rates[synth_resp_key] = synth_rate

    logger.debug(f'synth rate response: {synth_rates}')
    return synth_rates


@app.on_event("startup")
@repeat_every(seconds=endpoint_recheck_period)  # 1 min
def conversion_rates_checker() -> None:
    global currency_conversions_usd
    try:
        today = datetime.datetime.now(tz=tz.UTC)  # tz=tz.UTC
        ny_tz = pytz.timezone(converter_tz)
        today_tz = today.astimezone(ny_tz)
        today_date = today_tz.strftime('%Y-%m-%d')
        logger.info(f'{today_date}')

        # TODO - conversion_rate_endpoint.get('date') to see if the rates cache needs updating

        usd_rates_response = requests.get(conversion_rate_endpoint)
        usd_rates = usd_rates_response.content.decode('UTF-8')

        # TODO - informational checks to see if the currency list has changed

        logger.debug(f'{usd_rates}')
        currency_conversions_usd = json.loads(usd_rates)
    except:
        logger.error('exception trying to get rates')
        # traceback.format_exc()


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=int(serve_port), reload=True)
