import hmac
import hashlib
import os

import os
import shutil
from datetime import datetime
from bson import ObjectId
from app.config import settings
from fastapi import UploadFile
from app.models.kyc import KYCModel

# SECRET_KEY = os.getenv("KYC_FINGERPRINT_SECRET", "dev-secret-change-this")



class KYCController:
    
    @staticmethod
    def generate_id_fingerprint( kyc_data:dict ) -> str:
        """
        Generates irreversible fingerprint for government ID
        """
        # Normalize input
        try:
            raw = (
                f"{kyc_data['id_type'].upper()}|"
                f"{kyc_data['id_last4']}|"
                f"{kyc_data['dob']}|"
                f"{kyc_data['name_on_id'].lower()}"
                )
            
            # id_type = kyc_data['id_type'].upper().strip()
            # id_last4 = kyc_data['id_last4'].strip()
            # dob = kyc_data['dob'].strip()
            # name_on_id = kyc_data['name_on_id'].strip()
            
            # raw = f"{id_type}|{id_last4}|{dob}|{name_on_id.lower().strip()}"

            fingerprint = hmac.new(
                key=settings.KYC_FINGERPRINT_SECRET.encode(),
                msg=raw.encode(),
                digestmod=hashlib.sha256
            ).hexdigest()

            return fingerprint
        except Exception as e:
            print(str(e))
            return False

    async def create_kyc(self, kyc_data, fingerprint, file: UploadFile, current_user):
        # Implementation for creating KYC record
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = (
                f"{current_user['username']}_"
                f"{kyc_data['id_type']}_"
                f"{timestamp}_"
                f"{file.filename}"
            )
            file_path = os.path.join(settings.KYC_UPLOAD_FOLDER, filename)
            
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
            
            kyc = KYCModel(
                user_id=ObjectId(current_user["user_id"]),
                id_type=kyc_data["id_type"],
                id_last4=kyc_data["id_last4"],
                dob=kyc_data["dob"],
                name_on_id=kyc_data["name_on_id"],
                id_fingerprint=fingerprint,
                id_document_path=f"images/kyc/{filename}",
                kyc_status="PENDING"
            )
            await kyc.insert()
            return True
        
        except Exception as e:
            print(str(e))
            return False