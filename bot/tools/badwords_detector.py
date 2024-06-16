import re
from bot.tools.badwords_lists import base_badwords_list  # list with bad words (just python list)
try:
    print('DEBUG ToxicDetector (tools badwords detector): INIT START')
    from toxicity import ToxicCommentsDetector
    toxicDetector = ToxicCommentsDetector()
    print('DEBUG ToxicDetector: INIT END')
except BaseException as err:
    print('error when init ToxicDetector:',err)
def str_to_words(text: str) -> list:
    reg = re.compile('[^a-zA-Zа-яА-Я ]')
    text = reg.sub('', text)
    text = text.lower()
    result = text.split(' ')
    if result is None:
        result = []
    return result


def format_wordlist(inp: str, concat_list: list = None, remove=False) -> (list, str,):
    if concat_list is None:
        concat_list = []
    words = str_to_words(inp)
    exc = ""
    outwords = []
    if remove:
        concat_list = [word for word in concat_list if word not in words]
    else:
        for word in words:
            if not 20 >= len(word) > 1:
                return [], "Каждое слово должно быть не длинее 20 символов."
            if not len(outwords) < 10000:
                return [], "Число введенных слов превышает 10 000."
            if word not in concat_list:
                outwords.append(word)

        if len(outwords) <= 0:
            return [], "Новых слов для добавления нет."
        if len(outwords) + len(concat_list) > 10000:
            exc = "Суммарная длина слов превышает 10000."
        else:
            concat_list.extend(outwords)
    return concat_list, exc


def detect_badwords(text: str, badwords: list = None) -> dict:
    if badwords is None:
        badwords = base_badwords_list
    words = str_to_words(text)
    result = {"found": 0.0}
    for word in words:
        if word in badwords:
            result["found"] = 1.0
            result["word"] = word
            break

    return result




def toxic_analyze(text: str, result: dict = None) -> dict:
    try:
        if result is None:
            result = {}
        result["predict"] = toxicDetector.predict([text])[0]
        # predict analyze, front
        if result["predict"]>0.985:
            result["found"] = 1.0 # перезаписываем результат обычного анализатора
            if not result.get("word", None):
                result["word"] = "Недопустимое поведение"
    except BaseException as err:
        print('DEBUG ошибка работы ToxicDetector, err=',err)
    return result


if __name__ == "__main__":
    # проверка
    #print(toxic_analyze("Ну ты норм чел так то", {"found": 1}))

    print(format_wordlist("але", ["але", "пока"])) # remove=True
    #print(detect_badwords("Вы вчера бухали?"))
