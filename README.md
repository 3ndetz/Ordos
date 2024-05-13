---
Title: TheOrdosBot
for Telegram: quest game bot 
for Discord: automatic voice moderation
tg run command: python bot/telegram_bot.py
license: mit
---

## Что это?
Ordos — многофункциональный бот.
В репозиторий включен игровой квест-бот для Telegram и бот-модератор для Discord. Discord сразу запустить не получится (см. инструкцию запуска).

|Telegram|Discord|
|---|---|
|![image](https://github.com/3ndetz/Ordos/assets/30196290/d29a8eac-51d0-456a-a3c3-2ff0faae6b9a)|![image](https://github.com/3ndetz/Ordos/assets/30196290/fb3210ba-3dae-4303-ada1-ce6409a6981c)|


## Использование Discord

### Запущенный экземпляр (не на постоянном хосте, может быть отключен):
[Добавить бота к себе на сервер](https://discord.com/api/oauth2/authorize?client_id=1192729753392787456&permissions=8&scope=bot)

### Команды и описание:
[Документация](https://docs.google.com/document/d/1nsf2yZxk8Er3l-1EAKF9AaUWm_-bOYJf4Jv_lLzM5sg/edit)

## Использование Telegram

### Запущенный экземпляр (не на постоянном хосте, может быть отключен):
tg @the_ordos_bot

### Пара скриншотов:
<details>
  
  1.
  ![image](https://github.com/3ndetz/Ordos/assets/30196290/9ee9d6e3-0b64-4f80-9d22-c40b1d8b52b4)
  
  2.
  ![image](https://github.com/3ndetz/Ordos/assets/30196290/6f854295-6a78-4ec3-8a4d-7af952c39f6f)

  3.
  ![image](https://github.com/3ndetz/Ordos/assets/30196290/fbd46f58-43c5-45b5-95f4-5914362ff4e8)

  4.
  ![image](https://github.com/3ndetz/Ordos/assets/30196290/71c7d00f-635d-4b4b-ab9b-220849be0ad5)

</details>

## Для запуска
Для запуска ботов нужно создать папку config в корне и в неё поместить config.py.
Что писать в конфиг читайте далее.

### Telegram (игровой квест-бот)
Получите токен от Telegram @BotFather и внесите его в config.py.

| config.py | run command |
| --- | --- |
| tgbot_token (string, BotFather token) | python bot/telegram_bot.py |

### Discord (модератор голосовых каналов)

Предварительно нужно реализовать интерфейс STT ресивера аналогично примеру STT_Process_examples/docker_reciever.py

STT ресивер к репозиторию не прилагается, это отдельный скрипт (могу отдельно залить на GitHub или Docker если вдруг кому-то понадобится...).
Заливаю отдельно, т.к. в рамках ВКР я использовал STT Nvidia NEMO с Docker'a, соответственно у меня скрипт аж на другой системе (Docker -> Windows WSL -> Linux Docker NEMO Image), а этот интерфейс позволяет с помощью SyncManager общаться двум Python-процессам в рамках одной сети.


| config.py dsbot_token | stt_connect_key | run command |
| --- | --- | --- |
| (string, Discord Dev token)|bytes string ```b'key'``` for connect to stt reciever|python bot/discord_bot.py|

### Запуск обоих сразу

| config | run command |
| --- | --- |
| настроить оба | python main.py |
