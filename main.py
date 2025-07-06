# === TO'LIQ ISHLAYDIGAN TELEGRAM GAME BOT KODI ===
# O'yinlar: Mines, Aviator, Dice
# Tugmalar: balans, hisob toldirish, pul chiqarish, bonus, referal

from keep_alive import keep_alive
import telebot
from telebot import types
import random
import threading
import time
import datetime

TOKEN = "8161107014:AAGBWEYVxie7-pB4-2FoGCPjCv_sl0yHogc"
bot = telebot.TeleBot(TOKEN)

user_balances = {}
addbal_state = {}
lucky_users = set()
user_settings = {}
user_games = {}
user_mines_states = {}
user_aviator = {}
user_bonus_state = {}
user_positions = {}
withdraw_sessions = {}
user_states = {}
user_referred_by = {}
tic_tac_toe_states = {}
user_chicken_states = {}
multipliers = [1.08, 1.17, 1.27, 1.56, 1.89, 2.31, 2.8, 3.6, 5.5, 6.5]
azart_enabled = False
ADMIN_ID = 5815294733  # O'zingizning Telegram ID'ingiz
azart_enabled = True  # Dastlabki holat: yoqilgan

cancel_commands = [
    "/start", "/help", "/addbal", "/cancel",
    "❌ Bekor qilish", "🔙 Orqaga",
    "💰 Balance", "💳 Hisob toldirish", "🎲 Play Dice",
    "💣 Play Mines", "🛩 Play Aviator", "💸 Pul chiqarish",
    "🎁 Kunlik bonus", "👥 Referal link", "🎮 Play TicTacToe",
    "🐔 Play Chicken"  # 👈 Qo‘shildi
]


user_referred_by = {}  # Foydalanuvchi qaysi referal orqali kelganini saqlash uchun

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    if user_id not in user_balances:
        user_balances[user_id] = 3000  # boshlang‘ich balans

        if len(args) > 1:
            try:
                ref_id = int(args[1])
                if ref_id != user_id:
                    # Agar foydalanuvchi hali referal orqali bonus olmagan bo‘lsa
                    if user_id not in user_referred_by:
                        user_referred_by[user_id] = ref_id
                        user_balances[ref_id] = user_balances.get(ref_id, 0) + 1000
                        bot.send_message(ref_id, f"🎉 Siz yangi foydalanuvchini taklif qilib, 1000 so‘m bonus oldingiz!")
            except ValueError:
                pass
    else:
        # Foydalanuvchi mavjud bo‘lsa, referal kodi bilan bonus bermaymiz
        pass

    back_to_main_menu(message)



# === Asosiy menyuga qaytish funksiyasi ===
def back_to_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('💣 Play Mines', '🛩 Play Aviator')
    markup.add('🎲 Play Dice', '🎮 Play TicTacToe')
    markup.add('🐔 Play Chicken')  # 👈 Yangi tugma qo‘shildi
    markup.add('💰 Balance', '💸 Pul chiqarish')
    markup.add('💳 Hisob toldirish', '🎁 Kunlik bonus', '👥 Referal link')
    bot.send_message(message.chat.id, "🔙 Asosiy menyu:", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "💰 Balance")
def show_balance(message):
    user_id = message.from_user.id
    bal = user_balances.get(user_id, 0)
    bot.send_message(message.chat.id, f"💰 Sizning balansingiz: {bal} so‘m")

cancel_commands = [
    "/start", "/help", "/addbal", "/cancel",
    "💰 Balance", "💳 Hisob toldirish", "🎲 Play Dice", "💣 Play Mines",
    "🛩 Play Aviator", "🎮 Play TicTacToe",  # ✅ Qo‘shildi
    "💸 Pul chiqarish", "🎁 Kunlik bonus", "👥 Referal link",
    "🔙 Orqaga"
]

