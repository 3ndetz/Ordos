import time
import traceback

import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters, CallbackContext
from config.config import tgbot_token
import logging
import asyncio
import textwrap

logging.basicConfig()
logging.root.setLevel(logging.INFO)

#hdlr = logging.StreamHandler()
logger = logging.getLogger('TG_BOT')
#logger.addHandler(hdlr)
#file = logging.FileHandler(config.logdir)
#logger.addHandler(file)
#
logger.info('Starting tg bot...')
#updater = Updater(token=config.tgbot_token, use_context=True)

Chat_session = None
tg_job_queue = None

help_instruction = '''
Хочешь поиграть в захватывающие квест-игры? Тогда тебе сюда!

Список доступных команд:
/help - вызов данного сообщения
/game - выбор игры

Внимание!!!
1. Авторы не несут ответственности за ответы нейронных сетей (которых тут пока что нет)
2. Вы сами это используете, все вопросы к вам.
'''
chat_sessions = []

def create_chat_session(id: str) -> Chat_session:
    new_chat_session = Chat_session(id)
    chat_sessions.append(new_chat_session)
    return new_chat_session

def get_chat_session(id: str):
    for session in chat_sessions:
        if session.id == id:
            return session
    # todo LOAD chat sessions from DB
    return create_chat_session(id)

def tg_msg_process(id: str, msg:str, env:dict=None) -> (str, dict):
    if not env:
        env = {"type": "message"}
    tg_ans_dict = {}
    session = get_chat_session(id)

    answer, extra = session.process_message(msg, env=env)
    tg_ans_dict["text"] = answer

    photos = extra.get("photos", None)
    if photos:
        tg_ans_dict["photos"] = photos
    timer = extra.get("timer",None)
    if timer:
        tg_ans_dict["timer"] = timer
    variants = extra.get("variants",None)
    if variants:
        tg_ans_dict["markup"] = build_variant_buttons(variants)
    return tg_ans_dict

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = int(update.message.chat_id)
    await update.message.reply_text(help_instruction)

async def helper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(help_instruction)

async def game_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await reply_full(update.message, tg_msg_process(str(update.message.chat_id),"Выбор игры", {"type": "command"}))

#async def timeout_command(context: CallbackContext):
#    await reply_full(update.message, tg_msg_process(str(update.message.chat_id),"выбор игры", {"type": "command"}))

def build_variant_buttons_text(variants: list) -> telegram.ReplyKeyboardMarkup:
    # deprecated or need add support dict callback values variants
    result_list = []
    for variant in variants:
        result_list.append(telegram.KeyboardButton(variant))
    return telegram.ReplyKeyboardMarkup([result_list])
def build_variant_buttons(variants: list) -> telegram.InlineKeyboardMarkup:
    result_list = []
    #def sh(ttext):
#
    #    return textwrap.shorten(ttext,40)
    if callable(getattr(variants, "get", None)): # если кнопки переданы как словарь
        if variants.get("table",False): # если это таблица из нескольких рядов кнопок
            print('FOUND TABLE VARIANTS',variants)
            for variant_row in variants:
                print('variant row',variant_row,'val',variants[variant_row])
                var_row = variants[variant_row]
                if callable(getattr(var_row, "get", None)): # если передается массив с вариантами, пропускаем теги
                    this_variant_row = []
                    for variant in var_row:
                        print('LOWEST VARIANT', variant, 'val', var_row[variant])
                        try:

                            this_variant_row.append(telegram.InlineKeyboardButton(var_row[variant], callback_data=variant))
                        except:
                            pass
                    result_list.append(this_variant_row)
        else:
            for variant in variants:
                result_list.append([telegram.InlineKeyboardButton(variants[variant], callback_data=variant)])
    else:
        for variant in variants: # если кнопки переданы как список
            result_list.append([telegram.InlineKeyboardButton(variant, callback_data=variant)])
    #return telegram.InlineKeyboardMarkup([result_list])
    return telegram.InlineKeyboardMarkup(result_list)
