from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

# from app.controller.user_controller import UserController
from app.controller.token_controller import get_current_user
from app.schema.base_schema import BaseResponse
from app.controller.firm_controller import FirmController
from app.schema.firm_schema import AddPublisherSchema, FirmCreateSchema, FirmDetailsOutSchema
from fastapi import status
from app.models.users import UserModel
from app.models.kyc import KYCModel
from app.models.firm import FirmModel
from app.models.article import ArticleModel
from app.controller.article_controller import ArticleController
from app.schema.article_schema import ArticleOutSchema
from app.kafka.producer import send_kafka_event
from app.models.subscription import SubscriptionModel
from app.models.endorse import EndorsementModel


router = APIRouter(prefix="/firm", tags=["Firm"])

firm_controller = FirmController()
article_controller = ArticleController()

@router.post(
    "/register", response_model=BaseResponse, status_code=status.HTTP_201_CREATED
)
async def create_firm_api(
    firm_data: FirmCreateSchema, current_user: dict = Depends(get_current_user)
):
    """
    Create a new firm. Only KYC-verified users can create a firm.
    """
    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token, Login to continue",
            )

        user = await UserModel.find_one( UserModel.id ==ObjectId(current_user["user_id"]), UserModel.is_deleted == False)
        if not user or not user.is_verified or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User Not found"
            )

        kyc = await KYCModel.find_one(
            KYCModel.user_id.id == ObjectId(current_user["user_id"])
        )
        if not kyc or kyc.kyc_status != "VERIFIED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="KYC required to create firm",
            )

        success = await firm_controller.create_firm(
            firm_data, user, ObjectId(current_user["user_id"])
        )

        if not success:
            # Could be failure due to duplicate username, etc
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create firm."
            )

        return BaseResponse(
            status=1,
            message="Firm created successfully",
            data={"firm_username": success.firm_username},
        )

    except HTTPException as e:
        # propagate HTTPException so FastAPI can return it
        raise e

    except Exception as e:
        # catch all unexpected errors
        return BaseResponse(
            status=0, message=f"Internal server error: {str(e)}", data=None
        )


# @router.post("/add-publisher", response_model=BaseResponse)
# async def add_publisher(
#     data: AddPublisherSchema, current_user: dict = Depends(get_current_user)
# ):
#     try:
#         if current_user is None:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid access token, Login to continue",
#             )

#         new_publisher = await firm_controller.add_publisher(data)
#         response_data = {
#             "status": 1,
#             "message": "Publisher added successfully",
#             "data": {
#                 "publisher_user_id": str(new_publisher.publisher_user_id.id),
#                 "invited_at": new_publisher.invited_at,
#             },
#         }
#         return response_data
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#         )


@router.post("/follow", response_model=BaseResponse)
async def subscribe_to_entity(
    background_tasks: BackgroundTasks,
    firm_id: str | None = None,
    current_user: dict = Depends(get_current_user)
):
    try:
        if current_user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token, Login to continue")
            
        if not firm_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="firm_username is required")

        success = await firm_controller.subscribe(firm_id, current_user["user_id"])
        
        if success["status"] == "followed":
            background_tasks.add_task(
                send_kafka_event,  
                "firm.follow",  
                success["data"],  
            )

        response_data = {
            "status": 1,
            "message": (
                "Firm unfollowed" if success["status"] == "un-followed" else "Firm followed"
            ),
            "data": success,
        }
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# async def get_firm_articles(
#     firm: FirmModel,
#     current_user: dict,
#     page: int,
#     page_size: int
# ):
#     try:
#         skip = (page - 1) * page_size

#         # 1️⃣ Fetch articles
#         articles = await ArticleModel.find(
#             ArticleModel.firm_id.id == firm.id,
#             ArticleModel.status == "PUBLISHED",
#             ArticleModel.is_deleted == False
#         ).sort("-published_at").skip(skip).limit(page_size).to_list()

#         if not articles:
#             return []

#         article_ids = [a.id for a in articles]
#         publisher_ids = [a.publisher_id.id for a in articles]

#         # 2️⃣ Fetch publishers
#         publishers = await UserModel.find(
#             UserModel.id.in_(publisher_ids)
#         ).to_list()
#         publisher_map = {p.id: p for p in publishers}