@bot.message_handler(commands=['addbal'])
def addbal_start(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(message.chat.id, "🆔 Foydalanuvchi ID raqamini kiriting:")
    bot.register_next_step_handler(msg, addbal_get_id)

def addbal_get_id(message):
    if message.text.startswith("/") or message.text in cancel_commands:
        bot.send_message(message.chat.id, "❌ Jarayon bekor qilindi. /addbal ni qayta bosing.")
        addbal_state.pop(message.from_user.id, None)
        return

    try:
        target_id = int(message.text)
        addbal_state[message.from_user.id] = {'target_id': target_id}
        msg = bot.send_message(message.chat.id, "💵 Qo‘shiladigan miqdorni kiriting:")
        bot.register_next_step_handler(msg, addbal_get_amount)
    except Exception:
        msg = bot.send_message(message.chat.id, "❌ Noto‘g‘ri ID. Iltimos, raqam kiriting:")
        bot.register_next_step_handler(msg, addbal_get_id)

def addbal_get_amount(message):
    if message.text.startswith("/") or message.text in cancel_commands:
        bot.send_message(message.chat.id, "❌ Jarayon bekor qilindi. /addbal ni qayta bosing.")
        addbal_state.pop(message.from_user.id, None)
        return

    try:
        amount = int(message.text)
        if amount <= 0:
            raise ValueError()
        admin_id = message.from_user.id
        target_id = addbal_state[admin_id]['target_id']

        user_balances[target_id] = user_balances.get(target_id, 0) + amount

        bot.send_message(admin_id, f"✅ {amount:,} so‘m foydalanuvchi {target_id} ga qo‘shildi.")

        try:
            bot.send_message(target_id, f"✅ Hisobingizga {amount:,} so‘m tushirildi!", parse_mode="HTML")
        except Exception:
            # Foydalanuvchiga xabar yuborishda xato bo‘lsa, e'tiborsiz qoldiramiz
            pass

        del addbal_state[admin_id]

    except Exception:
        msg = bot.send_message(message.chat.id, "❌ Noto‘g‘ri miqdor. Qaytadan raqam kiriting:")
        bot.register_next_step_handler(msg, addbal_get_amount)


@bot.message_handler(func=lambda m: m.text == "👥 Referal link")
def referal_link(message):
    uid = message.from_user.id
    username = bot.get_me().username
    link = f"https://t.me/{username}?start={uid}"
    bot.send_message(message.chat.id, f"👥 Referal linkingiz:\n{link}")

@bot.message_handler(func=lambda message: message.text == "💳 Hisob toldirish")
def handle_deposit(message):
    user_id = message.from_user.id

    text = (
        f"🆔 <b>Sizning ID:</b> <code>{user_id}</code>\n\n"
        f"📨 Iltimos, ushbu ID raqamingizni <b>@for_X_bott</b> ga yuboring.\n\n"
        f"💳 Sizga to‘lov uchun karta raqami yuboriladi. \n"
        f"📥 Karta raqamiga to‘lov qilganingizdan so‘ng, to‘lov chekini adminga yuboring.\n\n"
        f"✅ Admin to‘lovni tekshirib, <b>ID raqamingiz asosida</b> balansingizni to‘ldirib beradi."
    )

    bot.send_message(message.chat.id, text, parse_mode="HTML")
    # Botni sozlash, importlar, token va boshqalar

def back_to_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('💣 Play Mines', '🛩 Play Aviator')
    markup.add('🎲 Play Dice', '🎮 Play TicTacToe')
    markup.add('🐔 Play Chicken')  # 🆕 Chicken o‘yini tugmasi qo‘shildi
    markup.add('💰 Balance', '💳 Hisob toldirish')
    markup.add('💸 Pul chiqarish', '🎁 Kunlik bonus')
    markup.add('👥 Referal link')
    bot.send_message(message.chat.id, "🔙 Asosiy menyu:", reply_markup=markup)


# Yoki boshqa joyda
@bot.message_handler(func=lambda m: m.text == "🔙 Orqaga")
def go_back(message):
    back_to_main_menu(message)


@bot.message_handler(func=lambda m: m.text == "💸 Pul chiqarish")
def withdraw_step1(message):
    msg = bot.send_message(message.chat.id, "💵 Miqdorni kiriting (min 20000 so‘m):")
    bot.register_next_step_handler(msg, withdraw_step2)

def withdraw_step2(message):
    try:
        amount = int(message.text)
        user_id = message.from_user.id
        if amount < 20000:
            bot.send_message(message.chat.id, "❌ Minimal chiqarish miqdori 20000 so‘m.")
            return
        if user_balances.get(user_id, 0) < amount:
            bot.send_message(message.chat.id, "❌ Mablag‘ yetarli emas.")
            return
        withdraw_sessions[user_id] = amount
        msg = bot.send_message(message.chat.id, "💳 Karta yoki to‘lov usulini yozing:")
        bot.register_next_step_handler(msg, withdraw_step3)
    except:
        bot.send_message(message.chat.id, "❌ Noto‘g‘ri miqdor.")

# === SHU YERGA QO‘Y — withdraw_step3 ===
def withdraw_step3(message):
    user_id = message.from_user.id
    amount = withdraw_sessions.get(user_id)
    info = message.text.strip()

    # === Karta yoki to‘lov tizimi tekshiruvlari ===
    valid = False
    digits = ''.join(filter(str.isdigit, info))
    if len(digits) in [16, 19] and (digits.startswith('8600') or digits.startswith('9860') or digits.startswith('9989')):
        valid = True
    elif any(x in info.lower() for x in ['click', 'payme', 'uzcard', 'humo', 'apelsin']):
        valid = True

    if not valid:
        bot.send_message(message.chat.id, "❌ To‘lov usuli noto‘g‘ri kiritildi. Karta raqami (8600...) yoki servis nomini kiriting.")
        return

    user_balances[user_id] -= amount
    text = f"🔔 Yangi pul chiqarish so‘rovi!\n👤 @{message.from_user.username or 'no_username'}\n🆔 ID: {user_id}\n💵 Miqdor: {amount} so‘m\n💳 To‘lov: {info}"
    bot.send_message(ADMIN_ID, text)
    bot.send_message(message.chat.id, "✅ So‘rov yuborildi, kuting.")
    del withdraw_sessions[user_id]

@bot.message_handler(commands=['lucky_list'])
def show_lucky_list(message):
    if message.from_user.id != ADMIN_ID:
        return

    if not lucky_users:
        bot.send_message(message.chat.id, "📭 Lucky foydalanuvchilar yo‘q.")
    else:
        users = "\n".join([f"🆔 {uid}" for uid in lucky_users])
        bot.send_message(message.chat.id, f"🎯 Lucky foydalanuvchilar ro‘yxati:\n{users}")


@bot.message_handler(func=lambda m: m.text == "🎮 Play TicTacToe")
def start_tictactoe_bet(message):
    user_id = message.from_user.id
    msg = bot.send_message(message.chat.id, "🎯 Stavka miqdorini kiriting (min 1000 so‘m):")
    bot.register_next_step_handler(msg, process_ttt_bet)

def process_ttt_bet(message):
    user_id = message.from_user.id
    try:
        stake = int(message.text)
        if stake < 1000:
            bot.send_message(message.chat.id, "❌ Minimal stavka 1000 so‘m.")
            return
        if user_balances.get(user_id, 0) < stake:
            bot.send_message(message.chat.id, "❌ Mablag‘ yetarli emas.")
            return
    except:
        bot.send_message(message.chat.id, "❌ To‘g‘ri raqam kiriting.")
        return

    user_balances[user_id] -= stake
    tic_tac_toe_states[user_id] = {
        "board": [" "] * 9,
        "stake": stake
    }
    board = tic_tac_toe_states[user_id]["board"]
    bot.send_message(message.chat.id, "🎮 O‘yin boshlandi! Siz 'X' bilan o‘ynaysiz. Katakni tanlang:", reply_markup=board_to_markup(board))

def board_to_markup(board):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    for i, cell in enumerate(board):
        text = cell if cell != " " else "⬜"
        buttons.append(types.InlineKeyboardButton(text, callback_data=f"ttt_{i}"))
    markup.add(*buttons)
    return markup

def check_winner(board, player):
    wins = [[0,1,2], [3,4,5], [6,7,8],
            [0,3,6], [1,4,7], [2,5,8],
            [0,4,8], [2,4,6]]
    return any(all(board[pos] == player for pos in line) for line in wins)

def is_board_full(board):
    return all(cell != " " for cell in board)

def find_best_move(board):
    # Agar bot yutishi mumkin bo'lsa, o'sha joyga boradi
    for i in range(9):
        if board[i] == " ":
            board[i] = "O"
            if check_winner(board, "O"):
                board[i] = " "
                return i
            board[i] = " "
    # Agar foydalanuvchi yutishi mumkin bo'lsa, bloklaydi
    for i in range(9):
        if board[i] == " ":
            board[i] = "X"
            if check_winner(board, "X"):
                board[i] = " "
                return i
            board[i] = " "
    # Aks holda random
    empty = [i for i, c in enumerate(board) if c == " "]
    return random.choice(empty)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ttt_"))
def ttt_handle_move(call):
    user_id = call.from_user.id
    state = tic_tac_toe_states.get(user_id)
    if not state:
        bot.answer_callback_query(call.id, "O'yin topilmadi.")
        return

    board = state["board"]
    idx = int(call.data.split("_")[1])
    if board[idx] != " ":
        bot.answer_callback_query(call.id, "Bu katak band.")
        return

    board[idx] = "X"
    if check_winner(board, "X"):
        prize = int(state["stake"] * 1.5)
        user_balances[user_id] += prize
        bot.edit_message_text(f"🌟 Siz yutdingiz! {prize} so‘m oldingiz. (1.5x)", call.message.chat.id, call.message.message_id)
        tic_tac_toe_states.pop(user_id)
        return

    if is_board_full(board):
        refund = int(state["stake"] * 0.5)
        user_balances[user_id] += refund
        bot.edit_message_text(f"⚖️ Durang. Faqat {refund} so‘m qaytdi. (50%)", call.message.chat.id, call.message.message_id)
        tic_tac_toe_states.pop(user_id)
        return

    bot_move = find_best_move(board)
    board[bot_move] = "O"
    if check_winner(board, "O"):
        bot.edit_message_text("😞 Bot yutdi! Siz stavkani yo‘qotdingiz.", call.message.chat.id, call.message.message_id)
        tic_tac_toe_states.pop(user_id)
        return

    if is_board_full(board):
        refund = int(state["stake"] * 0.5)
        user_balances[user_id] += refund
        bot.edit_message_text(f"⚖️ Durang. Faqat {refund} so‘m qaytdi. (50%)", call.message.chat.id, call.message.message_id)
        tic_tac_toe_states.pop(user_id)
        return

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=board_to_markup(board))
    bot.answer_callback_query(call.id, "Yurishingiz qabul qilindi!")

