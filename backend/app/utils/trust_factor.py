import asyncio
from fastapi import FastAPI
from app.models.firm import FirmModel
from app.models.article import ArticleModel, ArticleStatus

# Engagement weight constants
ARTICLE_WEIGHTS = {
    "firm_weight": 0.4,
    "base_weight": 0.6,
    "base_tf": 100,
    "endorse_weight": 1.0,
    "report_weight": 2.0,
    "like_weight": 0.5
}

FIRM_WEIGHTS = {
    "base_tf": 100,
    "endorse_weight": 1.0,
    "report_weight": 2.0,
    "article_engagement_weight": 0.5
}

BATCH_SIZE = 100 


def calculate_article_tf(firm_tf: float, article: ArticleModel) -> float:
    """Calculate article TF based on firm TF and engagement."""
    try:
        base_tf = ARTICLE_WEIGHTS["firm_weight"] * firm_tf + ARTICLE_WEIGHTS["base_weight"] * ARTICLE_WEIGHTS["base_tf"]
        engagement_delta = (
            ARTICLE_WEIGHTS["endorse_weight"] * article.endorse_count
            - ARTICLE_WEIGHTS["report_weight"] * article.report_count
            + ARTICLE_WEIGHTS["like_weight"] * article.like_count
        )
        return max(0, min(100, base_tf + engagement_delta))
    except Exception as e:
        return None

async def recalculate_trust_factors():
    """Recalculate TF for all firms and articles in batches."""
    try:
        skip = 0
        while True:
            firms_batch = await FirmModel.find(FirmModel.is_deleted == False).skip(skip).limit(BATCH_SIZE).to_list()
            if not firms_batch:
                break
            for firm in firms_batch:
                # calculate total article engagement
                total_article_engagement = 0
                async for article in ArticleModel.find( ArticleModel.firm_id.id == firm.id, ArticleModel.is_deleted == False, ArticleModel.status == ArticleStatus.PUBLISHED):
                    total_article_engagement += article.endorse_count - 2 * article.report_count + 0.5 * article.like_count

                # update firm TF
                firm_tf = max(0, min(100, FIRM_WEIGHTS["base_tf"] + FIRM_WEIGHTS["endorse_weight"]*firm.endorse_count
                                    - FIRM_WEIGHTS["report_weight"]*firm.report_count
                                    + FIRM_WEIGHTS["article_engagement_weight"]*total_article_engagement))
                # firm.trust_factor = firm_tf
                # await firm.save()
                await firm.update({"$set": {"trust_factor": firm_tf}})

                # update articles TF
                article_skip = 0
                while True:
                    articles_batch = await ArticleModel.find(ArticleModel.firm_id.id == firm.id, ArticleModel.is_deleted == False).skip(article_skip).limit(BATCH_SIZE).to_list()
                    if not articles_batch:
                        break
                    for article in articles_batch:
                        article_tf = calculate_article_tf(firm_tf, article)
                        await article.update({"$set": {"trust_score_snapshot": article_tf}})
                    article_skip += BATCH_SIZE
            skip += BATCH_SIZE
    except Exception as e:
        return None

async def background_tf_updater():
    """Background task that runs every hour."""
    while True:
        try:
            print("Starting TF recalculation...")
            await recalculate_trust_factors()
            print("TF recalculation completed.")
        except Exception as e:
            print(f"Error in TF updater: {e}")
        await asyncio.sleep(3600)


    




# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from fastapi import FastAPI
# from app.models.firm import FirmModel
# from app.models.article import ArticleModel

# # Engagement weight constants
# ARTICLE_WEIGHTS = {
#     "firm_weight": 0.4,     # weight of firm TF in article TF
#     "base_weight": 0.6,     # weight of base TF (100) in article TF
#     "base_tf": 100,         # base TF
#     "endorse_weight": 1.0,  # each article endorsement impact
#     "report_weight": 2.0,   # each article report impact
#     "like_weight": 0.5      # each like impact
# }

# FIRM_WEIGHTS = {
#     "base_tf": 100,
#     "endorse_weight": 1.0,  # each firm endorsement
#     "report_weight": 2.0,   # each firm report
#     "article_engagement_weight": 0.5  # fraction of total article engagement added to firm TF
# }


# scheduler = AsyncIOScheduler()


# def calculate_article_tf(firm_tf: float, article: ArticleModel) -> float:
#     """
#     Calculate article trust factor based on firm TF and article engagement.
#     """
#     base_tf = ARTICLE_WEIGHTS["firm_weight"] * firm_tf + ARTICLE_WEIGHTS["base_weight"] * ARTICLE_WEIGHTS["base_tf"]
    
#     engagement_delta = (
#         ARTICLE_WEIGHTS["endorse_weight"] * article.endorse_count
#         - ARTICLE_WEIGHTS["report_weight"] * article.report_count
#         + ARTICLE_WEIGHTS["like_weight"] * article.like_count
#     )
    
#     tf = max(0, min(100, base_tf + engagement_delta))
#     return tf


# async def recalculate_trust_factors():
#     """
#     Batch update: recalculates firm and article TFs hourly.
#     """
#     async for firm in FirmModel.find(FirmModel.is_deleted == False):
#         # 1️⃣ Calculate total article engagement for this firm
#         total_article_engagement = 0
#         async for article in ArticleModel.find(ArticleModel.firm_id.id == firm.id, ArticleModel.is_deleted == False):
#             article_engagement = (
#                 article.endorse_count
#                 - 2 * article.report_count
#                 + 0.5 * article.like_count
#             )
#             total_article_engagement += article_engagement

#         # 2️⃣ Calculate firm TF including firm counters + article engagement
#         firm_tf = (
#             FIRM_WEIGHTS["base_tf"]
#             + FIRM_WEIGHTS["endorse_weight"] * firm.endorse_count
#             - FIRM_WEIGHTS["report_weight"] * firm.report_count
#             + FIRM_WEIGHTS["article_engagement_weight"] * total_article_engagement
#         )
#         firm_tf = max(0, min(100, firm_tf))
#         await firm.update({"$set": {"trust_factor": firm_tf}})

#         # 3️⃣ Update article TFs for this firm
#         async for article in ArticleModel.find(ArticleModel.firm_id.id == firm.id, ArticleModel.is_deleted == False):
#             article_tf = calculate_article_tf(firm_tf, article)
#             await article.update({"$set": {"trust_score_snapshot": article_tf}})


# # Schedule job every 1 hour
# scheduler.add_job(recalculate_trust_factors, "interval", hours=1)

# # Start scheduler on app startup
