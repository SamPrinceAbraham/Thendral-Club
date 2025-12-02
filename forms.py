from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, FileField, DateField
from wtforms.validators import DataRequired, Length, Email

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    time = StringField('Time')
    description = TextAreaField('Description')
    poster = FileField('Poster')
    submit = SubmitField('Save')

class AnnouncementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Publish')


class MemberForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    role = StringField('Role')
    bio= TextAreaField('Bio')
    photo = FileField('Photo')
    submit = SubmitField('Save')

class AdminLoginForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')
from wtforms import SelectField

class GalleryForm(FlaskForm):
    image = FileField("Image")
    caption = StringField("Caption")
    category = SelectField("Category", choices=[
        ("Sports", "Sports"),
        ("Events", "Events"),
        ("welfare (சமூக நலம்))", "Welfare (சமூக நலம்)"),
        ("Nature", "Nature"),
        ("Uncategorized", "Uncategorized"),
        ("Videos", "Videos")
    ])
    submit = SubmitField("Upload")