@bot.message_handler(func=lambda m: m.text == "🎁 Kunlik bonus")
def daily_bonus(message):
    user_id = message.from_user.id
    today = datetime.date.today()
    if user_bonus_state.get(user_id) == today:
        bot.send_message(message.chat.id, "🎁 Siz bugun bonus oldingiz.")
        return
    bonus = random.randint(1000, 5000)
    user_balances[user_id] = user_balances.get(user_id, 0) + bonus
    user_bonus_state[user_id] = today
    bot.send_message(message.chat.id, f"🎉 Sizga {bonus} so‘m bonus berildi!")

@bot.message_handler(func=lambda m: m.text == "🎲 Play Dice")
def dice_start(message):
    msg = bot.send_message(message.chat.id, "🎯 Stavka miqdorini kiriting:")
    bot.register_next_step_handler(msg, dice_process)

def dice_process(message):
    if message.text == "🔙 Orqaga":
        return back_to_main_menu(message)
    try:
        user_id = message.from_user.id
        stake = int(message.text)
        if user_balances.get(user_id, 0) < stake:
            bot.send_message(message.chat.id, "❌ Mablag‘ yetarli emas.")
            return
        user_balances[user_id] -= stake
        bot.send_message(message.chat.id, "🎲 Qaytarilmoqda...")
        time.sleep(2)
        dice = random.randint(1, 6)
        if dice <= 2:
            win = 0
        elif dice <= 4:
            win = stake
        else:
            win = stake * 2
        user_balances[user_id] += win
        bot.send_dice(message.chat.id)
        time.sleep(3)
        bot.send_message(
            message.chat.id,
            f"🎲 Natija: {dice}\n"
            f"{'✅ Yutdingiz!' if win > stake else '❌ Yutqazdingiz.'}\n"
            f"💵 Yutuq: {win} so‘m"
        )
    except:
        bot.send_message(message.chat.id, "❌ Noto‘g‘ri stavka.")

