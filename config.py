import logging
from typing import Any

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from environs import Env
from loguru import logger
from redis.asyncio.client import Redis
from redis.backoff import ExponentialBackoff
from redis.exceptions import BusyLoadingError, ConnectionError, TimeoutError
from redis.retry import Retry
from telethon import TelegramClient
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

env = Env()
env.read_env()

info_logger = logger.info
error_logger = logger.error
warning_logger = logger.warning
exception_logger = logger.exception
debug_logger = logger.debug

logging.basicConfig(level=logging.INFO)


class BaseConfig:
    TIMEOUT = 4
    RETRY = 4

    @staticmethod
    def log_action(service_name: str = None, action: Any = None):
        log_file = f"logs/{service_name}.log"
        service_logger = logging.getLogger(f"service_{service_name}")
        service_logger.setLevel(logging.INFO)
        if not service_logger.handlers:
            file_handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)
            service_logger.addHandler(file_handler)

        service_logger.info(action)

    @staticmethod
    def log_retry_attempt(retry_state):
        exception = retry_state.outcome.exception()
        BaseConfig.log_action(
            service_name=retry_state.fn.__qualname__, action=exception
        )

    @staticmethod
    def log_final_exception(retry_state):
        exception = retry_state.outcome.exception()
        BaseConfig.log_action(
            service_name=retry_state.fn.__qualname__, action=exception
        )

    base_retry = retry(
        stop=stop_after_attempt(RETRY),
        wait=wait_fixed(TIMEOUT),
        retry=retry_if_exception_type(Exception),
        after=log_retry_attempt,
        retry_error_callback=log_final_exception,
    )


class RedisConfig(BaseConfig):
    redis_instance = None
    RETRY = 3
    TIMEOUT = 3

    @staticmethod
    @BaseConfig.base_retry
    def get_connection():
        redis_host = env("REDIS_HOST")
        # redis_host = "localhost"
        redis_port = env("REDIS_PORT")
        if not RedisConfig.redis_instance:
            RedisConfig.redis_instance = Redis(
                host=redis_host,
                port=int(redis_port),
                socket_timeout=RedisConfig.TIMEOUT,
                retry=Retry(ExponentialBackoff(), RedisConfig.RETRY),
                retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError],
            )
            info_logger("Redis подключен")

        return RedisConfig.redis_instance


class BotConfig:

    redis_host = env("REDIS_HOST")
    redis_port = int(env("REDIS_PORT"))
    redis = RedisConfig.get_connection()

    scheduler = AsyncIOScheduler(
        timezone="UTC",
        jobstores={"default": RedisJobStore(host=redis_host, port=redis_port, db=0)},
    )

    tele_ubot_id: int = int(env("TELE_UBOT_ID"))
    tele_ubot_hash: str = env("TELE_UBOT_HASH")

    tele_ubot = TelegramClient(
        session="auto_up_resume_session",
        api_id=tele_ubot_id,
        api_hash=tele_ubot_hash,
        device_model="POCO POCO X3 Pro",
        app_version="Telegram Android 11.9.0",
        system_version="Android 12",
        lang_code="ru",
    )
