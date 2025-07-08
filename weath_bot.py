from telegram import Update
from telegram.ext import Application, CommandHandler
from telegram.helpers import escape_markdown
import asyncio
import aiosqlite as sql
import getweather as gw


TOKEN = "8073885441:AAEDUWIW74OiGlG2g2zxcPIWETr21q6Kdv8"
DB_NAME = 'data.db'


async def init_db(_):
    async with sql.connect(DB_NAME) as conn:
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        city TEXT
        )
        ''')
        await conn.commit()


async def add_city(user_id, city):
    async with sql.connect(DB_NAME) as conn:
        cursor = await conn.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id, ))
        exists = await cursor.fetchone()
        if not exists:
            await conn.execute('''
            INSERT OR IGNORE INTO users (user_id, city)
            VALUES (?, ?)
            ''', (user_id, city))
            await conn.commit()
            return
        await conn.execute("UPDATE users SET city = ? WHERE user_id = ?", (city, user_id))
        await conn.commit()
        
        
async def add(update: Update, context):
    user = update.effective_user
    city = ' '.join(context.args)
    if len(city) == 0:
        await update.message.reply_text('Укажите город')
        return
    await add_city(user.id, city)
    await update.message.reply_text(f'{city} установлен как ваш город')


async def start(update: Update, context):
    await update.message.reply_text('''
    СПРАВКА:
    > Введите команду /get и название города через пробел;
    > Чтобы установить свой город, введите команду /add и название города. Команда /get выдаст погоду вашего города по умолчанию
    ''')


async def get(update: Update, context):
    city = ' '.join(context.args)
    
    if len(city) == 0:
        user = update.effective_user
        user_id = user.id
        async with sql.connect(DB_NAME) as conn:
            cursor = await conn.execute('SELECT city FROM users WHERE user_id = ?', (user_id,))
            result = await cursor.fetchone()
        
        if result:
            city = result[0]
        else:
            city = 'Смоленск'
            
    out = await asyncio.to_thread(gw.getw, city)
    
    if out['lat'] == "20.767" and out['lon'] == "105.000":
        await update.message.reply_text(f'Город {city} не найден')
    else: 
        out['date'] = escape_markdown(out['date'], version = 2)
        out['pressure'] = escape_markdown(str(out['pressure']), version = 2)
        
        getweather = f'''ПОГОДА в городе *{city}*:
        
        Текущие дата/время: *{out['date']}*
        
        Температура: *{out['temperature']}* °C
        Ощущается как: {out['feels']} °C
        На небе: *{out['sky']}*
        Покрытие облаками: *{out['cloudcover']}* %
        Влажность: *{out['humidity']}* %
        Скорость ветра: *{out['windspeed']}* км/ч
        Скорость порывов ветра: {out['windgust']} км/ч
        Атмосферное давление: *{out['pressure']}* мм рт\\. ст\\.
        \\-\\-\\-
        Вероятность тумана: {out['fog']} %
        Вероятность дождя: {out['rain']} %
        Вероятность грозы: {out['thunder']} %
        Вероятность выпадения снега: {out['snow']} %
        Вероятность оледенения: {out['frost']} %
        \\-\\-\\-
        Освещённость луны: *{out['moon']}* %
        Восход луны: *{out['moonrise']}*
        Заход луны: *{out['moonset']}*
        Рассвет: *{out['sunrise']}*
        Закат: *{out['sunset']}*
        Продолжительность дня: *{out['daylight']}*
        '''
        
        await update.message.reply_text(getweather, parse_mode = 'MarkdownV2')


def main():
    app = Application.builder().token(TOKEN).post_init(init_db).build()
    
    start_handler = CommandHandler('start', start)
    weather_handler = CommandHandler('get', get)
    set_handler = CommandHandler('add', add)
    
    app.add_handler(start_handler)
    app.add_handler(weather_handler)
    app.add_handler(set_handler)
    
    app.run_polling()


if __name__ == "__main__":
    main()