@bot.message_handler(commands=['make_lucky'])
def make_lucky(message):
    if message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "⛔ Sizda ruxsat yo‘q.")

    parts = message.text.strip().split()
    if len(parts) < 2:
        return bot.send_message(message.chat.id, "❗ Foydalanuvchi ID raqamini yozing. Masalan: /make_lucky 12345678")

    try:
        user_id = int(parts[1])
        lucky_users.add(user_id)
        bot.send_message(message.chat.id, f"✅ Foydalanuvchi {user_id} lucky ro‘yxatiga qo‘shildi.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ ID raqami noto‘g‘ri.")

@bot.message_handler(commands=['remove_lucky'])
def remove_lucky(message):
    if message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "⛔ Sizda ruxsat yo‘q.")

    parts = message.text.strip().split()
    if len(parts) < 2:
        return bot.send_message(message.chat.id, "❗ Foydalanuvchi ID raqamini yozing. Masalan: /remove_lucky 12345678")

    try:
        user_id = int(parts[1])
        if user_id in lucky_users:
            lucky_users.remove(user_id)
            bot.send_message(message.chat.id, f"🗑 Foydalanuvchi {user_id} lucky ro‘yxatidan o‘chirildi.")
        else:
            bot.send_message(message.chat.id, f"⚠️ {user_id} lucky ro‘yxatida yo‘q.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ ID raqami noto‘g‘ri.")

