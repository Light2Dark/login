from telegram_bot import start, username, password, student_id, loginCommand, loginText, unknown, storage_path, get_db, update_db, print_pickle_file, create_bot
from telegram import Update
import json
import asyncio
from telegram.ext import CommandHandler, MessageHandler, filters
import base64
from dotenv import load_dotenv
import os
load_dotenv()
import logging

# logging
logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level=logging.INFO
)
logging.getLogger().setLevel(logging.INFO)

def lambda_handler(event, context):
  get_db()  # pull from S3 and load to local file
  application = create_bot() # create a persistent telegram bot
  return asyncio.get_event_loop().run_until_complete(main(event, context, application))

async def main(event, context, application):  
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
  
  try:    
    await application.initialize()
    code_string = event["body"]
    decoded = base64.b64decode(code_string)
    
    await application.process_update(
        Update.de_json(json.loads(decoded), application.bot)
    )

    return {
        'statusCode': 200,
        'body': 'Success'
    }

  except Exception as exc:
    print("ERROR", exc)
    return {
        'statusCode': 500,
        'body': 'Failure: ' + str(exc)
  } 
  
  finally:
    update_db()
    print_pickle_file(storage_path)