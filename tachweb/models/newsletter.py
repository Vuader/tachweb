from uuid import uuid4
from luxon import database_model
from luxon import SQLModel
from luxon import Uuid
from luxon import Text
from luxon import DateTime
from luxon import Email
from luxon import LongText
from luxon import UniqueIndex
from luxon.utils.timezone import now

EMAILS = [
    (uuid4, 'chris@tachyonic.org', 'Christiaan Rademan', now),
    (uuid4, 'davek@tachyonic.org', 'Dave Kruger', now),
    ]


@database_model()
class newslist(SQLModel):
    id = Uuid(default=uuid4, internal=True)
    email = Email(null=False)
    name = Text()
    creation_time = DateTime(default=now, readonly=True)
    primary_key = id
    unique_email = UniqueIndex(email)
    db_default_rows = EMAILS


@database_model()
class newsletters(SQLModel):
    id = Uuid(default=uuid4, internal=True)
    message = LongText()
    creation_time = DateTime(default=now, readonly=True)
    primary_key = id
