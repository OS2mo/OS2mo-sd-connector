# SPDX-FileCopyrightText: Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import datetime
from datetime import time
from functools import wraps
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union
from uuid import UUID

from sd_soap_client import AsyncSDSoapClient
from sd_soap_client import SDSoapClient
from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_exponential


def is_uuid(uuid: Union[str, UUID]) -> bool:
    if isinstance(uuid, UUID):
        return True

    try:
        UUID(uuid)
        return True
    except ValueError:
        return False
    except AttributeError as exp:
        print(exp)
        return False


def today() -> date:
    today = date.today()
    return today


def set_identifier(
    identifier: str, value: Optional[Union[str, UUID]], params: Dict[str, Any]
) -> Dict[str, Any]:
    if value is None:
        return params
    if is_uuid(value):
        params[identifier + "UUIDIdentifier"] = str(value)
    else:
        params[identifier + "Identifier"] = value
    return params


def set_dates(
    start_date: Optional[date],
    end_date: Optional[date],
    params: Dict[str, Any],
) -> Dict[str, Any]:
    start_date = start_date or today()
    end_date = end_date or today()
    params.update({"ActivationDate": start_date, "DeactivationDate": end_date})
    return params


def set_datetimes(
    start_datetime: Optional[datetime],
    end_datetime: Optional[datetime],
    params: Dict[str, Any],
) -> Dict[str, Any]:
    start_datetime = start_datetime or datetime.combine(today(), time(0, 0))
    end_datetime = end_datetime or datetime.combine(today(), time(23, 59, 59))
    params.update(
        {
            "ActivationDate": start_datetime.date(),
            "ActivationTime": start_datetime.time(),
            "DeactivationDate": end_datetime.date(),
            "DeactivationTime": end_datetime.time(),
        }
    )
    return params


def getDepartmentParams(
    institution_identifier: Optional[Union[str, UUID]] = None,
    department_identifier: Optional[Union[str, UUID]] = None,
    department_level_identifier: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    contact_information_indicator: bool = False,
    department_name_indicator: bool = True,
    employment_department_indicator: bool = False,
    postal_address_indicator: bool = False,
    production_unit_indicator: bool = False,
    uuid_indicator: bool = True,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "ContactInformationIndicator": contact_information_indicator,
        "DepartmentNameIndicator": department_name_indicator,
        "EmploymentDepartmentIndicator": employment_department_indicator,
        "PostalAddressIndicator": postal_address_indicator,
        "ProductionUnitIndicator": production_unit_indicator,
        "UUIDIndicator": uuid_indicator,
    }
    params = set_identifier("Institution", institution_identifier, params)
    params = set_identifier("Department", department_identifier, params)
    if department_level_identifier:
        params["DepartmentLevelIdentifier"] = department_level_identifier
    params = set_dates(start_date, end_date, params)
    return params


def getDepartmentParentParams(
    department_uuid_identifier: UUID,
    effective_date: Optional[date] = None,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "EffectiveDate": effective_date or today(),
        "DepartmentUUIDIdentifier": str(department_uuid_identifier),
    }
    return params


def getInstitutionParams(
    region_identifier: Optional[Union[str, UUID]] = None,
    institution_identifier: Optional[Union[str, UUID]] = None,
    administration_indicator: bool = False,
    contact_information_indicator: bool = False,
    postal_address_indicator: bool = False,
    production_unit_indicator: bool = False,
    uuid_indicator: bool = True,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "AdministrationIndicator": administration_indicator,
        "ContactInformationIndicator": contact_information_indicator,
        "PostalAddressIndicator": postal_address_indicator,
        "ProductionUnitIndicator": production_unit_indicator,
        "UUIDIndicator": uuid_indicator,
    }
    params = set_identifier("Region", region_identifier, params)
    params = set_identifier("Institution", institution_identifier, params)
    return params


def getOrganizationParams(
    institution_identifier: Optional[Union[str, UUID]] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    uuid_indicator: bool = True,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "UUIDIndicator": uuid_indicator,
    }
    params = set_identifier("Institution", institution_identifier, params)
    params = set_dates(start_date, end_date, params)
    return params


