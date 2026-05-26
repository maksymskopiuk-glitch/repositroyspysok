"""
Телеграм-бот для пошуку учнів у списку класу.

ЗАЛЕЖНОСТІ (встанови перед запуском):
    pip install python-telegram-bot

ЗАПУСК:
    python bot.py

ЩО ПОТРІБНО:
    1. Створи бота через @BotFather у Телеграмі → отримаєш токен
    2. Встав свій токен у рядок BOT_TOKEN нижче
"""

import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# =====================================================================
# 👇 ВСТАВ СЮДИ ТОКЕН СВОГО БОТА (отримати у @BotFather у Телеграмі)
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
# =====================================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ---------------------------------------------------------------------------
# База даних учнів
# Ключ: нормалізоване ім'я (нижній регістр, відсортовані слова)
# Значення: словник з даними учня
# ---------------------------------------------------------------------------

def normalize(name: str) -> frozenset:
    """Розбиває рядок на слова і повертає frozenset у нижньому регістрі.
    Завдяки цьому 'Ахмед Жасмін' і 'жасмін ахмед' дадуть однаковий результат."""
    return frozenset(name.strip().lower().split())


STUDENTS: dict[frozenset, dict] = {
    normalize("Ахмед Жасмін"): {
        "full": "Ахмед Жасмін",
        "birthday": "14.05",
        "number": 1,
        "next": "Багнюк Максим",
    },
    normalize("Багнюк Максим"): {
        "full": "Багнюк Максим Богданович",
        "birthday": "12.06",
        "number": 2,
        "next": "Богданова Каріна",
    },
    normalize("Богданова Каріна"): {
        "full": "Богданова Каріна Олегівна",
        "birthday": "13.07",
        "number": 3,
        "next": "Бортнік Анна",
    },
    normalize("Бортнік Анна"): {
        "full": "Бортнік Анна Валентинівна",
        "birthday": "17.12",
        "number": 4,
        "next": "Брик Павло",
    },
    # Додатковий псевдонім для Бортнік
    normalize("Бортнік Аня"): {
        "full": "Бортнік Анна Валентинівна",
        "birthday": "17.12",
        "number": 4,
        "next": "Брик Павло",
    },
    normalize("Брик Павло"): {
        "full": "Брик Павло Павлович",
        "birthday": "07.10",
        "number": 5,
        "next": "Височанська Ангеліна",
    },
    normalize("Височанська Ангеліна"): {
        "full": "Височанська Ангеліна Ігорівна",
        "birthday": "10.04",
        "number": 6,
        "next": "Іщук Катерина",
    },
    normalize("Іщук Катерина"): {
        "full": "Іщук Катерина Сергіївна",
        "birthday": "18.09",
        "number": 7,
        "next": "Карп'як Денис",
    },
    normalize("Іщук Катя"): {
        "full": "Іщук Катерина Сергіївна",
        "birthday": "18.09",
        "number": 7,
        "next": "Карп'як Денис",
    },
    normalize("Карп'як Денис"): {
        "full": "Карп'як Денис Олександрович",
        "birthday": "07.09",
        "number": 8,
        "next": "Качмар Віталій",
    },
    normalize("Качмар Віталій"): {
        "full": "Качмар Віталій Олександрович",
        "birthday": "25.07",
        "number": 9,
        "next": "Кіц Христина",
    },
    normalize("Кіц Христина"): {
        "full": "Кіц Христина Михайлівна",
        "birthday": "22.05",
        "number": 10,
        "next": "Колб Максим",
    },
    normalize("Колб Максим"): {
        "full": "Колб Максим Павлович",
        "birthday": "22.09",
        "number": 11,
        "next": "Костіцина Влада",
    },
    # Псевдонім "Кок" із оригінального коду
    normalize("Кок"): {
        "full": "Колб Максим Павлович",
        "birthday": "22.09",
        "number": 11,
        "next": "Костіцина Влада",
    },
    normalize("Костіцина Влада"): {
        "full": "Костіцина Влада Віталійовна",
        "birthday": "08.05",
        "number": 12,
        "next": "Кролюк Влад",
    },
    normalize("Кролюк Влад"): {
        "full": "Кролюк Влад Дмитрович",
        "birthday": "28.08",
        "number": 13,
        "next": "Кураков Микита",
    },
    normalize("Кураков Микита"): {
        "full": "Кураков Микита Олексійович",
        "birthday": "19.09",
        "number": 14,
        "next": "Курилович Каріна",
    },
    normalize("Курилович Каріна"): {
        "full": "Курилович Каріна Вадимівна",
        "birthday": "14.03",
        "number": 15,
        "next": "Мирончик Софія",
    },
    normalize("Мирончик Софія"): {
        "full": "Мирончик Софія Миколаївна",
        "birthday": "24.12",
        "number": 16,
        "next": "Молодцов Валентин",
    },
    normalize("Молодцов Валентин"): {
        "full": "Молодцов Валентин Станіславович",
        "birthday": "12.02",
        "number": 17,
        "next": "Нікітюк Ванесса",
    },
    normalize("Нікітюк Ванесса"): {
        "full": "Нікітюк Ванесса Анатоліївна",
        "birthday": "16.06",
        "number": 18,
        "next": "Островська Марія",
    },
    normalize("Островська Марія"): {
        "full": "Островська Марія Ігорівна",
        "birthday": "22.08",
        "number": 19,
        "next": "Посполітак Дарина",
    },
    normalize("Посполітак Дарина"): {
        "full": "Посполітак Дарина Володимирівна",
        "birthday": "16.05",
        "number": 20,
        "next": "Равшанова Севінч",
    },
    normalize("Равшанова Севінч"): {
        "full": "Равшанова Севінч Азизбек Кизи",
        "birthday": "08.05",
        "number": 21,
        "next": "Сєркова Кіра",
    },
    normalize("Сєркова Кіра"): {
        "full": "Сєркова Кіра Сергіївна",
        "birthday": "08.03",
        "number": 22,
        "next": "Скопюк Максим",
    },
    normalize("Скопюк Максим"): {
        "full": "Скопюк Максим Дмитрович",
        "birthday": "19.10",
        "number": 23,
        "next": "Степасюк Софія",
    },
    # Псевдонім "Креатор"
    normalize("Креатор"): {
        "full": "Скопюк Максим Дмитрович",
        "birthday": "19.10",
        "number": 23,
        "next": "Степасюк Софія",
    },
    normalize("Степасюк Софія"): {
        "full": "Степасюк Софія Леонідівна",
        "birthday": "31.07",
        "number": 24,
        "next": "Філон Вероніка",
    },
    normalize("Філон Вероніка"): {
        "full": "Філон Вероніка Олександрівна",
        "birthday": "14.01",
        "number": 25,
        "next": "Шагута Давид",
    },
    normalize("Шагута Давид"): {
        "full": "Шагута Давид Артемович",
        "birthday": "27.11",
        "number": 26,
        "next": "Шиманська Ліза",
    },
    # Псевдонім "Богоподобний"
    normalize("Богоподобний"): {
        "full": "Шагута Давид Артемович",
        "birthday": "27.11",
        "number": 26,
        "next": "Шиманська Ліза",
    },
    normalize("Шиманська Ліза"): {
        "full": "Шиманська Ліза Ігорівна",
        "birthday": "26.04",
        "number": 27,
        "next": "Шума Іра",
    },
    normalize("Шума Іра"): {
        "full": "Шума Іра Сергіївна",
        "birthday": "19.05",
        "number": 28,
        "next": None,  # остання в списку
    },
}


