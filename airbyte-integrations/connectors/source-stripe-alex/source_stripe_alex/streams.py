from abc import ABC
import requests
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.core import Stream

# Basic full refresh stream
class StripeAlexStream(HttpStream, ABC):

    def __init__(self, *,
                 path: str,
                 url_base: str,
                 primary_key: str,
                 retry_factor: float,
                 max_retries: int,
                 headers: Mapping[str, str],
                 response_key: str,
                 request_parameters: Mapping[str, Any]):
        super().__init__()
        self._path = path
        self._primary_key = primary_key
        self.url_base = url_base
        self._retry_factor = retry_factor
        self._max_retries = max_retries
        self._headers = headers
        self._response_key = response_key
        self._request_parameters = request_parameters

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return self._headers

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = self._request_parameters
        # FIXME would be great to extract this too!
        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get(self._response_key, [])  # Stripe puts records in a container array "data"

    def url_base(self) -> str:
        return self._url_base

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return self._path

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    @primary_key.setter
    def set_primary_key(self, value):
        self._primary_key = value

    @property
    def retry_factor(self) -> float:
        return self._retry_factor

    @retry_factor.setter
    def set_retry_factor(self, value):
        self.retry_factor = value

    @property
    def max_retries(self) -> Union[int, None]:
        return self._max_retries

    @max_retries.setter
    def set_max_retries(self, value):
        self._max_retries = value


class Invoices(StripeAlexStream):
    def __init__(self, **kwargs):
        super().__init__(path="v1/invoices",**kwargs)
