import telebot
from telebot import types
import re

bot = telebot.TeleBot('7301626849:AAFSWCfvZifs8z8W0LawyLi7PpKr3G9g9g0')
mes = ['здравствуйте, укажите кабинет']
admin_id = ['5411263922', '5173714957', '1691099325']

kab = ['108', '111', '106', '109', '107', '104', '105', '102', '100', '103', '101',
       '207', '204', '203', '205', '200', '202', '201','208', '303', '306', '307а', '307б', '302',
       '303б', '303а', '304', '300', '305', '301', '401', '402', '400', '403', '404',
       '407', '409', '406', '408']

polom = ['Интерактивная доска не работает', 'Компьютер сломан', 'Проблемы с интернетом',
         'заправка принтеров', 'принтер сломан', 'другая причина']

user_data = {}

# Состояния пользователя
USER_STATES = {
    'WAITING_FOR_NAME': 'waiting_for_name',
    'WAITING_FOR_ROOM': 'waiting_for_room',
    'WAITING_FOR_ISSUE': 'waiting_for_issue'
}


@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'state': USER_STATES['WAITING_FOR_NAME']}
    bot.send_message(chat_id, "Для отправки заявки, введите ФИО.")


@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == USER_STATES['WAITING_FOR_NAME'])
def get_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text
    user_data[chat_id]['state'] = USER_STATES['WAITING_FOR_ROOM']
    bot.send_message(chat_id, "Теперь введите номер кабинета.")


@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == USER_STATES['WAITING_FOR_ROOM'])
def get_room(message):
    chat_id = message.chat.id
    if message.text in kab:
        user_data[chat_id]['room'] = message.text
        user_data[chat_id]['state'] = USER_STATES['WAITING_FOR_ISSUE']
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        buttons = [types.KeyboardButton(issue) for issue in polom]
        markup.add(*buttons)
        bot.send_message(chat_id, "Вы выбрали кабинет. Выберите неисправность:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Неправильный номер кабинета. Пожалуйста, введите правильный.")


@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == USER_STATES['WAITING_FOR_ISSUE'])
def get_issue(message):
    chat_id = message.chat.id
    if message.text in polom:
        user_data[chat_id]['issue'] = message.text

        report = f"Пользователь: {user_data[chat_id].get('name', 'Неизвестно')}\n" \
                 f"Кабинет: {user_data[chat_id].get('room', 'Неизвестно')}\n" \
                 f"Неисправность: {user_data[chat_id]['issue']}"

        for admin_ids in admin_id:
            try:
                bot.send_message(admin_ids, report)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка отправки сообщения администратору {admin_ids}: {e}")

        bot.send_message(chat_id, "Спасибо! Ваша заявка отправлена администратору.")
        user_data[chat_id] = {'state': USER_STATES['WAITING_FOR_NAME']}
        bot.send_message(chat_id, "Если хотите отправить новую заявку, введите ФИО.")
    else:
        bot.send_message(chat_id, "Ошибка выбора неисправности. Попробуйте снова.")


bot.polling()
