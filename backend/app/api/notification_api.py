
from bson import ObjectId
from fastapi import APIRouter, Depends, File, UploadFile,Form
from app.models.kyc import KYCModel
from fastapi import APIRouter, Depends, HTTPException
from app.controller.token_controller import get_current_user
from app.schema.base_schema import BaseResponse
from fastapi import status
from app.schema.kyc_schema import KYCSchema
from app.controller.kyc_controller import KYCController
import os
from app.models.notification import NotificationModel
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/unread_count")
async def get_unread_count(current_user: dict = Depends(get_current_user)):
    count = await NotificationModel.find({"send_to": ObjectId(current_user["user_id"]), "read_at": None}).count()
    return {"count": count}


@router.post("/mark_read")
async def mark_notifications_read(notification_ids: list[str], current_user: dict = Depends(get_current_user)):

    try:
        obj_ids = [ObjectId(nid) for nid in notification_ids]
        await NotificationModel.find(
            {"_id": {"$in": obj_ids}, "send_to": ObjectId(current_user["user_id"])}
        ).update({"$set": {"read_at": datetime.utcnow()}})
        return {"status": 1, "message": "Marked as read"}
    except Exception as e:
        return {"status": 0, "message": str(e)}
