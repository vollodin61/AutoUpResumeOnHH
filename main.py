import asyncio
import os
import sys

from apscheduler.triggers.cron import CronTrigger

from config import BotConfig

sys.path.insert(1, os.path.join(sys.path[0], '..'))


async def send_msg_to_begin():
    async with BotConfig.tele_ubot:
        await BotConfig.tele_ubot.send_message(
            entity="@hh_rabota_bot",
            message="В начало"
        )
        await asyncio.sleep(10)

        await BotConfig.tele_ubot.send_message(
            entity="@hh_rabota_bot",
            message="Поднять резюме в поиске"
        )
        await asyncio.sleep(10)

        await BotConfig.tele_ubot.send_message(
            entity="@hh_rabota_bot",
            message="Поднять"
        )


async def send_interval_reminder():
    BotConfig.scheduler.add_job(
        send_msg_to_begin,
        trigger=CronTrigger(hour=11, minute=0),
        id="daily_resume_up",
        replace_existing=True,
    )


async def main():
    BotConfig.scheduler.start()
    await send_interval_reminder()
    await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(main())
