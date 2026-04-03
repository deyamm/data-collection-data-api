from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from core.config import settings
from jobs.tasks.exchange_tasks import update_daily_stock_price_job
from jobs.tasks.basic_tasks import update_weekly_stock_info_job


scheduler = AsyncIOScheduler(timezone=settings.TIMEZONE)


def register_jobs():
    # 工作日17:00更新股票价格数据
    scheduler.add_job(
        func=update_daily_stock_price_job,
        trigger=CronTrigger(day_of_week="mon-fri", hour=17, minute=0),  
        id="update_daily_stock_price",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300  # 允许错过的执行时间最大为5分钟
    )
    
    # 每周五16:00更新股票基本信息
    # scheduler.add_job(
    #     func=update_weekly_stock_info_job,
    #     trigger=CronTrigger(day_of_week="fri", hour=16, minute=0),  
    #     id="update_weekly_stock_info",
    #     replace_existing=True,
    #     max_instances=1,
    #     coalesce=True,
    #     misfire_grace_time=300  # 允许错过的执行时间最大为5分钟
    # )

def start_scheduler():
    register_jobs()
    scheduler.start()

def shutdown_scheduler():
    scheduler.shutdown()