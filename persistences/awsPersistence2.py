from telegram.ext import PicklePersistence
import pickle
import boto3

import copyreg
import pickle
from copy import deepcopy
from pathlib import Path
from sys import version_info as py_ver
from typing import Any, Callable, Dict, Optional, Set, Tuple, Type, TypeVar, cast, overload

from telegram import Bot, TelegramObject
from telegram._utils.types import FilePathInput
from telegram._utils.warnings import warn
from telegram.ext import BasePersistence, PersistenceInput
from telegram.ext._contexttypes import ContextTypes
from telegram.ext._utils.types import BD, CD, UD, CDCData, ConversationDict, ConversationKey

class S3Persistence(PicklePersistence):
  """Overwrites certain functions from the base class
      get_user_data
      update_user_data
      drop_user_data
      flush
      __load_singlefile
      _dump_singlefile
  """
  
  bucket_name = "icheckin-user-data"
  key = "bot_data"
  
  s3 = boto3.resource('s3')
  # bot_data = pickle.loads(s3.Bucket(bucket_name).Object(key).get()['Body'].read())
  
  def _load_singlefile(self) -> None:
    try:
        # with self.filepath.open("rb") as file:
        #     data = super()._BotUnpickler(self.bot, file).load()
            
        bot_data = self.s3.Bucket("icheckin-user-data").Object("bot_data").get()['Body'].read()
        data = super()._BotUnpickler(self.bot, bot_data).load()

        self.user_data = data["user_data"]
        self.chat_data = data["chat_data"]
        # For backwards compatibility with files not containing bot data
        self.bot_data = data.get("bot_data", self.context_types.bot_data())
        self.callback_data = data.get("callback_data", {})
        self.conversations = data["conversations"]
    except OSError:
        self.conversations = {}
        self.user_data = {}
        self.chat_data = {}
        self.bot_data = self.context_types.bot_data()
        self.callback_data = None
    except pickle.UnpicklingError as exc:
        filename = self.filepath.name
        raise TypeError(f"File {filename} does not contain valid pickle data") from exc
    except Exception as exc:
        raise TypeError(f"Something went wrong unpickling {self.filepath.name}") from exc
      
  def _dump_singlefile(self) -> None:
    data = {
      "conversations": self.conversations,
      "user_data": self.user_data,
      "chat_data": self.chat_data,
      "bot_data": self.bot_data,
      "callback_data": self.callback_data,
    }
    with self.filepath.open("wb") as file:
      super().BotPickler(self.bot, file, protocol=pickle.HIGHEST_PROTOCOL).dump(data)