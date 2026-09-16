from typing import Any

from pydantic import Field

from .common import CamelCaseModel


class Enterprise(CamelCaseModel):
    sys_id: str
    title_enterprise: str = Field(alias="titleEnterprise")
    coordinate: str
    address: str
    info: str | None = None
    domain: str
    disponibilita: int
    extra: Any | None = None
    provincia: str
    regione: str | None = None


class Comune(CamelCaseModel):
    comune: str
    enterprises: list[Enterprise]


class ProvinceEnterprisesResponse(CamelCaseModel):
    province: str
    comunes: list[Comune]
