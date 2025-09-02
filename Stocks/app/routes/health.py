"""
Health check routes for monitoring system status.

This module contains endpoints for checking the health of various
system components and services.
"""

import logging
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..services.stock_service import StockService
from ..services.sms_service import SMSService
from ..services.chatbot_service import ChatbotService
from ..services.agent_service import AgentService
from ..services.scheduler_service import SchedulerService

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/health", tags=["health"])

# Service instances (in production, use dependency injection)
stock_service = StockService()
sms_service = SMSService()
chatbot_service = ChatbotService()
agent_service = AgentService()
scheduler_service = SchedulerService()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns:
        Basic system health status
    """
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "AI Stock Tracking Agent",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check for all system components.
    
    Returns:
        Detailed health status for all services
    """
    try:
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {}
        }
        
        # Check stock service
        try:
            stock_status = {
                "status": "healthy",
                "cache_stats": stock_service.get_cache_stats(),
                "service": "Stock Service"
            }
        except Exception as e:
            stock_status = {
                "status": "unhealthy",
                "error": str(e),
                "service": "Stock Service"
            }
            health_status["overall_status"] = "degraded"
        
        health_status["services"]["stock_service"] = stock_status
        
        # Check SMS service
        try:
            sms_status = sms_service.get_service_status()
            sms_status["status"] = "healthy"
        except Exception as e:
            sms_status = {
                "status": "unhealthy",
                "error": str(e),
                "service": "SMS Service"
            }
            health_status["overall_status"] = "degraded"
        
        health_status["services"]["sms_service"] = sms_status
        
        # Check chatbot service
        try:
            chatbot_status = chatbot_service.get_service_status()
            chatbot_status["status"] = "healthy"
        except Exception as e:
            chatbot_status = {
                "status": "unhealthy",
                "error": str(e),
                "service": "Chatbot Service"
            }
            health_status["overall_status"] = "degraded"
        
        health_status["services"]["chatbot_service"] = chatbot_status
        
        # Check agent service
        try:
            agent_status = agent_service.get_service_status()
            agent_status["status"] = "healthy"
        except Exception as e:
            agent_status = {
                "status": "unhealthy",
                "error": str(e),
                "service": "Agent Service"
            }
            health_status["overall_status"] = "degraded"
        
        health_status["services"]["agent_service"] = agent_status
        
        # Check scheduler service
        try:
            scheduler_status = scheduler_service.get_scheduler_status()
            scheduler_status["status"] = "healthy"
        except Exception as e:
            scheduler_status = {
                "status": "unhealthy",
                "error": str(e),
                "service": "Scheduler Service"
            }
            health_status["overall_status"] = "degraded"
        
        health_status["services"]["scheduler_service"] = scheduler_status
        
        # Determine HTTP status code
        status_code = 200
        if health_status["overall_status"] == "degraded":
            status_code = 207  # Multi-status
        elif health_status["overall_status"] == "unhealthy":
            status_code = 503  # Service unavailable
        
        return JSONResponse(content=health_status, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Health check failed")


@router.get("/services")
async def services_health_check() -> Dict[str, Any]:
    """
    Health check for individual services.
    
    Returns:
        Health status for each service
    """
    try:
        services = {}
        
        # Stock Service
        try:
            services["stock_service"] = {
                "status": "healthy",
                "cache_entries": len(stock_service._cache),
                "cache_ttl": stock_service._cache_ttl
            }
        except Exception as e:
            services["stock_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # SMS Service
        try:
            services["sms_service"] = sms_service.get_service_status()
        except Exception as e:
            services["sms_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Chatbot Service
        try:
            services["chatbot_service"] = chatbot_service.get_service_status()
        except Exception as e:
            services["chatbot_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Agent Service
        try:
            services["agent_service"] = agent_service.get_service_status()
        except Exception as e:
            services["agent_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Scheduler Service
        try:
            services["scheduler_service"] = scheduler_service.get_scheduler_status()
        except Exception as e:
            services["scheduler_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "services": services
        }
        
    except Exception as e:
        logger.error(f"Services health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Services health check failed")


@router.get("/readiness")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check for Kubernetes/container orchestration.
    
    Returns:
        Readiness status
    """
    try:
        # Check if all critical services are ready
        critical_services = ["stock_service", "sms_service", "chatbot_service"]
        ready_services = []
        not_ready_services = []
        
        # Check stock service
        try:
            # Simple validation - check if service can be instantiated
            stock_service.get_cache_stats()
            ready_services.append("stock_service")
        except:
            not_ready_services.append("stock_service")
        
        # Check SMS service
        try:
            sms_service.get_service_status()
            ready_services.append("sms_service")
        except:
            not_ready_services.append("sms_service")
        
        # Check chatbot service
        try:
            chatbot_service.get_service_status()
            ready_services.append("chatbot_service")
        except:
            not_ready_services.append("chatbot_service")
        
        is_ready = len(not_ready_services) == 0
        
        return {
            "ready": is_ready,
            "timestamp": datetime.utcnow().isoformat(),
            "ready_services": ready_services,
            "not_ready_services": not_ready_services,
            "critical_services": critical_services
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {
            "ready": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/liveness")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check for Kubernetes/container orchestration.
    
    Returns:
        Liveness status
    """
    try:
        # Simple liveness check - if we can respond, we're alive
        return {
            "alive": True,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": "N/A",  # In production, calculate actual uptime
            "memory_usage": "N/A",  # In production, get actual memory usage
            "cpu_usage": "N/A"  # In production, get actual CPU usage
        }
        
    except Exception as e:
        logger.error(f"Liveness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service not alive")


@router.get("/metrics")
async def metrics_endpoint() -> Dict[str, Any]:
    """
    Basic metrics endpoint for monitoring.
    
    Returns:
        System metrics
    """
    try:
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "uptime": "N/A",
                "memory_usage": "N/A",
                "cpu_usage": "N/A"
            },
            "application": {
                "total_requests": "N/A",
                "error_rate": "N/A",
                "response_time_avg": "N/A"
            },
            "business": {
                "stocks_tracked": 0,  # In production, get from database
                "alerts_sent": 0,  # In production, get from database
                "sms_messages": 0  # In production, get from database
            }
        }
        
        # Add service-specific metrics
        try:
            cache_stats = stock_service.get_cache_stats()
            metrics["stock_service"] = {
                "cache_entries": cache_stats["total_entries"],
                "cache_hit_rate": "N/A"
            }
        except:
            metrics["stock_service"] = {"error": "Unable to get metrics"}
        
        try:
            scheduler_status = scheduler_service.get_scheduler_status()
            metrics["scheduler"] = {
                "is_running": scheduler_status["is_running"],
                "check_count": scheduler_status["check_count"],
                "scheduled_tasks": scheduler_status["scheduled_tasks"]
            }
        except:
            metrics["scheduler"] = {"error": "Unable to get metrics"}
        
        return metrics
        
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Metrics unavailable")
