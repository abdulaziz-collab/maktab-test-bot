import asyncio
import sqlite3
from datetime import datetime
import random

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "BU_YERGA_BOT_TOKENINGIZNI_YOZING"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

db = sqlite3.connect("test_bot.db")
cursor = db.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    created_at TEXT
)
""")
db.commit()

users = {}

SUBJECTS = {
    1: ["Matematika", "Ona tili", "O‘qish", "Tabiatshunoslik"],
    2: ["Matematika", "Ona tili", "O‘qish", "Tabiatshunoslik"],
    3: ["Matematika", "Ona tili", "O‘qish", "Tabiatshunoslik"],
    4: ["Matematika", "Ona tili", "O‘qish", "Tabiatshunoslik", "Ingliz tili"],
    5: ["Matematika", "Ona tili", "Adabiyot", "Tarix", "Ingliz tili", "Tabiatshunoslik"],
    6: ["Matematika", "Ona tili", "Adabiyot", "Tarix", "Ingliz tili", "Biologiya", "Geografiya"],
    7: ["Matematika", "Algebra", "Geometriya", "Ona tili", "Adabiyot", "Tarix", "Ingliz tili", "Biologiya", "Geografiya", "Fizika"],
    8: ["Algebra", "Geometriya", "Ona tili", "Adabiyot", "Tarix", "Ingliz tili", "Biologiya", "Geografiya", "Fizika", "Kimyo"],
    9: ["Algebra", "Geometriya", "Ona tili", "Adabiyot", "Tarix", "Ingliz tili", "Biologiya", "Geografiya", "Fizika", "Kimyo"],
    10: ["Algebra", "Geometriya", "Ona tili", "Adabiyot", "Tarix", "Ingliz tili", "Biologiya", "Geografiya", "Fizika", "Kimyo", "Informatika"],
    11: ["Algebra", "Geometriya", "Ona tili", "Adabiyot", "Tarix", "Ingliz tili", "Biologiya", "Geografiya", "Fizika", "Kimyo", "Informatika"]
}

QUESTIONS = {}

def add_questions(class_number, subject, questions):
    QUESTIONS[(class_number, subject)] = questions

add_questions(7, "Algebra", [
    {"question": "5 + 7 nechaga teng?", "options": ["10", "11", "12", "13"], "answer": 2},
    {"question": "3 × 4 nechaga teng?", "options": ["7", "10", "12", "14"], "answer": 2},
    {"question": "20 ÷ 5 nechaga teng?", "options": ["2", "3", "4", "5"], "answer": 2},
    {"question": "x + 5 = 12. x nechaga teng?", "options": ["5", "6", "7", "8"], "answer": 2},
    {"question": "2² nechaga teng?", "options": ["2", "4", "6", "8"], "answer": 1},
    {"question": "10 - 6 nechaga teng?", "options": ["2", "3", "4", "5"], "answer": 2},
    {"question": "7 × 8 nechaga teng?", "options": ["54", "56", "58", "64"], "answer": 1},
    {"question": "81 ning kvadrat ildizi nechaga teng?", "options": ["7", "8", "9", "10"], "answer": 2},
    {"question": "15 + 25 nechaga teng?", "options": ["30", "35", "40", "45"], "answer": 2},
    {"question": "100 ÷ 10 nechaga teng?", "options": ["5", "10", "15", "20"], "answer": 1}
])

add_questions(5, "Matematika", [
    {"question": "8 + 9 nechaga teng?", "options": ["15", "16", "17", "18"], "answer": 2},
    {"question": "6 × 7 nechaga teng?", "options": ["36", "40", "42", "48"], "answer": 2},
    {"question": "50 - 23 nechaga teng?", "options": ["25", "27", "29", "30"], "answer": 1},
    {"question": "72 ÷ 8 nechaga teng?", "options": ["7", "8", "9", "10"], "answer": 2},
    {"question": "15 + 35 nechaga teng?", "options": ["40", "45", "50", "55"], "answer": 2}
])

def get_questions(class_number, subject):
    key = (class_number, subject)
    if key in QUESTIONS:
        return QUESTIONS[key].copy()

    return [{
        "question": f"{subject} fanidan {i}-savol. To‘g‘ri javobni tanlang.",
        "options": ["A variant", "B variant", "C variant", "D variant"],
        "answer": 0
    } for i in range(1, 51)]

def classes_keyboard():
    buttons = [InlineKeyboardButton(text=f"{i}-sinf", callback_data=f"class:{i}") for i in range(1, 12)]
    return InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)])

def subjects_keyboard(class_number):
    buttons = [[InlineKeyboardButton(text=f"📚 {subject}", callback_data=f"subject:{subject}")]
               for subject in SUBJECTS.get(class_number, [])]
    buttons.append([InlineKeyboardButton(text="⬅️ Sinfni almashtirish", callback_data="back_classes")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def test_count_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 10 ta test", callback_data="count:10")],
        [InlineKeyboardButton(text="📝 20 ta test", callback_data="count:20")],
        [InlineKeyboardButton(text="📝 50 ta test", callback_data="count:50")],
        [InlineKeyboardButton(text="⬅️ Fanga qaytish", callback_data="back_subjects")]
    ])

def reset_user(user_id, class_number=None):
    users[user_id] = {
        "class_number": class_number,
        "subject": None,
        "test_count": None,
        "questions": [],
        "current": 0,
        "correct": 0,
        "wrong": 0,
        "timer_task": None
    }

@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    cursor.execute(
        "INSERT OR REPLACE INTO users (user_id, username, created_at) VALUES (?, ?, ?)",
        (user_id, message.from_user.username, datetime.now().isoformat())
    )
    db.commit()
    reset_user(user_id)
    await message.answer(
        "👋 Assalomu alaykum!\n\n🎓 Maktab test botiga xush kelibsiz!\n\n"
        "Avval o‘zingiz o‘qiyotgan sinfni tanlang:",
        reply_markup=classes_keyboard()
    )

@dp.callback_query(F.data.startswith("class:"))
async def class_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    class_number = int(callback.data.split(":")[1])
    reset_user(user_id, class_number)
    await callback.message.edit_text(
        f"🎓 Siz {class_number}-sinfni tanladingiz.\n\n📚 Endi fanni tanlang:",
        reply_markup=subjects_keyboard(class_number)
    )
    await callback.answer()

@dp.callback_query(F.data == "back_classes")
async def back_classes(callback: CallbackQuery):
    await callback.message.edit_text("🎓 Sinfni tanlang:", reply_markup=classes_keyboard())
    await callback.answer()

@dp.callback_query(F.data.startswith("subject:"))
async def subject_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in users:
        await callback.answer("Avval /start buyrug‘ini bosing!", show_alert=True)
        return
    subject = callback.data.split(":", 1)[1]
    users[user_id]["subject"] = subject
    await callback.message.edit_text(
        f"📚 Fan: {subject}\n\nNechta test ishlamoqchisiz?",
        reply_markup=test_count_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "back_subjects")
async def back_subjects(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in users:
        return
    class_number = users[user_id]["class_number"]
    await callback.message.edit_text(
        f"🎓 {class_number}-sinf\n\n📚 Fanni tanlang:",
        reply_markup=subjects_keyboard(class_number)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("count:"))
async def count_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in users:
        await callback.answer("Avval /start buyrug‘ini bosing!", show_alert=True)
        return

    count = int(callback.data.split(":")[1])
    data = users[user_id]
    questions = get_questions(data["class_number"], data["subject"])

    if len(questions) < count:
        await callback.answer(
            f"Bu fan uchun hozircha {len(questions)} ta savol mavjud.",
            show_alert=True
        )
        return

    random.shuffle(questions)
    data["test_count"] = count
    data["questions"] = questions[:count]
    data["current"] = 0
    data["correct"] = 0
    data["wrong"] = 0

    await callback.message.edit_text(
        f"🚀 Test boshlanmoqda!\n\n"
        f"🎓 Sinf: {data['class_number']}-sinf\n"
        f"📚 Fan: {data['subject']}\n"
        f"📝 Savollar: {count} ta\n"
        f"⏱ Har bir savol uchun: 50 soniya\n\nBoshlaymiz! 🔥"
    )
    await asyncio.sleep(1)
    await send_question(callback.message, user_id)
    await callback.answer()

async def send_question(message: Message, user_id: int):
    data = users.get(user_id)
    if not data:
        return

    current = data["current"]
    questions = data["questions"]

    if current >= len(questions):
        await finish_test(message, user_id)
        return

    question = questions[current]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"A) {question['options'][0]}", callback_data="answer:0")],
        [InlineKeyboardButton(text=f"B) {question['options'][1]}", callback_data="answer:1")],
        [InlineKeyboardButton(text=f"C) {question['options'][2]}", callback_data="answer:2")],
        [InlineKeyboardButton(text=f"D) {question['options'][3]}", callback_data="answer:3")]
    ])

    await message.edit_text(
        f"📝 Savol {current + 1}/{len(questions)}\n\n"
        f"⏱ Vaqt: 50 soniya\n\n❓ {question['question']}",
        reply_markup=keyboard
    )

    old_timer = data.get("timer_task")
    if old_timer and not old_timer.done():
        old_timer.cancel()

    data["timer_task"] = asyncio.create_task(question_timer(message, user_id, current))

async def question_timer(message: Message, user_id: int, question_number: int):
    try:
        await asyncio.sleep(50)
        data = users.get(user_id)
        if not data or data["current"] != question_number:
            return

        data["wrong"] += 1
        await message.edit_text(
            "⏰ Vaqt tugadi!\n\n❌ Bu savolga javob berilmadi.\n\nKeyingi savolga o'tamiz..."
        )
        await asyncio.sleep(1)
        data["current"] += 1
        await send_question(message, user_id)
    except asyncio.CancelledError:
        pass

@dp.callback_query(F.data.startswith("answer:"))
async def answer_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in users:
        await callback.answer("Test topilmadi.", show_alert=True)
        return

    data = users[user_id]
    current = data["current"]
    questions = data["questions"]

    if current >= len(questions):
        return

    timer = data.get("timer_task")
    if timer and not timer.done():
        timer.cancel()

    selected_answer = int(callback.data.split(":")[1])
    question = questions[current]
    correct_answer = question["answer"]

    if selected_answer == correct_answer:
        data["correct"] += 1
        await callback.message.edit_text(
            "✅ TO‘G‘RI JAVOB!\n\n"
            f"📚 {question['question']}\n\n"
            f"✅ To‘g‘ri javob: {question['options'][correct_answer]}\n\n"
            "Keyingi savolga o'tamiz..."
        )
    else:
        data["wrong"] += 1
        await callback.message.edit_text(
            "❌ NOTO‘G‘RI JAVOB!\n\n"
            f"📚 {question['question']}\n\n"
            f"❌ Sizning javobingiz: {question['options'][selected_answer]}\n\n"
            f"✅ To‘g‘ri javob: {question['options'][correct_answer]}\n\n"
            "Keyingi savolga o'tamiz..."
        )

    await callback.answer()
    await asyncio.sleep(1.5)
    data["current"] += 1
    await send_question(callback.message, user_id)

async def finish_test(message: Message, user_id: int):
    data = users.get(user_id)
    if not data:
        return

    total = len(data["questions"])
    correct = data["correct"]
    wrong = data["wrong"]
    percentage = round((correct / total) * 100) if total else 0

    if percentage >= 90:
        result_text = "🏆 A’lo natija!"
    elif percentage >= 70:
        result_text = "👏 Juda yaxshi!"
    elif percentage >= 50:
        result_text = "👍 Yaxshi, yana mashq qiling!"
    else:
        result_text = "📚 Ko‘proq mashq qilish kerak."

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Yana test ishlash", callback_data="restart")],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="home")]
    ])

    await message.edit_text(
        "🎉 TEST YAKUNLANDI!\n\n"
        f"🎓 Sinf: {data['class_number']}-sinf\n"
        f"📚 Fan: {data['subject']}\n\n"
        f"📝 Jami: {total}\n"
        f"✅ To‘g‘ri: {correct}\n"
        f"❌ Noto‘g‘ri: {wrong}\n"
        f"📊 Natija: {percentage}%\n\n{result_text}",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "restart")
async def restart_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in users:
        await callback.answer()
        return
    await callback.message.edit_text(
        f"📚 Fan: {users[user_id]['subject']}\n\nNechta test ishlamoqchisiz?",
        reply_markup=test_count_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "home")
async def home_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    old = users.get(user_id, {}).get("timer_task")
    if old and not old.done():
        old.cancel()
    reset_user(user_id)
    await callback.message.edit_text(
        "🏠 BOSH MENYU\n\n🎓 O‘zingizning sinfingizni tanlang:",
        reply_markup=classes_keyboard()
    )
    await callback.answer()

async def main():
    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
