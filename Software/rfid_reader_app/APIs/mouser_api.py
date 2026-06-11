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
    params= {"apiKey" : MOUSER_API_KEY}
    
# Requête API mouser stockée dans data 
    response = requests.post(MOUSER_API_URL, json=payload, params=params)
    data = response.json() 
    
    parts = data.get("SearchResults", {}).get("Parts", [])
    if not parts:
        return None
    
    part=parts[0] #sélectionne les infos de la première section 
    return {
        "mpn":          part.get("ManufacturerPartNumber"),
        "manufacturer": part.get("Manufacturer"),
        "description":  part.get("Description"),
        "datasheet":    part.get("DataSheetUrl"),
        "price_ht":     _extract_price(part.get("PriceBreaks", [])),
        "supplier_pn":  part.get("MouserPartNumber"),
    }

def _extract_price(price_breaks: list) -> float:
    #Retourne le prix unitaire pour Quantity=1
    if not price_breaks:
        return None
    return float(price_breaks[0].get("Price", "0").replace(",", ".").replace("€", "").strip())