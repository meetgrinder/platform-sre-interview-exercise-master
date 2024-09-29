from fastapi import FastAPI
import asyncio
from fastapi_utils.tasks import repeat_every
import requests
import datetime
from dateutil import tz
import pytz
import traceback
import json
import uvicorn


app = FastAPI()

conversion_rate_endpoint = 'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json'
converter_tz = 'America/New_York'

currency_conversions_usd = {}
conversion_update_time = None

# TODO - consider putting this in the conv endpoint url but depends upon how thats passed into the service as configmap
conversion_base_cur = 'usd'
endpoint_recheck_period = 60 # in seconds

@app.get("/v1/currencies")
async def get_currencies():

    return {"message": "hello"}

@app.get("/v1/rates/direct/{from_currency}/{to_currency}")
async def get_currency_rate(from_currency:str, to_currency:str):
    usd_dict = currency_conversions_usd.get(conversion_base_cur)
    usd_from_currency = usd_dict.get(from_currency)
    usd_to_currency = usd_dict.get(to_currency)
    final_rate = usd_to_currency/usd_from_currency
    resp = {'from_currency': from_currency,
            'to_currency': to_currency,
            'rate': final_rate}
    return resp

@app.get("/v1/rates/synthetic/{from_currency}/{to_currency}")
async def get_synthetic_rate(from_currency:str, to_currency:str):
    usd_dict = currency_conversions_usd.get(conversion_base_cur)
    usd_from_currency = usd_dict.get(from_currency)
    usd_to_currency = usd_dict.get(to_currency)
    thru = usd_dict.get('jpy')
    jump1 = thru/usd_from_currency
    jump2 = thru/usd_to_currency
    final_rate = jump1/jump2
    return {"syn1 thru jpy": final_rate}

@app.on_event("startup")
@repeat_every(seconds=endpoint_recheck_period)  # 1 min
def conversion_rates_checker() -> None:
    global currency_conversions_usd

    try:
        today = datetime.datetime.now(tz=tz.UTC)  # tz=tz.UTC
        ny_tz = pytz.timezone('US/Eastern')
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
        #todo - logging
        print('exception trying to get rates')
        # traceback.format_exc()


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

