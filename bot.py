import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import PollType
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = "8034837573:AAHJ-LlvecgtBST9wQ2IKysnzv5hha9rh6c"
CHANNEL_ID = "@salomlarllll"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class PollForm(StatesGroup):
    question = State()
    image = State()
    options = State()
    correct = State()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Test yaratish uchun /poll buyrug'ini yuboring.")

@dp.message(Command("poll"))
async def poll_start(message: Message, state: FSMContext):
    await message.answer("📌 Savolni yozing:")
    await state.set_state(PollForm.question)

@dp.message(PollForm.question)
async def poll_question(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer("🖼 Rasm yuboring (yoki 'yo‘q' deb yozing):")
    await state.set_state(PollForm.image)

@dp.message(PollForm.image, F.photo)
async def poll_image(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await message.answer("✏️ Variantlarni kiriting (masalan: A) Toshkent, B) Samarqand, C) Buxoro):")
    await state.set_state(PollForm.options)

@dp.message(PollForm.image)
async def poll_image_text(message: Message, state: FSMContext):
    if message.text.lower() in ["yo‘q", "yoq"]:
        await state.update_data(photo=None)
        await message.answer("✏️ Variantlarni kiriting (masalan: A) Toshkent, B) Samarqand, C) Buxoro):")
        await state.set_state(PollForm.options)
    else:
        await message.answer("❗ Rasm yuboring yoki 'yo‘q' deb yozing.")

@dp.message(PollForm.options)
async def poll_options(message: Message, state: FSMContext):
    variantlar = [v.strip() for v in message.text.split(",")]
    if len(variantlar) < 2:
        await message.answer("❗ Kamida 2 ta variant kerak.")
        return
    await state.update_data(options=variantlar)
    await message.answer("✅ To‘g‘ri javob raqamini yozing (1 dan boshlab):")
    await state.set_state(PollForm.correct)

@dp.message(PollForm.correct)
async def poll_correct(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        correct_id = int(message.text) - 1
        if not (0 <= correct_id < len(data['options'])):
            raise ValueError
    except:
        await message.answer("❗ To‘g‘ri javob raqamini to‘g‘ri kiriting (masalan: 2)")
        return

    # Savol + variantlarni bitta pollga jamlash
    poll_question_text = f"{data['question']}\n" + "\n".join(data['options'])

    try:
        if data.get('photo'):
            await bot.send_photo(chat_id=CHANNEL_ID, photo=data['photo'])

        await bot.send_poll(
            chat_id=CHANNEL_ID,
            question=poll_question_text,
            options=[v.split(")", 1)[-1].strip() for v in data['options']],
            type=PollType.QUIZ,
            correct_option_id=correct_id,
            is_anonymous=True,
            explanation="✅ To‘g‘ri javob shuydi!"
        )
        await message.answer("✅ So‘rovnoma kanalga yuborildi.")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
