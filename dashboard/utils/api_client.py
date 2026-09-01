import asyncio
import time
from typing import Any, Dict, List, Optional, Union
from functools import lru_cache
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import streamlit as st


class APIError(Exception):
    """Raised when the API client encounters an error."""


class APIClient:
    """API Client with caching, retries, and error handling."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        cache_ttl: int = 30,  # seconds
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        
        # Session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Cache: {endpoint: (data, timestamp)}
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._cache_ttl = cache_ttl
    
    def _get_cache_key(self, endpoint: str, params: dict = None) -> str:
        """Generate cache key from endpoint and params."""
        if params:
            param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
            return f"{endpoint}?{param_str}"
        return endpoint
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get cached data if not expired."""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return data
            else:
                del self._cache[key]
        return None
    
    def _set_cache(self, key: str, data: Any) -> None:
        """Set cache with current timestamp."""
        self._cache[key] = (data, time.time())
    
    def invalidate_cache(self, pattern: str = None) -> None:
        """Invalidate cache entries matching pattern."""
        if pattern is None:
            self._cache.clear()
        else:
            keys_to_delete = [k for k in self._cache if pattern in k]
            for k in keys_to_delete:
                del self._cache[k]
    
    def clear_cache(self) -> None:
        """Clear all cache."""
        self._cache.clear()
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        json_data: dict = None,
        use_cache: bool = True,
    ) -> Optional[Any]:
        """Make HTTP request with retry and caching."""
        # Check cache for GET requests
        cache_key = self._get_cache_key(endpoint, params)
        if use_cache and method == "GET":
            cached = self._get_from_cache(self._get_cache_key(endpoint, params))
            if cached is not None:
                return cached
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data if method != "GET" else None,
                timeout=self.timeout,
            )
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                return None
            
            data = response.json()
            
            # Cache successful GET responses
            if use_cache and method == "GET":
                self._set_cache(cache_key, data)
            
            return data
        
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg = error_detail.get("detail", str(e))
                except:
                    error_msg = f"HTTP {e.response.status_code}: {e.response.reason}"
            else:
                error_msg = str(e)
            raise APIError(f"API Error: {error_msg}")
        
        except requests.exceptions.Timeout:
            raise APIError(f"Request timeout after {self.timeout}s")
        except requests.exceptions.ConnectionError:
            raise APIError("Cannot connect to API server. Is the backend running?")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
    
    def get(
        self,
        endpoint: str,
        params: Dict = None,
        use_cache: bool = True,
    ) -> Optional[Any]:
        """GET request with caching."""
        return self._request("GET", endpoint, params=params, use_cache=True)
    
    def post(
        self,
        endpoint: str,
        json_data: dict = None,
        params: Dict = None,
        use_cache: bool = False,
    ) -> Optional[Any]:
        """POST request without caching."""
        return self._request("POST", endpoint, params=params, json_data=json_data, use_cache=False)
    
    def put(
        self,
        endpoint: str,
        json_data: dict = None,
    ) -> Optional[Any]:
        """PUT request."""
        return self._request("PUT", endpoint, json_data=json_data, use_cache=False)
    
    def delete(self, endpoint: str) -> Optional[Any]:
        """DELETE request."""
        return self._request("DELETE", endpoint, use_cache=False)
    
    # Convenience methods for specific endpoints
    def get_health(self) -> Optional[dict]:
        return self.get("/health")
    
    def get_transactions(
        self,
        source: str = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Optional[List]:
        params = {"skip": skip, "limit": limit}
        if source:
            params["source"] = source
        return self.get("/transactions/", params=params)
    
    def get_canonical_transactions(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Optional[List]:
        return self.get("/canonical/", params={"skip": 0, "limit": 100})
    
    def run_reconciliation(self, force_rerun: bool = False) -> Optional[dict]:
        """Run full reconciliation pipeline."""
        return self.post("/reconciliation/run", json_data={"force_rerun": True})
    
    def get_matches(self, skip: int = 0, limit: int = 100) -> Optional[List]:
        return self.get("/reconciliation/results", params={"skip": 0, "limit": 100})
    
    def get_matches_paginated(
        self,
        page: int = 1,
        limit: int = 50,
        status: str = None,
        method: str = None,
        min_score: float = None,
    ) -> Optional[dict]:
        params = {"page": page, "limit": limit}
        if status:
            params["status"] = status
        if method:
            params["method"] = method
        if min_score is not None:
            params["min_score"] = min_score
        return self.get("/reconciliation/results/paginated", params=params)
    
    def get_exceptions(
        self,
        status: str = None,
        skip: int = 0,
        limit: int = 100,
) -> Optional[List]:
        params = {"skip": 0, "limit": 100}
        if status:
            params["status"] = status
        return self.get("/exceptions/", params=params)
    
    def investigate_exception(self, exc_id: int) -> Optional[dict]:
        return self.post(f"/exceptions/{exc_id}/investigate")
    
    def follow_up_exception(
        self,
        exc_id: int,
        question: str,
        investigation_result: dict,
        chat_history: list
    ) -> Optional[dict]:
        return self.post(
            f"/exceptions/{exc_id}/followup",
            json_data={
                "question": question,
                "investigation_result": investigation_result,
                "chat_history": chat_history
            }
        )
    
    def get_cash_position(self, date: str = None) -> Optional[dict]:
        params = {"date": date} if date else None
        return self.get("/cash/position", params=params)
    
    def calculate_cash_position(self) -> Optional[dict]:
        return self.post("/cash/position/calculate")
    
    def get_cash_variance(self) -> Optional[dict]:
        return self.get("/cash/variance")
    
    def get_forecast(self, days: int = 30) -> Optional[List]:
        return self.get("/cash/forecast", params={"days": days})
    
    def get_forecast_summary(self, days: int = 30) -> Optional[dict]:
        return self.get("/cash/forecast/summary", params={"days": days})
    
    def add_cash_adjustment(self, amount: float, note: str) -> Optional[dict]:
        return self.post("/cash/adjustment", json_data={"amount": amount, "note": note})
    
    def get_matches(self, skip: int = 0, limit: int = 100) -> Optional[List]:
        return self.get("/reconciliation/results", params={"skip": 0, "limit": 100})
    
    def get_matches_paginated(
        self,
        page: int = 1,
        limit: int = 50,
        status: str = None,
        method: str = None,
        min_score: float = None,
    ) -> Optional[dict]:
        params = {"page": page, "limit": limit}
        if status:
            params["status"] = status
        if method:
            params["method"] = method
        if min_score is not None:
            params["min_score"] = min_score
        return self.get("/reconciliation/results/paginated", params=params)
    
    def get_exceptions(self, status: str = None, skip: int = 0, limit: int = 100) -> Optional[List]:
        params = {"skip": 0, "limit": 100}
        if status:
            params["status"] = status
        return self.get("/exceptions/", params=params)
    
    def investigate_exception(self, exc_id: int) -> Optional[dict]:
        return self.post(f"/exceptions/{exc_id}/investigate")
    
    def get_cash_position(self, date: str = None) -> Optional[dict]:
        params = {"date": date} if date else None
        return self.get("/cash/position", params=params)
    
    def get_cash_variance(self) -> Optional[dict]:
        return self.get("/cash/variance")
    
    def get_forecast(self, days: int = 30) -> Optional[List]:
        return self.get("/cash/forecast", params={"days": days})
    
    def get_forecast_summary(self, days: int = 30) -> Optional[dict]:
        return self.get("/cash/forecast/summary", params={"days": days})
    
    def get_metrics(self) -> Optional[dict]:
        return self.get("/metrics/")
    
    def add_cash_adjustment(self, amount: float, note: str) -> Optional[dict]:
        return self.post("/cash/adjustment", json_data={"amount": amount, "note": note})
    
    def get_exceptions(self, status: str = None, skip: int = 0, limit: int = 100) -> Optional[List]:
        params = {"skip": 0, "limit": 100}
        if status:
            params["status"] = status
        return self.get("/exceptions/", params=params)
    
    def investigate_exception(self, exc_id: int) -> Optional[dict]:
        return self.post(f"/exceptions/{exc_id}/investigate")


# Global client instance (lazy initialization)
_client: Optional[APIClient] = None


def get_api_client() -> APIClient:
    """Get or create global API client instance."""
    global _client
    if _client is None:
        # Try to get base URL from streamlit secrets or environment
        import os
        base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
        _client = APIClient(base_url=base_url)
    return _client


# Synchronous wrapper for use in Streamlit (which runs in a thread)
def api_get(endpoint: str, params: dict = None) -> Optional[Any]:
    """Synchronous GET request wrapper."""
    client = get_api_client()
    try:
        return client.get(endpoint, params=params)
    except Exception as e:
        message = str(e)
        if "not found" in message.lower():
            return None
        import streamlit as st
        st.error(f"API Error: {message}")
        return None


def api_post(endpoint: str, json_data: dict = None, params: dict = None) -> Optional[Any]:
    """Synchronous POST request wrapper."""
    client = get_api_client()
    try:
        return client.post(endpoint, json_data=json_data, params=params)
    except Exception as e:
        import streamlit as st
        st.error(f"API Error: {str(e)}")
        return None


def api_post(endpoint: str, json_data: dict = None, params: dict = None) -> Optional[Any]:
    """Synchronous POST request wrapper."""
    client = get_api_client()
    try:
        return client.post(endpoint, json_data=json_data, params=params)
    except Exception as e:
        import streamlit as st
        st.error(f"API Error: {str(e)}")
        return None


# Streamlit cached API functions for better performance
import streamlit as st

@st.cache_data(ttl=30, show_spinner=False)
def cached_get_metrics() -> Optional[dict]:
    """Cached metrics endpoint."""
    client = get_api_client()
    try:
        return client.get_metrics()
    except Exception:
        return None


@st.cache_data(ttl=30, show_spinner=False)
def cached_get_cash_position() -> Optional[dict]:
    """Cached cash position."""
    client = get_api_client()
    try:
        return client.get_cash_position()
    except Exception:
        return None


@st.cache_data(ttl=30, show_spinner=False)
def cached_get_forecast(days: int = 30) -> Optional[List]:
    """Cached forecast."""
    client = get_api_client()
    try:
        return client.get_forecast(days=days)
    except Exception:
        return None


@st.cache_data(ttl=30, show_spinner=False)
def cached_get_forecast_summary(days: int = 30) -> Optional[dict]:
    """Cached forecast summary."""
    client = get_api_client()
    try:
        return client.get_forecast_summary(days=days)
    except Exception:
        return None


@st.cache_data(ttl=30, show_spinner=False)
def cached_get_matches(skip: int = 0, limit: int = 100) -> Optional[List]:
    """Cached matches list."""
    client = get_api_client()
    try:
        return client.get_matches(skip=skip, limit=limit)
    except Exception:
        return None


@st.cache_data(ttl=30, show_spinner=False)
def cached_get_exceptions(status: str = None) -> Optional[List]:
    """Cached exceptions list."""
    client = get_api_client()
    try:
        return client.get_exceptions()
    except Exception:
        return None


@st.cache_data(ttl=60, show_spinner=False)
def cached_get_cash_position() -> Optional[dict]:
    """Cached cash position."""
    client = get_api_client()
    try:
        return client.get_cash_position()
    except Exception:
        return None


@st.cache_data(ttl=60, show_spinner=False)
def cached_get_forecast_summary(days: int = 30) -> Optional[dict]:
    """Cached forecast summary."""
    client = get_api_client()
    try:
        return client.get_forecast_summary(days=days)
    except Exception:
        return None


@st.cache_data(ttl=30, show_spinner=False)
def cached_get_matches(skip: int = 0, limit: int = 100) -> Optional[List]:
    """Cached matches list."""
    client = get_api_client()
    try:
        return client.get_matches(skip=skip, limit=limit)
    except Exception:
        return None


@st.cache_data(ttl=30, show_spinner=False)
def cached_get_exceptions(status: str = None) -> Optional[List]:
    """Cached exceptions list."""
    client = get_api_client()
    try:
        return client.get_exceptions(status=status)
    except Exception:
        return None


def invalidate_caches() -> None:
    """Invalidate all cached API responses."""
    st.cache_data.clear()


def get_api_client_sync() -> APIClient:
    """Get synchronous API client for non-Streamlit contexts."""
    import os
    base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    return APIClient(base_url=base_url)