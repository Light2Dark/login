import boto3
from telegram.ext import BasePersistence

class awsPersistence(BasePersistence):
  s3 = boto3.client("s3")
  bot_data = s3.get_object(Bucket="icheckin-user-data", Key="bot_data")
  
  async def get_user_data(self) -> Dict[int, UD]:
    return await super().get_user_data()
  
  async def get_bot_data(self):
    pass
  
  async def update_bot_data(self, data):
    pass
  
  async def refresh_bot_data(self, bot_data):
    pass
  
  async def get_chat_data(self):
    pass
  
  async def update_chat_data(self, chat_id: int, data: CD):
    pass
  
  async def refresh_chat_data(self, chat_id: int, chat_data):
    pass
  
  async def drop_chat_data(self, chat_id: int) -> None:
    pass
  
  async def get_callback_data(self):
    pass
  
  async def update_callback_data(self, data):
    pass
  
  async def get_conversations(self, name: str):
    pass
  
  async def update_conversation(self, name: str, key, new_state) -> None:
    pass
  
  async def flush(self) -> None:
    return await super().flush()