import logging

from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from open_ai_file import send_analyzed_report
from config import telegram_token


bot = Bot(token=telegram_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


checklist = {
    "location_1": ["Кухня", "Коридор", "Спальня", "Зал", "Вбиральня"],
    "location_2": ["Коридор", "Балкон", "Спальня", "Кабінет", "Дитячя"],
    "location_3": ["Кабінет №1", "Кабінет №2", "Кабінет №3", "Кухня", "Вбиральня"],
    "location_4": ["Комора", "Кухня", "Зал", "Розважальна", "Роздягальня"],
    "location_5": ["Кухня", "Столова", "Спальня", "Прихожа", "Коридор"]
}


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message, state: FSMContext) -> None:
    """
    Sends a welcome message and presents a set of location options as inline keyboard buttons.

    Args:
        message (types.Message): The message object triggering the command.
        state (FSMContext): The FSM (finite state machine) context for handling user state.

    Returns:
        None
    """
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(types.InlineKeyboardButton(text="Локація 1", callback_data="location_1"))
    keyboard.add(types.InlineKeyboardButton(text="Локація 2", callback_data="location_2"))
    keyboard.add(types.InlineKeyboardButton(text="Локація 3", callback_data="location_3"))
    keyboard.add(types.InlineKeyboardButton(text="Локація 4", callback_data="location_4"))
    keyboard.add(types.InlineKeyboardButton(text="Локація 5", callback_data="location_5"))

    await message.reply("Вітаю! Оберіть одну з локацій:", reply_markup=keyboard)
    await state.update_data(started=True)


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("location_"))
async def handle_location(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Handles the callback query for selecting a location and presents a checklist of items related to that location.

    Args:
        callback_query (types.CallbackQuery): The callback query object containing the data of the selected location.
        state (FSMContext): The FSM (finite state machine) context for handling user state.

    Returns:
        None
    """
    # Checking if the conversation has been started
    data = await state.get_data("started")
    if not data.get("started"):
        print(data.get('started'))
        return

    # Extracting the selected location from the callback query
    location = callback_query.data

    # Acknowledging the callback query
    await bot.answer_callback_query(callback_query.id)

    # Generating inline keyboard buttons for checklist items related to the selected location
    keyboard = types.InlineKeyboardMarkup()
    for i in checklist[location]:
        keyboard.add(types.InlineKeyboardButton(text=f"{i}", callback_data=f"room_{i}"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))

    # Sending the checklist to the user
    await callback_query.message.reply('Перевірте пункти!', reply_markup=keyboard)
    await state.update_data(location=location)


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("room"))
async def handle_room(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
     Handles the callback query for selecting a room and presents options to mark it as clean or leave a comment.

     Args:
         callback_query (types.CallbackQuery): The callback query object containing the data of the selected room.
         state (FSMContext): The FSM (finite state machine) context for handling user state.

     Returns:
         None
     """
    # Acknowledging the callback query
    await bot.answer_callback_query(callback_query.id)

    # Extracting the selected room from the callback query
    room = callback_query.data

    # Generating inline keyboard buttons for marking the room as clean or leaving a comment
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="🟢 Все чисто", callback_data=f"clear_{room}"))
    keyboard.add(types.InlineKeyboardButton(text="🔴 Залишити коментар", callback_data=f"comment_{room}"))

    # Asking the user to mark the room as clean or leave a comment
    await callback_query.message.reply("Виберіть 'Все чисто', якщо немає зауважень, або додайте коментар...",
                                       reply_markup=keyboard)

    # Updating the user's state with the selected room
    await state.update_data(room=room[5:])


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("clear"))
async def handle_clear(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Handles the callback query for marking a room as clean and updates the state accordingly.

    Args:
        callback_query (types.CallbackQuery): The callback query object containing the data of the selected room.
        state (FSMContext): The FSM (finite state machine) context for handling user state.

    Returns:
        None
    """
    # Retrieving data from the state
    state_data = await state.get_data()
    location_data = state_data.get("location", None)
    room = state_data.get("room", None)

    # Updating the state with the clean status for the selected room
    location_comments = state_data.get(location_data, {})
    location_comments[room] = "Все чисто!"
    await state.update_data({location_data: location_comments})

    # Generating inline keyboard buttons
    keyboard = types.InlineKeyboardMarkup()
    if len(location_comments) == 5:
        keyboard.add(types.InlineKeyboardButton(text="Сформувати звіт! 📋", callback_data="report"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=location_data))

    # Sending a confirmation message with options to proceed or go back
    await callback_query.message.reply(f"Дякую, успішно збережено!: {location_comments}", reply_markup=keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("comment"))
async def handle_comment(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Handles the callback query for leaving a comment about a room.

    Args:
        callback_query (types.CallbackQuery): The callback query object containing the data of the selected room.
        state (FSMContext): The FSM (finite state machine) context for handling user state.

    Returns:
        None
    """
    # Updating the state to indicate that a message is expected
    await state.update_data(message=True)
    await state.update_data(query=callback_query)

    # Acknowledging the callback query
    await bot.answer_callback_query(callback_query.id)

    # Asking the user to leave a comment
    await callback_query.message.reply("Будь ласка, залиште коментар:")


@dp.message_handler(lambda message: message.text and not message.entities)
async def handle_text_message(message: types.Message, state: FSMContext) -> None:
    """
    Handles the text message input for leaving a comment about a room.

    Args:
        message (types.Message): The message object containing the text comment.
        state (FSMContext): The FSM (finite state machine) context for handling user state.

    Returns:
        None
    """
    # Retrieving data from the state
    data = await state.get_data()

    # Checking if a message is expected
    if not data.get("message"):
        return

    # Extracting the comment from the message
    comment = message.text

    # Retrieving additional state data
    state_data = await state.get_data()
    location_data = state_data.get("location", None)
    room = state_data.get("room", None)

    # Updating the state with the comment for the selected room
    location_comments = state_data.get(location_data, {})
    location_comments[room] = comment
    await state.update_data({location_data: location_comments})

    # Generating inline keyboard buttons
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=location_data))

    # Asking the user to upload a photo
    await message.reply(f"Будь ласка, завантажте фотографію:", reply_markup=keyboard)

    # Updating the state to indicate that a photo is expected
    await state.update_data(photo_true=True)
    await state.update_data(message=False)


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo_message(message: types.Message, state: FSMContext) -> None:
    """
       Handles the photo message input and updates the state with the photo link.

       Args:
           message (types.Message): The message object containing the photo.
           state (FSMContext): The FSM (finite state machine) context for handling user state.

       Returns:
           None
       """
    # Retrieving data from the state
    data = await state.get_data()

    # Checking if a photo is expected
    if not data.get("photo_true", None):
        return

    # Extracting the photo ID and constructing the photo link
    photo_id = message.photo[-1].file_id
    photo_link = f"t.me/{message.chat.username}?photo={photo_id}"

    # Retrieving additional state data
    state_data = await state.get_data()
    location_data = state_data.get("location")
    room = state_data.get("room")

    # Updating the state with the photo link for the selected room
    location_comments = state_data.get(location_data, {})
    location_comments[room] += f" {photo_link}"
    await state.update_data({location_data: location_comments})
    await state.update_data(started=True)

    # Generating inline keyboard buttons
    keyboard = types.InlineKeyboardMarkup()
    if len(location_comments) == 5:
        keyboard.add(types.InlineKeyboardButton(text="Сформувати звіт! 📋", callback_data="report"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=location_data))

    # Sending a confirmation message with options to proceed or go back
    await message.reply(f"Фотографію та коментар успішно збережено! {location_comments}", reply_markup=keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == "report")
async def handle_report(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
       Handles the callback query to generate and send a report based on the checklist entries.

       Args:
           callback_query (types.CallbackQuery): The callback query object containing the request to generate a report.
           state (FSMContext): The FSM (finite state machine) context for handling user state.

       Returns:
           None
       """
    # Acknowledging the callback query
    await bot.answer_callback_query(callback_query.id)

    # Retrieving data from the state
    state_data = await state.get_data()
    room = state_data.get("location")
    location_rooms = state_data.get(room, {})

    # Constructing the report based on checklist entries
    report = "Звіт за чек-лист:\n"
    for room_name, status in location_rooms.items():
        report += f"{room_name}: {status}\n"

    # Generating inline keyboard buttons
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back"))

    # Sending the generated report
    report = await send_analyzed_report(report)
    await callback_query.message.reply(f"{report}", reply_markup=keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == "back")
async def handle_back(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    await send_welcome(callback_query.message, state)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