@bot.message_handler(commands=['lucky_list'])
def lucky_list(message):
    if message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "⛔ Sizda ruxsat yo‘q.")

    if not lucky_users:
        return bot.send_message(message.chat.id, "📭 Lucky ro‘yxati bo‘sh.")

    text = "📋 Lucky foydalanuvchilar ro‘yxati:\n"
    for uid in lucky_users:
        text += f"🆔 {uid}\n"
    bot.send_message(message.chat.id, text)


ROWS, COLS = 5, 5
BOMBS_COUNT = 5
MIN_STAKE = 1000

def generate_bombs(exclude_cell):
    all_cells = [(r, c) for r in range(ROWS) for c in range(COLS) if (r, c) != exclude_cell]
    return set(random.sample(all_cells, BOMBS_COUNT))

def create_keyboard(opened):
    markup = types.InlineKeyboardMarkup()
    for i in range(ROWS * COLS):
        r, c = divmod(i, COLS)
        if i in opened:
            text = "💰"
            callback_data = "ignore"
        else:
            text = "⬜️"
            callback_data = f"mines_{i}"
        markup.insert(types.InlineKeyboardButton(text, callback_data=callback_data))
    if opened:
        markup.add(types.InlineKeyboardButton("💸 Pulni yechib olish", callback_data="mines_cashout"))
    markup.add(types.InlineKeyboardButton("❌ O‘yin tugatish", callback_data="mines_stop"))
    return markup

def send_grid(chat_id, user_id):
    state = user_mines_states[user_id]
    opened = state["opened"]
    stake = state["stake"]
    multiplier = state["multiplier"]
    winnings = int(stake * multiplier)

    text = (
        f"💣 Mines o'yini\n"
        f"📈 Koef: x{multiplier:.2f}\n"
        f"💰 Potensial yutuq: {winnings} so'm\n"
        f"⬇️ Bombasiz kataklarni tanlang:"
    )

    bot.edit_message_text(text, chat_id, state["msg_id"], reply_markup=create_keyboard(opened))

