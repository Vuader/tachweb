from uuid import uuid4
from luxon import register
from luxon import SQLModel
from luxon.utils.timezone import now

EMAILS = [
    (uuid4, 'chris@tachyonic.org', 'Christiaan Rademan', now),
    (uuid4, 'davek@tachyonic.org', 'Dave Kruger', now),
    ]


@register.model()
class NewsList(SQLModel):
    id = SQLModel.Uuid(default=uuid4, internal=True)
    email = SQLModel.Email(null=False)
    name = SQLModel.Text()
    creation_time = SQLModel.DateTime(default=now, readonly=True)
    primary_key = id
    unique_email = SQLModel.UniqueIndex(email)
    db_default_rows = EMAILS


@register.model()
class NewsLetters(SQLModel):
    id = SQLModel.Uuid(default=uuid4, internal=True)
    message = SQLModel.LongText()
    creation_time = SQLModel.DateTime(default=now, readonly=True)
    primary_key = id
