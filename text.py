from db import UserRecord, OrderRecord, ContactRecord


start = "* Тут текст приветствия *"

invalid_request = "Простите, я вас не понимаю 🙁..."

name_input_prompt = "Введите желамое имя для общения в чате:"

commands_guide = "Нажмите на строку ввода, чтобы увидеть доступные команды бота 💻"

in_development = "В разработке..."

send_message_text = "Чтобы связаться с нами, просто напишите боту свое сообщение"

message_send_success_text = "Cообщение отправлено ✅"

message_send_failed = "Отрпавить сообщение не удалось ❌"

def reg_success_text(name: str) -> str:
    return f'имя успешно изменено на <b>{name}</b> ✅'


# COMMANDS

start_command = 'start'
start_command_desc = "Начать"
service_1_command = 'assist'
service_1_command_desc = 'ПОМОЩЬ В ПОЛУЧЕНИИ ВИЗЫ В США'
service_2_command = 'consultation'
service_2_command_desc = 'ТРЕНИНГИ С ВИЗОВЫМ ЭКСПЕРТОМ'
service_3_command = 'fees'
service_3_command_desc = 'ОПЛАТА СБОРОВ'
change_name_command = 'change_name'
change_name_command_desc = 'Изменить имя для общения в чате'
send_message_command = 'msg'
send_message_command_desc = 'написать нам'

service_desc_dict = {1: service_1_command_desc,
                     2: service_2_command_desc,
                     3: service_3_command_desc}

# SHADOW COMMANDS
add_admin_command = 'add'
del_admin_command = 'del'
admin_list_command = 'list'
send_all_command = 'send_all'
users_info_command = 'users_info'

super_admin_guide = message_text = f"""
Как использовать команды суперпользователя?

1) <b>/{add_admin_command}</b> <i>username</i> - добавить админа  
2) <b>/{del_admin_command}</b> <i>username</i> - удалить админа
3) <b>/{admin_list_command}</b> - получить список админов 

Админы будут получать сообщения от пользователей бота, а также могут отвечать на них и использовать массовую рассылку.  

P.S. Список суперпользователей определён заранее и не может быть изменён через интерфейс бота.
"""

user_not_found = "Пользователь с таким именем не найден!\nУбедитесь, что данный пользователь уже писал боту (например использовал команду /start)"
invalid_args = "Вы не указали имя пользователя"
admin_guide = f"""
Вы являетесь админом!\n\n1) Чтобы ответить конкретному пользователю, используйте кнопку под сообщением, которое он прислал
2) Чтобы отправить сообщение для всех пользователей, используйте команду <b>/{send_all_command}</b>
3) Чтобы получить информацию обо всех зарегистрированных пользователях, используйте команду <b>/{users_info_command}</b>

"""

service_1_text = """
Заполним форму <b>DS-160</b> и запишем на собеседование в страну получения визы с \
высокой статистикой одобрений\n\n<b>Стоимость - 170 USD</b>
"""

service_2_text = """
Поможем сформировать индивидуальную визовую стратегию, составим пошаговый план действий, \
проведем расширенную тренировку по разносторонним вопросам для успешного прохождения \
собеседования и получения визы. Вы получите уверенность как отвечать на неожиданные вопросы. \
Эффективное решение даже если вы получали отказы ранее.\n\n<b>Стоимость - 350 USD</b>"""

service_3_text = """
Поможем оплатить консульский сбор для прохождения интервью на визу США, \
если у вас нет карты иностранного банка\n\n<b>Стоимость - 230 USD</b>"""

service_button_text_default = "ЗАКАЗАТЬ УСЛУГУ"

service_text = "Спасибо за ваш заказ. Мы свяжемся с вами как можно скорее."

send_contact_request_text = "Пожалуйста, оставьте ваши контактные данные (для этого можно использовать кнопку \"Отправить контакт 📞\")"

share_contact_button_text = "Отправить контакт 📞"

contact_message_success = "Ваш контакт записан успешно ✅"

def create_order_desc(user: UserRecord, order: OrderRecord, contact: ContactRecord | None = None) -> str:
    desc = f"""
<b>Поступил новый заказ!</b> 📝\n
Пользователь: <i>{user['name']} (@{user['username']})</i>
Имя: <i>{contact['first_name'] if contact else 'неизвестно'}</i>
Фамилия: <i>{contact['last_name'] if contact else 'неизвестно'}</i>
Телефон: <i>{contact['phone'] if contact else 'неизвестно'}</i>
Услуга: <i>{service_desc_dict[order['service_id']]}</i>
Дата: <i>{order['order_date'].strftime('%d-%m-%Y')}</i>"""
    
    return desc
