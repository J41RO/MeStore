"""
Surgical Modifier v6.0 - Base Operation (Integrated with existing architecture)
Integration of BaseOperation pattern with existing OperationSpec system
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

try:
    from utils.content_handler import content_handler
    from utils.debug_analyzer import PatternDebugger
    from utils.logger import logger
    from utils.path_resolver import path_resolver
    from utils.project_context import project_context
    from utils.retry_manager import retry_with_backoff

    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    logger = None
    path_resolver = None
    content_handler = None
    project_context = None
    retry_with_backoff = None
    PatternDebugger = None
import time

try:
    from utils.content_handler import content_handler
    from utils.logger import logger
    from utils.path_resolver import path_resolver
    from utils.project_context import project_context

    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    logger = None
    path_resolver = None
    content_handler = None
    project_context = None


class OperationType(Enum):
    """Enumeration of operation types"""

    CREATE = "create"
    REPLACE = "replace"
    AFTER = "after"
    BEFORE = "before"
    APPEND = "append"
    DELETE = "delete"
    EXTRACT = "extract"
    UPDATE = "update"
    MOVE = "move"
    COPY = "copy"


class OperationStatus(Enum):
    """Status enumeration for operations"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class OperationResult:
    """Result of an operation execution (compatible with v5.3)"""

    success: bool
    operation_type: OperationType
    target_path: str
    message: str
    details: Dict[str, Any]
    execution_time: float
    content_processed: Optional[str] = None
    backup_created: bool = False
    backup_path: Optional[str] = None
    operation_name: Optional[str] = None
    arguments_used: Optional[Dict[str, Any]] = None


@dataclass
class OperationContext:
    """Context information for operation execution (integrated)"""

    project_root: Path
    target_file: Path
    operation_type: OperationType
    content: Optional[str] = None
    position_marker: Optional[str] = None
    backup_enabled: bool = True
    dry_run: bool = False
    validate_content: bool = True
    framework_context: Optional[Dict[str, Any]] = None
    arguments: Optional[Dict[str, Any]] = None


@dataclass
class ArgumentSpec:
    """Specification for operation arguments"""

    name: str
    type: type
    required: bool = True
    help: str = ""
    example: str = ""
    default: Any = None