def find_student(query: str) -> dict | None:
    """Шукає учня за нормалізованим запитом."""
    key = normalize(query)
    return STUDENTS.get(key)


def format_student(data: dict) -> str:
    """Формує текст відповіді для учня."""
    lines = [
        f"👤 *{data['full']}*",
        f"🎂 День народження: {data['birthday']}",
        f"📋 Номер у списку: {data['number']}",
    ]
    if data.get("next"):
        lines.append(f"➡️ Наступний(-а): {data['next']}")
    else:
        lines.append("🏁 Останній(-я) у списку")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Обробники команд бота
# ---------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Відповідає на команду /start."""
    await update.message.reply_text(
        "Привіт! 👋\n"
        "Введи прізвище та ім'я однокласника — я знайду його в списку.\n\n"
        "Наприклад: *Ахмед Жасмін* або *жасмін ахмед*",
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Відповідає на команду /help."""
    await update.message.reply_text(
        "📖 *Як користуватись:*\n"
        "Просто напиши ім'я учня у будь-якому порядку.\n"
        "Регістр не важливий.\n\n"
        "Приклади:\n"
        "• `Ахмед Жасмін`\n"
        "• `жасмін ахмед`\n"
        "• `КАЧМАР ВІТАЛІЙ`",
        parse_mode="Markdown",
    )


async def search_student(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробляє текстові повідомлення — шукає учня."""
    query = update.message.text.strip()
    student = find_student(query)

    if student:
        await update.message.reply_text(
            f"🔍 Завантаження...\n\n{format_student(student)}",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            "❌ Такого учня не знайдено!\n"
            "Перевір правильність написання і спробуй ще раз.\n\n"
            "Введи /help щоб дізнатись як шукати."
        )


# ---------------------------------------------------------------------------
# Запуск бота
# ---------------------------------------------------------------------------

def main() -> None:
    # 👇 Тут використовується твій BOT_TOKEN
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Обробляє будь-яке текстове повідомлення (не команду)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_student))

    print("Бот запущений! Натисни Ctrl+C щоб зупинити.")
    app.run_polling()


if __name__ == "__main__":
    main()