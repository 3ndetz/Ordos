from games.forest import Forest_game


def get_game_description(game_class: Forest_game) -> (str, dict,):
    text = f"""{game_class.description}"""
    extra = {"variants":["Начать игру", "Выбор игры"]}
    if game_class.description_photo:
        extra["photos"] = [{"url":game_class.description_photo, "caption":game_class.name}]
    return text, extra

def game_started(game_class) -> bool:
    if game_class:
        return game_class.started
    else:
        return False

game_start_night_msg ="""Запущена игра "Судная ночь".
Правила:    
    - веди себя тихо
    - никому не перечь до судной ночи

Ты идешь в магазин и случайно толкнул(а) какую-то неприятную старуху. Она сразу выругалась в твою сторону матами."""
class core_session:
    id = ""
    game = ""
    g = None
    game_iter = -1
    last_msg = "Выбор игры"
    last_button_pressed_time = 0.0

    def __init__(self, id):
        self.id = id
        self.reset_game_vars()

    def reset_game_vars(self):
        self.game = ""
        self.game_iter = -1
        self.g = None

    def process_message(self, msg: str, env: dict = None) -> (str, dict,):
        extra = {}
        variants = None
        text = "нет не "+msg
        #games = ["Место, где милые зверушки...","Судная ночь","Тест","Выход"]
        games = ["Место, где милые зверушки...", "Выход"]
        if "Выход" == msg:
            text = "Выход в главное меню"
            extra["variants"] = ["Выбор игры"]
            self.reset_game_vars()
        else:
            if game_started(self.g):
                text, extra = self.g.update(msg, env=env)
            else:
                if "Выбор игры" == msg:
                    text = "Из игр доступны:"
                    variants = list(games)
                for game in games:
                    if game == msg:
                        if game == "Место, где милые зверушки...":
                            self.g = Forest_game()
                            text, extra = get_game_description(self.g)
                            variants = extra["variants"]
                            print(extra)
                    # old demo if-else games
                        self.game_iter = 0
                        self.game = game

                if "Начать игру" == msg and self.game:
                    self.g.reset_vars()
                    text, extra = self.g.update("start", env=env)
                    variants = extra["variants"]
                    print(extra)
                # old demo if-else games
                if self.game == "Тест":
                    if self.game_iter == 0:
                        if "timeout" == msg:
                            self.game_iter += 2
                        elif "привет" == msg:
                            self.game_iter += 1
                        else:
                            text = "timer test started!"
                            variants = ["привет"]
                            extra["timer"] = {"time": 5}
                    if self.game_iter == 1:
                        text = "timer test GAME ITER = 1"
                        variants = ["Выход"]
                    if self.game_iter == 2:
                        text = "timer test GAME ITER = 2 TIMEOUT"
                        variants = ["Выход"]
                elif self.game == "Судная ночь":
                    if self.game_iter==0:
                        text=game_start_night_msg
                        variants = ["Выругаться в ответ", "Попросить прощения"]
                        if "Выругаться в ответ" == msg:
                            text = "Она тебя запомнит"
                            self.game_iter += 1
                        elif "Попросить прощения" == msg:
                            text = "Она харкнула тебе под ноги"
                            self.game_iter += 1
                    elif self.game_iter==1:
                        text+="\nТы дошел(ла) до продуктового магазина и продавец сказал не покупать кока колу. Что купишь?"
                        variants = ["Кока колу", "Банку консервов"]
                        if "Кока колу" == msg:
                            text = "продавец разозлился, посмотрел на тебя с ненавистью и ты умер от страха"
                            game_iter = 0
                            variants = ["Выход"]
                        elif "Банку консервов" == msg:
                            text = "Ты сожрал всю банку консервов, пришел домой и заснул. Судная ночь прошла, ты выжил молодец!"
                            self.game_iter += 1
                    elif self.game_iter>1:
                        text+="\nВы победили!"
                        variants = ["Выход"]
                        game = ""
                        game_iter = -1
                extra["variants"] = variants
            print(
                f'[DEBUG GAME SESSION MSG PROCESS INFO]\nid={str(self.id)}\ngame_iter={str(self.game_iter)}\ngame={self.game}\nincoming msg={msg}')
            #if not variants:
            #    variants = ["Напиши свой ответ (выбора вариантов нет)"]

        self.last_msg = msg
        return text, extra
