import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))

    # NOTE: return error "Response is not valid 'application/json'" if not sending API KEY and DB URL
    # One solution is to define them as parameters directly in the definition of the function

    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(
            url, headers={"Content-Type": "application/json"}, params=kwargs
        )
    except:
        print("Network exception occurred")

    status_code = response.status_code
    print("With status {} ".format(status_code))

    json_data = json.loads(response.text)

    return json_data


# Create a `post_request` to make HTTP POST requests
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    print(json_payload)

    response = requests.post(url, params=kwargs, json=json_payload)

    status_code = response.status_code
    print("With Status {}".format(status_code))

    json_data = json.loads(response.text)

    return json_data


def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url, **kwargs)

    # print("JSON:", json_result)

    if "error" in json_result:
        raise Exception("An error has occurred:" + json_result["error"])

    if json_result:
        # Get the row list in JSON as dealers
        # dealers = json_result["rows"]

        for dealer_doc in json_result["result"]:
            # dealer_doc = dealer["doc"]

            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(
                address=dealer_doc["address"],
                city=dealer_doc["city"],
                full_name=dealer_doc["full_name"],
                id=dealer_doc["id"],
                lat=dealer_doc["lat"],
                long=dealer_doc["long"],
                short_name=dealer_doc["short_name"],
                st=dealer_doc["st"],
                zip=dealer_doc["zip"]
            )

            results.append(dealer_obj)

    return results


def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    json_result = get_request(url, dealerId=dealer_id)

    # print("JSON:", json_result)

    if "error" in json_result:
        raise Exception("An error has occurred:" + json_result["error"])

    if json_result:
        reviews = json_result["body"]["data"]["docs"]

        for review in reviews:
            sentiment = analyze_review_sentiments(review["review"])

            review_obj = DealerReview(
                dealership=review["dealership"],
                name=review["name"],
                purchase=review["purchase"],
                review=review["review"],
                purchase_date=review["purchase_date"],
                car_make=review["car_make"],
                car_model=review["car_model"],
                car_year=review["car_year"],
                sentiment=sentiment.strip('"'),
                id=review["id"],
            )
            results.append(review_obj)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
    api_key = "qZczlavBeZP1sRicJ2tFv-52bxvzYzUNn7sAIndwHHDn"
    api_url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/6dbbfc44-21ce-430b-8e47-3dcc1127e6c6"

    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version="2022-11-24", authenticator=authenticator
    )
    natural_language_understanding.set_service_url(api_url)

    response = natural_language_understanding.analyze(
        text=text,
        features=Features(
            # sentiment=SentimentOptions(model="sentiment-analysis-en-v1")
            sentiment=SentimentOptions()
        ),
        language="en",
    ).get_result()

    return response["sentiment"]["document"]["label"]