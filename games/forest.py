import copy
import random
from ctypes import Union

scene_1_msg = """Журчание воды, стук дятла... Утихающая боль в голове.. Вы открыли глаза.
Ваши мысли: где я? Что произошло? Последнее, что я помню - чей-то крик.. Вокруг всё смутно зеленое... Надо взять очки, ничего не вижу..."""
scene_1_photo = "https://i.ibb.co/02XvGd7/kandinsky-download-1699417600695.png"
scene_1_run_msg = """Вы бежали, бежали, вдруг потеряли землю из под ног и стали слышать какие-то голоса. Оказалось, что вода по ручьу вела к резкому обрыву, образуя водопад, с которого вы сиганули, так как ничего не видели. Бывает! Что ж, в другой жизни повезёт!"""
scene_1_death_photo = "https://i.ibb.co/RvQdHhD/kandinsky-download-1699448860430.png"

scene_2_msg = """Вы осторожно встали и обнаружили очки под ягодицей. К счастью, одно из стеклышков выжило!

Вы осматриваетесь. Вокруг зеленый лес. Вы под деревом на лужайке.
"Так хорошо... Эх, жаль что я без пикника!" """

scene_2_death_river = "Вы шли вверх по ручью. Чем дальше вы уходили тем более мелким он становился. Вы шли до тех пор пока он совсем не пропал из виду. Когда он пропал вы поняли что окончательно потерялись. Вас охватило уныние, вы сели у ближайшего дерева и остались умирать осознавая собственную никчемность..."

scene_2_skeleton_photo = """https://i.ibb.co/HNQJC0g/photo1699507411.jpg"""

scene_2_photo = "https://i.ibb.co/WDz5082/606013e4-982b-406e-a761-28d4edcfed70.jpg"

scene_2_mox = """Вы выбрали направление и шли без остановки несколько часов. Вы устали, проголодались и промокли, но перед вами все еще такой же лес. 

"Хмм... а точно ли я шел всегда прямо? Всё такое знакомое..
О, это же тот ручей! Повезло, что нашел его снова. Кстати, а может ещё раз попробовать, авось найду выход?" """

scene_2_mox_death = "Вы выбрали направление и шли без остановки несколько часов. Вы поняли, что окончательно потерялись. Ваше самочувствие достигло минимума, вы прилегли к ближайшему дереву и..."

scene_2_panic = """Вас охватила паника и вы поддались ей. Вы сорвались с места и побежали в случайном направлении. Вы не обращали внимание на то как вас больно ранят ветки кустов."""

scene_2_panic_alive = """\nВ конце концов вам еле еле удалось выйти к ручью. И что это была за тварь такая, что вас так испугала?"""

scene_2_panic_death = """Вы так бежали, что были истощены до смерти..."""

scene_3_msg = """Вы шли дальше вниз по ручью, с большим трудом пробираясь сквозь заросли леса, и, в конце концов, вы вышли к озеру у подножью большой горы."""
scene_3_photo = "https://i.ibb.co/VwPwTM9/kandinsky-download-1699416742112.png"

scene_3_wolf_death_photo = "https://pic.rutubelist.ru/video/c3/4c/c34cd23999d16b63781fe367923c3f53.jpg"
scene_3_water_death_photo = "https://i.ibb.co/m86K8PS/3waterdeath.png"

scene_4_izba_photo = "https://i.ibb.co/F5ydhVg/1703083153000ern39j4t.png"

emp = ("", {},)


def str2(any_data) -> str:
    punkt = """{}"'"""
    text = str(any_data)
    for symbol in punkt:
        text = text.replace(symbol, "")
    return text


def chance(chance_max=50):
    chh = random.randint(0, 100)
    return chh <= chance_max


def build_death(death_lvl_msg="", photo_url=scene_2_skeleton_photo):
    return (death_lvl_msg, {
        "variants": {"Итоги": "Подвести итоги", "Отменить действие": "Вернуть время назад", "Выход": "Выйти в меню", },
        "photos": ph(photo_url)},)


def ph(photo_url):
    return [{"url": photo_url}]


