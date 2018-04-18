from flask_wtf import Form
from wtforms import (StringField, IntegerField, TextAreaField,
                     PasswordField, DateTimeField, SelectMultipleField)
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)

from models import User


# noinspection PyUnusedLocal
def name_exists(form, field):
    """Checks if username already exist in database
    INPUT:
        form
        field
    """
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')


# noinspection PyUnusedLocal
def email_exists(form, field):
    """Checks if email already exist in database
    INPUT:
        form
        field
    """
    if User.select().where(User.email == field.data).exists():
        raise ValidationError("User with that email already exists.")


class RegisterForm(Form):
    """Form to register user
    INHERIT:
        Form from flask_wtf
    """
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, "
                         "numbers, and underscores only.")
            ),
            name_exists
        ])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6),
            EqualTo('password2', message='Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )


class LoginForm(Form):
    """Form to login user
    INHERIT:
        Form from flask_wtf
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class PostEntryForm(Form):
    """Form to post entry
    INHERIT:
        Form from flask_wtf
    """
    title = StringField('Title', validators=[DataRequired()])
    duration = IntegerField("Time spent", validators=[DataRequired()])
    content = TextAreaField('What you learned?', validators=[DataRequired()])
    resources = TextAreaField('Resources to remember', validators=[DataRequired()])
    created_at = DateTimeField(
        'Date (MM/DD/YYYY)',
        validators=[DataRequired()],
        format="%m/%d/%Y"
    )


class TagForm(Form):
    """Form for Tag
    INHERIT:
        Form from flask_wtf
    """
    name = StringField('Tag Name')


class EntryTagForm(Form):
    """Form for entry Tag
    INHERIT:
        Form from flask_wtf
    """
    tags = SelectMultipleField('Tags', coerce=int)


class RemoveEntryForm(Form):
    pass