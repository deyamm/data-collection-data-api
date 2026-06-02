from .stock_daily_price_by_code_task import register_stock_daily_price_by_code_task
from .stock_daily_price_by_date_task import register_stock_daily_price_by_date_task
from .stock_daily_price_init_task import register_stock_daily_price_init_task

def register_all_tasks():
    """注册所有任务模板和处理函数"""
    register_stock_daily_price_by_code_task()
    register_stock_daily_price_by_date_task()
    register_stock_daily_price_init_task()
