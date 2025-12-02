"""コード実行ツール.

Dockerコンテナ内でコードを安全に実行する。
"""

import asyncio
import logging
from typing import Any

from .base import BaseTool, ToolDefinition, ToolParameter, ToolResult

logger = logging.getLogger(__name__)

# Docker SDK imports - optional
try:
    import docker
    from docker.errors import ContainerError, DockerException, ImageNotFound

    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    docker = None  # type: ignore
    ContainerError = Exception  # type: ignore
    DockerException = Exception  # type: ignore
    ImageNotFound = Exception  # type: ignore


class CodeExecutionTool(BaseTool):
    """コード実行ツール.

    Dockerコンテナ内でPython/JavaScriptコードを実行する。
    セキュリティのため、ネットワークアクセスは無効化され、
    リソース制限が適用される。
    """

    SUPPORTED_LANGUAGES: dict[str, dict[str, Any]] = {
        "python": {
            "image": "python:3.12-slim",
            "cmd": ["python", "-c"],
            "description": "Python 3.12",
        },
        "javascript": {
            "image": "node:20-slim",
            "cmd": ["node", "-e"],
            "description": "Node.js 20",
        },
    }

    # 安全性制限
    DEFAULT_TIMEOUT = 30  # seconds
    MEMORY_LIMIT = "128m"
    CPU_PERIOD = 100000  # microseconds
    CPU_QUOTA = 50000  # 50% of one CPU

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        memory_limit: str = MEMORY_LIMIT,
    ):
        """Initialize code execution tool.

        Args:
            timeout: Execution timeout in seconds.
            memory_limit: Docker memory limit (e.g., '128m', '256m').
        """
        self._timeout = timeout
        self._memory_limit = memory_limit
        self._client: Any = None

    def _get_docker_client(self) -> Any:
        """Get or create Docker client.

        Returns:
            Docker client instance.

        Raises:
            RuntimeError: If Docker is not available.
        """
        if not DOCKER_AVAILABLE:
            raise RuntimeError(
                "Docker SDK not installed. Install with: pip install docker"
            )

        if self._client is None:
            try:
                self._client = docker.from_env()
                # Test connection
                self._client.ping()
            except DockerException as e:
                raise RuntimeError(f"Failed to connect to Docker: {e}") from e

        return self._client

    @property
    def definition(self) -> ToolDefinition:
        """Return tool definition for LLM."""
        languages = list(self.SUPPORTED_LANGUAGES.keys())
        return ToolDefinition(
            name="execute_code",
            description=(
                "Execute code in a secure sandboxed environment. "
                "Supported languages: Python 3.12, JavaScript (Node.js 20). "
                "The environment has no network access and limited resources. "
                "Use this to run calculations, data processing, or test code snippets."
            ),
            parameters=[
                ToolParameter(
                    name="language",
                    type="string",
                    description="Programming language to use",
                    enum=languages,
                ),
                ToolParameter(
                    name="code",
                    type="string",
                    description=(
                        "Code to execute. For Python, use print() to output results. "
                        "For JavaScript, use console.log()."
                    ),
                ),
            ],
        )

    async def execute(self, language: str, code: str) -> ToolResult:
        """Execute code in a Docker container.

        Args:
            language: Programming language ('python' or 'javascript').
            code: Code to execute.

        Returns:
            ToolResult with execution output or error.
        """
        # Validate language
        if language not in self.SUPPORTED_LANGUAGES:
            return ToolResult(
                success=False,
                output=None,
                error=f"Unsupported language: {language}. "
                f"Supported: {', '.join(self.SUPPORTED_LANGUAGES.keys())}",
            )

        # Validate code
        if not code or not code.strip():
            return ToolResult(
                success=False,
                output=None,
                error="Empty code provided",
            )

        # Check Docker availability
        try:
            client = self._get_docker_client()
        except RuntimeError as e:
            logger.error(f"Docker not available: {e}")
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
            )

        config = self.SUPPORTED_LANGUAGES[language]

        try:
            # Ensure image is available
            try:
                client.images.get(config["image"])
            except ImageNotFound:
                logger.info(f"Pulling image: {config['image']}")
                await asyncio.to_thread(client.images.pull, config["image"])

            # Run container
            logger.info(f"Executing {language} code (timeout={self._timeout}s)")
            result = await asyncio.to_thread(
                self._run_container,
                client,
                config,
                code,
            )

            return ToolResult(
                success=True,
                output=result,
            )

        except ContainerError as e:
            # Container exited with non-zero status
            stderr = e.stderr.decode("utf-8") if e.stderr else str(e)
            logger.warning(f"Code execution error: {stderr}")
            return ToolResult(
                success=False,
                output=None,
                error=f"Execution error: {stderr}",
            )
        except asyncio.TimeoutError:
            logger.warning(f"Code execution timed out after {self._timeout}s")
            return ToolResult(
                success=False,
                output=None,
                error=f"Execution timed out after {self._timeout} seconds",
            )
        except Exception as e:
            logger.exception(f"Unexpected error during code execution: {e}")
            return ToolResult(
                success=False,
                output=None,
                error=f"Unexpected error: {e}",
            )

    def _run_container(
        self,
        client: Any,
        config: dict[str, Any],
        code: str,
    ) -> str:
        """Run code in a Docker container.

        This method runs synchronously and should be called via asyncio.to_thread().

        Args:
            client: Docker client.
            config: Language configuration.
            code: Code to execute.

        Returns:
            Container output as string.
        """
        result = client.containers.run(
            image=config["image"],
            command=config["cmd"] + [code],
            remove=True,
            mem_limit=self._memory_limit,
            cpu_period=self.CPU_PERIOD,
            cpu_quota=self.CPU_QUOTA,
            network_disabled=True,
            security_opt=["no-new-privileges"],
            read_only=True,
            # tmpfs for /tmp with size limit
            tmpfs={"/tmp": "size=10m"},
            timeout=self._timeout,
        )

        if isinstance(result, bytes):
            return result.decode("utf-8").strip()
        return str(result).strip()


# ツール登録用のシングルトンインスタンス
_code_tool_instance: CodeExecutionTool | None = None


def get_code_execution_tool() -> CodeExecutionTool:
    """Get singleton code execution tool instance."""
    global _code_tool_instance
    if _code_tool_instance is None:
        _code_tool_instance = CodeExecutionTool()
    return _code_tool_instance


def register_code_execution_tool() -> None:
    """Register code execution tool to the registry."""
    from .registry import ToolRegistry

    tool = get_code_execution_tool()
    ToolRegistry.register(tool)
