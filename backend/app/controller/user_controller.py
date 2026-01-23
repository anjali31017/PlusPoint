from fastapi import HTTPException
from typing import Optional
from bson import ObjectId
from app.models.users import UserModel, UserRole
import random
from app.models.firm import FirmModel
from app.models.subscription import SubscriptionModel
from app.controller.email_controller import is_user_blocked
from app.controller.util_controller import UtilController
from app.models.article import ArticleModel
from app.models.comment import CommentModel
from app.models.kyc import KYCModel
from app.models.report import ReportModel
from app.models.endorse import EndorsementModel


util_controller = UtilController()

class UserController:
    
    async def create(self, user_data:dict) -> UserModel | None:
        try:
            
            user_exists = await UserModel.find_one(
                UserModel.email == user_data['email'],
                UserModel.is_deleted == False
            )
            
            if user_exists and user_exists.is_verified == True:
                return None
            
            if user_exists and user_exists.is_verified == False:
                update_password = UserModel.hash_detail(user_data['password'])
                await user_exists.set({UserModel.password_hash: update_password})
                return user_exists
            print("!!!!!!!!!!!!!")
            while True:
                username = await util_controller.generate_username(
                    firstname = user_data["first_name"], 
                    lastname = user_data["last_name"] if user_data.get("last_name") else None, 
                    firmname= None,
                    )
                user = await util_controller.check_username_exists(username)
                if not user:
                    break
            user = UserModel(**user_data)
            user.username = username
            user.role = ['E']
            user.password_hash = UserModel.hash_detail(user_data['password'])
            await user.insert()
            return user
        except Exception as e:
            print(str(e))
            return None
        
    async def _find_active_user(self, user_id: str) -> UserModel | None:
        try:
            obj_id = ObjectId(user_id)
            print(obj_id)
            return await UserModel.find_one(
                UserModel.id == obj_id,
                UserModel.is_deleted == False
            )
        except Exception as e:
            print("Error finding user:", e)
            return None
    
    
    async def get_user(self, id: str) -> UserModel | None:
        try:
            return await self._find_active_user(id)
        except Exception as e:
            print(str(e))
            return None
    
    async def update_user(self, user_id: str, update_data: dict) -> UserModel | None:
        try:
            user = await self._find_active_user(user_id)
            if not user:
                return None

            for key, value in update_data.items():
                setattr(user, key, value)

            await user.save()
            return user

        except Exception as e:
            print("Error updating user:", e)
            return None

    
    
    async def report_firm_article(self, firm_id: str|None, article_id: str|None, reason:str,  current_user:dict ):
        try:
            user = await UserModel.find_one( UserModel.id == ObjectId(current_user["user_id"]), UserModel.is_deleted == False)
            if not user:
                return None
            
            firm = None
            article = None

            if firm_id:
                firm = await FirmModel.find_one( FirmModel.id == ObjectId(firm_id), FirmModel.is_deleted == False)
                if not firm:
                    return None
                
            if article_id:
                article = await ArticleModel.find_one( ArticleModel.id == ObjectId(article_id), ArticleModel.is_deleted == False)
                if not article:
                    return None

            
            reported = await ReportModel.find_one(ReportModel.user_id.id == user.id,
                                                  ReportModel.firm_id.id == (firm.id if firm else None),
                                                  ReportModel.article_id.id == (article.id if article else None),
                                                  )
            if reported:
                return False
            
            report = ReportModel(user_id=user, firm_id=firm, article_id=article, reason=reason)
            await report.insert()

            if firm:
                await firm.update({"$inc": {"report_count": 1}})
            if article:
                await article.update({"$inc": {"report_count": 1}})
            
            return True
            
        except Exception as e:
            print("Error updating user:", e)
            return None


    async def endorse_firm_article(self, firm_id: str|None, article_id: str|None,  current_user:dict ):
        try:
            user = await UserModel.find_one( UserModel.id == ObjectId(current_user["user_id"]), UserModel.is_deleted == False)
            if not user:
                return None
            
            firm = None
            article = None

            if firm_id:
                firm = await FirmModel.find_one( FirmModel.id == ObjectId(firm_id), FirmModel.is_deleted == False)
                if not firm:
                    return None
                
            if article_id:
                article = await ArticleModel.find_one( ArticleModel.id == ObjectId(article_id), ArticleModel.is_deleted == False)
                if not article:
                    return None

            
            endorsed = await EndorsementModel.find_one(
                EndorsementModel.user_id.id == user.id,
                EndorsementModel.firm_id.id == (firm.id if firm else None),
                EndorsementModel.article_id.id == (article.id if article else None),
                )
            if endorsed:
                await endorsed.delete()
                if article:
                    await article.update({"$inc": {"endorse_count": -1}})
                if firm:
                    await firm.update({"$inc": {"endorse_count": -1}})
                return "removed"
            
            endorse = EndorsementModel(user_id=user, firm_id=firm, article_id=article)
            await endorse.insert()

            if firm:   
                await firm.update({"$inc": {"endorse_count": 1}})
            if article:
                await article.update({"$inc": {"endorse_count": 1}})
            
            return "endorsed"
            
        except Exception as e:
            print("Error updating user:", e)
            return None
    
    
    async def delete_user(self, current_user :dict):
        try:
            print(current_user)
            user = await self.get_user(current_user["user_id"])
            print(user)
            if user is None:
                return None
        
            # ------------------ Delete subscriptions ------------------
            subscriptions = await SubscriptionModel.find(
                SubscriptionModel.subscriber_id.id == user.id
            ).to_list()
            for sub in subscriptions:
                await sub.delete()
            
            
            # ------------------ Delete KYC ------------------
            kycs = await KYCModel.find(
                KYCModel.user_id.id == user.id,
                KYCModel.is_deleted == False
            ).to_list()
            for kyc in kycs:
                kyc.is_deleted = True
                kyc.is_active = False
                await kyc.save()
            
            # ------------------ Delete Firms ------------------
            firms = await FirmModel.find(
                FirmModel.owner_user_id.id == user.id,
                FirmModel.is_deleted == False
            ).to_list()
            for firm in firms:
                firm.is_deleted = True
                firm.is_active = False
                await firm.save()
            
            # ------------------ Delete Comments ------------------
            comments = await CommentModel.find(
                CommentModel.user_id.id == user.id,
                CommentModel.is_deleted == False
            ).to_list()
            for comment in comments:
                comment.is_deleted = True
                await comment.save()
            
            # ------------------ Delete Articles ------------------
            publisher_articles = await ArticleModel.find(
                ArticleModel.publisher_id.id == user.id,
                ArticleModel.is_deleted == False
            ).to_list()
            for article in publisher_articles:
                article.is_deleted = True
                await article.save()
            
            firm_articles = await ArticleModel.find(
                ArticleModel.firm_id.id == user.id,
                ArticleModel.is_deleted == False
            ).to_list()
            for article in firm_articles:
                article.is_deleted = True
                await article.save()
            
            # ------------------ Delete User ------------------
            user.is_deleted = True
            user.is_active = False
            await user.save()
            
            return True
        except Exception as e:
            return str(e)
        

    async def delete_request(self, reason:str, firm_id: str|None, article_id: str|None, current_user :dict):
            try:
                if firm_id:
                    firm = await FirmModel.find_one(
                        FirmModel.owner_user_id.id == ObjectId(current_user["user_id"]),
                        FirmModel.id == ObjectId(firm_id),
                        FirmModel.is_deleted == False
                    )

                    if firm is None:
                        return None
                    
                    if firm.delete_reason:
                        return False
                    
                    firm.delete_reason = reason
                    await firm.save()
                    
                if article_id:
                    article = await ArticleModel.find_one(
                        ArticleModel.publisher_id.id == ObjectId(current_user["user_id"]),
                        ArticleModel.id == ObjectId(article_id),
                        ArticleModel.is_deleted == False
                    )
                    
                    if article is None:
                        return None
                    
                    if article.delete_reason:
                        return False
                    
                    article.delete_reason = reason
                    await article.save()
                
                return True
            except Exception as e:
                return str(e)
        