@bot.message_handler(commands=['start', 'playmines'])
def start_mines(message):
    user_id = message.from_user.id
    if user_id not in user_balances:
        user_balances[user_id] = START_BALANCE
    bot.send_message(message.chat.id,
                     f"Salom! Sizning balansingiz: {user_balances[user_id]} so'm.\n"
                     f"Iltimos, stavka miqdorini kiriting (min {MIN_STAKE} so‘m):")
    bot.register_next_step_handler_by_chat_id(message.chat.id, process_stake)

def process_stake(message):
    user_id = message.from_user.id
    try:
        stake = int(message.text)
        if stake < MIN_STAKE:
            bot.send_message(message.chat.id, f"❌ Minimal stavka {MIN_STAKE} so‘m.")
            return
        if user_balances.get(user_id, 0) < stake:
            bot.send_message(message.chat.id, "❌ Mablag‘ yetarli emas.")
            return
    except:
        bot.send_message(message.chat.id, "❌ Iltimos, to‘g‘ri raqam kiriting.")
        return

    user_balances[user_id] -= stake
    user_mines_states[user_id] = {
        "stake": stake,
        "opened": [],
        "bombs": set(),
        "multiplier": 1.0,
        "alive": True,
        "first_click": True,
        "msg_id": None
    }

    msg = bot.send_message(message.chat.id, "O'yin boshlandi! 5x5 kataklardan birini tanlang.")
    user_mines_states[user_id]["msg_id"] = msg.message_id

@bot.callback_query_handler(func=lambda c: c.data.startswith('mines_') or c.data in ['mines_cashout', 'mines_stop', 'ignore'])
def handle_mines(call):
    user_id = call.from_user.id
    state = user_mines_states.get(user_id)

    if not state or not state["alive"]:
        bot.answer_callback_query(call.id, "O'yin boshlanmagan yoki tugagan.")
        return

    if call.data == "mines_cashout":
        winnings = int(state["stake"] * state["multiplier"])
        user_balances[user_id] += winnings
        bot.edit_message_text(
            f"🎉 Pulni yechib oldingiz!\nYutuq: {winnings} so'm\nBalansingiz: {user_balances[user_id]} so'm",
            call.message.chat.id, call.message.message_id
        )
        user_mines_states.pop(user_id)
        return

    if call.data == "mines_stop":
        bot.edit_message_text(
            f"O'yin to‘xtatildi.\nBalansingiz: {user_balances[user_id]} so'm",
            call.message.chat.id, call.message.message_id
        )
        user_mines_states.pop(user_id)
        return

    if call.data == "ignore":
        bot.answer_callback_query(call.id)
        return

    index = int(call.data.split("_")[1])
    if index in state["opened"]:
        bot.answer_callback_query(call.id, "Bu katak allaqachon ochilgan.")
        return

    if state["first_click"]:
        r, c = divmod(index, COLS)
        state["bombs"] = generate_bombs(exclude_cell=(r, c))
        state["first_click"] = False

    if index in [(r * COLS + c) for r, c in state["bombs"]]:
        state["alive"] = False
        state["opened"].append(index)
        bot.edit_message_text(
            f"💥 Boom! Siz bombani bosdingiz! 😢\nStavka yo‘qotildi.",
            call.message.chat.id, call.message.message_id,
            reply_markup=None
        )
        user_mines_states.pop(user_id)
        return

    state["opened"].append(index)
    state["multiplier"] += 0.2

    send_grid(call.message.chat.id, user_id)
    bot.answer_callback_query(call.id, "Katak ochildi!")


# === AVIATOR o'yini funksiyasi ===
@bot.message_handler(func=lambda m: m.text == "🛩 Play Aviator")
def play_aviator(message):
    user_id = message.from_user.id
    if user_id in user_aviator:
        bot.send_message(message.chat.id, "⏳ Avvalgi Aviator o‘yini tugamagani uchun kuting.")
        return
    msg = bot.send_message(message.chat.id, "🎯 Stavka miqdorini kiriting (min 1000 so‘m):")
    bot.register_next_step_handler(msg, process_aviator_stake)

