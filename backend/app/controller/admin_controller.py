from datetime import datetime

from bson import ObjectId
from app.models.admin import AdminModel

from app.controller.util_controller import UtilController

from fastapi import Depends, Request, HTTPException, status

from app.models.kyc import KYCModel
from app.models.firm import FirmModel


def admin_required(request: Request):
    admin_id = request.session.get("admin_id")
    if not admin_id:
        raise HTTPException(status_code=403, detail="Admin access required")
    return admin_id



class AdminController:
    
    async def create_admin(self, admin_data:dict) -> AdminModel | None:
        try:
            
            admin_exists = await AdminModel.find_one(
                AdminModel.email == admin_data['email'],
                AdminModel.is_deleted == False
            )
            
            if admin_exists and admin_exists.is_verified == True:
                return None
            

            admin = AdminModel(**admin_data)
            admin.password_hash = AdminModel.hash_detail(admin_data['password'])
            await admin.insert()
            return admin
        except Exception as e:
            print(str(e))
            return None

    
    
    
    # async def get_kyc(self):
    #     try: 
    #         kyc_data = await KYCModel.find(KYCModel.kyc_status == "UNDER_REVIEW").to_list()
    #         if not kyc_data or len(kyc_data) == 0:
    #             return []
    #         kyc_list = [item.dict() for item in kyc_data]
    #         return kyc_list
    #     except Exception as e:
    #         print(str(e))
    #         return []

    async def get_kyc(self):
        try: 
            kyc_data = await KYCModel.find(KYCModel.kyc_status == "UNDER_REVIEW").to_list()
            if not kyc_data:
                return []

            # # Convert each document to dict and convert ObjectId to str
            # kyc_list = []
            # for item in kyc_data:
            #     item_dict = item.dict()
            #     # Convert ObjectId to str for JSON serialization
            #     item_dict["id"] = str(item.id)
            #     kyc_list.append(item_dict)

            # return kyc_list
            return kyc_data
        except Exception as e:
            print("Error fetching KYC:", e)
            return []
        
    async def approve_kyc(self, user_id: str):
        try:
            id = ObjectId("696800f1d775ff4ccac9b04b")
            kyc_record = await KYCModel.find( 
                                                 KYCModel.id == id,
                # KYCModel.user_id.id == ObjectId(user_id), 
                # KYCModel.kyc_status == "UNDER_REVIEW"
                                                 )
            # kyc_record = await KYCModel.find(KYCModel.kyc_status == "UNDER_REVIEW")
            
            if not kyc_record:
                return None
            
            # kyc_record.kyc_status = "VERIFIED"
            # kyc_record.reviewed_at = datetime.now()
            # kyc_record.updated_at = datetime.now()
            # await kyc_record.save()
            return kyc_record
        except Exception as e:
            print(str(e))
            return None

    async def reject_kyc(self, user_id: str, reason: str):
        try:
            kyc_record = await KYCModel.find_one(KYCModel.user_id.id == user_id)
            if not kyc_record:
                return None
            kyc_record.kyc_status = "REJECTED"
            kyc_record.rejection_reason = reason
            kyc_record.reviewed_at = datetime.now()
            kyc_record.updated_at = datetime.now()
            await kyc_record.save()
            return kyc_record
        except Exception as e:
            print(str(e))
            return None




    async def get_firms(self):
        try: 
            firm_data = await FirmModel.find(KYCModel.verification_status == "UNDER_REVIEW").to_list()
            if not firm_data:
                return []

            # # Convert each document to dict and convert ObjectId to str
            # kyc_list = []
            # for item in kyc_data:
            #     item_dict = item.dict()
            #     # Convert ObjectId to str for JSON serialization
            #     item_dict["id"] = str(item.id)
            #     kyc_list.append(item_dict)

            # return kyc_list
            return firm_data
        except Exception as e:
            print("Error fetching KYC:", e)
            return []