# @alias_param("person_civil_registration_identifier", "cpr_identifier")
def getEmploymentParams(
    institution_identifier: str,
    person_civil_registration_identifier: Optional[str] = None,
    employment_identifier: Optional[str] = None,
    department_identifier: Optional[str] = None,
    department_level_identifier: Optional[str] = None,
    effective_date: Optional[date] = None,
    status_active_indicator: bool = True,
    status_passive_indicator: bool = False,
    department_indicator: bool = True,
    employment_status_indicator: bool = True,
    profession_indicator: bool = True,
    salary_agreement_indicator: bool = False,
    salary_code_group_indicator: bool = False,
    working_time_indicator: bool = False,
    uuid_indicator: bool = True,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "InstitutionIdentifier": institution_identifier,
        "PersonCivilRegistrationIdentifier": person_civil_registration_identifier,
        "EmploymentIdentifier": employment_identifier,
        "DepartmentIdentifier": department_identifier,
        "EffectiveDate": effective_date or today(),
        "StatusActiveIndicator": status_active_indicator,
        "StatusPassiveIndicator": status_passive_indicator,
        "DepartmentIndicator": department_indicator,
        "EmploymentStatusIndicator": employment_status_indicator,
        "ProfessionIndicator": profession_indicator,
        "SalaryAgreementIndicator": salary_agreement_indicator,
        "SalaryCodeGroupIndicator": salary_code_group_indicator,
        "WorkingTimeIndicator": working_time_indicator,
        "UUIDIndicator": uuid_indicator,
    }
    if department_level_identifier:
        params["DepartmentLevelIdentifier"] = department_level_identifier
    return params


def getEmploymentChangedParams(
    institution_identifier: str,
    person_civil_registration_identifier: Optional[str] = None,
    employment_identifier: Optional[str] = None,
    department_identifier: Optional[str] = None,
    department_level_identifier: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    department_indicator: bool = True,
    employment_status_indicator: bool = True,
    profession_indicator: bool = True,
    salary_agreement_indicator: bool = False,
    salary_code_group_indicator: bool = False,
    working_time_indicator: bool = False,
    uuid_indicator: bool = True,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "InstitutionIdentifier": institution_identifier,
        "PersonCivilRegistrationIdentifier": person_civil_registration_identifier,
        "EmploymentIdentifier": employment_identifier,
        "DepartmentIdentifier": department_identifier,
        "DepartmentIndicator": department_indicator,
        "EmploymentStatusIndicator": employment_status_indicator,
        "ProfessionIndicator": profession_indicator,
        "SalaryAgreementIndicator": salary_agreement_indicator,
        "SalaryCodeGroupIndicator": salary_code_group_indicator,
        "WorkingTimeIndicator": working_time_indicator,
        "UUIDIndicator": uuid_indicator,
    }
    if department_level_identifier:
        params["DepartmentLevelIdentifier"] = department_level_identifier
    params = set_dates(start_date, end_date, params)
    return params


def getEmploymentChangedAtDateParams(
    institution_identifier: str,
    person_civil_registration_identifier: Optional[str] = None,
    employment_identifier: Optional[str] = None,
    department_identifier: Optional[str] = None,
    department_level_identifier: Optional[str] = None,
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None,
    department_indicator: bool = True,
    employment_status_indicator: bool = True,
    profession_indicator: bool = True,
    salary_agreement_indicator: bool = False,
    salary_code_group_indicator: bool = False,
    working_time_indicator: bool = False,
    uuid_indicator: bool = True,
    future_information_indicator: bool = False,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "InstitutionIdentifier": institution_identifier,
        "PersonCivilRegistrationIdentifier": person_civil_registration_identifier,
        "EmploymentIdentifier": employment_identifier,
        "DepartmentIdentifier": department_identifier,
        "DepartmentIndicator": department_indicator,
        "EmploymentStatusIndicator": employment_status_indicator,
        "ProfessionIndicator": profession_indicator,
        "SalaryAgreementIndicator": salary_agreement_indicator,
        "SalaryCodeGroupIndicator": salary_code_group_indicator,
        "WorkingTimeIndicator": working_time_indicator,
        "UUIDIndicator": uuid_indicator,
        "FutureInformationIndicator": future_information_indicator,
    }
    if department_level_identifier:
        params["DepartmentLevelIdentifier"] = department_level_identifier
    params = set_datetimes(start_datetime, end_datetime, params)
    return params


