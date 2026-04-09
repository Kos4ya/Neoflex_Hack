import httpx
from fastapi import Request, HTTPException
from typing import Any
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
    ) -> Any:
        """Проксирует запрос к указанному сервису"""

        # Формируем целевой URL
        target_url = f"{service_url}{path}"

        # Получаем тело запроса
        body = await request.body()

        # Подготавливаем заголовки - убираем проблемные
        headers = {}
        for key, value in request.headers.items():
            key_lower = key.lower()
            # Пропускаем проблемные заголовки
            if key_lower in [
                "host",
                "content-length",
                "transfer-encoding",
                "connection",
                "accept-encoding"
            ]:
                continue
            headers[key] = value

        # Добавляем правильный Content-Type если есть тело
        if body and "content-type" not in headers:
            headers["content-type"] = "application/json"

        try:
            # Отправляем запрос к сервису
            response = await self.client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body if body else None,
                params=dict(request.query_params),
            )

            logger.info(f"Proxy {request.method} {path} → {response.status_code}")
            return response

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Service timeout"
            )
        except httpx.ConnectError as e:
            logger.error(f"Connect error to {service_url}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Service {service_url} unavailable"
            )
        except Exception as e:
            logger.error(f"Proxy error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Gateway error: {str(e)}"
            )

    async def close(self):
        await self.client.close()


# Создаем экземпляр gateway
gateway = ServiceGateway()