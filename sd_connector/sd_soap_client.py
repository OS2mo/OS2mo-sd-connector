# type: ignore
from abc import ABC
from abc import abstractmethod
from functools import partial
from functools import lru_cache
from io import StringIO
from typing import Any
from typing import Callable
from typing import Iterator
from typing import Tuple

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


WSDLS = [
    "https://service.sd.dk/sdws/GetDepartment20080201WSDL",
    "https://service.sd.dk/sdws/xml/schema/sd.dk/xml.wsdl/20111201/GetDepartment20111201.wsdl",
    "https://service.sd.dk/sdws/xml/schema/sd.dk/xml.wsdl/20190701/GetDepartmentParent20190701.wsdl",
    "https://service.sd.dk/sdws/GetInstitution20080201WSDL",
    "https://service.sd.dk/sdws/xml/schema/sd.dk/xml.wsdl/20111201/GetInstitution20111201.wsdl",
    "https://service.sd.dk/sdws/GetOrganizationWSDL",
    "https://service.sd.dk/sdws/GetOrganization20080201WSDL",
    "https://service.sd.dk/sdws/xml/schema/sd.dk/xml.wsdl/20111201/GetOrganization20111201.wsdl",
    "https://service.sd.dk/sdws/GetEmployment20070401WSDL",
    "https://service.sd.dk/sdws/xml/schema/sd.dk/xml.wsdl/20111201/GetEmployment20111201.wsdl",
    "https://service.sd.dk/sdws/GetEmploymentChanged20070401WSDL",
    "https://service.sd.dk/sdws/xml/schema/sd.dk/xml.wsdl/20111201/GetEmploymentChanged20111201.wsdl",
    "https://service.sd.dk/sdws/GetEmploymentChangedAtDate20070401WSDL",
    "https://service.sd.dk/sdws/xml/schema/sd.dk/xml.wsdl/20111201/GetEmploymentChangedAtDate20111201.wsdl",
    "https://service.sd.dk/sdws/GetPersonWSDL",
    "https://service.sd.dk/sdws/xml/schema/sd.dk/xml.wsdl/20111201/GetPerson20111201.wsdl",
    "https://service.sd.dk/sdws/GetPersonChangedAtDateWSDL",
    "https://service.sd.dk/sdws/xml/schema/sd.dk/xml.wsdl/20111201/GetPersonChangedAtDate20111201.wsdl",
    "https://service.sd.dk/sdws/GetProfessionWSDL",
    "https://service.sd.dk/sdws/GetProfession20080201WSDL",
]

class SDSoapClientBase(ABC):
    """SOAP Client for SDs SOAP service.

    Dynamically loads endpoints based on SDs WSDL definitions in __init__, thus
    endpoints could dynamically appear and disappear over time.

    This is mainly a theoretical point, as endpoints are pretty static.
    The endpoints are versioned using dates, and only the newest endpoints should
    be used, thus the list of endpoints reduce to the following:

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

    A derived and more user-friendly client should probably be developed.
    """

    def __init__(self, username: str, password: str):
        # Load our wsdls (specifying all endpoints) into the client
        for wsdl in WSDLS:
            client = self._create_client(wsdl, username, password)
            service = client.service
            assert len(service._operations) == 1

            operation_name, operation = next(iter(service._operations.items()))
            method_name = operation_name.rstrip("Operation")

            assert hasattr(self, method_name) is False
            setattr(self, method_name, operation)

    @abstractmethod
    def _create_client(self, wsdl: StringIO, username: str, password: str) -> Any:
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
        self.httpx_client = httpx.AsyncClient(auth=(username, password))
        wsdl_client = httpx.Client(auth=(username, password))
        return self.httpx_client, wsdl_client

    def _create_client(
        self, wsdl: StringIO, username: str, password: str
    ) -> AsyncClient:
        httpx_client, wsdl_client = self._create_async_client(username, password)
        client = AsyncClient(
            wsdl, transport=AsyncTransport(client=httpx_client, wsdl_client=wsdl_client, cache=SqliteCache())
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

    def _create_client(self, wsdl: StringIO, username: str, password: str) -> Client:
        session = self._create_session(username, password)
        client = Client(wsdl, transport=Transport(session=session, cache=SqliteCache()))
        return client

    def _create_service_proxy(self, client: Client, binding: Any, **kwargs) -> Any:
        return ServiceProxy(client, binding, **kwargs)


if __name__ == "__main__":
    import click
    from ra_utils.async_to_sync import async_to_sync

    @click.command()
    @click.option(
        "--username",
        required=True,
        help="SD username",
    )
    @click.option(
        "--password",
        required=True,
        help="SD password",
        prompt=True,
        hide_input=True,
    )
    @click.option(
        "--institution-identifier",
        required=True,
        help="SD identifier for the institution",
    )
    @async_to_sync
    async def main(username: str, password: str, institution_identifier: str):
        params = {
            "InstitutionIdentifier": institution_identifier,
            "AdministrationIndicator": False,
            "ContactInformationIndicator": False,
            "PostalAddressIndicator": False,
            "ProductionUnitIndicator": False,
            "UUIDIndicator": True,
        }
        soap_client = SDSoapClient(username, password)
        result = soap_client.GetInstitution20111201(**params)
        print(result)

        asoap_client = AsyncSDSoapClient(username, password)
        result = await asoap_client.GetInstitution20111201(**params)
        await asoap_client.aclose()
        print(result)

    main()