async def reply_full(tg_message, processed_ans):
    """reply_full(message=update.message or message=query.message)"""
    timer = processed_ans.get("timer", None)
    photos = processed_ans.get("photos",None)
    audios = processed_ans.get("audios", None)
    text = processed_ans.get("text",None)
    need_edit = processed_ans.get("edit_prev", False)
    markup = processed_ans.get("markup",None)

    if processed_ans.get("delayed_timeout_action", False):
        #if time.time()-get_chat_session(str(tg_message.chat_id)).last_button_pressed_time
        #if processed_ans["timeout_started_time"]<get_chat_session(str(tg_message.chat_id)).last_button_pressed_time<time.time():
        if get_chat_session(str(tg_message.chat_id)).last_button_pressed_time<processed_ans["timeout_started_time"]:
            print('DELAYED TIMER ACTUAL!')
        else:
            print('TIMER NOT ACTUAL')
            return


    photos_enabled = True # TODO убрать
    if photos and photos_enabled:
        try:
            for photo in photos:
                await tg_message.reply_photo(photo=photo["url"], caption=photo.get("caption",""))
        except:
            print('Не удалось отправить фото(')
    if audios:
        try:
            for audio in audios:
                if audio.get("voice",False):
                    await tg_message.reply_voice(voice=audio["url"], caption=audio.get("caption", ""))
                else:
                    await tg_message.reply_audio(audio=audio["url"], caption=audio.get("caption", ""))
        except:
            print('Не удалось отправить аудио(')
    new_tg_message = None
    if text:
        if need_edit:
            if markup:
                await tg_message.edit_text(text=text)
                await tg_message.edit_reply_markup(reply_markup=markup)
            else:
                await tg_message.edit_text(text=text)
        else:
            if markup:
                new_tg_message = await tg_message.reply_text(text=text,reply_markup=markup)
            else:
                new_tg_message = await tg_message.reply_text(text=text)
    if timer:
        async def timeout_callback_func(context: CallbackContext):
            print("[TG BOT PRINT]TIMER EXECTUING!!!!")
            new_processed_ans = tg_msg_process(str(new_tg_message.chat_id),timer.get("cmd","timeout"), env={"type": "command", "timeout":True})
            if new_tg_message:
                new_processed_ans["edit_prev"] = True
            new_processed_ans["delayed_timeout_action"] = True
            new_processed_ans["timeout_started_time"] = time.time()-timer["time"]
            await reply_full(new_tg_message, new_processed_ans)
        print('DEBUG TIMER QUEUE PRINT, time=',timer["time"])
        tg_job_queue.run_once(timeout_callback_func, timer["time"])
async def button_pressed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #print('debug button update:',update)
    query = update.callback_query # get user id - update.callback_query.from_user.id
    #print('debug button query:', query)
    await query.answer()
    if query.data == "button_from_prev_menu": # если эта кнопка нажата с предыдущих этапов, игнорируем...
        return
    try:
        chosen_button = None

        for button_row in query.message.reply_markup.inline_keyboard:
            for button in button_row:
                if button.callback_data==query.data:
                    button.update_callback_data("button_from_prev_menu")
                    chosen_button=telegram.InlineKeyboardMarkup(((button,),),)
        if chosen_button is None:
            raise Exception("NO BUTTON WITH Q DATA!")
        await query.edit_message_reply_markup(reply_markup=chosen_button)
    except BaseException as err:
        print('ERROR when altering prev msg buttons!', err)
        traceback.format_exc()

    get_chat_session(str(query.message.chat_id)).last_button_pressed_time = time.time()
    #query .edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пыщь")
    #print('debug button query ans:', query)
    #await query.edit_message_text(text=f"\nВыбрано: {query.data}")
    #await query.message.reply_text(text="☝ выбрано "+query.data)
    await reply_full(query.message, tg_msg_process(str(query.message.chat_id), query.data, {"type": "command"}))

