from typing import Any

from pydantic import BaseModel

from .common import ListaPrescrizioni, ResponseData


class Macrozona(BaseModel):
    idMacrozona: str | None = None
    codiceMacrozona: str | None = None
    descrizioneMacrozona: str | None = None


class Zona(BaseModel):
    idZona: str | None = None
    codiceZona: str | None = None
    descrizioneZona: str | None = None
    macrozona: Macrozona | None = None


class Ente(BaseModel):
    idEnte: str | None = None
    idEnteRegionale: str | None = None
    descrizioneEnte: str | None = None
    descrizioneRegionale: str | None = None


class Sede(BaseModel):
    idSede: str | None = None
    descSede: str | None = None
    nomeSede: str | None = None
    indirizzoSede: str | None = None
    capSede: str | None = None
    istatComuneSede: str | None = None
    nomeComuneSede: str | None = None
    provinciaSede: str | None = None
    telefonoSede: str | None = None
    ente: Ente | None = None
    zona: Zona | None = None


class Erogatore(BaseModel):
    idErogatore: str | None = None
    descErogatore: str | None = None
    nomeErogatore: str | None = None
    indirizzoErogatore: str | None = None
    capErogatore: str | None = None
    istatComuneErogatore: str | None = None
    nomeComuneErogatore: str | None = None
    provinciaErogatore: str | None = None
    telefonoErogatore: str | None = None


class Unita(BaseModel):
    idUnita: str | None = None
    descUnita: str | None = None
    nomeUnita: str | None = None
    nomeUnitaExt: str | None = None
    presidioUnita: str | None = None
    codicePresidioUnita: str | None = None
    indirizzoUnita: str | None = None
    capUnita: str | None = None
    istatComuneUnita: str | None = None
    nomeComuneUnita: str | None = None
    provinciaUnita: str | None = None
    telefonoUnita: str | None = None
    erogatore: Erogatore | None = None
    sede: Sede | None = None
    responsabile: Any | None = None
    aziendaUnita: str | None = None


class Prestazione(BaseModel):
    numPrescrizione: str | None = None
    idPrestazione: str | None = None
    idPrestazioneRmt: str | None = None
    idPrestazioneExt: str | None = None
    nome: str | None = None
    statoPrestazione: str | None = None
    idPrestazioneAnagrafica: str | None = None
    codicePrestazione: str | None = None
    codicePrestazioneExt: str | None = None
    codProdPrest: str | None = None
    codiceCatalogoRegionale: str | None = None
    descrizioneCatalogoRegionale: str | None = None
    codiceNomenclatoreRegionale: str | None = None
    descrizioneNomenclatoreRegionale: str | None = None
    costoPrestazione: str | None = None
    compEsePatologia: str | None = None
    descrizionePrestazione: str | None = None
    dataModificaStatoPre: str | None = None
    idDisdettaPre: str | None = None
    codiceInvio: str | None = None
    codiceBranca: str | None = None
    statoPagamento: str | None = None
    notaOperatore: str | None = None
    notaPaziente: str | None = None
    intervalloPrestazione: str | None = None
    listaPrestazioniCUP: list[Any] = []
    unitaPrimoAppuntamento: Unita | None = None
    dataPrimoAppuntamento: str | None = None
    tipoAccessoPriorita: str | None = None
    dataAttivita: str | None = None
    oraAttivita: str | None = None
    unitaAttivita: Unita | None = None
    codicePacchetto: str | None = None
    inserimentoListaAttesaPossibile: bool | None = None
    tipoListaAttesa: str | None = None
    canaleNotificaReminder: str | None = None
    numeroChiamata: str | None = None
    letteraChiamata: str | None = None
    distrettiAnatomici: list[Any] = []
    indirizzoErogazione: str | None = None


class ListaPrestazioni(BaseModel):
    prestazione: list[Prestazione] = []


class Appuntamento(BaseModel):
    idAppuntamento: str | None = None
    idAppuntamentoExt: str | None = None
    statoAppuntamento: str | None = None
    dataAppuntamento: str | None = None
    oraAppuntamento: str | None = None
    dataAppuntamentoPaziente: str | None = None
    oraAppuntamentoPaziente: str | None = None
    costo: float | None = None
    durata: int | None = None
    unitaMisuraDurata: str | None = None
    dataModificaStato: str | None = None
    codiceBranca: str | None = None
    unita: Unita | None = None
    sede: Sede | None = None
    listaPrestazioni: ListaPrestazioni | None = None
    idSoluzione: str | None = None
    tipologiaAppuntamento: str | None = None
    flagRaggruppamentoOttimizzato: bool | None = None
    flagRaggruppamentoCombinato: bool | None = None
    codiceCUP: str | None = None
    flagTelevisita: bool | None = None
    anticipoAttivazioneTelevisita: str | None = None
    linkTelevisitaCalcolabile: bool | None = None
    notificaArrivoPaziente: bool | None = None
    codiceRemoto: str | None = None
    tipoCodiceRemoto: str | None = None
    operazioniConsentite: list[Any] = []
    vincoloPazienteSesso: str | None = None
    vincoliPazienteEta: list[Any] = []
    indirizzoErogazione: str | None = None
    numeroOrariAlternativi: int | None = None


class ListaAppuntamenti(BaseModel):
    appuntamento: list[Appuntamento] = []


class AreaPaziente(BaseModel):
    livello: int | None = None
    id: str | None = None
    codice: str | None = None
    descrizione: str | None = None


class Area(BaseModel):
    livello: int | None = None
    id: str | None = None
    codice: str | None = None
    descrizione: str | None = None


class SfogliamentoAree(BaseModel):
    areaPaziente: AreaPaziente | None = None
    attuale: Area | None = None
    successiva: Area | None = None
    precedente: Area | None = None


class GetListaDisponibilitaPostRequest(BaseModel):
    calcoloOrari: str | None = None
    calcoloAppuntamenti: str | None = None
    livelloSfogliamentoAree: int | None = None
    tipo: str | None = None
    listaPrescrizioni: ListaPrescrizioni | None = None
    cf: str | None = None


class GetListaDisponibilitaPostResponse(ResponseData):
    listaAppuntamenti: ListaAppuntamenti | None = None
    listaPrestazioniIndisponibili: ListaPrestazioni | None = None
    sfogliamentoAree: SfogliamentoAree | None = None
