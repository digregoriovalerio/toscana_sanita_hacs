from pathlib import Path
from typing import Any

import httpx
from pydantic import TypeAdapter

from .data.availability import AvailabilityRequest, AvailabilityResponse
from .data.calendar import CalendarResponse
from .data.enterprises import ProvinceEnterprisesResponse
from .data.lock import LockResponse
from .data.reservation import ReservationRequest, ReservationResponse
from .data.search import SearchRequest, SearchResponse
from .errors import ZeroCodeAPIError


class ZeroCodeClient:
    """
    Client API for the ZeroCode Sanita Toscana Backend Service.
    Maintains session state and handles XSRF tokens automatically.
    """

    def __init__(self, base_url: str = "https://zerocode.sanita.toscana.it", timeout: float = 15.0):
        referer = base_url.rstrip("/") + "/"
        self.base_url = referer + "api"
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={"Accept": "application/json, text/plain, */*", "Referer": referer},
            timeout=timeout,
        )

    def close(self):
        """Close the underlying HTTPX client."""
        self.client.close()

    def __enter__(self):
        self.init_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _handle_response(self, response: httpx.Response) -> Any:
        """Centralized response evaluation."""
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise ZeroCodeAPIError(f"HTTP Error {e.response.status_code}: {e.response.text}") from e
        except Exception as e:
            raise ZeroCodeAPIError(f"Unexpected error: {e!s}") from e

    def init_session(self) -> None:
        """
        Initializes the session and securely extracts the XSRF-TOKEN for future requests.
        """
        response = self.client.get("/services")
        self._handle_response(response)

        # Extract XSRF-TOKEN from httpx managed cookies
        xsrf_token = self.client.cookies.get("XSRF-TOKEN")
        if not xsrf_token:
            raise ZeroCodeAPIError(
                "Initialization failed: XSRF-TOKEN cookie not found in the response."
            )

        # Add the token to default headers for all subsequent calls
        self.client.headers["x-xsrf-token"] = xsrf_token

    def search(self, request: SearchRequest) -> SearchResponse:
        """
        Search for available reservations via Fiscal Code and NRE list.
        """
        payload = request.model_dump(by_alias=True, exclude_none=True)
        response = self.client.post("/cerca", json=payload)

        data = self._handle_response(response)
        return SearchResponse.model_validate(data)

    def get_enterprises_with_comune(self, comune_id: int) -> list[ProvinceEnterprisesResponse]:
        """
        Retrieve details of enterprises/facilities operating in a specific Comune.
        """
        response = self.client.get(f"/enterprises-with-comune/{comune_id}")

        data = self._handle_response(response)
        adapter = TypeAdapter(list[ProvinceEnterprisesResponse])
        return adapter.validate_python(data)

    def get_calendar(self, sys_id: str) -> CalendarResponse:
        """
        Get available days for a specific enterprise/service system id.
        """
        response = self.client.get(f"/calendar/{sys_id}")

        data = self._handle_response(response)
        return CalendarResponse.model_validate(data)

    def get_availability(self, request: AvailabilityRequest) -> AvailabilityResponse:
        """
        Check exact time slots available for a specified day.
        """
        # Exclude defaults/nones and dump to standard JSON structure
        # Pydantic `date` parses automatically to 'YYYY-MM-DD'
        payload = request.model_dump(by_alias=True, exclude_none=True, mode="json")
        response = self.client.post("/disponibilita", json=payload)

        data = self._handle_response(response)
        return AvailabilityResponse.model_validate(data)

    def lock(self, queue_remote_id: str) -> LockResponse:
        """
        Lock a specific queue/reservation slot using its remote ID.
        """
        response = self.client.get(f"/lock/{queue_remote_id}")

        data = self._handle_response(response)
        return LockResponse.model_validate(data)

    def reserve(self, request: ReservationRequest) -> ReservationResponse:
        """
        Confirm the reservation for a previously locked queue remote ID.
        """
        payload = request.model_dump(by_alias=True, exclude_none=True)
        response = self.client.post("/prenota", json=payload)

        data = self._handle_response(response)
        return ReservationResponse.model_validate(data)

    def download_memo(self, activation_key: str, file_path: str | Path) -> None:
        """
        Downloads the PDF memo of the reservation and saves it to the specified local path.
        """
        response = self.client.get(f"/memo/{activation_key}")

        # We handle the response manually here instead of _handle_response
        # because the expected response is a raw binary file, not JSON.
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ZeroCodeAPIError(
                f"HTTP Error {e.response.status_code}: Failed to download memo."
            ) from e

        # Write the binary content to the specified file path
        path = Path(file_path)
        with path.open("wb") as f:
            f.write(response.content)
