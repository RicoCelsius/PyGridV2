from telegram_module import sendMessage
import traceback

def exception_handler(exception):
    try:
        message = f'Exception occurred:\n{exception}\nPlease contact the developer!\n'
        traceback_str = traceback.format_exc()
        sendMessage(message + "\n" + traceback_str)
        print(message)
    except Exception as e:
        print(f"Failed to send message: {e}")
