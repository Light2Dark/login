from login import Login
from telegram.ext import PicklePersistence, Application
from dotenv import load_dotenv
import os
load_dotenv()
import boto3
import pickle

import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, CommandHandler, ContextTypes

# creating the bot
storage_path = "/tmp/bot_data" if os.environ.get("AWS_EXECUTION_ENV") is not None else "bot_data"

def create_application():
  persistence = PicklePersistence(filepath=storage_path, on_flush=True) # on_flush true means that it will only save to file when flush() is called
  application = Application.builder().token(os.environ["telegram_bot_key"]).persistence(persistence=persistence).build()
  return application

def get_db():
  """Reads pickle data from S3, then loads it in temp file under lambda"""
  s3 = boto3.resource("s3")
  data = None
  try:
    data = s3.Bucket(os.environ["bucket_name"]).Object(os.environ["key"]).get()['Body'].read()
  except Exception as e:
    print("Error with s3 get_db", e)
    return
  with open(storage_path, 'wb') as file:
    file.write(data)

def update_db():
  """Replace existing S3 file with new pickle data"""
  s3 = boto3.client("s3")
  try:
    s3.delete_object(Bucket=os.environ["bucket_name"], Key=os.environ["key"])
  except Exception as e:
    print("Error with deleting object in db", e)
  try:
    s3.upload_file(storage_path, os.environ["bucket_name"], os.environ["key"])
  except Exception as e:
    print("error with uploading file", e)
    logging.error(e)
    
async def persist_data(persistence: PicklePersistence): # We need to control when the data is persisted, because Lambda may be ending the process/session before the data is persisted
  await persistence.flush()
  update_db()

logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level=logging.INFO
)
logging.getLogger().setLevel(logging.INFO)

persistence = PicklePersistence(filepath=storage_path, on_flush=True) # on_flush true means that it will only save to file when flush() is called
application = Application.builder().token(os.environ["telegram_bot_key"]).persistence(persistence=persistence).build()

# bot_data = pickle.loads(s3.Bucket("icheckin-user-data").Object("bot_data").get()['Body'].read())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
    Welcome to iCheckin Bot! Please use the following commands to set your login details:
    /studentID your_student_id
    /password your_izone_password
    
    Then, enter an iCheckin code like 12345 and voila! :D
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    
async def username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = ' '.join(context.args)
    context.user_data['username'] = username
    await persist_data(persistence)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Your username has been set to {}".format(username))

async def password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = ' '.join(context.args)
    context.user_data['password'] = password
    await persist_data(persistence)
    print(persistence.chat_data)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Your password has been set")
    
async def student_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    student_id = ' '.join(context.args)
    context.user_data['student_id'] = student_id
    await persist_data(persistence)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Your student ID has been set to {}".format(student_id))
    
async def login(icheckinCode, context: ContextTypes.DEFAULT_TYPE):
    student_id = context.user_data.get('student_id', None)
    password = context.user_data.get('password', None)
    if (student_id == None or password == None):
        return "Please set your studentID and password first"
    try:
        return Login(student_id, password, icheckinCode)
    except Exception as e:
        return e
    
async def loginCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    icheckinCode = ' '.join(context.args)
    reply = await login(icheckinCode, context)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)
    
async def loginText(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inputMessage = update.message.text
    reply = await login(inputMessage, context)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)
    
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
 
    
def run_bot():    
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    persistence = PicklePersistence(filepath='bot_data')
    
    # application = ApplicationBuilder().token(os.environ["telegram_bot_key"]).build()
    application = Application.builder().token(os.environ["telegram_bot_key"]).persistence(persistence=persistence).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    username_handler = CommandHandler('username', username)
    application.add_handler(username_handler)
    
    student_id_handler = CommandHandler('studentID', student_id)
    application.add_handler(student_id_handler)
    
    password_handler = CommandHandler('password', password)
    application.add_handler(password_handler)
    
    login_handler = CommandHandler('login', loginCommand)
    application.add_handler(login_handler)
    
    login_text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), loginText)
    application.add_handler(login_text_handler)
    
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)
    
    # runs the bot server until interrupted
    application.run_polling()

if __name__ == '__main__':
    run_bot()
    
    
    
# async def main():
#   bot = telegram.Bot(os.environ["telegram_bot_key"])
#   async with bot:
#     # print(await bot.get_me())
#     # print((await bot.get_updates())[0])
#     # await bot.send_message("5144627212", "Hi Shahmir")

def print_pickle_file(path: str):
  objects = []
  with (open(path, "rb")) as openfile:
    while True:
        try:
            objects.append(pickle.load(openfile))
        except EOFError:
            break
  print("objects", objects)