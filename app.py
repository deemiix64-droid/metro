import os, asyncio, json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

TOKEN = os.getenv("BOT_TOKEN")
MANAGER = "@timixXmetro"
OWNER_ID = 8239542728  # ТВОЙ ID
# Ссылка на твой GitHub Pages (шаг 2)
APP_URL = "https://deemiix64-droid.github.io/metro/" 

bot = Bot(token=TOKEN)
dp = Dispatcher()

admins = set() 

class AdminStates(StatesGroup):
    adding_admin = State()

def main_kb(user_id):
    btns = [[InlineKeyboardButton(text="🛒 Магазин Metro", web_app=WebAppInfo(url=APP_URL))]]
    if user_id == OWNER_ID or user_id in admins:
        btns.append([InlineKeyboardButton(text="⚙️ Админ-панель", callback_data="adm_menu")])
    return InlineKeyboardMarkup(inline_keyboard=btns)

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer(f"Привет! Это TIMIX SHOP.\nТвой ID: `{m.from_user.id}`", 
                   reply_markup=main_kb(m.from_user.id), parse_mode="Markdown")

@dp.callback_query(F.data == "adm_menu")
async def adm_menu(call: types.CallbackQuery):
    kb = [[InlineKeyboardButton(text="📢 Рассылка (в разработке)", callback_data="none")]]
    if call.from_user.id == OWNER_ID:
        kb.append([InlineKeyboardButton(text="➕ Добавить Админа", callback_data="add_adm")])
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])
    await call.message.edit_text("🔧 Панель управления", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data == "add_adm")
async def add_adm_step(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Введите ID нового админа:")
    await state.set_state(AdminStates.adding_admin)

@dp.message(AdminStates.adding_admin)
async def save_adm(m: types.Message, state: FSMContext):
    if m.text.isdigit():
        admins.add(int(m.text))
        await m.answer(f"✅ Пользователь {m.text} добавлен в админы.")
    await state.clear()

@dp.message(F.web_app_data)
async def buy_process(m: types.Message):
    data = json.loads(m.web_app_data.data)
    await bot.send_invoice(
        m.chat.id, title=data['item'], description=f"Оплата в TIMIX. Менеджер: {MANAGER}",
        payload="order", currency="XTR", prices=[LabeledPrice(label="Звезды", amount=int(data['price']))],
        provider_token=""
    )

@dp.pre_checkout_query()
async def pre(q: PreCheckoutQuery): await q.answer(ok=True)

@dp.message(F.successful_payment)
async def success(m: types.Message):
    await m.answer(f"✅ Оплачено! Отправь скриншот менеджеру: {MANAGER}")

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
