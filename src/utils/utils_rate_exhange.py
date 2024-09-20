import requests
import logging
from src.constants.constants import currencies


def get_code_by_country(country: str) -> str:
    """Get country code with country."""
    return [item["code"] for item in currencies if item["country"] == country][0]


def get_trm(url: str) -> str:
    """Get trm with endpoint to cosume api"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        logging.info(response.json())
    except requests.exceptions.HTTPError as errh:
        logging.error(errh.response.json())