def getPersonParams(
    institution_identifier: str,
    person_civil_registration_identifier: Optional[str] = None,
    employment_identifier: Optional[str] = None,
    department_identifier: Optional[str] = None,
    department_level_identifier: Optional[str] = None,
    effective_date: Optional[date] = None,
    status_active_indicator: bool = True,
    status_passive_indicator: bool = False,
    contact_information_indicator: bool = False,
    postal_address_indicator: bool = False,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "InstitutionIdentifier": institution_identifier,
        "PersonCivilRegistrationIdentifier": person_civil_registration_identifier,
        "EmploymentIdentifier": employment_identifier,
        "DepartmentIdentifier": department_identifier,
        "EffectiveDate": effective_date or today(),
        "StatusActiveIndicator": status_active_indicator,
        "StatusPassiveIndicator": status_passive_indicator,
        "ContactInformationIndicator": contact_information_indicator,
        "PostalAddressIndicator": postal_address_indicator,
    }
    if department_level_identifier:
        params["DepartmentLevelIdentifier"] = department_level_identifier
    return params


def getPersonChangedAtDateParams(
    institution_identifier: str,
    person_civil_registration_identifier: Optional[str] = None,
    employment_identifier: Optional[str] = None,
    department_identifier: Optional[str] = None,
    department_level_identifier: Optional[str] = None,
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None,
    contact_information_indicator: bool = False,
    postal_address_indicator: bool = False,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "InstitutionIdentifier": institution_identifier,
        "PersonCivilRegistrationIdentifier": person_civil_registration_identifier,
        "EmploymentIdentifier": employment_identifier,
        "DepartmentIdentifier": department_identifier,
        "ContactInformationIndicator": contact_information_indicator,
        "PostalAddressIndicator": postal_address_indicator,
    }
    if department_level_identifier:
        params["DepartmentLevelIdentifier"] = department_level_identifier
    params = set_datetimes(start_datetime, end_datetime, params)
    return params


def getProfessionParams(
    institution_identifier: str,
    job_position_identifier: Optional[str] = None,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "InstitutionIdentifier": institution_identifier,
        "JobPositionIdentifier": job_position_identifier,
    }
    return params


class AsyncSDConnector:
    def __init__(
        self,
        username: str,
        password: str,
    ):
        self.asoap_client = AsyncSDSoapClient(username, password)

    async def aclose(self) -> None:
        await self.asoap_client.aclose()

    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=2, min=1),
        stop=stop_after_attempt(7),
    )
    async def call_soap(self, endpoint: str, params: Dict[str, Any]) -> Any:
        return await getattr(self.asoap_client, endpoint)(**params)

    # Organization
    # -------------
    @wraps(getDepartmentParams)
    async def getDepartment(self, *args: Any, **kwargs: Any) -> Any:
        params = getDepartmentParams(*args, **kwargs)
        return await self.call_soap("GetDepartment20111201", params)

    @wraps(getDepartmentParentParams)
    async def getDepartmentParent(self, *args: Any, **kwargs: Any) -> Any:
        params = getDepartmentParentParams(*args, **kwargs)
        return await self.call_soap("GetDepartmentParent20190701", params)

    @wraps(getInstitutionParams)
    async def getInstitution(self, *args: Any, **kwargs: Any) -> Any:
        params = getInstitutionParams(*args, **kwargs)
        return await self.call_soap("GetInstitution20111201", params)

    @wraps(getOrganizationParams)
    async def getOrganization(self, *args: Any, **kwargs: Any) -> Any:
        params = getOrganizationParams(*args, **kwargs)
        return await self.call_soap("GetOrganization20111201", params)

    # Person and employment
    # ----------------------
    @wraps(getEmploymentParams)
    async def getEmployment(self, *args: Any, **kwargs: Any) -> Any:
        params = getEmploymentParams(*args, **kwargs)
        return await self.call_soap("GetEmployment20111201", params)

    @wraps(getEmploymentChangedParams)
    async def getEmploymentChanged(self, *args: Any, **kwargs: Any) -> Any:
        params = getEmploymentChangedParams(*args, **kwargs)
        return await self.call_soap("GetEmploymentChanged20111201", params)

    @wraps(getEmploymentChangedAtDateParams)
    async def getEmploymentChangedAtDate(self, *args: Any, **kwargs: Any) -> Any:
        params = getEmploymentChangedAtDateParams(*args, **kwargs)
        return await self.call_soap("GetEmploymentChangedAtDate20111201", params)

    @wraps(getPersonParams)
    async def getPerson(self, *args: Any, **kwargs: Any) -> Any:
        params = getPersonParams(*args, **kwargs)
        return await self.call_soap("GetPerson20111201", params)

    @wraps(getPersonChangedAtDateParams)
    async def getPersonChangedAtDate(self, *args: Any, **kwargs: Any) -> Any:
        params = getPersonChangedAtDateParams(*args, **kwargs)
        return await self.call_soap("GetPersonChangedAtDate20111201", params)

    # Profession
    # -----------
    @wraps(getProfessionParams)
    async def getProfession(self, *args: Any, **kwargs: Any) -> Any:
        params = getProfessionParams(*args, **kwargs)
        return await self.call_soap("GetProfession20080201", params)


