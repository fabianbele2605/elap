"""Cliente HTTP para Ollama - Modelos locales de IA"""

import asyncio
import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OllamaClient:
    """Cliente para interactuar con Ollama"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=600)  # 10 minutos timeout para modelos grandes
        logger.info(f"OllamaClient initialized with {base_url}")

    async def generar(
        self,
        modelo: str,
        prompt: str,
        stream: bool = False,
    ) -> str:
        """Generar texto usando Ollama

        Args:
            modelo: Nombre del modelo (ej: "glm4:9b")
            prompt: Texto de entrada
            stream: Si usar streaming (no implementado aún)

        Returns:
            Texto generado
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                payload = {
                    "model": modelo,
                    "prompt": prompt,
                    "stream": False,
                }

                logger.info(f"Calling Ollama: model={modelo}, prompt={prompt[:50]}...")

                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama error: {error_text}")
                        raise Exception(f"Ollama error: {error_text}")

                    data = await response.json()
                    resultado = data.get("response", "")

                    logger.info(f"Ollama response: {resultado[:100]}...")
                    return resultado

        except asyncio.TimeoutError:
            logger.error(f"Ollama timeout for model {modelo}")
            raise Exception(f"Timeout calling Ollama model {modelo}")
        except Exception as e:
            logger.error(f"Error calling Ollama: {str(e)}")
            raise

    async def generar_streaming(self, modelo: str, prompt: str):
        """Genera texto en streaming, yield token por token

        Args:
            modelo: Nombre del modelo (ej: "glm4:9b")
            prompt: Texto de entrada

        Yields:
            Tokens de respuesta uno por uno
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                payload = {
                    "model": modelo,
                    "prompt": prompt,
                    "stream": True,
                }

                logger.info(f"Streaming Ollama: model={modelo}, prompt={prompt[:50]}...")

                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama error: {error_text}")
                        raise Exception(f"Ollama error: {error_text}")

                    async for line in response.content:
                        if line:
                            import json
                            try:
                                data = json.loads(line.decode().strip())
                                token = data.get("response", "")
                                if token:
                                    yield token
                            except json.JSONDecodeError:
                                pass

        except asyncio.TimeoutError:
            logger.error(f"Ollama streaming timeout for model {modelo}")
            raise Exception(f"Timeout calling Ollama model {modelo}")
        except Exception as e:
            logger.error(f"Error calling Ollama streaming: {str(e)}")
            raise

    async def listar_modelos(self) -> list:
        """Listar modelos disponibles en Ollama

        Returns:
            Lista de nombres de modelos
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status != 200:
                        return []

                    data = await response.json()
                    modelos = [m["name"] for m in data.get("models", [])]
                    logger.info(f"Available models: {modelos}")
                    return modelos

        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return []

    async def health_check(self) -> bool:
        """Verificar si Ollama está disponible

        Returns:
            True si está disponible, False en caso contrario
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    return response.status == 200
        except Exception:
            return False
