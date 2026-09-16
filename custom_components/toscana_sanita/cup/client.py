import json
import logging
import pprint

import requests

from .data.common import RootResponse
from .data.disponibilita import (
    GetListaDisponibilitaPostRequest,
    GetListaDisponibilitaPostResponse,
)
from .data.prescrizione import (
    GetPrescrizioneElettronicaRequest,
    GetPrescrizioneElettronicaResponse,
)

logger = logging.getLogger(__name__)


class CUPToscanaClient:
    BASE_URL = "https://prenota.sanita.toscana.it/sis-portalepren/sis-portale-prenotazione/sis-portale-prenotazione"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "it-IT,it;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6",
                "Connection": "keep-alive",
                "DNT": "1",
                "Host": "prenota.sanita.toscana.it",
                "Referer": "https://prenota.sanita.toscana.it/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/152.0.0.0 Safari/537.36"
                ),
                "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
            }
        )
        self.session.cookies.set("cookieModale", "true", domain="prenota.sanita.toscana.it")

    def get_prescrizione_elettronica(
        self, request: GetPrescrizioneElettronicaRequest
    ) -> RootResponse[GetPrescrizioneElettronicaResponse]:
        params = request.model_dump(by_alias=True)
        logger.debug(pprint.pformat(params))
        url = f"{self.BASE_URL}/getPrescrizioneElettronica"
        response = self.session.get(url, params=params, timeout=15.0)
        logger.debug(pprint.pformat(response.content))
        response.raise_for_status()
        return RootResponse[GetPrescrizioneElettronicaResponse].model_validate(response.json())

    def get_lista_disponibilita(
        self, request: GetListaDisponibilitaPostRequest
    ) -> RootResponse[GetListaDisponibilitaPostResponse]:
        lista_prescrizioni = (
            request.listaPrescrizioni.model_dump(by_alias=True)
            if request.listaPrescrizioni is not None
            else None
        )

        body_payload = {
            "listaPrescrizioni": lista_prescrizioni,
            "calcoloOrari": request.calcoloOrari,
            "calcoloAppuntamenti": request.calcoloAppuntamenti,
            "tipo": request.tipo,
        }
        if request.livelloSfogliamentoAree is not None:
            body_payload["livelloSfogliamentoAree"] = request.livelloSfogliamentoAree
        body = json.dumps(body_payload, separators=(",", ":"))
        logger.debug(pprint.pformat(json.loads(body)))
        endpoint = f"{self.BASE_URL}/getListaDisponibilitaPost"
        headers = {
            "Origin": "https://prenota.sanita.toscana.it",
            "cf": request.cf or "",
            "Content-Type": "application/json",
            "Content-Length": str(len(body.encode("utf-8"))),
        }
        response = self.session.post(endpoint, data=body, headers=headers, timeout=15.0)
        logger.debug(pprint.pformat(response.content))
        response.raise_for_status()
        return RootResponse[GetListaDisponibilitaPostResponse].model_validate(response.json())
