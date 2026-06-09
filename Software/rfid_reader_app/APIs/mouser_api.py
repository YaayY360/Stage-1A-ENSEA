import requests

MOUSER_API_KEY="3bb4d1f3-9ee2-458d-ba45-839175385dad"
MOUSER_API_URL="https://api.mouser.com/api/v1/search/partnumber"

def get_component_info(mpn :str):
    payload = {
        "SearchByPartRequest":{
            "mouserPartNumber": mpn,
            "partSearchOptions": "string"
            }
        }