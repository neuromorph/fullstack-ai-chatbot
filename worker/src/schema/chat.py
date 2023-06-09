from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
import uuid

class Message(BaseModel):
    id = str(uuid.uuid4())
    msg: str
    source: str
    timestamp = str(datetime.now())