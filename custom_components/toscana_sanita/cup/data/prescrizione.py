from typing import Any

from pydantic import BaseModel, ConfigDict

from .common import ListaPrescrizioni, ResponseData


class TesseraTeam(BaseModel):
    model_config = ConfigDict(extra="ignore")
    numeroTessera: str | None = None
    numeroPersonale: str | None = None
    numeroIstituzione: str | None = None
    dataScadenza: str | None = None
    idSiglaNazione: str | None = None
    siglaNazione: str | None = None


class Paziente(BaseModel):
    model_config = ConfigDict(extra="ignore")
    siglaRegole: Any | None = None
    idPaziente: str | None = None
    idPazienteSGP: str | None = None
    idPazienteCUP: str | None = None
    nome: str | None = None
    cognome: str | None = None
    dataNascita: str | None = None
    idComuneNascita: str | None = None
    comuneNascita: str | None = None
    comuneNascitaDesc: str | None = None
    sesso: str | None = None
    codiceFiscale: str | None = None
    indirizzoDomicilio: str | None = None
    idComuneDomicilio: str | None = None
    comuneDomicilio: str | None = None
    comuneDomicilioDesc: str | None = None
    capDomicilio: str | None = None
    indirizzoResidenza: str | None = None
    idComuneResidenza: str | None = None
    comuneResidenza: str | None = None
    comuneResidenzaDesc: str | None = None
    capResidenza: str | None = None
    idAslAppartenenza: str | None = None
    aslAppartenenza: str | None = None
    aslAppartenenzaDesc: str | None = None
    idAslAssistenza: str | None = None
    aslAssistenza: str | None = None
    aslAssistenzaDesc: str | None = None
    idCittadinanza: str | None = None
    cittadinanza: str | None = None
    cittadinanzaDesc: str | None = None
    tel1: str | None = None
    tel2: str | None = None
    tel3: str | None = None
    tesseraTeam: TesseraTeam | None = None
    codiceSTP: str | None = None
    dataRilascioSTP: str | None = None
    dataScadenzaSTP: str | None = None
    codiceENI: str | None = None
    dataRilascioENI: str | None = None
    dataScadenzaENI: str | None = None
    email: str | None = None
    codiceEsterno: str | None = None
    vincoliProfilo: Any | None = None
    tokenRegistrazione: str | None = None
    rapprLegale: Any | None = None
    rapprLegaleTipoDocumento: Any | None = None
    rapprLegaleNumDocumento: Any | None = None
    rapprLegaleRilascioDocumento: Any | None = None
    rapprLegaleDataRilascioDocumento: Any | None = None
    ncivicoResidenza: str | None = None
    tsan: Any | None = None
    ncivicoDomicilio: str | None = None


class GetPrescrizioneElettronicaRequest(BaseModel):
    cf: str | None = None
    nre: str | None = None
    numbersTeam: str | None = None


class GetPrescrizioneElettronicaResponse(ResponseData):
    paziente: Paziente | None = None
    listaPrescrizioni: ListaPrescrizioni | None = None
