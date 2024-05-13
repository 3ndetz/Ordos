import asyncio
import datetime
import io
import json
import time
import traceback
from multiprocessing.managers import SyncManager
# pip install py-cord
# py -3 -m pip install -U py-cord[voice]
# pip install PyNaCl
import discord
from discord.ext import commands, tasks

from datetime import datetime

from bot.tools.badwords_detector import toxic_analyze, detect_badwords, base_badwords_list, format_wordlist

from config.config import dsbot_token, stt_connect_key  # token - just string 'key', connect_key - bytes string: b'key'


def eztime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def tm(x):
    return datetime.strptime(x, '%Y-%m-%d %H:%M:%S')


class GuildData:

    def __init__(self, guild_id):
        if guild_id is None:
            self.guild_id = 1122595942986694658
        else:
            self.guild_id = guild_id
        self.loyal = False
        self.badwords = base_badwords_list
        self.guild = None
        self.listening_loop_started = True
        self.sink = None
        self.vc_channel = None
        self.vc = None
        self.debug_text_channel = None
        self.loop_container = None
        # init recogloop  variables
        self.voice_streak_found = 0
        self.silence_streak_found = 0
        self.voice_confirmed_iters = 0

        self.accepted_role_id = None
        self.warned_role_id = None
        self.blocked_role_id = None

        self.toxic_check = False

        self.voice_recog_stared = False
        self.prev_voice_recog_stared = False
        self.collected_voice_data = {}

    def get(self, field_name, return_type=None):
        try:
            if field_name == "voice_id":
                return self.vc_channel.id
            elif field_name == "guild_id":
                return self.guild_id
            elif field_name == "toxic_check":
                return self.toxic_check
            elif field_name == "accepted_role_id":
                return self.accepted_role_id
            elif field_name == "warned_role_id":
                return self.warned_role_id
            elif field_name == "blocked_role_id":
                return self.blocked_role_id
            elif field_name == "enabled":
                return self.listening_loop_started
            else:
                return return_type
        except:
            return return_type

    def set(self, field_name, value):
        if field_name == "voice_id":
            self.vc_channel.id = value
        elif field_name == "guild_id":
            self.guild_id = value
        elif field_name == "accepted_role_id":
            self.accepted_role_id = value
        elif field_name == "warned_role_id":
            self.warned_role_id = value
        elif field_name == "blocked_role_id":
            self.blocked_role_id = value
        elif field_name == "enabled":
            self.listening_loop_started = value

    def start_listening(self):
        self.listening_loop_started = True

    async def stop_listening(self):
        self.listening_loop_started = False
        try:
            # voice = self.vc  # discord.utils.get(self.bot.voice_clients, guild=self.guild)
            if self.vc and self.vc.is_connected():
                await self.vc.move_to(None)
                # await voice.disconnect()
        except BaseException as err:
            print('err when Voice disconnect:', err)


