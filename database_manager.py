import aiosqlite
import random
from config import DB_NAME

async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER, user_name VARCHAR, last_score INTEGER, high_score INTEGER, current_score INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_questions (question_id INTEGER PRIMARY KEY, question VARCHAR, answer VARCHAR, options VARCHAR)''')
        await db.commit()

async def add_new_user(user_id, user_name):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT * FROM quiz_state WHERE user_id = ?', (user_id,))
        user = await cursor.fetchone()

        if user is None:
            await db.execute('''
                INSERT INTO quiz_state (user_id, question_index, user_name, last_score, high_score, current_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, 0, user_name, 0, 0, 0))
        else:
            await db.execute('''
                UPDATE quiz_state
                SET current_score = 0,
                    question_index = 0
                WHERE user_id = ?
            ''', (user_id,))
        
        await db.commit()
        
async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        quiz_state = await db.execute('SELECT * FROM quiz_state WHERE user_id = ?', (user_id,))
        quiz_state = await quiz_state.fetchall()
        await db.execute('UPDATE quiz_state SET question_index = ? WHERE user_id = ?', (index, user_id))
        await db.commit()

async def update_current_score(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE quiz_state SET current_score = current_score + 1 WHERE user_id = ?', (user_id,))
        await db.commit()

        
async def update_high_score(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        quiz_state = await db.execute('SELECT * FROM quiz_state WHERE user_id = ?', (user_id, ))
        quiz_state = await quiz_state.fetchone()
        if quiz_state is not None and quiz_state[5] > quiz_state[4]:
            await db.execute('UPDATE quiz_state SET high_score = ? WHERE user_id = ?', (quiz_state[5], user_id))
        
        await db.execute('UPDATE quiz_state SET last_score = ? WHERE user_id = ?', (quiz_state[5], user_id))  
        await db.commit()
        

async def get_next_question(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            SELECT * FROM quiz_questions 
            WHERE question_id = (
                SELECT question_index 
                FROM quiz_state 
                WHERE user_id = ?
            )
        ''', (user_id,))
        question = await cursor.fetchone()
        return question

async def seed_questions():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT COUNT(*) FROM quiz_questions')
        question_count = await cursor.fetchone()
        if question_count[0] == 0:
            await db.executemany('''
                INSERT INTO quiz_questions (question_id, question, answer, options)
                VALUES (?, ?, ?, ?)
            ''', [
                # Вопрос 1
                (0, "Что такое Python?", "Язык программирования", prepare_options("Язык программирования", "Тип данных, Музыкальный инструмент, Змея на английском")),
                # Вопрос 2
                (1, "Какой тип данных используется для хранения целых чисел?", "int", prepare_options("int", "float, str, natural")),
                # Вопрос 3
                (2, "Кто разработчик языка Python?", "Гвидо ван Россум", prepare_options("Гвидо ван Россум", "Деннис Ритчи, Бьёрн Страуструп, Джеймс Гослинг")),
                # Вопрос 4
                (3, "Назовите ключевое слово для создания цикла со счетчиком в Python?", "for", prepare_options("for", "if, while, let")),
                # Вопрос 5
                (4, "Каким образом в Python оформляется блок кода?", "Отступом", prepare_options("Отступом", "Скобками, ключевым словом BEGIN-END, №")),
                # Вопрос 6
                (5, "Что выведет это выражение: 'Python' * 3?", "PythonPythonPython", prepare_options("PythonPythonPython", "Python 3, PythonPython3, Ошибка")),
                                
                # Вопрос 7
                (6, "Какое исключение вызывается при делении на ноль?", "ZeroDivisionError", prepare_options("ZeroDivisionError", "DivideByZeroException, ArithmeticError, ValueError")),
                                
                # Вопрос 8
                (7, "Что делает функция len()?", "Определяет длину объекта", prepare_options("Определяет длину объекта", "Удаляет последний элемент, Выводит элемент с определенным индексом, Преобразует объект в список")),
                                
                # Вопрос 9
                (8, "Что такое список в Python?", "Структура данных состоящая из элементов которая может изменяться", prepare_options("Структура данных состоящая из элементов которая может изменяться", "Функция для вывода данных, Тип числовых данных, Неизменяемый тип данных")),
                                
                # Вопрос 10
                (9, "Что такое функция в Python?", "Блок повторно используемого кода который выполняет определенное действие", prepare_options("Блок повторно используемого кода который выполняет определенное действие", "Это место для хранения данных, Это основной модуль языка, Это специальный метод для операторов"))
                ])
            await db.commit()
            
def prepare_options(answer, wrong_options):
                options = wrong_options.split(', ')
                options.insert(random.randint(0, len(options)), answer)
                return ', '.join(options)
            
async def prepare_db():
   await create_tables()
   await seed_questions()