"""
Prometheus metrics endpoint for MeStore monitoring

This endpoint exposes metrics in Prometheus text format for scraping.
In production, this endpoint should be protected via:
- IP whitelist (only allow Prometheus server)
- Internal network only
- API key authentication

Security Note:
-------------
The /metrics endpoint exposes operational metrics but no sensitive data.
However, it should still be restricted to monitoring infrastructure only.
"""

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from typing import Optional
from app.core.logger import get_logger
from app.core.config import settings

router = APIRouter()
logger = get_logger(__name__)

# Metrics endpoint API key (set in environment for production)
METRICS_API_KEY = getattr(settings, 'METRICS_API_KEY', None)


@router.get(
    "/metrics",
    response_class=PlainTextResponse,
    summary="Prometheus metrics endpoint",
    description="Exposes metrics in Prometheus text format for monitoring",
    tags=["monitoring"]
)
async def metrics_endpoint(
    authorization: Optional[str] = Header(None)
):
    """
    Prometheus metrics endpoint

    Returns all registered Prometheus metrics in text format suitable for
    scraping by Prometheus server.

    Security:
    ---------
    - In production, protect this endpoint with:
      1. IP whitelist (nginx/load balancer level)
      2. Internal network only access
      3. Optional API key authentication (set METRICS_API_KEY env var)

    Returns:
    --------
    Prometheus text format metrics including:
    - SMS send performance (sms_send_requests_total, sms_send_duration_seconds)
    - SMS verification success (sms_verification_attempts_total)
    - Twilio API health (twilio_api_calls_total, twilio_api_errors_total)
    - Redis performance (redis_rate_limit_checks_total, redis_errors_total)
    - Registration flow metrics (registration_flow_events_total)
    - Cost tracking (twilio_cost_usd_total)

    Example Prometheus scrape config:
    ----------------------------------
    ```yaml
    scrape_configs:
      - job_name: 'mestore'
        static_configs:
          - targets: ['mestore-backend:8000']
        metrics_path: '/api/v1/metrics'
        scrape_interval: 15s

        # Optional: Add API key authentication
        # authorization:
        #   type: Bearer
        #   credentials: your-metrics-api-key
    ```
    """

    # Optional API key authentication (if configured)
    if METRICS_API_KEY:
        if not authorization:
            logger.warning("Metrics endpoint accessed without authentication")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Check authorization header format: "Bearer <token>"
        auth_parts = authorization.split()
        if len(auth_parts) != 2 or auth_parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Use: Bearer <token>"
            )

        provided_key = auth_parts[1]
        if provided_key != METRICS_API_KEY:
            logger.warning("Metrics endpoint accessed with invalid API key")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )

    try:
        # Generate Prometheus metrics in text format
        metrics_output = generate_latest(REGISTRY)

        logger.debug("Metrics endpoint scraped successfully")

        return PlainTextResponse(
            content=metrics_output,
            media_type=CONTENT_TYPE_LATEST
        )

    except Exception as e:
        logger.error(f"Error generating metrics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating metrics"
        )


@router.get(
    "/metrics/health",
    summary="Metrics system health check",
    tags=["monitoring"]
)
async def metrics_health():
    """
    Health check for metrics system

    Returns basic information about the metrics collection system.
    This endpoint is safe to expose publicly as it doesn't contain sensitive data.
    """
    try:
        from app.core.monitoring import get_all_metrics

        # Count registered metrics
        all_metrics = get_all_metrics()

        return {
            "status": "healthy",
            "metrics_registered": len(all_metrics),
            "collection_active": True,
            "prometheus_registry": "active"
        }

    except Exception as e:
        logger.error(f"Error checking metrics health: {str(e)}")
        return {
            "status": "degraded",
            "error": str(e)
        }


@router.get(
    "/metrics/summary",
    summary="Metrics summary (development only)",
    tags=["monitoring"]
)
async def metrics_summary():
    """
    Get a human-readable summary of current metrics

    WARNING: This endpoint is for development/debugging only.
    It should be disabled in production as it may expose operational data.
    """

    # Only enable in development
    if settings.ENVIRONMENT.lower() not in ['development', 'dev', 'testing']:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not available in production"
        )

    try:
        from prometheus_client.parser import text_string_to_metric_families

        # Get raw metrics
        metrics_output = generate_latest(REGISTRY).decode('utf-8')

        # Parse metrics for summary
        summary = {
            "sms_metrics": [],
            "twilio_metrics": [],
            "redis_metrics": [],
            "registration_metrics": []
        }

        for family in text_string_to_metric_families(metrics_output):
            metric_info = {
                "name": family.name,
                "type": family.type,
                "documentation": family.documentation
            }

            # Categorize metrics
            if 'sms' in family.name:
                summary["sms_metrics"].append(metric_info)
            elif 'twilio' in family.name:
                summary["twilio_metrics"].append(metric_info)
            elif 'redis' in family.name:
                summary["redis_metrics"].append(metric_info)
            elif 'registration' in family.name:
                summary["registration_metrics"].append(metric_info)

        return summary

    except Exception as e:
        logger.error(f"Error generating metrics summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating summary"
        )
