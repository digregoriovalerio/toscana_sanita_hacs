from typing import Any, Generic, TypeVar

from pydantic import BaseModel


class DatiSPA(BaseModel):
    tipoAccesso: str | None = None
    tipoPrescrittore: str | None = None
    verificaCF: str | None = None
    stampaPC: str | None = None
    suggerita: str | None = None
    classePriorita: str | None = None
    finalita: str | None = None


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
    costoPrestazione: float | None = None
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
    unitaPrimoAppuntamento: str | None = None
    dataPrimoAppuntamento: str | None = None
    tipoAccessoPriorita: str | None = None
    dataAttivita: str | None = None
    oraAttivita: str | None = None
    unitaAttivita: str | None = None
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


class Prescrizione(BaseModel):
    numPrescrizione: str | None = None
    idEpisodio: str | None = None
    idPrescrizione: str | None = None
    idPrescrizioneRmt: str | None = None
    nome: str | None = None
    convenzione: str | None = None
    codiceConvenzione: str | None = None
    descrizioneConvenzione: str | None = None
    tipoPrescrizione: str | None = None
    codiceTipoPrescrizione: str | None = None
    descrizioneTipoPrescrizione: str | None = None
    tipoErogazione: str | None = None
    tipoRicetta: str | None = None
    fasciaReddito: str | None = None
    descrizioneFasciaReddito: str | None = None
    numeroImpegnativa: str | None = None
    numeroImpegnativaRossa: str | None = None
    numeroNRE: str | None = None
    dataImpegnativa: str | None = None
    dataContatto: str | None = None
    esenzione: str | None = None
    codiceEsenzione: str | None = None
    descrizioneEsenzione: str | None = None
    datiSPA: DatiSPA | None = None
    cfPrescrittore: str | None = None
    codiceRegPrescrittore: str | None = None
    calcoloImporto: str | None = None
    classePriorita: str | None = None
    descrizioneClassePriorita: str | None = None
    tipoAccessoPriorita: str | None = None
    costoPrescrizione: float | None = None
    quotaRicetta: float | None = None
    quotaCD: float | None = None
    statoPagamento: str | None = None
    listaPrestazioni: ListaPrestazioni | None = None
    listaAppuntamenti: Any | None = None
    statoCorrettezzaAmministrativa: str | None = None
    esitoPrescrizione: str | None = None
    inviaMailPromemoria: bool | None = None
    iuv: str | None = None
    valoreStatoPagamento: str | None = None
    listaConsensi: Any | None = None
    visualizzaErogatoRicevuta: str | None = None
    descrizioneDiagnosi: str | None = None
    listaReportDisponibili: Any | None = None
    notePrescrizione: str | None = None
    quesitoDiagnostico: str | None = None
    invioSMSAbilitato: bool | None = None
    codiceCUP: str | None = None
    promemoriaRicettaDema: str | None = None
    modalitaTrascodifiche: str | None = None
    datiTamponiCovid: Any | None = None
    richiedente: str | None = None
    codiceRichiedente: str | None = None
    descrizioneRichiedente: str | None = None
    cdcRichiedente: str | None = None
    codiceCDCRichiedente: str | None = None
    descrizioneCDCRichiedente: str | None = None
    datiPagoPA: Any | None = None
    listaLink: Any | None = None
    inviante: str | None = None
    terzoPagante: str | None = None
    tipoConvenzione: str | None = None
    codiceTipoConvenzione: str | None = None
    descrizioneTipoConvenzione: str | None = None


class ListaPrescrizioni(BaseModel):
    prescrizione: list[Prescrizione] = []


class Esito(BaseModel):
    codice: str | None = None
    descrizione: str | None = None
    tipo: str | None = None


class ResponseData(BaseModel):
    esito: list[Esito] = []


class Message(BaseModel):
    description: str | None = None
    code: str | None = None
    level: str | None = None


RD = TypeVar("RD", bound=ResponseData)


class RootResponse(BaseModel, Generic[RD]):
    response: RD | None = None
    message: Message | None = None