#         # 3️⃣ Likes + endorsements (batched)
#         likes_map = set()
#         endorsements_map = set()

#         user_id = ObjectId(current_user["user_id"])

#         likes = await ArticleLikeModel.find(
#             ArticleLikeModel.user_id.id == user_id,
#             ArticleLikeModel.article_id.id.in_(article_ids)
#         ).to_list()

#         endorsements = await EndorsementModel.find(
#             EndorsementModel.user_id.id == user_id,
#             EndorsementModel.article_id.id.in_(article_ids)
#         ).to_list()

#         likes_map = {l.article_id.id for l in likes}
#         endorsements_map = {e.article_id.id for e in endorsements}

#         # 4️⃣ Build response
#         result = []
#         for article in articles:
#             publisher = publisher_map.get(article.publisher_id.id)

#             result.append(ArticleOutSchema(
#                 id=str(article.id),
#                 title=article.title,
#                 summary=article.summary,
#                 content=article.content,
#                 content_text=article.content_text,
#                 endorse_count=article.endorse_count,
#                 like_count=article.like_count,
#                 trust_score_snapshot=article.trust_score_snapshot,
#                 tags=article.tags,
#                 category=article.category,
#                 published_at=article.published_at,
#                 publisher={
#                     "id": str(publisher.id),
#                     "username": publisher.username,
#                     "first_name": publisher.first_name,
#                     "last_name": publisher.last_name,
#                 } if publisher else None,
#                 endorsed=article.id in endorsements_map,
#                 liked=article.id in likes_map,
#                 is_self=str(user_id) == str(publisher.id)
#             ))

#         return result
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.get("/details", response_model=BaseResponse)
async def get_firm_details(
    firm_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token, Login to continue",
            )
        if not firm_id:
            raise HTTPException(status_code=400, detail="firm_id is required")
        
        # Fetch firm by ID
        firm = await FirmModel.find_one( FirmModel.id == ObjectId(firm_id), FirmModel.is_deleted == False)
        if not firm or firm.is_deleted or not firm.is_active:
            raise HTTPException(status_code=404, detail="Firm not found")
        
        # Resolve the owner link
        owner = await firm.owner_user_id.fetch()
        owner_info = {
            "id": str(owner.id),
            "username": owner.username,
            "first_name":owner.first_name,
            "last_name":owner.last_name,
        } if owner else None

        # Pagination
        skip = (page - 1) * page_size

        # Fetch published articles
        articles_cursor = ArticleModel.find(
            ArticleModel.firm_id.id == firm.id,
            ArticleModel.status == "PUBLISHED",
            ArticleModel.is_deleted == False
        ).sort("-published_at").skip(skip).limit(page_size)

        # print(articles_cursor)
        articles = []
        
        async for article in articles_cursor:

            article_data = {
                "id":str(article.id),
                "title":article.title,
                "summary":article.summary,
                "tags":article.tags,
                "category":article.category,
            }
            articles.append(article_data)
        print(articles)
        # Check if current user is the owner
        
        is_self = False
        if owner and current_user:
            is_self = str(current_user["user_id"]) == str(owner.id)

        following_details = await SubscriptionModel.find_one(
            SubscriptionModel.subscriber_id.id == ObjectId(current_user["user_id"]),
            SubscriptionModel.firm_id.id == firm.id
        )
        following = True if following_details else False
        
        endorsement_details = await EndorsementModel.find_one(
            EndorsementModel.user_id.id == ObjectId(current_user["user_id"]),
            EndorsementModel.firm_id.id == firm.id
        )
        endorsed = True if endorsement_details else False
        
        # Build final response
        response_data = FirmDetailsOutSchema(
            id=str(firm.id),
            following=following,
            endorsed=endorsed,
            firm_name=firm.firm_name,
            firm_username=firm.firm_username,
            bio=firm.bio,
            verification_status=firm.verification_status.value,
            trust_factor=firm.trust_factor,
            violations_count=firm.violations_count,
            follow_count=firm.follow_count,
            endorse_count=firm.endorse_count,
            is_verified=firm.is_verified,
            created_at=firm.created_at,
            owner=owner_info,
            articles=articles,
            is_self=is_self
        )
        
        return{
            "status": 1,
            "message": "Firm fetched successfully",
            "data": response_data.dict()
        } 
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
        
        
