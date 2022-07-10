# Нейрогороскопы (бот)

## Описание

Бот предоставляет гороскопы, сгенерированные нейросетью GPT-2, обученной на текстах Владимира Сорокина и Виктора Пелевина.

Автор проекта с нейрогороскопами - http://t.me/krasniy_doshik  
- Нейрогороскопы в ВК: https://vk.com/neural_horo  
- Нейрогороскопы в Telegram: https://t.me/neural_horo

Автор бота - XRain (то есть я :)  
- Бот в ВК: https://vk.com/neural_horo_bot  
- Бот в Telegram: https://t.me/neural_horo_bot

## Как запустить бота

1. Указать токены и другие необходимые для работы бота данные в .env файле:
```shell
cp .env.example .env
edit .env
```
2. Собрать docker-контейнеры
```shell
docker build -t neural_horo_bot_vk --target bot_vk .
docker build -t neural_horo_bot_tg --target bot_tg .
```

3. Запустить docker-контейнеры
```shell
docker run --name neural_horo_bot_vk --restart always --detach neural_horo_bot_vk
docker run --name neural_horo_bot_tg --restart always --detach neural_horo_bot_tg
```