class pycord_voice_client():
    def __init__(self, bot, ctx_chat=None, docker_sender=None):
        if ctx_chat is None:
            self.ctx_chat = []
        else:
            self.ctx_chat = ctx_chat
        self.stt_class = docker_sender
        self.bot = bot
        self.PendingApprovalMembers = {}
        self.listening_loop_delay = 1.0
        self.GuildList = {}  # {1192780668950810685: {"voice_id": 1192780669647077462, "badwords_list": base_badwords_list}}
        self.violations = {}

    def start_recognition_functions(self):

        stt_class = self.stt_class
        bot = self.bot

        def speech_recognition(bytes_io_audio):
            if stt_class is not None:
                return stt_class.transcribe(audio_bytes_io=bytes_io_audio)
            else:
                return "Not implemented =( надо stt class передать, а он None почему-то"

        # class Sinks(Enum):
        #    mp3 = discord.sinks.MP3Sink()
        #    wav = discord.sinks.WaveSink()
        #    pcm = discord.sinks.PCMSink()
        #    ogg = discord.sinks.OGGSink()
        #    mka = discord.sinks.MKASink()
        #    mkv = discord.sinks.MKVSink()
        #    mp4 = discord.sinks.MP4Sink()
        #    m4a = discord.sinks.M4ASink()
        # self.listening_loop_started = False

        async def finished_callback_sendfiles(sink, channel: discord.TextChannel, *args):

            # await sink.vc.disconnect()
            # audio wav Audio: PCM 48000Hz stereo 1536kbps [A: pcm_s16le, 48000 Hz, 2 channels, s16, 1536 kb/s]
            # Audio: PCM 48000Hz stereo 1536kbps [A: pcm_s16le, 48000 Hz, 2 channels, s16, 1536 kb/s]
            # Audio: 0x0000 48000Hz stereo 1536kbps [A: adpcm_dtk, 48000 Hz, stereo, s16]
            ###audiolist = []
            ###for user_id, audio in sink.audio_data.items():
            ###    f = wave.open(audio.file, "rb")
            ###    audiolist.append([f.getparams(), f.getnframes()])
            ###    print('params =',f.getparams())
            ###    f.close()
            ###    #f.seek(0)
            # wave merge https://stackoverflow.com/questions/2890703/how-to-join-two-wav-files-using-python
            # f.seek(0) #0 - установить курсор в начало файла, 1 - на файл в последнюю измененную видимо позицию, 2 - в конец файла
            # print('AUDIOLIST >>',audiolist,'<<')
            recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
            if len(recorded_users) > 0:

                files = []
                for user_id, audio in sink.audio_data.items():
                    send_filename = bot.get_user(user_id).display_name + "-" + datetime.datetime.now().strftime(
                        '%Mm-%Ss') + f".{sink.encoding}"
                    files.append(discord.File(audio.file, send_filename))
                await channel.send(
                    f"Finished! Recorded audio for {', '.join(recorded_users)}.", files=files
                )

        async def schelude_task(coro, seconds):
            # suspend for a time limit in seconds
            await asyncio.sleep(seconds)
            # execute the other coroutine
            await coro

        async def unpunish_user(member: discord.Member, gd: GuildData):
            try:
                # await member.edit(mute=False)
                await add_role(member, "blocked_role_id", remove_role=True)
                await member.send(
                    f"""Вы снова можете говорить! Впредь старайтесь быть вежливее в голосовом канале "{gd.vc_channel.name}" сервера "{gd.guild.name}".""")
            except BaseException as err:
                print('ERR when edit (unmute) user', err)
                await member.send(
                    f"""Не удалось снять вам наказание в голосовом канале "{gd.vc_channel.name}" сервера "{gd.guild.name}" =(\nОбратитесь к администратору за помощью""")

        def detect_violation(text: str, gd: GuildData):
            result = detect_badwords(text, gd.badwords)
            if gd.toxic_check:
                toxic_analyze(text, result)
            return result

        async def finished_callback_recognize(sink, gd: GuildData, *args):
            # recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
            sink_audio_data = sink.audio_data.copy()
            sink_audio_data_items = sink_audio_data.items()
            if len(sink_audio_data_items) > 0:
                speechmas = []
                for user_id, audio in sink_audio_data_items:
                    # files.append(audio.file)
                    recognized = speech_recognition(audio.file)
                    if recognized.strip() != "" and len(recognized) > 2:
                        username = bot.get_user(user_id).name
                        speechmas.append((username, recognized, user_id, audio.file, detect_violation(recognized,
                                                                                                      gd),))
                        # await channel.send(f"""<@{user_id}>: {recognized}""")
                channel_stt = await get_bot_chat(gd.guild, thread_name="распознавание")
                channel = await get_bot_chat(gd.guild, thread_name="нарушения")
                if len(speechmas) > 0:
                    # nww = datetime.now().strftime('%M:%S')
                    nw = datetime.now().strftime('%M_%S')
                    for record in speechmas:
                        line = "[ОТЛАДКА] [РАСПОЗНАНО] " + record[0] + ": " + record[1] + "; Нарушения: " + str(
                            record[4])
                        print(f"[DISCORD VC] [{nw}] {line}")
                        await channel_stt.send(line)

                        if record[4]["found"] == 1.0:
                            files = []
                            send_filename = record[0] + "-" + nw + f".{sink.encoding}"
                            files.append(discord.File(record[3], send_filename))
                            badword = record[4]["word"]
                            user_id = int(record[2])
                            punish = False
                            if user_id in self.violations:
                                if self.violations[user_id] > 0:
                                    punish = True
                                    self.violations[user_id] = 0
                                else:
                                    self.violations[user_id] += 1
                            else:
                                self.violations[user_id] = 1

                            v_str = "" if (gd.loyal or punish) else f" ({str(self.violations[user_id])}/2)"
                            user = self.bot.get_user(record[2])
                            if punish:
                                member = gd.guild.get_member(user_id)
                                try:
                                    # await check_member_role(member,"")
                                    await add_role(member, "blocked_role_id")
                                    try:
                                        await kick_voice(member)
                                    except:
                                        pass
                                    # await member.edit(mute=True)
                                    asyncio.create_task(schelude_task(unpunish_user(member, gd), 300))
                                except BaseException as err:
                                    print('не получилось ЗАМУТИТЬ!', err)
                            punishment = "наказание (мут на 5 минут)" if punish else "предупреждение"
                            await channel.send(
                                f"""Пользователь <@{record[2]}> выразился словом ||{badword}|| в голосовом чате "{gd.vc_channel.name}" и получил {punishment}{v_str}.""")
                            await user.send(
                                f"""Вы использовали запрещенное слово ||{badword}|| в голосовом канале "{gd.vc_channel.name}" сервера "{gd.guild.name}" и получаете {punishment}{v_str}. Воздержитесь от использования подобной лексики в голосовом канале.""")
                            await user.send(
                                f"""\nК этому сообщению прикреплен фрагмент вашей речи, содержащий нарушение. Если в записанном фрагменте нарушения не было, вы можете доказать администратору вашу непричастность к нарушению, отправив данную запись модератору сервера. \nУчтите, что распространение записей личных разговоров может преследоваться по закону и входит в вашу зону ответственности.\n\nВнимание! Фрагмент будет НАВСЕГДА УДАЛЁН через 60 секунд! Скачайте его, если желаете что-то доказать.""",
                                file=discord.File(record[3],
                                                  send_filename),
                                delete_after=60.0)  # [discord.File(record[3], send_filename)])

        async def get_bot_chat(guild, debug_chat_name="чат-ordos", thread_name=None):
            debug_text_channel = discord.utils.get(guild.text_channels, name=debug_chat_name)
            if debug_text_channel is None:
                debug_text_channel = await guild.create_text_channel(debug_chat_name)
            if thread_name:
                thread = discord.utils.get(debug_text_channel.threads, name=thread_name)
                if thread is None:
                    start_msg = await debug_text_channel.send("Тут будут сообщения на тему «" + thread_name + "»")
                    thread = await debug_text_channel.create_thread(name=thread_name, message=start_msg,
                                                                    auto_archive_duration=0, type=None, reason=None)
                return thread
            return debug_text_channel

        async def voice_listen_start(ctx, gd: GuildData):  # создаем асинхронную фунцию бота
            guild = gd.guild
            # 1122595944798625925
            debug_text_channel = get_bot_chat(guild)

            print('Voice starting initiated')
            # channel = self.bot.get_channel(1122595944798625925)  # голосовой Комната для траснляций
            channel = gd.vc_channel
            contextless = False

            # if ctx is None:
            #    contextless = True
            # if ctx is None and guild is None:
            #    print('Мда?')
            #    return
            # if contextless:
            vc = gd.vc
            if gd.vc is None:
                vc = discord.utils.get(self.bot.voice_clients, guild=guild)
            # else:
            #    vc = ctx.voice_client
            # vc.start_recording
            # vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if vc is not None:
                await vc.move_to(channel)
                print('Moving to channel..')
            else:
                print('Connecting..')
                vc = await channel.connect()
                print('Connected!')
            if vc is None:
                print("FFFF НЕ ПОДКЛЮЧИЛИСЬ")
            else:
                gd.vc = vc
                # gd.vc_channel = channel
            if not gd.loop_container:
                gd.loop_container = LoopContainer()
                gd.loop_container.loop = gd.loop_container.voice_recognition_loop.start(gd)
            else:
                await gd.stop_listening()
                if gd.loop_container.loop:
                    gd.loop_container.loop.cancel()
                try:
                    gd.loop_container.voice_recognition_loop.cancel()
                    gd.loop_container.voice_recognition_loop.stop()
                except BaseException as err:
                    print('err when cancel n stopping loop container,', err)
                    print('трейсбек', traceback.print_exc())

                del gd.loop_container.loop
                del gd.loop_container.voice_recognition_loop

                del gd.loop_container
                gd.loop_container = LoopContainer()
                gd.loop_container.loop = gd.loop_container.voice_recognition_loop.start(gd)
                gd.start_listening()
            gd.debug_text_channel = debug_text_channel

        @bot.event
        async def on_guild_join(guild: discord.Guild):
            print('Бот добавлен на сервер!')

            # print('Удаляется ', self.GuildList[guild.id])
            # del self.GuildList[guild.id]
            # todo remove from bd

        @bot.event
        async def on_guild_remove(guild: discord.Guild):
            print('Бот удален с сервера! Удаляем все следы, что с ним связаны из бд и памяти!')
            print('Удаляется ', self.GuildList[guild.id])
            del self.GuildList[guild.id]
            # todo remove from bd

        @bot.event
        async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
            message = reaction.message
            if user != self.bot.user and message.author == self.bot.user:
                if reaction.emoji == "✅":
                    print('CONFIRMED REACTION!')
                    for react in message.reactions:
                        async for re_user in reaction.users():
                            if re_user == self.bot.user and react.emoji == "✅":
                                print('DOUBLE CONFIRMED REACTION!!!')
                                if user.id in self.PendingApprovalMembers:
                                    await self.PendingApprovalMembers[user.id]()
                                    del self.PendingApprovalMembers[user.id]

                print('REACTION!', reaction, "emoji", reaction.emoji)

        @bot.event
        async def on_voice_state_update(member: discord.Member, prev, cur):
            if (self.bot.user.id == member.id):  # исключить себя
                return
            if prev.channel == cur.channel:  # изменения в текущем канале игнорируем
                return
            g_data = self.GuildList.get(member.guild.id, None)
            if (g_data is not None):
                voice_id = g_data.get('voice_id', None)
                print('voice_id,', voice_id)
                if g_data.get("enabled",
                              False) and voice_id is not None and cur is not None and cur.channel is not None:
                    channel = cur.channel

                    if channel.id == voice_id:
                        user = f"{member.name}#{member.discriminator}"
                        print(f"[DISCORD VOICE CHANNEL] {user} JOINED CHANNEL! (other, join or smth)")
                        if not await check_member_role(member, "accepted_role_id"):  # check user
                            try:
                                license_text = """```Текст соглашения об обработке персональных данных\n\nВаши голосовые данные будут обработаны для распознавания речи и автоматической проверки её на соответствие правилам этого сервера. Система хранит данные разговоров не дольше минуты, затем они будут удалены. Принимая данное соглашение работы с ботом, вы подтверждаете свое согласие на обработку персональных данных вашего голоса из этого голосового канала. Данные ваших разговоров не будут переданы третьим лицам; они хранятся не более минуты, после чего подлежат удалению.```"""
                                print('Kicking user', user)
                                await kick_voice(member)
                                kick_reason = f""":exclamation: Для того, чтобы использовать модерируемый голосовой чат "{channel.name}" на сервере "{member.guild.name}", вам нужно принять следующее соглашение об обработке вашей речи ботом:\n{license_text}\n\nЕсли вы согласны и принимаете это соглашение, поставьте, пожалуйста, на это сообщение реакцию зеленой галочки :white_check_mark:, (реакция уже стоит, просто жмакните её). После этого вы сразу сможете присоединиться к чату :face_holding_back_tears:"""
                                sent_msg = await member.send(kick_reason, mention_author=True)
                                await sent_msg.add_reaction("✅")

                                async def pending_approval_func():
                                    if await add_role(member, "accepted_role_id"):
                                        await member.send(
                                            f"""Спасибо! Вы подтвердили соглашение и допускаетесь к чату "{channel.name}" сервера "{member.guild.name}"! :tada:""")
                                    else:
                                        await member.send(
                                            f"""Спасибо! Вы подтвердили соглашение, НО НЕ УДАЛОСЬ присвоить вам роль, чтобы допустить к чату "{channel.name}" сервера "{member.guild.name}" =( Обратитесь к его администратору, пожалуйста!""")

                                self.PendingApprovalMembers[member.id] = pending_approval_func

                            except BaseException as err:
                                print('Не удалось исключить пользователя', user, 'из чата, ошибка:', err)
                        else:
                            await check_authorized_member(member, channel)

        async def check_authorized_member(member: discord.Member, channel: discord.VoiceChannel):
            g_data = self.GuildList.get(member.guild.id, None)
            try:
                # warned_role_id = g_data.get("warned_role_id", None)
                blocked_role_id = g_data.get("blocked_role_id", None)
                # выкидываем заблоканных
                for role in member.roles:
                    if role.id == blocked_role_id:
                        print('Kicking member', member.name)
                        await kick_voice(member)
                        kick_reason = f""":exclamation: Вы были заблокированы за нарушение в модерируемом голосовом чате "{channel.name}" на сервере "{member.guild.name}" и не можете присоединиться. Ожидайте снятия блокировки :fearful:"""
                        sent_msg = await member.send(kick_reason, mention_author=True)
                        return
                    # if role.id == warned_role_id
            except BaseException as err:

                print('err when check authed memb role,', err)

                print('трейсбек', traceback.print_exc())

        async def kick_voice(member: discord.Member):
            await member.edit(
                voice_channel=None)  # The voice channel to move the member to. Pass None to kick them from voice.

        async def create_role(g_data: GuildData, role_name_id: str, default_role_name: str):
            try:
                role = await g_data.guild.create_role(name=default_role_name)
                g_data.set(role_name_id, role.id)
                print('создана роль', default_role_name, 'id name', role_name_id, 'internal id', role.id)
                return True
            except BaseException as err:
                print('Не удалось создать роль ерр=', err)
                print('трейсбек', traceback.print_exc())
            return False

        async def check_member_role(member: discord.Member, role_id_name: str, g_data=None):
            if g_data is None:
                g_data = self.GuildList.get(member.guild.id, None)
            try:

                role_id = g_data.get(role_id_name, None)
                for role in member.roles:
                    if role.id == role_id:
                        return True
            except BaseException as err:
                print('err when check memb role,', err)
                print('трейсбек', traceback.print_exc())
            return False

        async def check_created_role(g_data: GuildData, role_id_name):
            try:
                role_id = g_data.get(role_id_name, None)
                guild = self.bot.get_guild(g_data.get("guild_id"))
                role = discord.utils.get(guild.roles, id=role_id)
                # role = self.bot.get_guild(g_data.get("guild_id")).get_role(role_id)
                print('[DEBUG] чекаем роль role_id_name', role_id_name, 'role', role, 'guild', guild, 'role_id',
                      role_id, 'g_data.accepted_role_id', g_data.accepted_role_id, 'g',
                      g_data.get("accepted_role_id", None), )
                if role:
                    return True
            except BaseException as err:
                print('Не удалось чекнуть роль НА СЕРВЕ ерр=', err)
                print('трейсбек', traceback.print_exc())
            return False

        async def check_all_roles(g_data: GuildData):
            default_role_list = [["accepted_role_id", "Верифицирован в ГС ботом"],
                                 ["warned_role_id", "Предупреждение о нарушении в ГС"],
                                 ["blocked_role_id", "Заблокирован в ГС"]]
            for role_name_id, role_default_name in default_role_list:
                if await check_created_role(g_data, role_name_id):
                    print('роль', role_name_id, 'уже создана')
                else:
                    await create_role(g_data, role_name_id, role_default_name)

        async def add_role(member: discord.Member, role_id_name: str, remove_role=False):
            g_data = self.GuildList.get(member.guild.id, None)
            try:
                # print('role id name', role_id_name, 'gdata',g_data,'gdata role',g_data.accepted_role_id)
                role_id = g_data.get(role_id_name, None)
                # print('role id', role_id)
                role = member.guild.get_role(role_id)
                # print('role', role)
                if remove_role:
                    await member.remove_roles(role)
                else:
                    await member.add_roles(role)
                return True
            except BaseException as err:
                print('Не удалось добавить ролью юзеру ерр=', err)
                print('трейсбек', traceback.print_exc())
                # channel = await get_bot_chat(member.guild, thread_name="нарушения")
                # channel.send("Не удалось добавить пользователя в чат проверенных")
            return False

        # async def get_member_dm_info(member: discord.Member):
        # dm_channels = await discord.utils.get_or_fetch(self.bot, 'private_channels')
        async def get_last_pin(channel):
            pins = await channel.pins()
            if len(pins) > 0:
                return pins[-1]
            return None

        async def load_guild_config(guild):
            chat = await get_bot_chat(guild, thread_name="параметры")
            config_msg = await get_last_pin(chat)
            config = None
            if config_msg:
                if config_msg.attachments:
                    config_file = io.BytesIO(await config_msg.attachments[-1].read())
                    config = json.load(config_file)
                    print('loaded config!', config, '; guild =', guild)
            if config:
                return config
            else:
                return {}

        async def save_guild_config(guild):
            chat = await get_bot_chat(guild, thread_name="параметры")
            config_msg = await get_last_pin(chat)
            if config_msg:
                await config_msg.delete()
            saved_message = await chat.send("Конфигурация бота сохранена.",
                                            file=discord.File(io.BytesIO(guild_data_to_json(guild.id).encode()),
                                                              "ordos_config.json_cfg", spoiler=True))
            await saved_message.pin()

        def guild_data_to_json(guild_id) -> str:
            gd = self.GuildList[guild_id]
            result_dict = {}
            success = False
            if gd:
                if isinstance(gd, GuildData):
                    try:
                        result_dict["enabled"] = gd.listening_loop_started
                        result_dict["voice_id"] = gd.vc_channel.id
                        result_dict["badwords_list"] = gd.badwords
                        result_dict["loyal"] = gd.loyal
                        result_dict["accepted_role_id"] = gd.accepted_role_id
                        result_dict["toxic_check"] = gd.toxic_check
                        result_dict["warned_role_id"] = gd.warned_role_id
                        result_dict["blocked_role_id"] = gd.blocked_role_id
                        success = True
                    except BaseException as err:
                        print('ОШИБКА при конвертировании guild data', err)
            if not success:
                result_dict["badwords_list"] = base_badwords_list
            return json.dumps(result_dict, ensure_ascii=False)

            # "voice_id": 1192780669647077462, "badwords_list": base_badwords_list}

        async def init_gdata(guild: discord.Guild):
            gu_id = guild.id
            gu = self.bot.get_guild(gu_id)
            data_dict = await load_guild_config(guild)
            gd = GuildData(guild_id=gu_id)
            gd.badwords = data_dict.get("badwords_list", base_badwords_list)
            gd.accepted_role_id = data_dict.get("accepted_role_id", None)
            gd.toxic_check = data_dict.get("toxic_check", False)
            gd.warned_role_id = data_dict.get("warned_role_id", None)
            gd.blocked_role_id = data_dict.get("blocked_role_id", None)
            gd.listening_loop_started = data_dict.get("enabled", True)
            gd.vc_channel = bot.get_channel(data_dict.get("voice_id", None))
            gd.loyal = bot.get_channel(data_dict.get("loyal", False))
            # todo чо делать если голосовой чат чат удален
            gd.guild = gu
            self.GuildList[gu_id] = gd
            return gd

        @bot.event
        async def on_ready():
            # print('\n'.join(map(repr, self.get_all_channels())))
            # loop_start()

            print('[PYCORD] Logged in to Discord as {} - ID {}'.format(bot.user.name, bot.user.id))
            print('all systems ready')
            # loop_start()
            # voice_recognition_loop.start()

            for guild in self.bot.guilds:  # gu_id in self.GuildList
                print(guild)
                gu_id = guild.id
                gu = self.bot.get_guild(gu_id)
                gd = await init_gdata(gu)
                if gd.vc_channel and gd.listening_loop_started:
                    await voice_listen_start(None, gd=gd)

        @bot.command(name='документация', aliases=['documentation'], pass_context=True)
        async def documentation(ctx):
            """Максимально объемное описание команд этого бота."""
            await ctx.send("""Данный бот создан с целью автоматической модерации голосовых чатов и пресечения использования запрещенной лексики на вашем сервере Discord. Список запрещенных слов можно изменить, добавить собственные. На данный момент бот может модерировать не более 1 голосового чата на сервере.

Список доступных команд:

- help / помощь – вызывает текст: список остальных команд и их описание. 

- настроить – вызывает процедуру настройки выбора модерируемого голосового чата. Если пользователь уже подключен к голосовому каналу, бот запоминает этот голосовой канал для последующей модерации.

Включение и отключение модерации:

- включить – включает модерацию голосового чата, если была выключена

- отключить – выключает модерацию голосового чата, если была включена

Режимы модерации:

- режим стандарт – устанавливает режим модерации, в котором за 2 нарушения выдается наказание

- режим лояльный – устанавливает режим модерации, в котором только выдаются предупреждения, но не наказания

Настройка списка запрещенных слов:

- список свой – заменяет встроенный список плохих слов на тот, который напишет далее пользователь (ожидается ввод слов в следующем сообщении через запятую). 
Ограничения: слов не больше 10000, 1 слово не длиннее 20 символов, слов не может быть 0.

- список добавить – добавляет к имеющемуся списку слов (встроенному или замененному) ещё слова, которые далее после команды введет пользователь (ожидается ввод слов через запятую). 
Ограничения: ВСЕГО слов не больше 10000, 1 слово не длиннее 20 символов.

Функция проверки оскорбительного поведения в речи:

- поведение вкл – включает проверку

- поведение выкл – выключает проверку
Ограничение: функция находится в стадии альфа-тестирования и может быть неточной - наказывать невиновных или пропускать нарушителей.""")

        @bot.command(name='настроить', aliases=['configure'], pass_context=True,
                     description="Вызывает процедуру настройки выбора модерируемого голосового чата. Если пользователь уже подключен к голосовому каналу, бот запоминает этот голосовой канал для последующей модерации. Если пользователь не подключен к голосовому каналу, ему будет предложено это сделать.")
        @commands.has_permissions(administrator=True)
        async def voice_configure(ctx):
            """Настройте голосовой канал!"""
            voice = ctx.author.voice
            guild = ctx.message.guild
            if not voice or not voice.channel:
                return await ctx.send(
                    "Для настройки автомодерируемого голосового чата присоединитесь к голосовому каналу, который хотите выбрать для модерации, и снова повторите данную команду.")

            voice = voice.channel

            gd = self.GuildList.get(guild.id, None)
            if gd.get("voice_id") == voice.id:
                await ctx.send(
                    "Вы пытаетесь перенастроить уже настроенный голосовой чат. Будет выполнена переконфигурация!")
            if isinstance(gd, GuildData):

                gd.vc_channel = voice
                await gd.vc.move_to(voice)
            else:
                gd = await init_gdata(guild)
                gd.vc_channel = voice
                if gd.vc_channel and gd.listening_loop_started:
                    await voice_listen_start(ctx, gd=gd)
                    print('voice listen reloaded!', gd.listening_loop_started, gd.vc, gd.vc_channel, 'lp',
                          gd.loop_container)
            await save_guild_config(ctx.message.guild)
            # data_changed=False
            # if old_gd:
            #    old_vc_channel = old_gd.vc_channel
            #    old_gd.vc_channel = voice
            #    await check_all_roles(old_gd)
            #    await save_guild_config(ctx.message.guild)
            #    data_changed = True
            #    old_gd.vc_channel = old_vc_channel
            #
            #    #old_gd = GuildData({})
            #    await old_gd.stop_listening()
            #    old_gd.loop_container.voice_recognition_loop.stop()
            #    del self.GuildList[guild.id]
            ##except BaseException as err:
            ##    print('НЕ УДАЛОСЬ УДАЛИТЬ old_gd',err)
            ##    print('трейсбек', traceback.print_exc())
            #
            # gd = await init_gdata(guild) #old bug gd = GuildData(guild_id=guild.id)
            # gd.vc_channel = voice
            # gd.start_listening()
            ##gd.guild = guild
            # if not data_changed:
            #    await check_all_roles(gd)
            #    await save_guild_config(ctx.message.guild)
            #
            ##self.GuildList[guild.id] = gd
            #
            ## todo update voice id
            ## TODO UPDATE GUILD DATA METHOD
            # if gd.vc_channel and gd.listening_loop_started:
            #    await voice_listen_start(ctx, gd=gd)
            #    print('voice listen reloaded!',gd.listening_loop_started,gd.vc,gd.vc_channel,'lp',gd.loop_container)
            # await voice_listen_start(, gd=gd)

            await ctx.send(
                f"""Голосовой чат настроен – теперь модерироваться будет голосовой чат с названием {voice.name}.

Отключить/включить модерацию вы можете при помощи команд «отключить» или «включить» соответственно.
Также вы можете поменять режим модерации и установить свой список слов – подробнее узнайте при помощи команды «помощь».""")

        @bot.command(name='режим', aliases=['mode'], pass_context=True)
        @commands.has_permissions(administrator=True)
        async def change_mode(ctx, mode_name: str):
            """Изменить режим (лояльный или стандарт)."""
            if mode_name not in ["лояльный", "стандарт"]:
                return await ctx.send(f"""Такого режима нет! На данный момент доступны режимы стандарт и лояльный.""")
            gd = self.GuildList[ctx.message.guild.id]
            if isinstance(gd, GuildData):
                if mode_name == "лояльный":
                    gd.loyal = True
                else:
                    gd.loyal = False
                await save_guild_config(ctx.message.guild)
                return await ctx.send(f"""Режим {mode_name} установлен.""")

        @bot.command(name='поведение', aliases=['toxic'], pass_context=True)
        @commands.has_permissions(administrator=True)
        async def toxic_check_change(ctx, state: str):
            """Включить/отключить проверку речи на оскорбительное поведение (токсичность вкл или выкл). [ALPHA TEST]"""
            if state not in ["вкл", "выкл"]:
                return await ctx.send(f"""Введите "поведение вкл" или "поведение выкл".""")
            gd = self.GuildList[ctx.message.guild.id]
            if isinstance(gd, GuildData):
                if state == "вкл":
                    gd.toxic_check = True
                else:
                    gd.toxic_check = False
                await save_guild_config(ctx.message.guild)
                return await ctx.send(
                    f"""Проверка речи на оскорбительное поведение {state}. Учтите, что она строгая, находится в стадии альфа тестирования и может ошибаться.""")

        @bot.command(name='список', aliases=['list'], pass_context=True)
        @commands.has_permissions(administrator=True)
        async def edit_badwords(ctx, list_type: str, *, text):
            """Изменить список плохих слов для модерации.
Использование: "список свой/добавить (список слов через запятую, без этих скобок)".
Пример: "список добавить водка, коньяк" - добавит в список слова "водка" и "коньяк"."""
            if list_type not in ["свой", "добавить", "удалить"]:
                return await ctx.send(
                    f"""Неправильно задана команда. Ввести нужно "список свой..." или "список добавить..." или "список удалить...". """)
            gd = self.GuildList[ctx.message.guild.id]
            if isinstance(gd, GuildData):

                result_msg = ""
                if list_type == "свой":
                    new_list, exc = format_wordlist(text, [])
                    result_msg = f"Установлен новый список из {str(len(new_list))} слов."
                else:
                    oldlen = len(gd.badwords)
                    remove_words = False if list_type == "удалить" else True
                    new_list, exc = format_wordlist(text, gd.badwords, remove=remove_words)
                    result_msg = (
                                     "Удалено" if remove_words else "Добавлено") + f" {str(len(new_list) - oldlen)} новых слов (всего {len(new_list)})"

                if exc:
                    return await ctx.send(f"""Неправильно заданы слова: {exc}""")

                gd.badwords = new_list
                await save_guild_config(ctx.message.guild)
                return await ctx.send(f"""Успешно! {result_msg}""")
            else:
                await ctx.send(
                    f"""Кажется, Вы ещё не настроили голосовой канал! Воспользуйтесь командой настроить и выберите канал, пожалуйста!""")

        @bot.command(name='включить', aliases=['turn_on'], pass_context=True)
        @commands.has_permissions(administrator=True)
        async def activate(ctx):
            """Включить автоматическую модерацию голосового канала."""
            await activation(ctx, True)

        @bot.command(name='отключить', aliases=['turn_off', 'выключить'], pass_context=True)
        @commands.has_permissions(administrator=True)
        async def deactivate(ctx):
            """Выключить автоматическую модерацию голосового канала."""
            await activation(ctx, False)

        async def activation(ctx, enable=True):
            try:
                gd = self.GuildList[ctx.message.guild.id]
                if isinstance(gd, GuildData):
                    if enable:

                        if gd.listening_loop_started:
                            await ctx.send(
                                f"""Модерация голосового канала уже была включена. Если ничего не происходит, попробуйте перенастроить выбор голосового канала.""")
                        else:
                            gd.start_listening()
                            await save_guild_config(ctx.message.guild)
                            await ctx.send(f"""Модерация голосового канала включена.""")
                        if not gd.vc:
                            await voice_listen_start(None, gd)
                        elif not gd.vc.is_connected():
                            try:
                                # loop.stop()
                                await gd.stop_listening()
                                print('GD not connected! ReConnecting..')
                                # loop.cancel()
                                # gd.listening_loop_started = False
                                # await gd.vc.disconnect()
                                # gd.vc = discord.utils.get(self.bot.voice_clients, guild=gd.guild)
                                # await gd.vc.connect(timeout=10.0, reconnect=False)
                                await gd.vc.move_to(gd.vc_channel)
                                gd.start_listening()
                                # loop.cancel()
                                # await gd.vc_channel.connect()  # gd.vc = ...
                                # gd.vc = discord.utils.get(self.bot.voice_clients, guild=gd.guild)
                                # gd.listening_loop_started = True
                                # loop.start()
                                # await voice_listen_st art(None, gd)
                            except BaseException as err:
                                print('ERRRRRRR gs otladka ', err)
                                print('traceback:::', traceback.print_exc())

                    else:
                        if not gd.listening_loop_started:
                            await ctx.send(
                                f"""Модерация голосового канала уже выключена.""")
                        else:
                            await gd.stop_listening()
                            await save_guild_config(ctx.message.guild)
                            await ctx.send(f"""Модерация голосового канала отключена.""")
                else:
                    await ctx.send(
                        f"""Кажется, Вы ещё не настроили голосовой канал! Воспользуйтесь командой настроить и выберите канал, пожалуйста!""")
            except BaseException as err:
                print('ERROR WHEN ON/OFF AUTOMODERATION', err)
                print('трейсбек', traceback.print_exc())
                await ctx.send(
                    f"""Кажется, произошла ошибка при действии голосового чата. Попробуйте удалить бота и снова его добавить.""")

        async def check_vc_initialize(gd: GuildData):
            if gd.vc is not None:

                if gd.sink is None:
                    gd.sink = discord.sinks.WaveSink()
                # if self.sink.finished:
                #    self.sink = discord.sinks.WaveSink()

                if not gd.vc.is_connected():
                    # gd.vc = discord.utils.get(self.bot.voice_clients, guild=gd.guild)
                    print('gd vc init pass 1 fail')
                    if not gd.vc.is_connected():
                        try:
                            # loop.stop()
                            print('GD not connected! ReConnecting.. (no)')
                            # loop.cancel()
                            # gd.listening_loop_started = False
                            # await gd.vc.disconnect()
                            # gd.vc = discord.utils.get(self.bot.voice_clients, guild=gd.guild)
                            # await gd.vc.connect(timeout=10.0, reconnect=False)
                            # await gd.vc.move_to(gd.vc_channel)
                            # loop.cancel()
                            # await gd.vc_channel.connect()  # gd.vc = ...
                            # gd.vc = discord.utils.get(self.bot.voice_clients, guild=gd.guild)
                            # gd.listening_loop_started = True
                            # loop.start()
                            # await voice_listen_st art(None, gd)

                            if (gd.vc.is_connected()):
                                print('Connected!')
                            else:
                                print('Connection in progress/error?')
                                return False
                        except BaseException as err:
                            print('err while connecting!', err)
                            print('трейсбек', traceback.print_exc())
                            return False

                if not gd.vc.recording:
                    gd.vc.start_recording(gd.sink, finished_callback_recognize, gd, )
                    # self.vc.start_recording(self.sink, finished_callback_recognize, self.debug_text_channel, )
                return True
            else:
                if gd.guild is not None:
                    gd.vc = discord.utils.get(self.bot.voice_clients, guild=gd.guild)
                else:
                    gd.guild = self.bot.get_guild(gd.guild_id)
                    gd.vc = discord.utils.get(self.bot.voice_clients, guild=gd.guild)
                return False

        class LoopContainer:
            this_listening_loop_delay = self.listening_loop_delay
            loop = None

            # def __exit__(self, exc_type, exc_value, traceback):
            #    self.voice_recognition_loop.stop()
            #    print('removing loopContainer.. Stopped recog loop')

            @tasks.loop(seconds=self.listening_loop_delay)
            async def voice_recognition_loop(self, gd: GuildData):
                nw = datetime.now().strftime('%M_%S')
                # print('cho')
                # print('voice_recognition_loop, gd class:',gd)
                if not gd.listening_loop_started:
                    print(nw, 'lol listening loop not started')
                if gd.listening_loop_started:
                    # print('cho2')
                    initialized = await check_vc_initialize(gd)
                    if not initialized:
                        print(nw, 'not init')
                        return
                    # print('listening voice, sink',gd.sink,'lol',gd.vc.is_connected())
                    print(nw, 'running task check')
                    vc = gd.vc
                    listening_loop_delay = self.this_listening_loop_delay
                    voice_streak_found = gd.voice_streak_found
                    silence_streak_found = gd.silence_streak_found
                    voice_confirmed_iters = gd.voice_confirmed_iters
                    voice_recog_stared = gd.voice_recog_stared
                    prev_voice_recog_stared = gd.prev_voice_recog_stared

                    collected_voice_data = gd.collected_voice_data

                    # listening_loop_delay = 1
                    # await asyncio.sleep(listening_loop_delay)

                    audios = gd.sink.get_all_audio()
                    sound_found = False
                    if audios is not None:
                        for snd in audios:
                            sound_found = True
                            break
                    # print('[DISCORD VOICE DEUBG] soundfound,len_collected',sound_found,len(collected_voice_data))
                    if sound_found:
                        silence_streak_found = 0
                        voice_streak_found += 1
                        # print('Речь обнаружена!')
                        for user, audio in gd.sink.audio_data.items():
                            if user not in collected_voice_data:
                                file = io.BytesIO()
                                collected_voice_data.update({user: discord.sinks.AudioData(file)})
                            collected_voice_data[user].write(audio.file.getvalue())
                            # collected_voice_data = collected_voice_data | sink.audio_data
                        if voice_streak_found > 1:
                            # print('НАЧАТО РАСПОЗНАВАНИЕ РЕЧИ!')
                            voice_confirmed_iters += 1
                            voice_recog_stared = True
                        if voice_confirmed_iters > 0:
                            pass
                            # print('sound record iter',voice_confirmed_iters,'time =',voice_confirmed_iters*listening_loop_delay)
                        if voice_confirmed_iters * listening_loop_delay >= 10:  # 10 сек
                            # print('sound record time reached')
                            # print('Завершение записи речи')
                            voice_recog_stared = False
                            voice_confirmed_iters = 0
                    else:
                        silence_streak_found += 1
                        voice_streak_found = 0
                        if voice_confirmed_iters > 0:
                            if voice_recog_stared == True:
                                # print('ВАННА ОЧИЩЕНА!!!!')
                                # sink.cleanup()
                                voice_recog_stared = False
                        elif voice_confirmed_iters > 1:  # более 2 пустот подряд
                            # print('Завершение записи речи')
                            voice_recog_stared = False
                            voice_confirmed_iters = 0
                        if silence_streak_found > 1:
                            collected_voice_data.clear()
                    # if sound_found_attempts
                    if prev_voice_recog_stared != voice_recog_stared:
                        if voice_recog_stared:
                            pass
                            # print('ЗАПИСЬ РЕЧИ CONFIRMED! len =',len(collected_voice_data))
                        else:
                            # print('СТОП 100% ЗАПИСЬ РЕЧИ!')
                            voice_confirmed_iters = 0
                            await asyncio.sleep(1)
                            if vc.recording and not vc.paused:
                                vc.toggle_pause()
                            # sink.audio_data = sink.audio_data | collected_voice_data
                            gd.sink.audio_data = collected_voice_data
                            if vc.recording:
                                vc.stop_recording()
                            await asyncio.sleep(1)
                            # print('RECORD RESTARTING!')
                            try:
                                if not vc.recording:
                                    gd.sink = discord.sinks.WaveSink()
                                    vc.start_recording(gd.sink, finished_callback_recognize, gd, )  # already recording
                            except BaseException as err:
                                print('err when recording', err)
                                print('trcbk', traceback.print_exc())
                            # merge collected data!
                            collected_voice_data.clear()
                        prev_voice_recog_stared = voice_recog_stared
                    # sink.cleanup()
                    gd.sink.audio_data = {}
                    gd.collected_voice_data = collected_voice_data
                    # self.listening_loop_delay = listening_loop_delay
                    gd.voice_streak_found = voice_streak_found
                    gd.silence_streak_found = silence_streak_found
                    gd.voice_confirmed_iters = voice_confirmed_iters
                    gd.voice_recog_stared = voice_recog_stared
                    gd.prev_voice_recog_stared = prev_voice_recog_stared


