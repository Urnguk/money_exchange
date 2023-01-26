import telebot
from telebot import types
from money_data import MoneyOpen
from wakepy import set_keepawake, unset_keepawake

token = "5955076570:AAFkRSP0Jzgp05iTtpP7UTI06GeTnK-nDcw"
bot = telebot.TeleBot(token)
users_dict = {428041713: "Timofey", 255501902: "Ilya", 202167212: "Valek", 115726489: "Timoha"}
users_dict_reverse = {"Timofey": 428041713, "Ilya": 255501902, "Valek": 202167212, "Timoha": 115726489}
ban = set()
filename = "data.bin"

payer = ''
recipient = ""
value = 0
id = 0


@bot.message_handler(content_types=["text"])
def message_reply(message):
    global id
    id = message.from_user.id
    print(message.from_user.id, message.text)
    if id in ban:
        bot.send_message(id,
                         "М'Айк закончил разговор")
        return
    if id not in users_dict.keys():
        bot.send_message(id,
                         "Мама не разрешает мне разговаривать с незнакомцами")
        ban.add(id)
        return
    if message.text == "печать":
        with MoneyOpen(filename) as work:
            print_res = work.__str__()
            bot.send_message(id, print_res)
            return
    if message.text == "оплата":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for user_name in users_dict.values():
            user_button = types.KeyboardButton(user_name)
            markup.add(user_button)
        bot.send_message(id,
                         "Кто платил?",
                         reply_markup=markup)
        bot.register_next_step_handler(message, get_payer)
        return
    bot.send_message(id,
                     "Постой, я тебя знаю! Привет, {}!".format(users_dict[id]))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    print_button = types.KeyboardButton("печать")
    pay_button = types.KeyboardButton("оплата")
    markup.add(print_button)
    markup.add(pay_button)
    bot.send_message(id,
                     "Выберите операцию",
                     reply_markup=markup)

def get_payer(message):
    global payer
    global id
    payer = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if payer not in users_dict.values():
        markup.add(types.KeyboardButton("Вернуться в меню"))
        bot.send_message(id,
                         "Произошла ошибка, некорректное имя. Напиши что угодно, чтобы вернуться в меню.",
                         reply_markup=markup)
        bot.register_next_step_handler(message, message_reply)
        return
    for user_name in users_dict.values():
        user_button = types.KeyboardButton(user_name)
        markup.add(user_button)
    markup.add(types.KeyboardButton("all"))
    bot.send_message(id,
                     "За кого?",
                     reply_markup=markup)
    bot.register_next_step_handler(message, get_recipient)


def get_recipient(message):
    global recipient
    recipient = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if recipient not in users_dict.values() and recipient != "all":
        markup.add(types.KeyboardButton("Вернуться в меню"))
        bot.send_message(id,
                         "Произошла ошибка, некорректное имя. Напиши что угодно, чтобы вернуться в меню.",
                         reply_markup=markup)
        bot.register_next_step_handler(message, message_reply)
        return
    for price in ["X", 1000, 2000, 5000, 10000, 75000, 100000]:
        price_button = types.KeyboardButton(str(price))
        markup.add(price_button)
    bot.send_message(id,
                     "Введите сумму оплаты в теньге или нажмите на крест чтобы отменить операцию",
                     reply_markup=markup)
    bot.register_next_step_handler(message, get_value)


def get_value(message):
    global payer
    global recipient
    global value
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    try:
        value = int(message.text)
    except ValueError:
        markup.add(types.KeyboardButton("Вернуться в меню"))
        bot.send_message(id,
                         "Произошла ошибка, некорректная сумма. Напиши что угодно, чтобы вернуться в меню.",
                         reply_markup=markup)
        bot.register_next_step_handler(message, message_reply)
        return
    with MoneyOpen("data.bin")as work, open("log.txt", mode="a") as log:
        log.write("writer: {0}; payer: {1}; recipient: {2}; value: {3}\n"
                  .format(users_dict[id], payer, recipient, value))
        work.pay(payer, recipient, value)
    if recipient == "all":
        for user_id in users_dict.keys():
            bot.send_message(user_id,
                             "{} сообщил, что {} заплатил за всех {} теньге."
                             .format(users_dict[id], payer, value))
    else:
        bot.send_message(users_dict_reverse[recipient],
                         "{} сообщил, что {} заплатил за тебя {} теньге."
                         .format(users_dict[id], payer, value))
    markup.add(types.KeyboardButton("Вернуться в меню"))
    bot.send_message(id,
                     "Оплата успешно произведена. Напиши что угодно, чтобы вернуться в меню.",
                     reply_markup=markup)
    bot.register_next_step_handler(message, message_reply)


set_keepawake(keep_screen_awake=False)
bot.infinity_polling()
unset_keepawake()


