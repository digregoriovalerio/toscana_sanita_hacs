from collections.abc import Generator
from pathlib import Path

from pydantic import BaseModel

from .client import ZeroCodeClient
from .data.availability import AvailabilityRequest, QueueRemoteItem
from .data.calendar import AvailableDay
from .data.enterprises import Enterprise
from .data.reservation import ReservationRequest, ReservationResponse
from .data.search import SearchRequest


class SearchFilters(BaseModel):
    province: list[str] = []
    comuni: list[str] = []
    start_time: str = "00:00"
    end_time: str = "24:00"

    def filter_province(self, provincia: str) -> bool:
        return not self.province or provincia in self.province

    def filter_comuni(self, comune: str) -> bool:
        return not self.comuni or comune in self.comuni

    def filter_time(self, time: str) -> bool:
        return self.start_time <= time <= self.end_time


def search(
    client: ZeroCodeClient, search_req: SearchRequest, filters: SearchFilters
) -> Generator[tuple[Enterprise, AvailableDay, QueueRemoteItem], None, None]:
    client.search(search_req)
    enterprises_res = client.get_enterprises_with_comune(1)
    for response in enterprises_res:
        if filters.filter_province(response.province):
            for comune in response.comunes:
                if filters.filter_comuni(comune.comune):
                    for enterprise in comune.enterprises:
                        if enterprise.disponibilita > 0:
                            calendar_res = client.get_calendar(enterprise.sys_id)
                            for availability in calendar_res.available_days:
                                avail_req = AvailabilityRequest(
                                    day=availability.day, timeDelay="06:00"
                                )
                                avail_res = client.get_availability(avail_req)
                                for item in avail_res.queue_remote:
                                    if filters.filter_time(item.time):
                                        yield (enterprise, availability, item)


def reserve(client: ZeroCodeClient, item: QueueRemoteItem) -> ReservationResponse:
    client.lock(item.queue_remote_id)
    reserve_req = ReservationRequest(time=item.time, queue_remote_id=item.queue_remote_id)
    reserve_res = client.reserve(reserve_req)
    return reserve_res


def download_memo(
    client: ZeroCodeClient, reservation: ReservationResponse, download_dir: Path | None = None
) -> Path:
    memo_path = (download_dir or Path.cwd()) / f"{reservation.number.replace(' ', '_')}_memo.pdf"
    client.download_memo(reservation.activation_key, memo_path)
    return memo_path
