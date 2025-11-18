from datetime import datetime
from fastapi import HTTPException
from app.models.firm import FirmModel, PublisherInfo
from app.schema.firm_schema import AddPublisherSchema, FirmRegisterSchema
from app.models.users import UserModel, UserRole

class FirmController:
    
    # async def register_firm(self, firm_data) -> bool:
    #     try:
    #         firm = FirmModel(**firm_data.dict())
    #         await firm.insert()
    #         ###############  add role as F in user model    ######################
    #         return True
    #     except Exception as e:
    #         print("Error registering firm:", e)
    #         return False
    
    async def register_firm(self, firm_data:FirmRegisterSchema, user_id:str) -> bool:
        try:
            
            user = await UserModel.get(user_id)
            if user:
                firm_data_dict = firm_data.dict()
                firm_data_dict['firm_user_id'] = user_id

                firm = FirmModel(**firm_data_dict)
                register_firm = await firm.insert()
                if register_firm is None:
                    return False
                print("Registered Firm:", register_firm.firm_username)
                pub_data = {
                    "firm_username": register_firm.firm_username,   
                    "publisher_username": user.username,
                    
                }
                # 
                register_firm.publishers = [await self.add_publisher(AddPublisherSchema(**pub_data))]
                # register_firm.publishers.append(new_pub)
                # register_firm.publishers = [await self.add_publisher(new_pub)]
                await firm.save()
                
                if UserRole.founder not in user.role:
                    user.role.append(UserRole.founder)
                    if UserRole.publisher not in user.role:
                        user.role.append(UserRole.publisher)
                    await user.save()
                return True
                
        except Exception as e:
            print("Error registering firm:", e)
            return False


    async def add_publisher(self, data: AddPublisherSchema):
        try:
            # Fetch publisher by username
            publisher = await UserModel.find_one(UserModel.username == data.publisher_username)
            if not publisher:
                raise HTTPException(status_code=404, detail="Publisher (user) not found")

            # Fetch firm by username
            firm = await FirmModel.find_one(FirmModel.firm_username == data.firm_username)
            if not firm:
                raise HTTPException(status_code=404, detail="Firm not found")

            # Check if publisher is already in firm's publisher list
            for existing_pub in firm.publishers or []:
                if str(existing_pub.publisher_user_id.id) == str(publisher.id):
                    raise HTTPException(status_code=400, detail="Publisher already added to firm")

            # Create new PublisherInfo object
            new_publisher = PublisherInfo(
                publisher_user_id=publisher,
                invited_at=datetime.now()
            )

            if firm.publishers is None:
                firm.publishers = []

            firm.publishers.append(new_publisher)

            # Ensure the user has the publisher role
            if UserRole.publisher not in publisher.role:
                publisher.role.append(UserRole.publisher)
                await publisher.save()

            await firm.save()

            return new_publisher

        except HTTPException as e:
            raise e
        except Exception as e:
            print("Error adding publisher to firm:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

        
