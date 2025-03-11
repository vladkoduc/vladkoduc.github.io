import logging
import asyncio
import sqlite3
from contextlib import closing
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import openpyxl
from io import BytesIO

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = 'TOKEN'
ADMIN_IDS = {1781692500}  
DB_FILE = "users_data.db"
REFERRAL_CHANNEL_ID = "ID"  
REFERRAL_CHANNEL_LINK = "LINK"  

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

def init_db():
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            user_id INTEGER PRIMARY KEY,
                            balance INTEGER DEFAULT 0,
                            was_subscribed TEXT DEFAULT '',
                            start_count INTEGER DEFAULT 0
                         )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS channels (
                            channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            link TEXT NOT NULL,
                            reward INTEGER NOT NULL,
                            chat_id TEXT NOT NULL
                         )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS withdraw_requests (
                            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            amount INTEGER NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users(user_id)
                         )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS referrals (
                            user_id INTEGER,
                            referrer_id INTEGER,
                            PRIMARY KEY (user_id, referrer_id),
                            FOREIGN KEY (user_id) REFERENCES users(user_id),
                            FOREIGN KEY (referrer_id) REFERENCES users(user_id)
                         )''')
            columns = conn.execute("PRAGMA table_info(users)").fetchall()
            if any(col[1] == "was_subscribed" and col[2].upper() != "TEXT" for col in columns):
                conn.executescript('''
                    ALTER TABLE users RENAME TO users_old;
                    CREATE TABLE users (
                        user_id INTEGER PRIMARY KEY,
                        balance INTEGER DEFAULT 0,
                        was_subscribed TEXT DEFAULT ''
                    );
                    INSERT INTO users (user_id, balance, was_subscribed)
                    SELECT user_id, balance, '' FROM users_old;
                    DROP TABLE users_old;
                ''')

def get_user_data(user_id):
    with closing(sqlite3.connect(DB_FILE)) as conn:
        result = conn.execute("SELECT balance, was_subscribed, start_count FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if result:
            was_subscribed = result[1].split(",") if result[1] else []
            return {"balance": result[0], "was_subscribed": was_subscribed, "start_count": result[2]}
        return {"balance": None, "was_subscribed": [], "start_count": 0}

def update_user_data(user_id, balance=None, was_subscribed=None, start_count=None):
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with conn:
            conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
            updates, params = [], []
            if balance is not None:
                updates.append("balance = ?")
                params.append(balance)
            if was_subscribed is not None:
                updates.append("was_subscribed = ?")
                params.append(",".join(was_subscribed))
            if start_count is not None:
                updates.append("start_count = ?")
                params.append(start_count)
            params.append(user_id)
            if updates:
                conn.execute(f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?", params)

def get_all_user_ids():
    with closing(sqlite3.connect(DB_FILE)) as conn:
        return [row[0] for row in conn.execute("SELECT user_id FROM users")]

def add_channel(name, link, reward, chat_id):
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with conn:
            conn.execute("INSERT INTO channels (name, link, reward, chat_id) VALUES (?, ?, ?, ?)", (name, link, reward, chat_id))

def get_channels():
    with closing(sqlite3.connect(DB_FILE)) as conn:
        return [{"id": row[0], "name": row[1], "link": row[2], "reward": row[3], "chat_id": row[4]} 
                for row in conn.execute("SELECT channel_id, name, link, reward, chat_id FROM channels")]

def delete_channel(channel_id):
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with conn:
            conn.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))

def add_withdraw_request(user_id, amount):
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with conn:
            conn.execute("INSERT INTO withdraw_requests (user_id, amount) VALUES (?, ?)", (user_id, amount))

def get_withdraw_requests():
    with closing(sqlite3.connect(DB_FILE)) as conn:
        return [{"request_id": row[0], "user_id": row[1], "amount": row[2]} 
                for row in conn.execute("SELECT request_id, user_id, amount FROM withdraw_requests ORDER BY request_id")]

def get_user_withdraw_requests(user_id):
    with closing(sqlite3.connect(DB_FILE)) as conn:
        return [{"request_id": row[0], "amount": row[1]} 
                for row in conn.execute("SELECT request_id, amount FROM withdraw_requests WHERE user_id = ? ORDER BY request_id", (user_id,))]

def update_withdraw_request(request_id, new_amount):
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with conn:
            conn.execute("UPDATE withdraw_requests SET amount = ? WHERE request_id = ?", (new_amount, request_id))

def delete_withdraw_request(request_id):
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with conn:
            conn.execute("DELETE FROM withdraw_requests WHERE request_id = ?", (request_id,))

def add_referral(user_id, referrer_id):
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with conn:
            existing_referral = conn.execute("SELECT referrer_id FROM referrals WHERE user_id = ?", (user_id,)).fetchone()
            if existing_referral:
                return False
            if user_id == referrer_id:
                return False
            conn.execute("INSERT INTO referrals (user_id, referrer_id) VALUES (?, ?)", (user_id, referrer_id))
            return True

class AddChannel(StatesGroup):
    name = State()
    link = State()
    reward = State()
    chat_id = State()

class CreatePost(StatesGroup):
    message = State()

def get_main_menu(user_id):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("⭐️Заработать звёзды", callback_data="earn_stars")
    ).add(
        InlineKeyboardButton("ℹ️Мой баланс", callback_data="balance")
    ).add(
        InlineKeyboardButton("👥Реферальная система", callback_data="referral_system")
    ).add(
        InlineKeyboardButton("🔈Канал бота", url="https://t.me/cow_invest")
    ).row(
        InlineKeyboardButton("📙FAQ", url="https://otvet.mail.ru/question/25122414"),
        InlineKeyboardButton("👨‍💻Поддержка", url="https://t.me/Free_Stars_Support_bot")
    )
    if user_id in ADMIN_IDS:
        keyboard.add(InlineKeyboardButton("⚙️Админ панель", callback_data="admin_panel"))
    return keyboard

def get_earn_stars_keyboard():
    keyboard = InlineKeyboardMarkup()
    for channel in get_channels():
        keyboard.add(InlineKeyboardButton(channel["name"], url=channel["link"]))
    if get_channels():
        keyboard.add(InlineKeyboardButton("✅Я подписался!", callback_data="i_subscribed"))
    keyboard.add(InlineKeyboardButton("◀️Назад", callback_data="back"))
    return keyboard

def get_balance_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("🌟Вывести звёзды", callback_data="withdraw_stars")
    ).add(
        InlineKeyboardButton("◀️Назад", callback_data="back")
    )

def get_referral_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("◀️Назад", callback_data="back")
    )

def get_referral_subscribe_keyboard(referrer_id):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Канал", url=REFERRAL_CHANNEL_LINK),
        InlineKeyboardButton("Проверить подписку", callback_data=f"check_ref_sub_{referrer_id}")
    )
    return keyboard

def get_admin_panel_keyboard():
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("➕Добавить канал", callback_data="add_channel")
    ).add(
        InlineKeyboardButton("🚹Все пользователи🚺", callback_data="all_users")
    ).add(
        InlineKeyboardButton("⭐️Отправить звёзды", callback_data="send_stars_0")
    ).add(
        InlineKeyboardButton("🌐Сделать пост", callback_data="create_post")
    )
    for channel in get_channels():
        keyboard.add(InlineKeyboardButton(f"{channel['name']} (+{channel['reward']}⭐️)", callback_data=f"delete_channel_{channel['id']}"))
    keyboard.add(InlineKeyboardButton("◀️Назад", callback_data="back"))
    return keyboard

def get_withdraw_request_keyboard(request_id, current_page, total_pages, user_id):
    keyboard = InlineKeyboardMarkup()
    if current_page > 0:
        keyboard.add(InlineKeyboardButton("◀️Назад", callback_data=f"send_stars_{current_page - 1}"))
    if current_page < total_pages - 1:
        keyboard.add(InlineKeyboardButton("Вперёд▶️", callback_data=f"send_stars_{current_page + 1}"))
    keyboard.add(
        InlineKeyboardButton("🗑Удалить", callback_data=f"delete_request_{request_id}"),
        InlineKeyboardButton("⚙️Назад в админ-панель", callback_data="admin_panel")
    )
    keyboard.add(
        InlineKeyboardButton("💬Перейти в ЛС", url=f"tg://user?id={user_id}"),
        InlineKeyboardButton("🔄Вернуть звёзды", callback_data=f"return_stars_{request_id}")
    )
    return keyboard

def get_cancel_keyboard():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("❌Отмена", callback_data="cancel_post"))

async def check_subscription(user_id):
    channels = get_channels()
    if not channels:
        await bot.send_message(user_id, "➖Нет доступных каналов для подписки!")
        return

    user_data = get_user_data(user_id)
    was_subscribed = set(user_data["was_subscribed"])
    new_balance = user_data["balance"]

    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel["chat_id"], user_id=user_id)
            is_subscribed = member.status in {'member', 'administrator', 'creator'}
            channel_id_str = str(channel["chat_id"])

            if is_subscribed and channel_id_str not in was_subscribed:
                new_balance += channel["reward"]
                was_subscribed.add(channel_id_str)
                await bot.send_message(user_id, f"🎉Вы подписались на {channel['name']}!\nВаш баланс увеличен на <b>{channel['reward']}</b>⭐️", parse_mode="HTML")
            elif is_subscribed:
                await bot.send_message(user_id, f"✅Вы уже подписаны на {channel['name']}!")
            else:
                await bot.send_message(user_id, f"🚫Вы не подписаны на {channel['name']}!")
        except Exception:
            await bot.send_message(user_id, f"❓Ошибка при проверке подписки на {channel['name']}!\nПоддержка - ...")

    update_user_data(user_id, balance=new_balance, was_subscribed=list(was_subscribed))

async def check_unsubscription_status(user_id):
    channels = get_channels()
    user_data = get_user_data(user_id)
    was_subscribed = set(user_data["was_subscribed"])
    new_balance = user_data["balance"]

    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel["chat_id"], user_id=user_id)
            is_subscribed = member.status in {'member', 'administrator', 'creator'}
            channel_id_str = str(channel["chat_id"])

            if not is_subscribed and channel_id_str in was_subscribed:
                new_balance = max(0, new_balance - channel["reward"])
                was_subscribed.remove(channel_id_str)
                await bot.send_message(user_id, f"🚫Вы отписались от канала '{channel['name']}'!\nВаш баланс уменьшен на <b>{channel['reward']}</b>⭐️", parse_mode="HTML")

                withdraw_requests = get_user_withdraw_requests(user_id)
                if withdraw_requests:
                    remaining_penalty = channel["reward"]
                    for request in withdraw_requests:
                        if remaining_penalty <= 0:
                            break
                        request_id, amount = request["request_id"], request["amount"]
                        new_amount = max(0, amount - remaining_penalty)
                        remaining_penalty = max(0, remaining_penalty - amount)
                        if new_amount > 0:
                            update_withdraw_request(request_id, new_amount)
                            await bot.send_message(user_id, f"🚫Вы отписались от канала '{channel['name']}' и ваши звёзды уменьшились при выводе!")
                        else:
                            delete_withdraw_request(request_id)
                            await bot.send_message(user_id, f"🚫Вы отписались от канала '{channel['name']}' и ваши звёзды при выводе обнулились (запрос #{request_id})!")
        except Exception:
            pass

    update_user_data(user_id, balance=new_balance, was_subscribed=list(was_subscribed))

async def unsubscription_checker():
    while True:
        tasks = [check_unsubscription_status(user_id) for user_id in get_all_user_ids()]
        if tasks:
            await asyncio.gather(*tasks)
        await asyncio.sleep(30)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args()
    user_data = get_user_data(user_id)
    
    # Increment start_count
    new_start_count = user_data["start_count"] + 1
    update_user_data(user_id, start_count=new_start_count, balance=user_data["balance"] or 0)
    
    if args:
        try:
            referrer_id = int(args)
            if user_id != referrer_id:
                if new_start_count == 1:  
                    await message.answer("Подпишись на канал:", 
                                       reply_markup=get_referral_subscribe_keyboard(referrer_id))
                else:
                    await message.answer("Вы не новый пользователь бота, вы не можете воспользоваться ссылкой")
                return
            else:
                await message.answer("❌ Вы владелец ссылки\nНажмите /start ещё раз для главного меню")
                return
        except ValueError:
            pass
    
    await message.answer("👋Добро пожаловать в бота бесплатных звёзд!\n\n⭐️Здесь ты сможешь заработать бесплатные звёзды в Telegram!\nСледуй по кнопкам ниже, чтобы заработать или вывести свои звёзды в Telegram!\n\nВерсия: 0.4.6", 
                        reply_markup=get_main_menu(user_id))

@dp.callback_query_handler(lambda c: c.data == "earn_stars")
async def process_earn_stars(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if not get_channels():
        await bot.answer_callback_query(callback_query.id, "⚠️Пока что нет кнопок для заработка звёзд в Telegram!\nСледи за ботом, чтобы заработать звёзды ⭐️", show_alert=True)
    else:
        await bot.delete_message(user_id, callback_query.message.message_id)
        await bot.send_message(user_id, "⭐️Чтобы заработать звёзды, подпишись на каналы и нажми на кнопку: Я подписался!\n❗️В случае отписки из одного канала, звёзды с твоего баланса будут вычтены (как за отдельную отписку)!", 
                             reply_markup=get_earn_stars_keyboard())

@dp.callback_query_handler(lambda c: c.data == "balance")
async def process_balance(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user = callback_query.from_user
    username = user.username or "Нет юзернейма в Telegram"
    balance = get_user_data(user_id)["balance"]
    if balance is None:
        update_user_data(user_id, balance=0)
        balance = 0
    await bot.delete_message(user_id, callback_query.message.message_id)
    await bot.send_message(user_id, f"Username пользователя: @{username}\nID пользователя: {user_id}\nТвой баланс: {balance}⭐️", 
                         reply_markup=get_balance_keyboard())

@dp.callback_query_handler(lambda c: c.data == "withdraw_stars")
async def process_withdraw_stars(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    balance = get_user_data(user_id)["balance"]
    if balance < 50:
        await bot.answer_callback_query(callback_query.id, "Нужно более 50⭐️ для вывода!", show_alert=True)
    else:
        add_withdraw_request(user_id, balance)
        update_user_data(user_id, balance=0)
        await bot.send_message(user_id, "✅Ваши звёзды успешно обнулились в боте и отправились на модерацию, чтобы отправить их Вам!\n❗️В случае отписки от любого канала, бот автоматически вычтет звёзды или удалит вашу заявку с модерации!\n\nВ течение 72-х часов, на ваш аккаунт в Telegram будут отправлены Ваши ⭐️\nНе переживайте, мы уведомим Вас о зачисление звёзд. Если прошло больше времени, пишите в поддержку: @Free_Stars_Support_bot")

@dp.callback_query_handler(lambda c: c.data == "i_subscribed")
async def process_i_subscribed(callback_query: types.CallbackQuery):
    await check_subscription(callback_query.from_user.id)

@dp.callback_query_handler(lambda c: c.data == "referral_system")
async def process_referral_system(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    referral_link = f"https://t.me/TaskCryptoBot?start={user_id}"
    await bot.delete_message(user_id, callback_query.message.message_id)
    await bot.send_message(user_id, f"👥Ваша реферальная ссылка:\n<code>{referral_link}</code>\n*Тыкни, что бы ссылка скопировалась\n\nПриглашайте друзей и получайте <b>0.5</b>⭐️ за каждого нового подписчика!", parse_mode='HTML',
                         reply_markup=get_referral_keyboard())

@dp.callback_query_handler(lambda c: c.data.startswith("check_ref_sub_"))
async def process_check_referral_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    referrer_id = int(callback_query.data.split("_")[3])
    
    try:
        member = await bot.get_chat_member(chat_id=REFERRAL_CHANNEL_ID, user_id=user_id)
        if member.status in {'member', 'administrator', 'creator'}:
            await bot.delete_message(user_id, callback_query.message.message_id)
            
            if add_referral(user_id, referrer_id):
                referrer_data = get_user_data(referrer_id)
                new_balance = (referrer_data["balance"] or 0) + 0.5
                update_user_data(referrer_id, balance=new_balance)
                await bot.send_message(referrer_id, "🎉Активирована реферальная ссылка!\nВам начислено <b>0.5<b>⭐️", parse_mode='HTML')
            
            await bot.send_message(user_id, "👋Добро пожаловать в бота бесплатных звёзд!\n\n⭐️Здесь ты сможешь заработать бесплатные звёзды в Telegram!\nСледуй по кнопкам ниже, чтобы заработать или вывести свои звёзды в Telegram!\n\nВерсия: 0.4.6",
                                 reply_markup=get_main_menu(user_id))
        else:
            await bot.answer_callback_query(callback_query.id, "❌Вы ещё не подписались на канал!", show_alert=True)
    except Exception as e:
        logging.error(f"Error checking subscription for user {user_id}: {e}")
        await bot.answer_callback_query(callback_query.id, "❌Ошибка при проверке подписки! Обратитесь в поддержку.", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == "back")
async def process_back(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await bot.delete_message(user_id, callback_query.message.message_id)
    await bot.send_message(user_id, "👋Добро пожаловать в бота бесплатных звёзд!\n\n⭐️Здесь ты сможешь заработать бесплатные звёзды в Telegram!\nСледуй по кнопкам ниже, чтобы заработать или вывести свои звёзды в Telegram!\n\nВерсия: 0.4.6", 
                         reply_markup=get_main_menu(user_id))

@dp.callback_query_handler(lambda c: c.data == "admin_panel")
async def process_admin_panel(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id in ADMIN_IDS:
        await bot.delete_message(user_id, callback_query.message.message_id)
        await bot.send_message(user_id, "👋Добро пожаловать в Админ панель!", reply_markup=get_admin_panel_keyboard())
    else:
        await bot.answer_callback_query(callback_query.id, "❌У вас нет доступа к этой функции!", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == "add_channel", state=None)
async def process_add_channel(callback_query: types.CallbackQuery):
    if callback_query.from_user.id in ADMIN_IDS:
        await bot.send_message(callback_query.from_user.id, "1️⃣Введите название кнопки:")
        await AddChannel.name.set()
    else:
        await bot.answer_callback_query(callback_query.id, "❌У вас нет доступа к этой функции!", show_alert=True)

@dp.message_handler(state=AddChannel.name)
async def process_channel_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await bot.send_message(message.from_user.id, "2️⃣Введите ссылку на канал (например, https://t.me/+xxxx):")
    await AddChannel.link.set()

@dp.message_handler(state=AddChannel.link)
async def process_channel_link(message: types.Message, state: FSMContext):
    await state.update_data(link=message.text)
    await bot.send_message(message.from_user.id, "3️⃣Введите количество звёзд за подписку:")
    await AddChannel.reward.set()

@dp.message_handler(state=AddChannel.reward)
async def process_channel_reward(message: types.Message, state: FSMContext):
    try:
        reward = float(message.text)
        if reward <= 0:
            raise ValueError
        await state.update_data(reward=reward)
        await bot.send_message(message.from_user.id, "4️⃣Введите ID канала (например, -123456789):")
        await AddChannel.chat_id.set()
    except ValueError:
        await bot.send_message(message.from_user.id, "❗️Пожалуйста, введите положительное число, ноль нельзя!\nДесятичные числа можно вводить, только через точку, например: 0.5!")
        await AddChannel.reward.set()

@dp.message_handler(state=AddChannel.chat_id)
async def process_channel_chat_id(message: types.Message, state: FSMContext):
    data = await state.get_data()
    add_channel(data["name"], data["link"], data["reward"], message.text)
    await bot.send_message(message.from_user.id, f"🥳Канал '{data['name']}' добавлен!", reply_markup=get_admin_panel_keyboard())
    await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith("delete_channel_"))
async def process_delete_channel(callback_query: types.CallbackQuery):
    if callback_query.from_user.id in ADMIN_IDS:
        channel_id = int(callback_query.data.split("_")[2])
        delete_channel(channel_id)
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        await bot.send_message(callback_query.from_user.id, "🗑Канал удалён!", reply_markup=get_admin_panel_keyboard())
    else:
        await bot.answer_callback_query(callback_query.id, "❌У вас нет доступа к этой функции!", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == "all_users")
async def process_all_users(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in ADMIN_IDS:
        await bot.answer_callback_query(callback_query.id, "❌У вас нет доступа к этой функции!", show_alert=True)
        return

    user_ids = get_all_user_ids()
    if not user_ids:
        await bot.answer_callback_query(callback_query.id, "❌Пользователей нет!", show_alert=True)
        return

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Users"
    ws.append(["Telegram Link"])

    for uid in user_ids:
        try:
            chat = await bot.get_chat(uid)
            username = chat.username  
            if username and username.strip():  
                link = f"https://t.me/{username} @{username}"
            else:
                link = f"tg://user?id={uid} {uid}"  
            ws.append([link])
        except Exception as e:
            logging.error(f"Ошибка при получении данных пользователя {uid}: {e}")
            link = f"tg://user?id={uid} {uid}" 
            ws.append([link])

    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    await bot.send_message(user_id, "Нажмите /start ещё раз для главного меню")
    await bot.send_document(user_id, document=types.InputFile(excel_file, filename="users.xlsx"), caption="Список всех пользователей")

@dp.callback_query_handler(lambda c: c.data.startswith("send_stars_"))
async def process_send_stars(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in ADMIN_IDS:
        await bot.answer_callback_query(callback_query.id, "❌У вас нет доступа к этой функции!", show_alert=True)
        return

    page = int(callback_query.data.split("_")[2])
    requests = get_withdraw_requests()
    if not requests:
        await bot.answer_callback_query(callback_query.id, "❌Нет запросов на вывод!", show_alert=True)
        return
    if page < 0 or page >= len(requests):
        return

    request = requests[page]
    try:
        chat = await bot.get_chat(request["user_id"])
        username = chat.username or "Нет юзернейма в Telegram"
    except Exception:
        username = "❌Ошибка получения данных"

    await bot.delete_message(user_id, callback_query.message.message_id)
    await bot.send_message(user_id, 
                         f"ID пользователя: {request['user_id']}\nЮзернейм: @{username}\nКоличество звёзд: {request['amount']}⭐️", 
                         reply_markup=get_withdraw_request_keyboard(request["request_id"], page, len(requests), request["user_id"]))

@dp.callback_query_handler(lambda c: c.data.startswith("return_stars_"))
async def process_return_stars(callback_query: types.CallbackQuery):
    admin_id = callback_query.from_user.id
    if admin_id not in ADMIN_IDS:
        await bot.answer_callback_query(callback_query.id, "❌У вас нет доступа к этой функции!", show_alert=True)
        return

    request_id = int(callback_query.data.split("_")[2])
    requests = get_withdraw_requests()
    request = next((r for r in requests if r["request_id"] == request_id), None)

    if not request:
        await bot.answer_callback_query(callback_query.id, "❌Запрос не найден!", show_alert=True)
        return

    user_id = request["user_id"]
    amount = request["amount"]

    user_data = get_user_data(user_id)
    new_balance = user_data["balance"] + amount
    update_user_data(user_id, balance=new_balance)

    delete_withdraw_request(request_id)

    await bot.delete_message(admin_id, callback_query.message.message_id)
    await bot.send_message(admin_id, f"✅Звёзды ({amount}⭐️) возвращены пользователю {user_id}!", 
                         reply_markup=get_admin_panel_keyboard())

    try:
        await bot.send_message(user_id, f"🔄Ваш запрос на вывод {amount}⭐️ был отклонён, звёзды возвращены на ваш баланс!\nНовый баланс: {new_balance}⭐️")
    except Exception as e:
        logging.error(f"❌Не удалось уведомить пользователя {user_id}: {e}")


@dp.callback_query_handler(lambda c: c.data.startswith("delete_request_"))
async def process_delete_request(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in ADMIN_IDS:
        await bot.answer_callback_query(callback_query.id, "❌У вас нет доступа к этой функции!", show_alert=True)
        return

    request_id = int(callback_query.data.split("_")[2])
    requests = get_withdraw_requests()
    request = next((r for r in requests if r["request_id"] == request_id), None)
    if request:
        try:
            await bot.send_message(request["user_id"], f"🥳Успешно! В ваш профиль Telegram зачислено: {request['amount']}⭐️\nЕсли что пошло не так, то напишите пожалуйста в поддержку: @Free_Stars_Support_bot")
        except Exception as e:
            logging.error(f"❌Не удалось отправить сообщение пользователю {request['user_id']}: {e}")
        delete_withdraw_request(request_id)
        await bot.delete_message(user_id, callback_query.message.message_id)
        await bot.send_message(user_id, "✅Запрос удалён и звёзды отправлены!", reply_markup=get_admin_panel_keyboard())
    else:
        await bot.answer_callback_query(callback_query.id, "❌Запрос не найден!", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == "create_post", state=None)
async def process_create_post(callback_query: types.CallbackQuery):
    if callback_query.from_user.id in ADMIN_IDS:
        await bot.send_message(callback_query.from_user.id, "Введите текст сообщения для отправки всем пользователям:", reply_markup=get_cancel_keyboard())
        await CreatePost.message.set()
    else:
        await bot.answer_callback_query(callback_query.id, "❌У вас нет доступа к этой функции!", show_alert=True)

@dp.message_handler(state=CreatePost.message)
async def process_post_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.answer("❌У вас нет доступа к этой функции!")
        await state.finish()
        return

    post_text = message.text
    user_ids = get_all_user_ids()
    success_count = 0

    for uid in user_ids:
        try:
            await bot.send_message(uid, post_text)
            success_count += 1
        except Exception as e:
            logging.error(f"❌Не удалось отправить сообщение пользователю {uid}: {e}")
        await asyncio.sleep(0.05)

    await bot.send_message(user_id, f"🥳Пост отправлен!\nУспешно: {success_count}\nНе удалось: {len(user_ids) - success_count}", reply_markup=get_admin_panel_keyboard())
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "cancel_post", state=CreatePost.message)
async def process_cancel_post(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id in ADMIN_IDS:
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        await bot.send_message(callback_query.from_user.id, "❌Создание поста отменено!", reply_markup=get_admin_panel_keyboard())
        await state.finish()
    else:
        await bot.answer_callback_query(callback_query.id, "❌У вас нет доступа к этой функции!", show_alert=True)

async def on_startup(_):
    init_db()
    asyncio.create_task(unsubscription_checker())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)