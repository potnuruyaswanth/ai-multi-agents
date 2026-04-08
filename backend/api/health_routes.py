from fastapi import APIRouter, HTTPException
from config.settings import get_settings
from database.repository import Repository
import asyncio
from datetime import datetime

router = APIRouter(tags=["Health & Monitoring"])
settings = get_settings()

class HealthCheck:
    @staticmethod
    async def check_database() -> dict:
        """Check database connectivity"""
        try:
            repo = Repository()
            # Try to access a test collection
            users = await repo.list_users()
            return {
                "status": "healthy",
                "backend": settings.storage_backend,
                "latency_ms": 0
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "backend": settings.storage_backend,
                "error": str(e)
            }
    
    @staticmethod
    async def check_google_oauth() -> dict:
        """Check Google OAuth configuration"""
        try:
            client_id = settings.google_oauth_client_id
            client_secret = settings.google_oauth_client_secret
            redirect_uri = settings.google_oauth_redirect_uri
            
            if not all([client_id, client_secret, redirect_uri]):
                return {"status": "incomplete", "message": "OAuth credentials not fully configured"}
            
            return {"status": "configured", "client_id": client_id[:10] + "..."}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    @staticmethod
    async def check_smtp() -> dict:
        """Check SMTP configuration"""
        try:
            import smtplib
            
            smtp_host = settings.smtp_host
            smtp_port = settings.smtp_port
            smtp_user = settings.smtp_user
            
            if not all([smtp_host, smtp_port, smtp_user]):
                return {"status": "incomplete"}
            
            # Try to connect (without sending email)
            try:
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=5)
                server.starttls()
                server.quit()
                return {"status": "configured", "host": smtp_host}
            except Exception as connect_error:
                return {"status": "connection_failed", "error": str(connect_error)}
        except Exception as e:
            return {"status": "error", "error": str(e)}

@router.get("/health")
async def health_check():
    """Main health check endpoint"""
    db_health = await HealthCheck.check_database()
    oauth_health = await HealthCheck.check_google_oauth()
    smtp_health = await HealthCheck.check_smtp()
    
    overall_status = "healthy" if db_health["status"] == "healthy" else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "database": db_health,
            "oauth": oauth_health,
            "smtp": smtp_health
        }
    }

@router.get("/health/deep")
async def deep_health_check():
    """Comprehensive health check with diagnostics"""
    
    checks = {
        "database": await HealthCheck.check_database(),
        "oauth": await HealthCheck.check_google_oauth(),
        "smtp": await HealthCheck.check_smtp(),
        "config": {
            "app_name": settings.app_name,
            "api_prefix": settings.api_prefix,
            "storage_backend": settings.storage_backend,
            "location": settings.google_location
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Determine overall status
    unhealthy_components = [
        k for k, v in checks.items() 
        if isinstance(v, dict) and v.get("status") == "unhealthy"
    ]
    
    overall_status = "healthy" if not unhealthy_components else "unhealthy"
    
    return {
        "status": overall_status,
        "unhealthy_components": unhealthy_components,
        "checks": checks
    }

@router.get("/metrics")
async def metrics():
    """Application metrics endpoint"""
    from datetime import datetime, timedelta
    
    try:
        repo = Repository()
        
        # Get user count
        users = await repo.list_users()
        user_count = len(users) if users else 0
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_check": "ok",
            "metrics": {
                "total_users": user_count,
                "api_version": "1.0.0"
            }
        }
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.get("/version")
async def version():
    """Get application version and build info"""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "build_timestamp": datetime.utcnow().isoformat(),
        "environment": "production" if settings.storage_backend == "firestore" else "development",
        "api_version": settings.api_prefix
    }
