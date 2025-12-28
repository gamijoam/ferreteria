from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database.db import get_db
from ..services import sync_client

router = APIRouter(prefix="/sync-local", tags=["sync-local"])

@router.post("/trigger")
async def trigger_manual_sync(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Called by Desktop App Frontend to start a full sync from VPS.
    """
    try:
        # We run this synchronously for now to report immediate errors, 
        # or use background tasks if it takes too long.
        # For a "Loading..." spinner on frontend, sync is better for MVP.
        
        pull_result = await sync_client.pull_catalog_from_cloud(db)
        
        # 2. Push Pending Sales
        push_result = await sync_client.push_sales_to_cloud(db)
        
        return {
            "message": "Sincronización completada", 
            "details": {
                "pull": pull_result,
                "push": push_result
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
