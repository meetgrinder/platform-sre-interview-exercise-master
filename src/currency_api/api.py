import asyncio
import datetime
from dateutil import tz
from fastapi import FastAPI, HTTPException
from fastapi_utils.tasks import repeat_every
# from http.client import HTTPException
import json
import os
import pytz
import requests
import uvicorn

root_path = os.getenv('CURRENCY_API_PATH_PREFIX', None)
app = FastAPI(root_path=root_path)

conversion_base_cur = os.getenv('CONVERSION_BASE_CUR', 'usd')
conversion_rate_endpoint = os.getenv('CONVERSION_RATE_ENDPOINT',
                                     f'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{conversion_base_cur}.json')
converter_tz = os.getenv('CONVERTER_TIMEZONE', 'US/Eastern')
endpoint_recheck_period = os.getenv('ENDPOINT_RECHECK_PERIOD', 60)  # secs
serve_port = os.getenv('SERVE_PORT', 8000)

currency_conversions_usd = {}


@app.get("/v1/currencies")
async def get_currencies():
    usd_dict = currency_conversions_usd.get(conversion_base_cur)
    key_list = list(usd_dict.keys())
    print(f'key_list: {key_list}')
    if not usd_dict:
        raise HTTPException(status_code=404, detail=f"currency conversion is experiencing issues")

    return {"currency_list":  key_list}


@app.get("/v1/rates/direct/{from_currency}/{to_currency}")
async def get_currency_rate(from_currency: str, to_currency: str):
    usd_dict = currency_conversions_usd.get(conversion_base_cur)
    if not usd_dict:
        raise HTTPException(status_code=404, detail=f"currency conversion is experiencing issues")

    usd_from_currency = usd_dict.get(from_currency)
    if not usd_from_currency:
        raise HTTPException(status_code=404, detail=f"from_currency {from_currency} not found")

    usd_to_currency = usd_dict.get(to_currency)
    if not usd_to_currency:
        raise HTTPException(status_code=404, detail=f"to_currency {to_currency} not found")

    final_rate = usd_to_currency / usd_from_currency
    resp = {'from_currency': from_currency,
            'to_currency': to_currency,
            'rate': final_rate}
    return resp


@app.get("/v1/rates/synthetic/{from_currency}/{to_currency}")
async def get_synthetic_rate(from_currency: str, to_currency: str):
    usd_dict = currency_conversions_usd.get(conversion_base_cur)
    usd_from_currency = usd_dict.get(from_currency)
    usd_to_currency = usd_dict.get(to_currency)
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
        print(f'{today_date}')

        # TODO - conversion_rate_endpoint.get('date') to see if the rates cache needs updating

        usd_rates_response = requests.get(conversion_rate_endpoint)
        usd_rates = usd_rates_response.content.decode('UTF-8')

        # TODO - informational checks to see if the currency list has changed

        print(f'{usd_rates}')
        currency_conversions_usd = json.loads(usd_rates)
    except:
        # todo - logging
        print('exception trying to get rates')
        # traceback.format_exc()


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=int(serve_port), reload=True)
