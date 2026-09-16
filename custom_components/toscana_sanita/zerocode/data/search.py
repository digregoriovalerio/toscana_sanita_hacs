from datetime import datetime
from typing import Any

from pydantic import Field

from .common import CamelCaseModel


class SearchRequest(CamelCaseModel):
    phone_number: str = Field(alias="phoneNumber")
    tax_code: str = Field(alias="taxCode")
    nre: list[str]


class SearchUserData(CamelCaseModel):
    fiscal_code: str = Field(alias="fiscalCode")
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    phone_number: str | None = Field(None, alias="phoneNumber")
    email: str | None = None
    nre: list[str]
    reserved_by_cf: str | None = Field(None, alias="reservedByCf")
    selected_service: str | None = Field(None, alias="selectedService")


class Prestazione(CamelCaseModel):
    id: str | None = None
    codice: str | None = None
    codice_catalogo_regionale: str | None = Field(None, alias="codiceCatalogoRegionale")
    codice_nomenclatore_regionale: str | None = Field(None, alias="codiceNomenclatoreRegionale")
    descrizione_nomenclatore_regionale: str | None = Field(
        None, alias="descrizioneNomenclatoreRegionale"
    )


class SearchResponse(CamelCaseModel):
    id: str
    user_data: SearchUserData = Field(alias="userData")
    time: datetime
    lista_disponibilita: Any | None = Field(None, alias="listaDisponibilita")
    service: Any | None = None
    id_richiesta_lis: str | None = Field(None, alias="idRichiestaLis")
    selected_service: str | None = Field(None, alias="selectedService")
    queue_id: str | None = Field(None, alias="queueId")
    queue_remote: Any | None = Field(None, alias="queueRemote")
    selected_prefix: str | None = Field(None, alias="selectedPrefix")
    dati_prestazioni: dict[str, list[Prestazione]] = Field(
        default_factory=dict, alias="datiPrestazioni"
    )
