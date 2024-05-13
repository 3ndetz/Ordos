from multiprocessing import Process, Manager

if __name__ == '__main__':
    from bot.telegram_bot import telegram_bot_run
    from datetime import datetime
    from core import core_session

    from bot.discord_bot import dsbot_start

    print('main started. Cores imported')



    tg_process = Process(target=telegram_bot_run, args=(core_session,))
    tg_process.start()

    # сперва запустите docker или где STT процесс
    ds_process = Process(target=dsbot_start)
    ds_process.start()