# INFO
# update struct debug button update: Update(callback_query=CallbackQuery(chat_instance='2918854200295963328', data='Выход', from_user=User(first_name='Hyper', id=855417724, is_bot=False, language_code='en', username='HyperVlad'), id='3673991150458401288', message=Message(channel_chat_created=False, chat=Chat(first_name='Hyper', id=855417724, type=<ChatType.PRIVATE>, username='HyperVlad'), date=datetime.datetime(2023, 12, 14, 17, 17, 44, tzinfo=<UTC>), delete_chat_photo=False, from_user=User(first_name='Ordos', id=6687571039, is_bot=True, username='the_ordos_bot'), group_chat_created=False, message_id=1699, reply_markup=InlineKeyboardMarkup(inline_keyboard=((InlineKeyboardButton(callback_data='Итоги', text='Подвести итоги'),), (InlineKeyboardButton(callback_data='Отменить действие', text='Вернуть время назад'),), (InlineKeyboardButton(callback_data='Выход', text='Выйти в меню'),))), supergroup_chat_created=False, text='Вы полезли в карман за ножом и волк в страхе... Откусил вам голову, пометил захваченную территорию и победно взвыл!\nКак же так? А с чего вы взяли, что у вас был нож, мистер сверхразум?)')), update_id=528767377)

# query struct CallbackQuery(chat_instance='2918854200295963328', data='Выход', from_user=User(first_name='Hyper', id=855417724, is_bot=False, language_code='en', username='HyperVlad'), id='3673991150458401288', message=Message(channel_chat_created=False, chat=Chat(first_name='Hyper', id=855417724, type=<ChatType.PRIVATE>, username='HyperVlad'), date=datetime.datetime(2023, 12, 14, 17, 17, 44, tzinfo=<UTC>), delete_chat_photo=False, from_user=User(first_name='Ordos', id=6687571039, is_bot=True, username='the_ordos_bot'), group_chat_created=False, message_id=1699, reply_markup=InlineKeyboardMarkup(inline_keyboard=((InlineKeyboardButton(callback_data='Итоги', text='Подвести итоги'),), (InlineKeyboardButton(callback_data='Отменить действие', text='Вернуть время назад'),), (InlineKeyboardButton(callback_data='Выход', text='Выйти в меню'),))), supergroup_chat_created=False, text='Вы полезли в карман за ножом и волк в страхе... Откусил вам голову, пометил захваченную территорию и победно взвыл!\nКак же так? А с чего вы взяли, что у вас был нож, мистер сверхразум?)'))


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query_data = None
    if query:
        if query.data:
            query_data = query.data
            print("QUERY DATA =",query_data)
    chat_id = int(update.message.chat_id)
    message = update.message.text
    ans_builded = tg_msg_process(str(update.message.chat_id), message, {"type": "msg"})
    logger.info('User = [{}]'.format(chat_id))
    logger.info('Message = [{}]'.format(message))
    logger.info('Answer = [{}]'.format(str(ans_builded)))
    logger.info('-' * 20)
    await reply_full(update.message, ans_builded)



#async def default(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    user_id = int(update.message.chat_id) #команда /default, в telegram_bot_run внести также application.add_handler(CommandHandler("default", default))
#    core.set_system_prompt(user_id, 'Ты девушка Анфиса, разговаривающая с незнакомым человеком.')
#    await update.message.reply_text('Режим по умолчанию установлен!')


def telegram_bot_run(Session):
    global Chat_session
    global tg_job_queue
    logger.info('[TG BOT STARTING]')
    Chat_session = Session
    application = Application.builder().token(tgbot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", helper))
    application.add_handler(CommandHandler("game", game_command))
    application.add_handler(CallbackQueryHandler(button_pressed))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    tg_job_queue = application.job_queue
    application.run_polling()
    logger.info('[TG BOT CLOSING]')

if __name__ == "__main__":
    from core import core_session
    telegram_bot_run(core_session)