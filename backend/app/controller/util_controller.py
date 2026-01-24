from fastapi import HTTPException
from typing import Optional
from bson import ObjectId
from app.models.users import UserModel, UserRole
import random
from app.models.firm import FirmModel
from app.models.subscription import SubscriptionModel
from app.controller.email_controller import is_user_blocked
from app.models.article import ArticleModel

class UtilController:
    
    async def check_username_exists(self, username: str) -> Optional[UserModel | FirmModel]:
        try:
            print("Checking username:", username)
            
            # Querying the users collection
            username_in_users = await UserModel.find_one(
                UserModel.username == username,
                UserModel.is_deleted == False,
                UserModel.is_verified == True
                )
            if username_in_users:
                return username_in_users  # Return the user document if found

            # Querying the firms collection
            username_in_firms = await FirmModel.find_one(
                FirmModel.firm_username == username,
                FirmModel.is_deleted == False
                )
            if username_in_firms:
                return username_in_firms  # Return the firm document if found

            # If neither user nor firm is found
            return None 

        except Exception as e:
            print(f"Error checking username existence: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    
    async def generate_username(self, firstname:str|None, lastname:str|None, firmname:str|None) -> str:
        try:
            # Generate a random 10-digit number
            # random_number = random.randint(10**9, 10**10 - 1)
            
            num_digits = random.randint(3, 6)
            random_number = random.randint(10**(num_digits - 1), 10**num_digits - 1)
            if firmname:
                username = firmname.lower().replace(" ", "_") +"_"+ str(random_number)
                return username
            if lastname is None:
                username = firstname.lower() +"_"+ str(random_number)
            username = firstname.lower() +"_"+ lastname.lower() +"_"+ str(random_number)
            
            # user = await self.check_username_exists(username)
            # if user and user.is_verified == True:
            #     raise HTTPException(status_code=400, detail="Username already exists")
            
            return username
        except Exception as e:
            print("Error generating username:", e)
            raise HTTPException(status_code=500, detail="Internal server error")
        
