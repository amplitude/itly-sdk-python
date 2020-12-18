from typing import Optional, Dict, Any

from itly_sdk import EventMetadata


class AmplitudeMetadata(EventMetadata):
    def __init__(self,
                 device_id: Optional[str] = None,
                 time: Optional[int] = None,
                 event_properties: Optional[Dict[str, Any]] = None,
                 user_properties: Optional[Dict[str, Any]] = None,
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
                 price: Optional[float] = None,
                 quantity: Optional[int] = None,
                 revenue: Optional[float] = None,
                 productId: Optional[str] = None,
                 revenueType: Optional[str] = None,
                 location_lat: Optional[float] = None,
                 location_lng: Optional[float] = None,
                 ip: Optional[str] = None,
                 idfa: Optional[str] = None,
                 idfv: Optional[str] = None,
                 adid: Optional[str] = None,
                 android_id: Optional[str] = None,
                 event_id: Optional[int] = None,
                 session_id: Optional[int] = None,
                 insert_id: Optional[str] = None,
                 ):
        self.device_id = device_id
        self.time = time
        self.event_properties = event_properties
        self.user_properties = user_properties
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
        self.price = price
        self.quantity = quantity
        self.revenue = revenue
        self.productId = productId
        self.revenueType = revenueType
        self.location_lat = location_lat
        self.location_lng = location_lng
        self.ip = ip
        self.idfa = idfa
        self.idfv = idfv
        self.adid = adid
        self.android_id = android_id
        self.event_id = event_id
        self.session_id = session_id
        self.insert_id = insert_id
