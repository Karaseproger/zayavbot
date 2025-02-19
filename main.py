import telebot
from telebot import types

bot = telebot.TeleBot('7751378397:AAFGTMoCNSekyzpNubWOrhyYfFfzBmwbln4')

admin_id = ['5411263922', '5173714957', '1691099325']

kab = ['108', '111', '106', '109', '107', '104', '105', '102', '100', '103', '101',
       '207', '204', '203', '205', '200', '202', '201', '208', '303', '306', '307а', '307б', '302',
       '303б', '303а', '304', '300', '305', '301', '401', '402', '400', '403', '404',
       '407', '409', '406', '408']

faulty_equipment = {
    'ПК': ['Не загружается ОС', 'Мерцает экран', 'не включается', 'не подключается к интернету','не работает мышка/клавиатура', 'системная ошибка', 'Не загружается ПО'],
    'Принтер': ['Не печатает', 'Замятие бумаги', 'Заканчивается тонер'],
    'Проектор': ['Не включается', 'Плохая проекция', 'Не подключается'],
    'Интерактивная доска': ['Не реагирует на касания', 'Проблемы с калибровкой', 'Не подключается к ПК'],
    'Голова': ['Не соображает', 'Отсутствует лоническое мышление','Полностью отсутствует содержимое']
}

user_data = {}

USER_STATES = {
    'WAITING_FOR_NAME': 'waiting_for_name',
    'WAITING_FOR_ROOM': 'waiting_for_room',
    'WAITING_FOR_EQUIPMENT': 'waiting_for_equipment',
    'WAITING_FOR_ISSUE': 'waiting_for_issue'
}


def remove_keyboard():
    return types.ReplyKeyboardRemove()


@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'state': USER_STATES['WAITING_FOR_NAME']}
    bot.send_message(chat_id, "Введите ваше ФИО для подачи заявки.", reply_markup=remove_keyboard())


@bot.message_handler(
    func=lambda message: user_data.get(message.chat.id, {}).get('state') == USER_STATES['WAITING_FOR_NAME'])
def get_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text
    user_data[chat_id]['state'] = USER_STATES['WAITING_FOR_ROOM']
    bot.send_message(chat_id, "Теперь введите номер кабинета.", reply_markup=remove_keyboard())


@bot.message_handler(
    func=lambda message: user_data.get(message.chat.id, {}).get('state') == USER_STATES['WAITING_FOR_ROOM'])
def get_room(message):
    chat_id = message.chat.id
    if message.text in kab:
        user_data[chat_id]['room'] = message.text
        user_data[chat_id]['state'] = USER_STATES['WAITING_FOR_EQUIPMENT']
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        buttons = [types.KeyboardButton(eq) for eq in faulty_equipment.keys()]
        markup.add(*buttons)
        bot.send_message(chat_id, "Выберите неисправное оборудование:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Некорректный кабинет. Попробуйте снова.")


@bot.message_handler(
    func=lambda message: user_data.get(message.chat.id, {}).get('state') == USER_STATES['WAITING_FOR_EQUIPMENT'])
def equipment(message):
    chat_id = message.chat.id
    if message.text in faulty_equipment:
        user_data[chat_id]['equipment'] = message.text
        user_data[chat_id]['state'] = USER_STATES['WAITING_FOR_ISSUE']

        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        buttons = [types.KeyboardButton(issue) for issue in faulty_equipment[message.text]]
        markup.add(*buttons)
        bot.send_message(chat_id, "Выберите проблему:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Такого оборудования нет в списке. Попробуйте снова.")


@bot.message_handler(
    func=lambda message: user_data.get(message.chat.id, {}).get('state') == USER_STATES['WAITING_FOR_ISSUE'])
def get_issue(message):
    chat_id = message.chat.id
    if message.text in faulty_equipment.get(user_data[chat_id]['equipment'], []):
        user_data[chat_id]['issue'] = message.text
        report = (f"Пользователь: {user_data[chat_id]['name']}\n"
                  f"Кабинет: {user_data[chat_id]['room']}\n"
                  f"Оборудование: {user_data[chat_id]['equipment']}\n"
                  f"Проблема: {user_data[chat_id]['issue']}")

        for admin in admin_id:
            try:
                bot.send_message(admin, report)
            except Exception as e:
                print(f"Ошибка отправки админу {admin}: {e}")

        bot.send_message(chat_id, "Спасибо! Ваша заявка отправлена администратору.", reply_markup=remove_keyboard())
        user_data[chat_id] = {'state': USER_STATES['WAITING_FOR_NAME']}
        bot.send_message(chat_id, "Для новой заявки введите ФИО.")
    else:
        bot.send_message(chat_id, "Ошибка выбора проблемы. Попробуйте снова.")


bot.polling(none_stop=True)