class Forest_game:
    name = "Место, где милые зверушки сбегают с ума"
    description = """Журчание воды, стук дятла... Где я? Вокруг ни души! Что случилось?
Чтобы выжить, вам придется разобраться в произошедшем и выбраться, используя таинственное окружение.

Рейтинг: 16+
Сложность: 99999/10
Механики: выбор вариантов, таймеры
Навыки: скорость реакции, выживание в лесу, логические размышления"""
    description_photo = "https://catherineasquithgallery.com/uploads/posts/2023-02/1676616325_catherineasquithgallery-com-p-temno-zelenii-fon-anime-132.jpg"
    started = False
    last_variants = None

    def reset_vars(self):
        self.iter = 0
        self.started = True
        self.level = "scene_1"
        self.active_timeout = ""
        self.data = {}
        self.data_backup = {}

    def __init__(self):
        self.data = None
        self.data_backup = None
        self.level = None
        self.started = None
        self.iter = 0
        self.active_timeout = ""

    def update(self, t, env=None) -> (str, dict):
        return (*self.update_cb(t, env),)

    def update_cb(self, t, env=None, start_text="") -> (str, dict):
        self.iter += 1
        print("ALL GAME DATA DEBUG", self.data, "self.data\n", self.level, "self.level\n", self.iter, "self.iter\n",
              self.started, "self.started\n", self.active_timeout, "self.active_timeout\n")

        def gen_msg(textt: str) -> str:
            return start_text + "\n\n" + textt

        d = self.data

        def save_data() -> None:
            self.data_backup = copy.deepcopy(self.data)

        def apply_time(tti=0, mult=1) -> bool:

            d["Время"] += tti
            tti *= mult
            d["Жажда"] += tti
            d["Голод"] += tti / 2
            # d["Температура"] = 36.6
            d["Выносливость"] -= tti / 2
            if d["Жажда"] > 8:
                d["Здоровье"] -= 1 * tti
            if d["Голод"] > 8:
                d["Здоровье"] -= 1 * tti
            if d["Здоровье"] > 0:
                return True
            else:
                return False

        def str_data() -> str:
            result_str = "Самочувствие и карманы:"
            printable_params = ("Здоровье", "Жажда", "Голод",)
            printable_items = ("Штаны", "Ботинки", "Верх", "Спички",
                               "Береста", "Бутылка", "Фонарик", "Нож", "Веревка", "Ружье",)
            for key in d:
                if key in printable_params:
                    result_str += f"""\n{key}: {str(d[key])}"""  # Здоровье: 10
                elif key in printable_items:
                    result_str += f"""\n{key} ({str2(d[key])})"""  # Одежда: штаны, худи # Спички {число:5, ляля }
                elif key == "Часы":
                    dtime = d["Время"]
                    time = dtime - (dtime // 24) * 24
                    result_str += f"""\nВремя: {str(time)} часов (всего {str(dtime)})"""
                # print(d[key])
            return result_str

        if "Итоги" == t:
            return f"Итоги:\nСчёт: {str(self.iter)}", {"variants": {"Выход": "Выйти в меню"}}
        # если это таймаут, он реально таймаут и не совпадает с ожидаемым таймаутом, то НИЧЕГО не делаем
        timeout_valid = (("timeout" in t) and env and env.get("timeout", False))
        timeout_active = (timeout_valid and t == self.active_timeout)
        print("TIMEOUT DEBUG", """"\ntimeout in t""", "timeout" in t,
              "\nenv (нужно чтобы был timeout:true)", env,
              "\ntimeout_active", timeout_active)

        if timeout_valid and t != self.active_timeout:
            return emp

        if timeout_active:
            self.active_timeout = ""
        # hint: check for timeout: if timeout_active and t=="timeout_3": <scenario>

        if self.level == "scene_1":
            if t == "1":
                self.level = "scene_2"
                return (*self.update_cb("start"),)
            elif t == "2":
                # SAVE
                return build_death(scene_1_run_msg, scene_1_death_photo)
            elif t == "3":
                return (*self.update_cb("idle",
                                        start_text="Эхо... Больше ничего не произошло. Даже если бы произошло, вы бы не увидели."),)
            else:  # start
                if t == "start":
                    self.last_variants = {"1": "Осторожно встать и осмотреться",
                                          "2": "Встать и начать бежать в сторону звука воды",
                                          "3": "Прокричать АУУУ"}
                    return gen_msg(scene_1_msg), {"variants": self.last_variants, "photos": ph(scene_1_photo)}
                else:
                    return gen_msg("Вы открыли глаза. Что произошло? Вокруг всё смутно зеленое..."), {
                        "variants": self.last_variants}

        elif self.level == "scene_2":
            if not d.get("сц2_скример", False) and t != "start":
                if chance(30):
                    d["сц2_скример"] = True
                    self.active_timeout = "timeout_1"
                    return "*КУСТЫ* *ЛИСТЬЯ*\nАААА ЧТО ЭТО ЗА ЗВУК???\n" * random.choice([2, 5])+"\n⏳❗", {
                        "variants": {"паника_1": "ААААААААААААА", "паника_2": "БЕЖАТЬ", "паника_3": " БЕЖАТЬ"},
                        "timer": {"cmd": "timeout_1", "time": 3}}
            if "паника" in t:
                save_data()
                alive = apply_time(4)
                if alive:
                    return (*self.update_cb("idle",
                                            start_text=scene_2_panic + scene_2_panic_alive),)
                else:
                    self.data = self.data_backup
                    return build_death(scene_2_panic + scene_2_panic_death, scene_2_skeleton_photo)

            elif t == "timeout_1":  # and timeout_active
                return "ЧТО ЭТО БЫЛ ЗА ЗВУК СЕКУНДУ НАЗАД?", {
                    "variants": {"паника_1": "ААААААААААААА", "паника_2": "БЕЖАТЬ",
                                 "Успокоиться": "Успокоиться и затаиться"}, }
            elif t == "Успокоиться":
                return (*self.update_cb("idle",
                                        start_text="Вы успокоились. Оказалось, это просто лисичка пробегала."),)
            elif t == "1":
                return (*self.update_cb("idle",
                                        start_text=str_data()),)
            elif t == "2":
                save_data()
                adding_text = "Часок прогулялись..."

                alive = apply_time(1)
                if alive:
                    if chance(30) and d.get("Веревка", None) is None:
                        adding_text += "\nВы нашли веревку!"
                        d["Веревка"] = {"Длина": 5}
                    if chance(30) and d.get("Нож", None) is None:
                        adding_text += "\nВы нашли нож!"
                        d["Нож"] = {"Тип": "Охотничий"}
                    return (*self.update_cb("idle",
                                            start_text=adding_text),)
                else:
                    self.data = self.data_backup
                    return build_death(scene_2_mox_death, scene_2_skeleton_photo)
            elif t == "3":
                save_data()
                adding_text = ""
                if d.get("сц2_был_выбран_2", 0) > 0 and chance(30):
                    alive = apply_time(3)
                    if chance(50):
                        alive = apply_time(100)
                    else:
                        adding_text = "\nВы многовато бродили, кажется, больше 3 часов! Следите за состоянием!"
                else:
                    alive = apply_time(1)
                if alive:

                    d["сц2_был_выбран_2"] = d.get("сц2_был_выбран_2", 0) + 1
                    return (*self.update_cb("idle",
                                            start_text=scene_2_mox + adding_text),)
                else:
                    self.data = self.data_backup
                    return build_death(scene_2_mox_death, scene_2_skeleton_photo)
            elif t == "4":
                return "Вы пошли вниз по ручью. На пути вам встретился большой водопад. Что будете делать?", \
                    {"variants": {"4_1": "Аккуратно спуститься", "4_2": "Обойти"}}
            elif t == "4_1":
                if d.get("Веревка", None) is not None:
                    self.level = "scene_3"
                    return (*self.update_cb("start", start_text="Вы использовали верёвку для того, чтобы не упасть!"),)
                else:
                    return build_death("Вы всё-таки поскользнулись..", scene_2_skeleton_photo)
            elif t == "4_2":
                self.level = "scene_3"
                return (*self.update_cb("start", start_text="Вы обошли водопад и спустились по пологому склону."),)
            elif t == "5":
                return build_death(scene_2_death_river, scene_2_skeleton_photo)
            else:
                if t == "start":
                    d["Здоровье"] = 9.5
                    d["Жажда"] = 0.5
                    d["Голод"] = 0.5
                    d["Температура"] = 36.6
                    d["Выносливость"] = 10.0
                    d["Время"] = 12.0

                    d["Бутылка"] = {"Емкость": 2, "Заполнена": 1}
                    d["Штаны"] = {"Есть": "Да", "Тёплые": "Да"}
                    d["Верх"] = {"Тип": "Куртка"}
                    if chance(50):  # set ohotnik
                        d["Ружье"] = {"Патроны": 1}
                        d["Штаны"]["Тёплые"] = "Нет"
                        d["Ботинки"] = {"Тип": "Кеды"}
                        d["Верх"]["Тип"] = "Худи"
                    else:
                        d["Ботинки"] = {"Тип": "Берцы"}
                        d["Фонарик"] = {"Рабочий": "Да"}
                        d["Часы"] = True
                        d["Бутылка"]["Заполнена"] = 2

                    self.last_variants = {"1": "Карманы и самочувствие",
                                          "2": "Недалеко прогуляться",
                                          "3": "Идти, ориентируясь по мху",
                                          "4": "Пойти вниз по ручью",
                                          "5": "Пойти вверх по ручью"}
                    return gen_msg(scene_2_msg), {"variants": self.last_variants, "photos": ph(scene_2_photo)}
                else:
                    return gen_msg("Вы на лужайке леса. Рядом с вами ручей."), {"variants": self.last_variants}
        elif self.level == "scene_3":
            if d.get("сц3_волк_атакует", False):
                if "паника" in t:
                    # save_data()
                    # self.data = self.data_backup
                    return build_death("Волк же читер! Так не честно!!!",
                                       scene_3_wolf_death_photo)
                elif t == "timeout_wolf":
                    return (*self.update_cb("idle", start_text=""),)
                elif t == "timeout_wolf_death":
                    return build_death(
                            "Ну что, успели допить чай?\nПока вы пили чай, волк пил вашу кровь...",
                            scene_3_wolf_death_photo)
                elif t == "атака_ножом":
                    if d.get("Нож", None) is not None:
                        return (*self.update_cb("атака", {"нож_волк": True}, start_text="Вы рыванули волка ножом в глаз!"),)
                    else:
                        return build_death(
                            "Вы полезли в карман за ножом и волк в страхе... Откусил вам голову, пометил захваченную территорию и победно взвыл!\nКак же так? А с чего вы взяли, что у вас был нож, мистер сверхразум?)",
                            scene_3_wolf_death_photo)
                elif t == "атака_ружьем":
                    if d.get("Нож", None) is not None:
                        return (*self.update_cb("атака", {"нож_волк": True}, start_text="Вы схватили ружье и сделали в волке дырку!"),)
                    else:
                        return build_death(
                            "Вы полезли в карман за ружьем и волк в страхе... Откусил вам голову, пометил захваченную территорию и победно взвыл!\nКак же так? А с чего вы взяли, что у вас было ружье, мистер сверхразум?) Вы вообще проверяли свои карманы?",
                            scene_3_wolf_death_photo)
                elif t == "попадание":
                    if d.get("сц3_волк_нож", False):
                        alive = apply_time(1, 2)
                    else:
                        alive = apply_time(1, 10)
                    if alive:
                        d["сц3_волк_атакует"] = False
                        return (*self.update_cb("idle",
                                                start_text="Волк, хромая, скрылся в чаще леса. Неизвестно, выживет ли он... главное, что вы отделались небольшими травмами и остались в живых. ВЫ решаете вернуться обратно к озеру"),)
                    else:
                        self.data = self.data_backup
                        return build_death("Вы попали волку в глаз! Он агрессивно взвыл и кинулся на вас с ещё большей злобой... Без шансов...\nВозможно, вам стоило внимательнее следить за своим здоровьем и снаряжением!", scene_3_wolf_death_photo)

                elif t == "атака":
                    def r(m):
                        return random.choice(m)

                    attack_variants = {"table": True}  # передаём таблицу из кнопок
                    knife = False
                    if env and env.get("нож_волк", False):
                        d["сц3_волк_нож"] = True
                        knife = True
                    if knife:
                        range_len = random.choice([5, 6, 7]) * 2
                    else:
                        range_len = random.choice([9, 10, 12]) * 2
                    range_arr = range(1, range_len)
                    insert_idx = random.choice(range_arr)
                    k = 0
                    ii = 0
                    row_name = "row_0"
                    row_len = random.choice([2, 4, 5, 6])
                    for i in range_arr:
                        if k == 0:
                            ii += 1
                            row_name = "row_" + str(ii)
                            attack_variants[row_name] = {}

                        if i == insert_idx:
                            attack_variants[row_name]["попадание"] = r(("👁️", "👀", "👁️‍🗨️", "👁",))  # "👊"
                        else:
                            attack_variants[row_name]["паника_" + str(i)] = r(("♿", "♿", "♿", "♿", "🐾", "🤰🏻",))
                        k += 1
                        if k >= row_len:
                            k = 0
                    # attack_vars = {"паника_1": "♿️", "паника_2": "♿️", "паника_3": "♿️",
                    #                 "паника_4": "♿️", "паника_5": "♿️", "паника_6": "♿️", "попадание": "👊"}
                    # keyss = list(attack_vars.keys())
                    # random.shuffle(keyss)
                    # attack_variants = dict()
                    # for key in keyss:
                    #    attack_variants.update({key: attack_vars[key]})
                    save_data()
                    self.active_timeout = "timeout_wolf_death"
                    timeout_death_time = 10 if knife else 3
                    return "Волк прыгнул на вас! Куда 👊?\n⏳❗", {"variants": attack_variants,
                                                    "timer": {"cmd": "timeout_wolf_death", "time": timeout_death_time}}
                else:
                    return "Волк настроен агрессивно и рычит! Что делать?!", {
                        "variants": {"паника_1": "ПАНИКОВАТЬ", "паника_2": "БЕЖАТЬ", "паника_3": "БЕЖАТЬ",
                                     "паника_4": "Кинуть в него палку", "атака_ножом": "достать нож",
                                     "атака_ружьем": "достать ружье",
                                     "атака": "ОТПОР МУСКУЛАМИ"}}
            elif t == "1":
                return (*self.update_cb("idle", start_text=str_data()),)
            elif t == "2":
                save_data()
                self.active_timeout = "timeout_wolf"
                d["сц3_волк_атакует"] = True
                return "*КУСТЫ* *ЛИСТЬЯ*\nЭТО ЖЕ ВОЛК!!! ЧТО МНЕ ДЕЛАТЬ???\n⏳❗", {
                    "variants": {"паника_1": "ААААААААААААА", "паника_2": "ПАНИКОВАТЬ", "паника_3": "БЕЖАТЬ"},
                    "timer": {"cmd": "timeout_wolf", "time": 3}}
            elif t == "3":
                alive = apply_time(1, 5)
                if alive:
                    return (*self.update_cb("idle", start_text="Вы залезли в воду и на вас напал таинственный противник.. Вы яростно боролись с ним, со всей дури мочили его руками, ногами, кричали, и, о, чудо, вам удалось победить! Но противник мог остаться жив, может, стоит проверить и ещё раз полезть в воду?)"),)
                else:
                    return build_death("На вас напал таинственный противник. Он... утащил вас под воду и.. задушил...\n(вашим противником оказалось неумение плавать)", scene_3_water_death_photo)
            elif t == "4":
                alive = apply_time(1, 4)
                if alive:
                    return build_death("""Вы добрались до верха горы. На верху горы стояла избушка...
1 часть закончилась, поздравляем, вы победили!
Жмите на кнопку "подвести итоги"!
Также, вы можете вернуть время назад, если хотите проверить другие варианты =) """,
                    scene_4_izba_photo)
                #return (*self.update_cb("idle", start_text=str_data()),)
            else:
                if t == "start":
                    self.last_variants = {"1": "Карманы и самочувствие",
                                          "2": "Умный в гору не пойдет, умный гору обойдет!",
                                          "3": "Искупаться в озере",
                                          "4": "Пойти на гору"}
                    return gen_msg(scene_3_msg), {"variants": self.last_variants, "photos": ph(scene_3_photo)}
                else:
                    return gen_msg("Вы у озера у подножья горы."), {"variants": self.last_variants}
