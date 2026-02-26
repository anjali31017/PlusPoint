import hmac
import hashlib
import os

import os
import shutil
from datetime import datetime, timezone
from bson import ObjectId
from app.config import settings
from fastapi import UploadFile
from app.models.kyc import KYCModel

# SECRET_KEY = os.getenv("KYC_FINGERPRINT_SECRET", "dev-secret-change-this")



class KYCController:
    
    @staticmethod
    def generate_id_fingerprint( id_type:str, id_last4:str , dob:str, name_on_id:str  ) -> str:
        """
        Generates irreversible fingerprint for government ID
        """
        # Normalize input
        try:
            # raw = (
            #     f"{kyc_data['id_type'].upper()}|"
            #     f"{kyc_data['id_last4']}|"
            #     f"{kyc_data['dob']}|"
            #     f"{kyc_data['name_on_id'].lower()}"
            #     )
            
            # id_type = kyc_data['id_type'].upper().strip()
            # id_last4 = kyc_data['id_last4'].strip()
            # dob = kyc_data['dob'].strip()
            # name_on_id = kyc_data['name_on_id'].strip()
            
            raw = f"{id_type}|{id_last4}|{dob}|{name_on_id.lower().strip()}"

            fingerprint = hmac.new(
                key=settings.KYC_FINGERPRINT_SECRET.encode(),
                msg=raw.encode(),
                digestmod=hashlib.sha256
            ).hexdigest()

            return fingerprint
        except Exception as e:
            print(str(e))
            return False

    async def create_kyc(self, 
                         id_type:str, id_last4:str, dob:str, name_on_id:str, 
                         fingerprint:str, file: UploadFile, current_user:dict):
        # Implementation for creating KYC record
        try:
            os.makedirs(settings.KYC_UPLOAD_FOLDER, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            ext = os.path.splitext(file.filename)[1]

            safe_username = "".join(x for x in current_user['username'] if x.isalnum())
            safe_id_type = "".join(x for x in id_type if x.isalnum())

            filename = f"{safe_username}_{safe_id_type}_{timestamp}{ext}"
            file_path = os.path.join(settings.KYC_UPLOAD_FOLDER, filename)
        
            # filename = (
            #     f"{current_user['username']}_"
            #     f"{id_type}_"
            #     f"{timestamp}{ext}"
            # )
            # file_path = os.path.join(settings.KYC_UPLOAD_FOLDER, filename)
            
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
                print("File saved:", file_path, os.path.exists(file_path))

            
            kyc = KYCModel(
                user_id=ObjectId(current_user["user_id"]),
                id_type=id_type,
                id_last4=id_last4,
                dob=dob,
                name_on_id=name_on_id,
                id_fingerprint=fingerprint,
                id_document_path=f"images/kyc/{filename}",
                kyc_status="UNDER_REVIEW",
                kyc_consent=True,
            )
            await kyc.insert()
            return True
        
        except Exception as e:
            print(str(e))
            return False