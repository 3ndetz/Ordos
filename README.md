---
title: TheOrdosBot
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

<details>
<summary>
Что делают 2 разных бота в 1 репозитории?
</summary>

Изначально планировалось, что будет игровой бот, который будет поддерживать как Discord, так и Telegram, но по итогу я ограничился лишь одним ботом для игр. Соответственно, базу для обоих ботов я уже написал, но в Discord-бота попросту не успел внедрить функционал. Далее я делал ВКР по теме, связанной с модерацией голосовых чатов, и поэтому использовал Discord-базу для его создания. Выложить на GitHub всё это я решился только недавно ну и у меня не было много лишнего времени, чтобы заморачиваться над разделением репозиториев) Поэтому вот так.

</details>


## Использование Discord-бота
_Ordos (греч.) — порядок_

### Демо

<details>
<summary>
Video demo
</summary>

https://github.com/3ndetz/Ordos/assets/30196290/17ac3ebb-3536-432a-8b46-6b47b1b7909e

[(Или скачать ссылкой)](https://github.com/3ndetz/Ordos/raw/master/demo/VoiceModerLight.mp4)

</details>

<video src='https://github.com/3ndetz/Ordos/assets/30196290/17ac3ebb-3536-432a-8b46-6b47b1b7909e'> </video>



### Команды и описание:

Бот автоматически модерирует один из голосовых чатов на серверах Discord. Список запрещенных слов можно настроить индивидуально для каждого сервера. Есть функция определния **токсичного** поведения.

Подробнее:

[Документация (Google Docs)](https://docs.google.com/document/d/1nsf2yZxk8Er3l-1EAKF9AaUWm_-bOYJf4Jv_lLzM5sg/edit)

### Запущенный экземпляр от автора:
_Не на постоянном хосте, может быть отключен_

[Ссылка для добавления бота к себе на сервер](https://discord.com/api/oauth2/authorize?client_id=1192729753392787456&permissions=8&scope=bot)


## Использование Telegram-бота

### Запущенный экземпляр:
_Не на постоянном хосте, может быть отключен_

Telegram [@the_ordos_bot](https://t.me/the_ordos_bot/)

### Пара скриншотов работы квеста в Telegram-боте:
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

## Для запуска своих экземпляров
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