class BaseOperation(ABC):
    """
    Abstract base class integrating with existing Surgical Modifier architecture.
    """

    def __init__(
        self, operation_type: OperationType, operation_name: Optional[str] = None
    ):
        self.operation_type = operation_type
        self.operation_name = operation_name or operation_type.value
        self.execution_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_execution_time": 0.0,
        }
        self.backup_registry = {}

    @abstractmethod
    def execute(self, context: OperationContext) -> OperationResult:
        """Execute the operation with the given context"""
        pass

    @abstractmethod
    def validate_context(self, context: OperationContext) -> List[str]:
        """Validate that the context is suitable for this operation"""
        pass

    @abstractmethod
    def can_rollback(self) -> bool:
        """Check if this operation supports rollback"""
        pass

    def prepare_context(
        self, target_file: Union[str, Path], content: Optional[str] = None, **kwargs
    ) -> OperationContext:
        """Prepare operation context with intelligent defaults"""
        if INTEGRATION_AVAILABLE and path_resolver:
            resolved_path = path_resolver.resolve(str(target_file))
            project_root = path_resolver.find_project_root() or Path.cwd()
        else:
            resolved_path = Path(target_file).resolve()
            project_root = Path.cwd()

        processed_content = None
        if content and INTEGRATION_AVAILABLE and content_handler:
            content_result = content_handler.get_safe_content(
                
            )
            processed_content = content_result[0]  # get_safe_content() returns (content, None)
        else:
            processed_content = content

        # CÓDIGO PARA AGREGAR DESPUÉS DE LA LÍNEA: processed_content = content

        # Integrar nuevos validadores si están disponibles
        validation_results = {}
        if kwargs.get("validate_before_insert", False):
            try:
                from utils.content_validator import PreInsertionValidator

                validator = PreInsertionValidator()
                target_context = kwargs.get("target_context", "general")
                is_valid, issues = validator.validate_syntax_compatibility(
                    processed_content, target_context
                )
                validation_results["syntax_validation"] = {
                    "is_valid": is_valid,
                    "issues": issues,
                }
                if not is_valid and logger:
                    logger.warning(
                        f"Content validation failed: {len(issues)} issues found"
                    )
            except ImportError:
                if logger:
                    logger.debug("Content validator not available")

        # Procesar patrones multi-línea si está habilitado
        if kwargs.get("multiline_native", False):
            try:
                from utils.universal_pattern_helper import UniversalPatternHelper

                helper = UniversalPatternHelper()
                pattern = kwargs.get("pattern", "")
                if pattern:
                    processed_pattern = helper.process_multiline_patterns(pattern)
                    kwargs["processed_pattern"] = processed_pattern
                    if logger:
                        logger.debug("Applied multiline pattern processing")
            except ImportError:
                if logger:
                    logger.debug("Universal pattern helper not available")

        # Procesar contenido raw si está especificado
        raw_mode = kwargs.get("raw_mode", "auto")
        if raw_mode != "auto":
            try:
                from utils.escape_processor import EscapeProcessor

                processor = EscapeProcessor()
                # processed_content = processor.process_raw_content(processed_content, mode=raw_mode)  # BUGFIX
                if logger:
                    logger.debug(f"Applied raw content processing in mode: {raw_mode}")
            except ImportError:
                if logger:
                    logger.debug("Escape processor not available")

        framework_context = None
        if INTEGRATION_AVAILABLE and project_context:
            try:
                metadata = project_context.analyze_project(project_root, use_cache=True)
                framework_context = {
                    "frameworks": [fw.name for fw in metadata.frameworks],
                    "primary_language": metadata.primary_language,
                    "build_system": metadata.build_system,
                }
            except Exception:
                pass

        return OperationContext(
            project_root=project_root,
            target_file=resolved_path,
            operation_type=self.operation_type,
            content=processed_content,
            position_marker=kwargs.get("position_marker"),
            backup_enabled=kwargs.get("backup_enabled", True),
            dry_run=kwargs.get("dry_run", False),
            validate_content=kwargs.get("validate_content", True),
            framework_context=framework_context,
            arguments=kwargs,
        )

    def execute_with_logging(self, context: OperationContext) -> OperationResult:
        """Execute operation with comprehensive logging, retry, and debug capabilities"""
        start_time = time.time()
        operation_name = f"{self.operation_type.value.upper()}"

        # Inicializar debug analyzer si está disponible
        debug_analyzer = None
        if (
            INTEGRATION_AVAILABLE
            and PatternDebugger
            and context.arguments.get("debug_mode", False)
        ):
            debug_analyzer = PatternDebugger(verbose=True)
            if INTEGRATION_AVAILABLE and logger:
                logger.info("🔍 Debug mode activated for pattern analysis")

        if INTEGRATION_AVAILABLE and logger:
            logger.operation_start(
                f"Operation {operation_name}", f"Target: {context.target_file}"
            )

        # Definir función de ejecución para retry
        def _execute_operation():
            validation_errors = self.validate_context(context)
            if validation_errors:
                error_msg = f"Context validation failed: {'; '.join(validation_errors)}"
                raise ValueError(error_msg)

            # Debug pattern analysis si está habilitado
            if debug_analyzer and hasattr(context, "pattern") and context.pattern:
                debug_info = debug_analyzer.debug_pattern_matching(
                    file_path=str(context.target_file),
                    pattern=context.pattern,
                    content_preview=True,
                )
                if INTEGRATION_AVAILABLE and logger:
                    logger.info(
                        f"🔍 Pattern analysis: {len(debug_info['matches_found'])} matches found"
                    )

            if context.dry_run:
                if INTEGRATION_AVAILABLE and logger:
                    logger.info("DRY RUN: Operation simulation")
                return self._simulate_execution(context)
            else:
                return self.execute(context)

        try:
            self.execution_stats["total_executions"] += 1

            # Aplicar retry si está disponible y habilitado
            if (
                INTEGRATION_AVAILABLE
                and retry_with_backoff
                and context.arguments.get("enable_retry", True)
            ):

                # Configurar retry basado en argumentos
                max_attempts = context.arguments.get("retry_attempts", 3)
                base_delay = context.arguments.get("retry_delay", 1.0)

                @retry_with_backoff(max_attempts=max_attempts, base_delay=base_delay)
                def retry_execution():
                    return _execute_operation()

                result = retry_execution()
            else:
                result = _execute_operation()

            result.execution_time = time.time() - start_time
            result.operation_name = self.operation_name
            result.arguments_used = context.arguments

            if result.success:
                self.execution_stats["successful_executions"] += 1
                if INTEGRATION_AVAILABLE and logger:
                    logger.operation_end(f"Operation {operation_name}", success=True)
                    logger.success(result.message)
            else:
                self.execution_stats["failed_executions"] += 1
                if INTEGRATION_AVAILABLE and logger:
                    logger.operation_end(f"Operation {operation_name}", success=False)
                    logger.error(result.message)

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            self.execution_stats["failed_executions"] += 1
            self.execution_stats["total_execution_time"] += execution_time

            # Análisis detallado de fallos con nuevo sistema
            if (
                INTEGRATION_AVAILABLE
                and logger
                and hasattr(logger, "detailed_failure_analysis")
            ):
                failure_context = {
                    "operation": operation_name,
                    "file": str(context.target_file),
                    "pattern": getattr(context, "pattern", None),
                    "content_length": len(getattr(context, "content", "") or ""),
                    "arguments": context.arguments,
                }

                analysis = logger.detailed_failure_analysis(e, context=failure_context)
                error_category = logger.log_operation_failure(
                    operation_name=operation_name,
                    error=e,
                    file_path=str(context.target_file),
                    pattern=getattr(context, "pattern", None),
                )

                error_msg = f"Operation failed [{error_category}]: {str(e)}"
            else:
                error_msg = f"Operation failed with exception: {str(e)}"

            if INTEGRATION_AVAILABLE and logger:
                logger.operation_end(f"Operation {operation_name}", success=False)
                logger.error(error_msg)

            return OperationResult(
                success=False,
                operation_type=self.operation_type,
                target_path=str(context.target_file),
                message=error_msg,
                details={"exception": str(e), "exception_type": type(e).__name__},
                execution_time=execution_time,
                operation_name=self.operation_name,
            )

    def execute_v53_compatible(self, arguments: Dict[str, Any]) -> OperationResult:
        """
        Execute operation with v5.3 compatibility layer.

        Converts v5.3 style arguments to current OperationContext format.

        Args:
            arguments: Dictionary with v5.3 style arguments

        Returns:
            OperationResult compatible with both v5.3 and current version
        """
        try:
            # Extract v5.3 arguments
            target_file = Path(arguments.get("target_file", ""))
            content = arguments.get("content", "")
            position_marker = arguments.get("position_marker", "")

            # Remove v5.3 specific keys from arguments for context
            context_args = {
                k: v
                for k, v in arguments.items()
                if k not in ["target_file", "content", "position_marker"]
            }

            # Create OperationContext from v5.3 arguments with required fields
            context = OperationContext(
                project_root=Path("."),  # Default to current directory
                target_file=target_file,
                operation_type=self.operation_type,
                content=content,
                position_marker=position_marker,
                arguments=context_args,
            )

            # Execute with current interface
            return self.execute_with_logging(context)

        except Exception as e:
            return OperationResult(
                success=False,
                operation_type=self.operation_type,
                target_path=str(arguments.get("target_file", "")),
                message=f"v5.3 compatibility error: {e}",
                details={"v53_compatibility_error": str(e)},
                execution_time=0.0,
                operation_name=self.operation_name,
            )

    def _simulate_execution(self, context: OperationContext) -> OperationResult:
        """Simulate operation execution for dry run mode"""
        return OperationResult(
            success=True,
            operation_type=self.operation_type,
            target_path=str(context.target_file),
            message=f"DRY RUN: {self.operation_type.value} operation would be executed",
            details={
                "dry_run": True,
                "would_create_backup": context.backup_enabled
                and context.target_file.exists(),
                "content_length": len(context.content) if context.content else 0,
            },
            execution_time=0.001,
            operation_name=self.operation_name,
        )


class OperationError(Exception):
    """Base exception for operation errors"""

    def __init__(
        self,
        message: str,
        operation_type: OperationType,
        target_file: Optional[str] = None,
        details: Optional[Dict] = None,
    ):
        super().__init__(message)
        self.operation_type = operation_type
        self.target_file = target_file
        self.details = details or {}


class ValidationError(OperationError):
    """Exception for context validation errors"""

    pass


class ContentError(OperationError):
    """Error related to content processing"""

    pass


class FileSystemError(OperationError):
    """Exception for file system related errors"""

    pass