class MyManager(SyncManager):
    pass


MyManager.register("syncdict")

MyManager.register("tts_input_q")
MyManager.register("tts_output_q")

MyManager.register("llm_input_q")
MyManager.register("llm_output_q")

MyManager.register("llm_loading_flag")


class DockerSender():
    def __init__(self):
        self.manager = None
        self.initialized = False
        self.check_connection()

    def check_connection(self, force=False):
        if not self.initialized or force:
            try:
                print('[DOCKER SENDER INIT] Starting SENDER manager...')
                self.manager = MyManager(('localhost', 6006), authkey=stt_connect_key)
                self.manager.connect()
                self.initialized = True
                print('[DOCKER SENDER INIT] SUCCESSFULL CONNECTED!')
            except BaseException as err:
                print('[DOCKER STT SENDER] Ошибка при подключении:', err, 'запуск чекера')

    def stop_docker_reciever(self):
        if self.initialized:
            self.manager.syncdict()["stop"] = True

    def llm_loading_flag(self):
        if self.initialized:
            return self.manager.llm_loading_flag()
        else:
            self.check_connection()
            return self.manager.llm_loading_flag()

    def transcribe(self, audio_bytes_io, audio_settings=None):
        self.check_connection()
        try:
            if audio_settings is None:
                audio_settings = {"sr": 48000, "channels": 2}
            self.manager.tts_input_q().put({"bytes_io": audio_bytes_io, "audio_settings": audio_settings})
            out = self.manager.tts_output_q().get()
            return out
        except BaseException as err:
            print('[DOCKER TTS SEND] Ошибка', err, ' ПЕРЕПОДКЛЮЧЕНИЕ!')
            self.check_connection(force=True)


