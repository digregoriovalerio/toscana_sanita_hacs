from pydantic import Field

from .common import CamelCaseModel


class ReservationRequest(CamelCaseModel):
    time: str
    queue_remote_id: str


class ReservationResponse(CamelCaseModel):
    number: str
    activation_key: str = Field(alias="activationKey")
    payment_advice_available: bool = Field(alias="paymentAdviceAvailable")
