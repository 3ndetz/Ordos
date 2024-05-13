---
title: TheOrdosBot
for Telegram: quest game bot
for Discord: automatic voice moderation
tg run command: python bot/telegram_bot.py
license: mit
---

Ordos — многофункциональный бот.
В репозиторий включен игровой квест-бот для Telegram и бот-модератор для Discord. Discord сразу запустить не получится (см. инструкцию запуска).

## Для запуска
Для запуска ботов нужно создать папку config в корне и в неё поместить config.py.
Что писать в конфиг читайте далее.

### Telegram (игровой квест-бот)
Получите токен от BotFather и внесите его в config.py.
---
config.py: tgbot_token (string, BotFather token)
run command: python bot/telegram_bot.py
---

### Discord (модератор голосовых каналов)

Предварительно нужно реализовать интерфейс STT ресивера аналогично примеру STT_Process_examples/docker_reciever.py

STT ресивер к репозиторию не прилагается, это отдельный скрипт (могу отдельно залить на GitHub или Docker если вдруг кому-то понадобится...).
Заливаю отдельно, т.к. в рамках ВКР я использовал STT Nvidia NEMO с Docker'a, соответственно у меня скрипт аж на другой системе (Docker -> Windows WSL -> Linux Docker NEMO Image), а этот интерфейс позволяет с помощью SyncManager общаться двум процессам в рамках одной системы с помощью сети.

---
config.py dsbot_token: (string, Discord Dev token)
config.py stt_connect_key: (bytes string for connect to stt)
run command: python bot/discord_bot.py
---

### Запуск обоих сразу
---
config: настроить оба
run command: python main.py
---