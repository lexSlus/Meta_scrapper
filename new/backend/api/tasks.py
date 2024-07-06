import json
import logging
from dataclasses import asdict
from datetime import datetime

from celery import shared_task

from api.dto import FakeAccount, GroupDTO
from api.models import PVA, Broker, Group, Keyword
from api.services.fb_messenger import FBMessengerService
from api.services.openai_service import OpenAIService
from api.services.scrapper import Scrapper

import redis

logger = logging.getLogger(__name__)
redis_client = redis.Redis(host='redis', port=6379, db=0)

@shared_task
def healthcheck():
    logger.info("Celery healthcheck completed")


@shared_task
def send_new_posts(posts: list[str], broker_fb_id: str):
    messenger = FBMessengerService()
    messenger.send_posts(posts, broker_fb_id)


@shared_task
def detect_new_post_per_account(fake_account: dict, keywords: dict):
    logger.warning(f"detect_new_post_per_account started at: {datetime.now()}")
    scrapper = Scrapper()
    openai_service = OpenAIService()

    groups = [GroupDTO(**group) for group in fake_account.pop("groups")]
    account = FakeAccount(**fake_account, groups=groups)

    recent_posts = scrapper.get_new_posts(account)

    if account.new_cookies:
        pva = PVA.objects.get(username=account.username)
        pva.cookies = account.new_cookies
        pva.save()
        logger.warning(f"Updated cookie for: {pva.username}")

    for group in account.groups:
        last_post_id = ""

        for post in recent_posts[group.group_link]:
            detected_keywords = openai_service.classify_action(post.post_text, keywords)
            if "None" in detected_keywords:
                continue

            post.post_keywords = detected_keywords
            post.generated_message = openai_service.generate_response(post.post_text)
            last_post_id = post.post_id

        if last_post_id:
            group_obj = Group.objects.get(fb_id=group.group_id)
            group_obj.last_post_id = last_post_id
            group_obj.save()

        logger.warning(f"Found posts: {len(recent_posts)}, at {datetime.now()} for group {group.group_link}")

    leads = [post for posts in recent_posts.values() for post in posts if post.generated_message]
    brokers = Broker.objects.filter(is_active=True, company__is_active=True)
    for broker in brokers:
        broker_keywords = list(broker.keywords.filter(is_active=True, keywordbroker__is_active=True).distinct().values_list('name', flat=True))
        correct_leads = [lead for lead in leads if lead.matches_keyword(broker_keywords)]
        leads_to_send = []
        for lead in correct_leads:
            lead_id = lead.post_id  # Use post_id as a unique identifier for the lead
            redis_key = f"sent_leads:{broker.fb_id}"
            if not redis_client.sismember(redis_key, lead_id):
                leads_to_send.append(str(lead))
                redis_client.sadd(redis_key, lead_id)

        if leads_to_send:
            send_new_posts.apply_async((leads_to_send, broker.fb_id))

        


@shared_task
def groups_detect_new_posts():
    keywords = {k.name: k.description for k in Keyword.objects.all()}

    logger.warning(f"Keywords count: {len(keywords)}")

    pvas = PVA.objects.all()
    logger.warning(f"Found PVAs: {len(pvas)}")

    groups = Group.objects.all()
    groups_per_pva = 7

    for index, pva in enumerate(pvas):
        current_groups = groups[index * groups_per_pva : (index + 1) * groups_per_pva]

        if not current_groups:
            logger.warning(f"No groups left for {pva.id}")
            continue

        pva_dto = FakeAccount(
            username=pva.username,
            password=pva.password,
            cookies=json.loads(pva.cookies) if pva.cookies else [],
            proxy_ip=pva.proxy_ip,
            groups=[GroupDTO(group_id=group.fb_id, last_post_id=group.last_post_id) for group in current_groups],
        )
        logger.warning(f"Detected {len(pva_dto.groups)} groups for {pva_dto.username}")
        detect_new_post_per_account.apply_async((asdict(pva_dto), keywords))

    logger.warning(f"groups_detect_new_posts executed at {datetime.now()}")