def process_aviator_stake(message):
    if message.text == "🔙 Orqaga":
        return back_to_main_menu(message)
    try:
        user_id = message.from_user.id
        stake = int(message.text)
        if stake < 1000:
            bot.send_message(message.chat.id, "❌ Minimal stavka 1000 so‘m.")
            return
        if user_balances.get(user_id, 0) < stake:
            bot.send_message(message.chat.id, "❌ Yetarli balans yo‘q.")
            return
        user_balances[user_id] -= stake
        user_aviator[user_id] = {
            'stake': stake,
            'multiplier': 1.0,
            'chat_id': message.chat.id,
            'message_id': None,
            'stopped': False
        }
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛑 STOP", callback_data="aviator_stop"))
        msg = bot.send_message(message.chat.id, f"🛫 Boshlanmoqda... x1.00", reply_markup=markup)
        user_aviator[user_id]['message_id'] = msg.message_id
        threading.Thread(target=run_aviator_game, args=(user_id,)).start()
    except:
        bot.send_message(message.chat.id, "❌ Xatolik. Raqam kiriting.")


def run_aviator_game(user_id):
    data = user_aviator.get(user_id)
    if not data:
        return
    chat_id = data['chat_id']
    message_id = data['message_id']
    stake = data['stake']
    multiplier = data['multiplier']
    for _ in range(30):
        if user_aviator.get(user_id, {}).get('stopped'):
            win = int(stake * multiplier)
            user_balances[user_id] += win
            bot.edit_message_text(f"🛑 To‘xtatildi: x{multiplier}\n✅ Yutuq: {win} so‘m", chat_id, message_id)
            del user_aviator[user_id]
            return
        time.sleep(1)
        multiplier = round(multiplier + random.uniform(0.15, 0.4), 2)
        chance = random.random()
        if (multiplier <= 1.6 and chance < 0.3) or (1.6 < multiplier <= 2.4 and chance < 0.15) or (multiplier > 2.4 and chance < 0.1):
            bot.edit_message_text(f"💥 Portladi: x{multiplier}\n❌ Siz yutqazdingiz.", chat_id, message_id)
            del user_aviator[user_id]
            return
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛑 STOP", callback_data="aviator_stop"))
        try:
            bot.edit_message_text(f"🛩 Ko‘tarilmoqda... x{multiplier}", chat_id, message_id, reply_markup=markup)
        except:
            pass
        user_aviator[user_id]['multiplier'] = multiplier
@bot.callback_query_handler(func=lambda call: call.data == "aviator_stop")
def aviator_stop(call):
    user_id = call.from_user.id
    if user_id in user_aviator:
        user_aviator[user_id]['stopped'] = True
        bot.answer_callback_query(call.id, "🛑 O'yin to'xtatildi, pulingiz qaytarildi.")


CHICKEN = "🐔"
PASSED = "✅"
UNLOCKED = "🔓"
LOCKED = "🔒"
BOMB = "💥"

azart_enabled = True  # Agar admin sozlasa, global azart yoqiladi