class SDConnector:
    def __init__(
        self,
        username: str,
        password: str,
    ):
        self.soap_client = SDSoapClient(username, password)

    #    @retry(
    #        reraise=True,
    #        wait=wait_exponential(multiplier=2, min=1),
    #        stop=stop_after_attempt(7),
    #    )
    def call_soap(self, endpoint: str, params: Dict[str, Any]) -> Any:
        return getattr(self.soap_client, endpoint)(**params)

    # Organization
    # -------------
    @wraps(getDepartmentParams)
    def getDepartment(self, *args: Any, **kwargs: Any) -> Any:
        params = getDepartmentParams(*args, **kwargs)
        return self.call_soap("GetDepartment20111201", params)

    @wraps(getDepartmentParentParams)
    def getDepartmentParent(self, *args: Any, **kwargs: Any) -> Any:
        params = getDepartmentParentParams(*args, **kwargs)
        return self.call_soap("GetDepartmentParent20190701", params)

    @wraps(getInstitutionParams)
    def getInstitution(self, *args: Any, **kwargs: Any) -> Any:
        params = getInstitutionParams(*args, **kwargs)
        return self.call_soap("GetInstitution20111201", params)

    @wraps(getOrganizationParams)
    def getOrganization(self, *args: Any, **kwargs: Any) -> Any:
        params = getOrganizationParams(*args, **kwargs)
        return self.call_soap("GetOrganization20111201", params)

    # Person and employment
    # ----------------------
    @wraps(getEmploymentParams)
    def getEmployment(self, *args: Any, **kwargs: Any) -> Any:
        params = getEmploymentParams(*args, **kwargs)
        return self.call_soap("GetEmployment20111201", params)

    @wraps(getEmploymentChangedParams)
    def getEmploymentChanged(self, *args: Any, **kwargs: Any) -> Any:
        params = getEmploymentChangedParams(*args, **kwargs)
        return self.call_soap("GetEmploymentChanged20111201", params)

    @wraps(getEmploymentChangedAtDateParams)
    def getEmploymentChangedAtDate(self, *args: Any, **kwargs: Any) -> Any:
        params = getEmploymentChangedAtDateParams(*args, **kwargs)
        return self.call_soap("GetEmploymentChangedAtDate20111201", params)

    @wraps(getPersonParams)
    def getPerson(self, *args: Any, **kwargs: Any) -> Any:
        params = getPersonParams(*args, **kwargs)
        return self.call_soap("GetPerson20111201", params)

    @wraps(getPersonChangedAtDateParams)
    def getPersonChangedAtDate(self, *args: Any, **kwargs: Any) -> Any:
        params = getPersonChangedAtDateParams(*args, **kwargs)
        return self.call_soap("GetPersonChangedAtDate20111201", params)

    # Profession
    # -----------
    @wraps(getProfessionParams)
    def getProfession(self, *args: Any, **kwargs: Any) -> Any:
        params = getProfessionParams(*args, **kwargs)
        return self.call_soap("GetProfession20080201", params)
