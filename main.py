import csv
import logging
from random import choice, choices

import telebot
from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton)

TOKEN = '...'

logging.basicConfig(
   level=logging.INFO,
   encoding='utf-8',
   format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')


class Bot:
    def __init__(self):
        self.bot = telebot.TeleBot(TOKEN)
        self.data = self.load_capitals()
        self.correct_answer = None
        self.count_answers = 0

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            if call.data == 'end':
                logging.debug('Запрос на завершение игры')
                self.bot.delete_message(call.message.chat.id,
                                        call.message.message_id)
                self.bot.send_message(call.message.chat.id,
                                      self.show_results(),
                                      parse_mode='HTML')
                self.count_answers = 0
            else:
                if call.data == self.correct_answer:
                    logging.info(f'Был дан верный ответ')
                    self.bot.answer_callback_query(call.id, "Верно!")
                    self.count_answers += 1
                else:
                    logging.info(f'Был дан неверный ответ')
                    self.bot.answer_callback_query(call.id, "Неверно!")
                text, self.correct_answer, options = self.get_question()
                keyboard = self.inline_keyboard(options)
                self.bot.edit_message_text(text,
                                           call.message.chat.id,
                                           call.message.message_id,
                                           reply_markup=keyboard,
                                           parse_mode='HTML')

        @self.bot.message_handler(commands=['help'])
        def help_game(message):
            logging.info('Получена команда /help')
            text = 'Я бот для проведения игры <b>Угадай столицу</b>.\n'
            text += 'Отправьте /start чтобы начать.'
            self.bot.send_message(message.chat.id,
                                  text,
                                  parse_mode='HTML')

        @self.bot.message_handler(commands=['start'])
        def start_game(message):
            logging.info('Получена команда /start')
            text, self.correct_answer, options = self.get_question()
            keyboard = self.inline_keyboard(options)
            self.bot.send_message(message.chat.id,
                                  text,
                                  reply_markup=keyboard,
                                  parse_mode='HTML')

    def run(self):
        self.bot.infinity_polling()

    @staticmethod
    def inline_keyboard(options):
        logging.info('Создание inline клавиатуры')
        keyboard = InlineKeyboardMarkup(row_width=2)
        buttons = [InlineKeyboardButton(s, callback_data=s) for s in options]
        keyboard.add(*buttons)
        keyboard.add(InlineKeyboardButton('Стоп игра', callback_data='end'))
        logging.info('inline клавиатура создана')
        return keyboard

    @staticmethod
    def load_capitals():
        capitals = dict()
        logging.info('Загрузка файла и получения списка стран и столиц')
        try:
            with open('capitals.csv', newline='', encoding='utf-8') as f:
                data = csv.reader(f, delimiter=';')
                for line in data:
                    capitals[line[0]] = line[1]
        except Exception as e:
            logging.exception(e)
        logging.info('Список стран и столиц загружен')
        return capitals

    def get_question(self):
        logging.info('Получение нового вопроса')
        countries, capitals = list(self.data.keys()), list(self.data.values())
        random_countries = choices(countries, k=4)
        country = choice(random_countries)
        answer = self.data[country]
        options = [self.data[country] for country in random_countries]
        logging.info(f'Вопрос получен. Страна: '
                     f'{country}, столица: {answer}, '
                     f'варианты ответов: {options}')
        return f'Назови столицу страны: <b>{country}</b>?', answer, options

    def show_results(self):
        logging.info('Отправка результатов')
        text = f'Вы дали правильных ответов: {self.count_answers}\n'
        text += 'Отправьте /start чтобы начать заново.'
        return text


if __name__ == '__main__':
    bot = Bot()
    bot.run()