@bot.message_handler(func=lambda m: m.text == "🐔 Play Chicken")
def start_chicken(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    msg = bot.send_message(chat_id, "💸 Stavka miqdorini kiriting (min 1000 so‘m):")
    bot.register_next_step_handler(msg, lambda m: process_chicken_stake(m, user_id))

def process_chicken_stake(message, user_id):
    chat_id = message.chat.id
    try:
        stake = int(message.text)
        if stake < 1000:
            return bot.send_message(chat_id, "❌ Minimal stavka 1000 so‘m.")
        if user_balances.get(user_id, 0) < stake:
            return bot.send_message(chat_id, "❌ Mablag‘ yetarli emas.")
    except:
        return bot.send_message(chat_id, "❌ Raqam kiriting.")

    user_balances[user_id] -= stake
    user_chicken_states[user_id] = {
        'pos': 0,
        'stake': stake,
        'multiplier': 1.0,
        'alive': True
    }

    send_chicken_grid(chat_id, user_id)

def send_chicken_grid(chat_id, user_id):
    state = user_chicken_states[user_id]
    pos = state['pos']
    cells = []
    markup = types.InlineKeyboardMarkup(row_width=5)

    for i in range(10):
        if i < pos:
            cells.append(PASSED)
            markup.add(types.InlineKeyboardButton(PASSED, callback_data="ignore"))
        elif i == pos:
            cells.append(CHICKEN)
            markup.add(types.InlineKeyboardButton(CHICKEN, callback_data="ignore"))
        elif i == pos + 1:
            cells.append(UNLOCKED)
            markup.add(types.InlineKeyboardButton(UNLOCKED, callback_data=f"chicken_jump_{i}"))
        else:
            cells.append(LOCKED)
            markup.add(types.InlineKeyboardButton(LOCKED, callback_data="ignore"))

    pot_win = int(state['stake'] * state['multiplier'])

    markup.add(types.InlineKeyboardButton("💸 Pulni yechib olish", callback_data="chicken_cashout"))

    line = " > ".join(cells)
    bot.send_message(chat_id,
        f"🐔 Chicken Road o‘yini\n\n"
        f"{line}\n\n"
        f"📈 Koef: x{round(state['multiplier'], 2)}\n"
        f"💰 Potensial yutuq: {pot_win} so‘m\n\n"
        f"🐔 Keyingi katakka sakrash uchun 🔓 tugmasini bosing yoki pulni yeching.",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("chicken_"))
def handle_chicken(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    state = user_chicken_states.get(user_id)

    if not state or not state['alive']:
        return bot.answer_callback_query(call.id, "⛔ O‘yin mavjud emas.")

    if call.data == "chicken_cashout":
        win = int(state['stake'] * state['multiplier'])
        user_balances[user_id] += win
        user_chicken_states.pop(user_id)
        return bot.edit_message_text(f"✅ Pul chiqarildi! Yutuq: {win:,} so‘m", chat_id, call.message.message_id)

    if call.data.startswith("chicken_jump_"):
        target = int(call.data.split("_")[-1])
        pos = state['pos']
        if target != pos + 1:
            return bot.answer_callback_query(call.id, "⛔ Faqat yonidagi katakka sakrashingiz mumkin.")

        # Azart xavfi
        if azart_enabled:
            risk = 0.6 + (pos * 0.08)
        else:
            risk = 0.9 + (pos * 0.3)

        if random.random() < risk:
            line = []
            for i in range(10):
                if i == target:
                    line.append(BOMB)
                elif i < pos:
                    line.append(PASSED)
                elif i == pos:
                    line.append(CHICKEN)
                else:
                    line.append(LOCKED)
            return bot.edit_message_text(
                f"💥 Boom! Bombaga tushdi!\nStavka yo‘qotildi.\n\n{' > '.join(line)}",
                chat_id, call.message.message_id
            )

        # Xavfsiz sakrash
        state['pos'] += 1
        state['multiplier'] = multipliers[state['pos']]
        if state['pos'] == 9:
            win = int(state['stake'] * state['multiplier'])
            user_balances[user_id] += win
            line = get_final_chicken_line(state['pos'])
            user_chicken_states.pop(user_id)
            return bot.edit_message_text(
                f"🎉 Tovuq manzilga yetdi! Yutuq: {win:,} so‘m\n\n{line}",
                chat_id, call.message.message_id
            )
        send_chicken_grid(chat_id, user_id)

def get_final_chicken_line(pos):
    cells = []
    for i in range(10):
        if i < pos:
            cells.append(PASSED)
        elif i == pos:
            cells.append(CHICKEN)
        else:
            cells.append(LOCKED)
    return " > ".join(cells)


print("Bot ishga tushdi...")
keep_alive()
bot.polling(none_stop=True)
