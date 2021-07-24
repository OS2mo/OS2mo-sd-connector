# type: ignore
from abc import ABC
from abc import abstractmethod
from functools import lru_cache
from typing import Any

import httpx
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import AsyncClient
from zeep import Client
from zeep.cache import SqliteCache
from zeep.proxy import AsyncServiceProxy
from zeep.proxy import ServiceProxy
from zeep.transports import AsyncTransport
from zeep.transports import Transport


WSDL_PREFIX = "https://service.sd.dk/sdws/"
WSDLS = [
    "GetDepartment20080201WSDL",
    "xml/schema/sd.dk/xml.wsdl/20111201/GetDepartment20111201.wsdl",
    "xml/schema/sd.dk/xml.wsdl/20190701/GetDepartmentParent20190701.wsdl",
    "GetInstitution20080201WSDL",
    "xml/schema/sd.dk/xml.wsdl/20111201/GetInstitution20111201.wsdl",
    "GetOrganizationWSDL",
    "GetOrganization20080201WSDL",
    "xml/schema/sd.dk/xml.wsdl/20111201/GetOrganization20111201.wsdl",
    "GetEmployment20070401WSDL",
    "xml/schema/sd.dk/xml.wsdl/20111201/GetEmployment20111201.wsdl",
    "GetEmploymentChanged20070401WSDL",
    "xml/schema/sd.dk/xml.wsdl/20111201/GetEmploymentChanged20111201.wsdl",
    "GetEmploymentChangedAtDate20070401WSDL",
    "xml/schema/sd.dk/xml.wsdl/20111201/GetEmploymentChangedAtDate20111201.wsdl",
    "GetPersonWSDL",
    "xml/schema/sd.dk/xml.wsdl/20111201/GetPerson20111201.wsdl",
    "GetPersonChangedAtDateWSDL",
    "xml/schema/sd.dk/xml.wsdl/20111201/GetPersonChangedAtDate20111201.wsdl",
    "GetProfessionWSDL",
    "GetProfession20080201WSDL",
]


class SDSoapClientBase(ABC):
    """SOAP Client for SDs SOAP service.

    Dynamically loads endpoints based on SDs WSDL definitions in __init__.
    Thus __init__ does IO and may be slow.

    The list of endpoints which should be used are:

    Organization Endpoints:
    * GetDepartment20111201
    * GetDepartmentParent20190701
    * GetInstitution20111201
    * GetOrganization20111201

    Person and employment Endpoints:
    * GetEmployment20111201
    * GetEmploymentChanged20111201
    * GetEmploymentChangedAtDate20111201
    * GetPerson20111201
    * GetPersonChangedAtDate20111201

    Profession Endpoints:
    * GetProfession20080201

    A derived and more user-friendly client can be found in sd_connector.
    """

    def __init__(self, username: str, password: str):
        # Load our wsdls (specifying all endpoints) into the client
        for wsdl in WSDLS:
            client = self._create_client(WSDL_PREFIX + wsdl, username, password)
            service = client.service
            assert len(service._operations) == 1

            operation_name, operation = next(iter(service._operations.items()))
            method_name = operation_name.rstrip("Operation")

            assert hasattr(self, method_name) is False
            setattr(self, method_name, operation)

    @abstractmethod
    def _create_client(self, wsdl: str, username: str, password: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def _create_service_proxy(self, client: Any, binding: Any, **kwargs) -> Any:
        raise NotImplementedError


class AsyncSDSoapClient(SDSoapClientBase):
    """Async SOAP Client for SDs SOAP service.

    Using this client all endpoint are now async and must be awaited.
    Additionally `.aclose()` must be called to explicitly close the client.
    """

    @lru_cache(maxsize=None)
    def _create_async_client(self, username: str, password: str):
        self.httpx_client = httpx.AsyncClient(auth=(username, password), timeout=60)
        wsdl_client = httpx.Client(auth=(username, password), timeout=60)
        return self.httpx_client, wsdl_client

    def _create_client(self, wsdl: str, username: str, password: str) -> AsyncClient:
        httpx_client, wsdl_client = self._create_async_client(username, password)
        client = AsyncClient(
            wsdl,
            transport=AsyncTransport(
                client=httpx_client,
                wsdl_client=wsdl_client,
                cache=SqliteCache(),
                timeout=60,
            ),
        )
        return client

    def _create_service_proxy(self, client: AsyncClient, binding: Any, **kwargs) -> Any:
        return AsyncServiceProxy(client, binding, **kwargs)

    async def aclose(self):
        await self.httpx_client.aclose()


class SDSoapClient(SDSoapClientBase):
    """Sync SOAP Client for SDs SOAP service."""

    @lru_cache(maxsize=None)
    def _create_session(self, username: str, password: str) -> Session:
        session = Session()
        session.auth = HTTPBasicAuth(username, password)
        return session

    def _create_client(self, wsdl: str, username: str, password: str) -> Client:
        session = self._create_session(username, password)
        client = Client(
            wsdl, transport=Transport(session=session, cache=SqliteCache(), timeout=60)
        )
        return client

    def _create_service_proxy(self, client: Client, binding: Any, **kwargs) -> Any:
        return ServiceProxy(client, binding, **kwargs)
