import logging
import pprint
from collections.abc import Generator

from .client import CUPToscanaClient
from .data.common import ListaPrescrizioni, RootResponse
from .data.disponibilita import (
    Appuntamento,
    Area,
    GetListaDisponibilitaPostRequest,
    GetListaDisponibilitaPostResponse,
)
from .data.prescrizione import GetPrescrizioneElettronicaRequest

logger = logging.getLogger(__name__)


def cerca_appuntamenti_per_area(
    client: CUPToscanaClient,
    listaPrescrizioni: ListaPrescrizioni | None = None,
    livelloSfogliamentoAree: int | None = None,
    cf: str | None = None,
) -> tuple[Area | None, list[Appuntamento]]:
    logger.info(f"cerca_appuntamenti_per_area(livelloSfogliamentoAree={livelloSfogliamentoAree})")
    data: RootResponse[GetListaDisponibilitaPostResponse] = client.get_lista_disponibilita(
        GetListaDisponibilitaPostRequest(
            calcoloOrari="ORARI_PRIMO_ORARIO",
            calcoloAppuntamenti="APP_DISP_UNO_PER_STRUTTURA",
            listaPrescrizioni=listaPrescrizioni,
            livelloSfogliamentoAree=livelloSfogliamentoAree,
            tipo="S" if livelloSfogliamentoAree else "R",
            cf=cf,
        )
    )

    if not data.message or data.message.level != "SUCCESS":
        raise RuntimeError(data.message.description if data.message else "Unknown error")

    if not data.response:
        raise RuntimeError("No server response")

    logger.debug(pprint.pformat(data.response.model_dump()))

    if not data.response.listaAppuntamenti or not data.response.listaAppuntamenti.appuntamento:
        raise RuntimeError("No appointment available")

    if not data.response.sfogliamentoAree:
        raise RuntimeError("Areas not available")

    if not data.response.sfogliamentoAree.attuale:
        raise RuntimeError("Current area not available")

    if not data.response.listaAppuntamenti:
        return data.response.sfogliamentoAree.successiva, []

    logger.info(
        f"attuale={data.response.sfogliamentoAree.attuale}, "
        f"successiva={data.response.sfogliamentoAree.successiva}, "
        f"appuntamenti={data.response.listaAppuntamenti.appuntamento}"
    )

    return (
        data.response.sfogliamentoAree.successiva,
        data.response.listaAppuntamenti.appuntamento,
    )


def cerca_appuntamenti(
    cf: str, nre: str, team_num: str, single_area: bool = False
) -> Generator[Appuntamento, None, None]:
    client = CUPToscanaClient()
    data = client.get_prescrizione_elettronica(
        GetPrescrizioneElettronicaRequest(cf=cf, nre=nre, numbersTeam=team_num)
    )

    if not data.message or data.message.level != "SUCCESS":
        raise RuntimeError(data.message.description if data.message else "Unknown error")

    if not data.response:
        raise RuntimeError("No server response")

    logger.debug(pprint.pformat(data.response.model_dump()))

    if not data.response.listaPrescrizioni or not data.response.listaPrescrizioni.prescrizione:
        raise RuntimeError("No prescription available")

    paziente_cf = data.response.paziente.codiceFiscale if data.response.paziente else None
    successiva = (
        None
        if single_area
        else Area(livello=2147483647, codice="ALL", descrizione="Area fittizia di ultimo livello")
    )  # set this to None to cycle all areas one by one
    while True:
        successiva, appuntamenti = cerca_appuntamenti_per_area(
            client=client,
            listaPrescrizioni=data.response.listaPrescrizioni,
            livelloSfogliamentoAree=successiva.livello if successiva else None,
            cf=paziente_cf,
        )
        yield from appuntamenti
        if not successiva:
            break
