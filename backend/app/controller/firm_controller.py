from datetime import datetime
from fastapi import HTTPException
from app.models.firm import FirmModel
from app.schema.firm_schema import AddPublisherSchema
from app.models.users import UserModel, UserRole
from app.controller.util_controller import UtilController
from typing import Optional


class FirmController:
    
    async def create_firm(self, firm_data: FirmModel, user:UserModel, user_id: str) -> Optional[FirmModel]:
        """
        Create a firm for a user. Returns FirmModel on success, None on failure.
        No HTTPException raised here.
        """
        try:
            util_controller = UtilController()
            while True:
                username = await util_controller.generate_username(
                    firstname=None,
                    lastname=None,
                    firmname=firm_data.firm_name
                )
                existing = await util_controller.check_username_exists(username)
                if not existing:
                    break

            # 4️⃣ Prepare firm data
            firm_data_dict = firm_data.dict(exclude_unset=True)
            firm_data_dict["owner_user_id"] = user  # Link to UserModel
            firm_data_dict["firm_username"] = username
            # firm_data_dict["created_at"] = datetime.now()

            firm = FirmModel(**firm_data_dict)
            
            registered_firm = await firm.insert()
            if not registered_firm:
                return None


            # 6️⃣ Assign roles
            if UserRole.founder not in user.role:
                user.role.append(UserRole.founder)
            if UserRole.publisher not in user.role:
                user.role.append(UserRole.publisher)
            await user.save()

            return registered_firm

        except Exception as e:
            print("Error registering firm:", e)
            return None
        
        

        
   # async def register_firm(self, firm_data) -> bool:
    #     try:
    #         firm = FirmModel(**firm_data.dict())
    #         await firm.insert()
    #         ###############  add role as F in user model    ######################
    #         return True
    #     except Exception as e:
    #         print("Error registering firm:", e)
    #         return False
    
    # async def create_firm(self, firm_data:FirmCreateSchema, user_id:str) -> bool:
    #     try:
            
    #         user = await UserModel.get(user_id)
    #         if user:
    #             firm_data_dict = firm_data.dict()
    #             firm_data_dict['owner_user_id'] = user_id

    #             firm = FirmModel(**firm_data_dict)
    #             register_firm = await firm.insert()
    #             if register_firm is None:
    #                 return False
    #             print("Registered Firm:", register_firm.firm_username)
    #             pub_data = {
    #                 "firm_username": register_firm.firm_username,   
    #                 "publisher_username": user.username,
                    
    #             }
    #             # 
    #             register_firm.publishers = [await self.add_publisher(AddPublisherSchema(**pub_data))]
    #             await firm.save()
                
    #             if UserRole.founder not in user.role:
    #                 user.role.append(UserRole.founder)
    #                 if UserRole.publisher not in user.role:
    #                     user.role.append(UserRole.publisher)
    #                 await user.save()
    #             return True
                
    #     except Exception as e:
    #         print("Error registering firm:", e)
    #         return False

    # async def create_firm(self, firm_data: FirmCreateSchema, user_id: str) -> bool:
    #     try:
    #         # 1️⃣ Fetch user
    #         user = await UserModel.get(user_id)
    #         if not user or not user.is_verified or not user.is_active:
    #             raise HTTPException(403, "User not eligible")

    #         # 2️⃣ KYC check (THIS IS THE KEY PART)
    #         kyc = await KYCModel.find_one(KYCModel.user_id == user)
    #         if not kyc or kyc.kyc_status != "VERIFIED":
    #             raise HTTPException(403, "KYC required to create firm")

    #         # 3️⃣ Create firm
    #         firm_data_dict = firm_data.dict(exclude_unset=True)
    #         firm_data_dict["owner_user_id"] = user  # <-- pass UserModel

    #         firm = FirmModel(**firm_data_dict)
    #         register_firm = await firm.insert()

    #         if not register_firm:
    #             return False

    #         # 4️⃣ Add creator as publisher
    #         pub_data = {
    #             "firm_username": register_firm.firm_username,
    #             "publisher_username": user.username,
    #         }

    #         register_firm.publishers = [
    #             await self.add_publisher(AddPublisherSchema(**pub_data))
    #         ]
    #         await register_firm.save()

    #         # 5️⃣ Assign roles
    #         if UserRole.founder not in user.role:
    #             user.role.append(UserRole.founder)
    #         if UserRole.publisher not in user.role:
    #             user.role.append(UserRole.publisher)

    #         await user.save()
    #         return True

    #     except HTTPException:
    #         raise
    #     except Exception as e:
    #         print("Error registering firm:", e)
    #         return False
