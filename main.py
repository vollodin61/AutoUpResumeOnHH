import asyncio
import os
import sys

from config import BotConfig

sys.path.insert(1, os.path.join(sys.path[0], '..'))


async def send_msg_to_begin():
    async with BotConfig.tele_ubot:
        await BotConfig.tele_ubot.send_message(
            entity="@hh_rabota_bot",
            message="В начало"
        )
        # await asyncio.sleep(10)
        await asyncio.sleep(1)

        await BotConfig.tele_ubot.send_message(
            entity="@hh_rabota_bot",
            message="Поднять резюме в поиске"
        )
        # await asyncio.sleep(10)
        await asyncio.sleep(1)

        await BotConfig.tele_ubot.send_message(
            entity="@hh_rabota_bot",
            message="Поднять"
        )


async def send_interval_reminder():
    from apscheduler.triggers.interval import IntervalTrigger
    BotConfig.scheduler.add_job(
        send_msg_to_begin,
        trigger=IntervalTrigger(seconds=20),
        # trigger=CronTrigger(hour=11, minute=0),
        id="daily_resume_up",
        replace_existing=True,
    )


async def main():
    BotConfig.scheduler.start()
    await send_interval_reminder()
    await asyncio.Event().wait()
    # await stop_event.wait()


if __name__ == '__main__':
    # asyncio.run(send_interval_reminder())
    asyncio.run(main())
    #
    # try:
    #     asyncio.get_event_loop().run_forever()
    # except (KeyboardInterrupt, SystemExit):
    #     pass
