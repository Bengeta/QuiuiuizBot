import asyncio
from config import TELEGRAM_BOT_TOKEN
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database_manager import *

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = TELEGRAM_BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await add_new_user(message.from_user.id, message.from_user.username)
    await new_quiz(message)
    
@dp.message(F.text=="Вывести таблицу рекордов")
@dp.message(Command("records"))
async def cmd_quiz(message: types.Message):
    result_list = await get_best_results()
    result_text = ''
    for result in result_list:
        result_text = "\n" + str(result [2]) + " " + str(result[4]) + "\n"
        
    await message.answer(f"А вот и таблица результатов!{result_text}")

@dp.message(F.text=="Вывести последний результат")
@dp.message(Command("last_result"))
async def cmd_quiz(message: types.Message):
    last_result = await get_last_result(message.from_user.id)
    await message.answer(f"Ваш полседний результат: {last_result}")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Вывести таблицу рекордов"))
    builder.add(types.KeyboardButton(text="Вывести последний результат"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))
    
@dp.callback_query(F.data.contains("right_answer"))
async def right_answer(callback: types.CallbackQuery):
    await callback.message.answer("Верно!")
    current_question = await get_next_question(callback.from_user.id)
    await update_current_score(callback.from_user.id) 
    await get_question_or_finish_quiz(callback, current_question)


@dp.callback_query(F.data.contains("wrong_answer"))
async def wrong_answer(callback: types.CallbackQuery):
    current_question = await get_next_question(callback.from_user.id)
    right_answer = current_question[2]
    await callback.message.answer(f"Неправильно. Правильный ответ: {right_answer}")
    await get_question_or_finish_quiz(callback, current_question)
        
async def get_question_or_finish_quiz(callback, current_question):
        await callback.bot.edit_message_reply_markup(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            reply_markup=None
        )
        option = callback.data.split('|')[0]
        await callback.message.answer(f"Вы выбрали вариант: {option}")
        
        current_question_index = current_question[0]

        await update_quiz_index(callback.from_user.id, current_question_index + 1)
        current_question = await get_next_question(callback.from_user.id)

        if current_question is not None:
           await get_question(callback.message, callback.from_user.id)
        else:
            await update_high_score(callback.from_user.id)
            await callback.message.answer("Это был последний вопрос. Квиз завершен!")
            

async def start_bot():
    await dp.start_polling(bot)
    
    
async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)
    
    
async def get_question(message, user_id):
    current_question = await get_next_question(user_id)
    opts = current_question[3].split(', ')
    answer = current_question[2]

    kb = generate_options_keyboard(opts, answer)
    await message.answer(f"{current_question[1]}", reply_markup=kb)
    
def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        text = f"{option}|{'right_answer' if option == right_answer else 'wrong_answer'}"
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data= text
        ))
    builder.adjust(1)
    return builder.as_markup()