import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from slugify import slugify

from peewee import *


DATABASE = SqliteDatabase('record.db')


class User(UserMixin, Model):
    """Model for user
    INHERIT:
        UserMixin from flask_login
        Model from peewee
    """
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    def get_entry(self):
        """Select user from the database
        RETURNS:
            user which equals with the object instance
        """
        return Entry.select().where(Entry.user == self)

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        """User classmethod which creates an user, if user exist it will raise a valuer error
        INPUT:
            object instance(self)
            username
            email address
            password - hashes password with generate_password_hash from flask_bcrypt
            admin - default=False
        """
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin
                )
        except IntegrityError:
            raise ValueError("User already exist!")


class Entry(Model):
    """Model for entry(post), related to User Model
    INHERIT:
        Model from peewee
    """
    title = CharField(max_length=255)
    duration = IntegerField()
    content = TextField()
    resources = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)
    slug = CharField(unique=True)
    user = ForeignKeyField(
        User, related_name='entries'
    )

    class Meta:
        database = DATABASE
        order_by = ('-created_at',)

    @classmethod
    def create_entry(cls, title, duration, content, resources, created_at, user):
        """Entry classmethod which creates an user, if user exist it will raise a value error
            Slugifies title
        INPUT:
             title
             duration (time_spent)
             content (what you learned)
             resources (resources to remember)
             created_at (date)
             user - related to User Model
        """
        slug = slugify(title)
        slugs = []
        for x in cls.select(cls.slug).where(cls.slug.contains(slug)):
            slugs.append(x.slug)
        if slugs:
            slug_check = slug
            slug_number = 1
            while slug_check in slugs:
                slug_check = slug + str(slug_number)
                slug_number += 1
            slug = slug_check
        cls.create(title=title,
                   duration=duration,
                   content=content,
                   resources=resources,
                   created_at=created_at,
                   user=user,
                   slug=slug)

    def get_tags(self):
        """
        RETURNS:
             a peewee model select with all of the entry's tags
        """
        # noinspection PyUnresolvedReferences
        tags = (Tag.select()
                .join(EntryTag)
                .join(Entry)
                .where(Entry.id == self.id))
        return tags


class Tag(Model):
    """Model for tag
    INHERIT:
        Model from peewee
    """
    name = CharField(max_length=100)

    class Meta:
        database = DATABASE
        order_by = ('name',)


class EntryTag(Model):
    """Model for entry tag
        Holds the relationship between entries and tags
    INHERIT:
        Model from peewee
    """
    entry = ForeignKeyField(Entry, related_name='entries')
    tag = ForeignKeyField(Tag, related_name='tags')

    class Meta:
        database = DATABASE


def initialize():
    """Initialize the database
        Creates tables after close it
    """
    DATABASE.connect()
    DATABASE.create_tables([User, Entry, EntryTag, Tag], safe=True)
    DATABASE.close()
