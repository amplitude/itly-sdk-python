from typing import Optional, Dict, Any

from itly_sdk import EventMetadata


class AmplitudeMetadata(EventMetadata):
    def __init__(self,
                 device_id: Optional[str] = None,
                 groups: Optional[Dict[str, Any]] = None,
                 app_version: Optional[str] = None,
                 platform: Optional[str] = None,
                 os_name: Optional[str] = None,
                 os_version: Optional[str] = None,
                 device_brand: Optional[str] = None,
                 device_manufacturer: Optional[str] = None,
                 device_model: Optional[str] = None,
                 carrier: Optional[str] = None,
                 country: Optional[str] = None,
                 region: Optional[str] = None,
                 city: Optional[str] = None,
                 dma: Optional[str] = None,
                 language: Optional[str] = None,
                 ):
        self.device_id = device_id
        self.groups = groups
        self.app_version = app_version
        self.platform = platform
        self.os_name = os_name
        self.os_version = os_version
        self.device_brand = device_brand
        self.device_manufacturer = device_manufacturer
        self.device_model = device_model
        self.carrier = carrier
        self.country = country
        self.region = region
        self.city = city
        self.dma = dma
        self.language = language

    @staticmethod
    def merge(first: Optional["AmplitudeMetadata"], second: Optional["AmplitudeMetadata"]) -> Optional["AmplitudeMetadata"]:
        if first is None and second is None:
            return None

        first_data = {k: v for (k, v) in vars(first).items() if v is not None} if first is not None else {}
        second_data = {k: v for (k, v) in vars(second).items() if v is not None} if second is not None else {}
        return AmplitudeMetadata(**{**first_data, **second_data})
