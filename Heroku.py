from typing import Union
import aiohttp
import glob
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
import uuid
import argparse

# Hi i only convert This scripts into OOP for learning purpose
# DM Telegram @Fxsihad



# issue arrived for aiohttp, asyncio 

class Heroku:
    _API_ENDPOINT = "https://api.heroku.com/account/payment-method/client-token"
    _PAYMENT_ENDPOINT = "https://api.stripe.com/v1/payment_methods"

    def __init__(self, card: str) -> None:
        self._card = card.split("|")
        self._cc = self._card[0]
        self._exp = self._card[1]
        self._year = self._card[2]
        self._cvv = self._card[3]

    async def __make_request(
        self, session, url, method="POST", headers=None, data=None
    ):
        async with session.request(method, url, headers=headers, data=data) as response:
            return await response.text()

    async def request_endpoint(self):
        guid = str(uuid.uuid4())
        muid = str(uuid.uuid4())
        sid = str(uuid.uuid4())

        async with aiohttp.ClientSession() as my_session:
            headers = {
                "accept": "application/vnd.heroku+json; version=3",
                "accept-language": "en-US,en;q=0.9",
                "authorization": "Bearer HRKU-074e250b-4966-4983-9f25-3101db1a7bac",  # You Can Change WIth Your Own Heroku API Key. https://dashboard.heroku.com/account
                "origin": "https://dashboard.heroku.com",
                "priority": "u=1, i",
                "referer": "https://dashboard.heroku.com/",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                "x-heroku-requester": "dashboard",
                "x-origin": "https://dashboard.heroku.com",
            }

            headers2 = {
                "accept": "application/json",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://js.stripe.com",
                "priority": "u=1, i",
                "referer": "https://js.stripe.com/",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            }

            data = {
                "type": "card",
                "billing_details[name]": "Ahmed Afnan",
                "billing_details[address][city]": "Anchorage",
                "billing_details[address][country]": "US",
                "billing_details[address][line1]": "245 W 5th Ave",
                "billing_details[address][postal_code]": "99501",
                "billing_details[address][state]": "AK",
                "card[number]": self._cc,
                "card[cvc]": self._cvv,
                "card[exp_month]": self._exp,
                "card[exp_year]": self._year,
                "guid": guid,
                "muid": muid,
                "sid": sid,
                "pasted_fields": "number",
                "payment_user_agent": "stripe.js/4b35ef0d67; stripe-js-v3/4b35ef0d67; split-card-element",
                "referrer": "https://dashboard.heroku.com",
                "time_on_page": "403570",
                "key": "pk_live_51KlgQ9Lzb5a9EJ3IaC3yPd1x6i9e6YW9O8d5PzmgPw9IDHixpwQcoNWcklSLhqeHri28drHwRSNlf6g22ZdSBBff002VQu6YLn",
            }

            try:
                req = await self.__make_request(
                    my_session, self._API_ENDPOINT, headers=headers
                )
                client_secret = self.parse_value(req, '"token":"', '"')

                req2 = await self.__make_request(
                    my_session, self._PAYMENT_ENDPOINT, headers=headers2, data=data
                )

                if "pm_" not in req2:
                    print("Error adding card:", req2)
                    return

                json_sec = json.loads(req2)
                pmid = json_sec["id"]
                piid = client_secret.split("_secret_")[0]

                headers3 = {
                    "accept": "application/json",
                    "accept-language": "en-US,en;q=0.9",
                    "content-type": "application/x-www-form-urlencoded",
                    "origin": "https://js.stripe.com",
                    "priority": "u=1, i",
                    "referer": "https://js.stripe.com/",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                }
                data3 = {
                    "payment_method": pmid,
                    "expected_payment_method_type": "card",
                    "use_stripe_sdk": "true",
                    "key": "pk_live_51KlgQ9Lzb5a9EJ3IaC3yPd1x6i9e6YW9O8d5PzmgPw9IDHixpwQcoNWcklSLhqeHri28drHwRSNlf6g22ZdSBBff002VQu6YLn",
                    "client_secret": client_secret,
                }

                req3 = await self.__make_request(
                    my_session,
                    f"https://api.stripe.com/v1/payment_intents/{piid}/confirm",
                    headers=headers3,
                    data=data3,
                )
                ljson = json.loads(req3)
                # print(ljson)

                if ljson.get("status") == "succeeded":
                    print("Card Added")
                else:
                    print("Payment error:", ljson.get("error", {}).get("message"))

            except Exception as e:
                print(f"Request failed: {e}")

    @staticmethod
    def parse_value(source, left: str, right: str) -> str:
        try:
            start = source.index(left) + len(left)
            end = source.index(right, start)
            return source[start:end]
        except ValueError:
            return None


async def task_concurently(cards):
    heroku_instance = Heroku(cards)
    await heroku_instance.request_endpoint()


async def main():
    parser = argparse.ArgumentParser(description="Heroku Card Adder!")
    parser.add_argument(
        "-p", "-Path", type=str, help="The path .txt files", required=True
    )
    parser.add_argument(
        "-t", "-Thread", type=int, help="Number of Threads To Use", default=5
    )
    args = parser.parse_args()
    # thread = int('THREAD: ')
    # path = glob.glob('*.txt')
    try:
        with open(args.p, "r") as file:
            cards = file.readlines()
            with ThreadPoolExecutor(max_workers=args.t) as executor:
                loop = asyncio.get_event_loop()
                task = [
                    await loop.run_in_executor(executor, task_concurently, card.strip())
                    for card in cards
                ]
                asyncio.gather(*task)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
