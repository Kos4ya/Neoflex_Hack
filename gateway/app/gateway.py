import httpx
from fastapi import Request, HTTPException
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ServiceGateway:
    """Gateway для проксирования запросов к микросервисам"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def proxy(
            self,
            request: Request,
            service_url: str,
            path: str,
            method: str = None,
    ) -> Any:
        """
        Проксирует запрос к указанному сервису
        """
        target_url = f"{service_url}{path}"

        body = None
        if method in ["POST", "PUT", "PATCH"]:
            body = await request.body()

        headers = dict(request.headers)
        headers.pop("host", None)

        try:
            response = await self.client.request(
                method=method or request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params,
            )

            logger.debug(f"Proxy {request.method} {path} → {response.status_code}")

            return response

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Service timeout"
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail="Service unavailable"
            )
        except Exception as e:
            logger.error(f"Proxy error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Gateway error: {str(e)}"
            )

    async def close(self):
        await self.client.close()


gateway = ServiceGateway()