class OrdosHelpCommand(commands.DefaultHelpCommand):
    def get_ending_note(self) -> str:
        """Returns help command's ending note. This is mainly useful to override for i18n purposes."""
        command_name = self.invoked_with
        return (
            f"Все команды вводятся с помощью {self.context.clean_prefix} название_команды [аргументы] (если они есть, без квадратных скобок).\nВведите команду {self.context.clean_prefix}{command_name} название_команды для получения большей информации о команде."
        )


def dsbot_start():
    intents = discord.Intents().all()

    bot = commands.Bot(
        command_prefix=('@Ordos ', '<@1192729753392787456> ', '@ord ', 'Ordos ', 'ordos ', 'Ord ', 'ord '),
        intents=intents)
    # https://guide.pycord.dev/extensions/commands/help-command
    bot.help_command = OrdosHelpCommand(
        command_attrs={"name": "help", "aliases": ["помощь"], "help": "Вызвать окно помощи.",
                       "description": "Вызывает текстовую помощь.",
                       "cooldown": commands.CooldownMapping.from_cooldown(3, 5, commands.BucketType.guild)},
        indent=3,
        no_category=f"Данный бот создан с целью автоматической модерации голосовых чатов и пресечения использования запрещенной лексики на вашем сервере Discord. Список запрещенных слов можно изменить, добавить собственные. На данный момент бот может модерировать не более 1 голосового чата на сервере.\n\nДоступные команды")
    # commands.CooldownMapping.from_cooldown(1,10,commands.BucketType.guild)
    stt_class_client_sender = DockerSender()

    bot_voice_class = pycord_voice_client(bot, docker_sender=stt_class_client_sender)
    bot_voice_class.start_recognition_functions()
    # bot_voice_class.
    bot.run(dsbot_token)


if __name__ == '__main__':  # for debug run this file
    dsbot_start()
