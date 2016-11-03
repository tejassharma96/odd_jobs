from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email
from app import models


class JobForm(FlaskForm):
    """
    This is the form that will be used to create a job
    """
    employer_name = StringField('Your Name', validators=[DataRequired()])
    employer_email = StringField('Your Email Address', validators=[DataRequired(), Email()])
    description = TextAreaField('Description', validators=[DataRequired()])
    compensation = StringField('Compensation', validators=[DataRequired()])
    location = StringField('Compensation', validators=[DataRequired()])

    # Get dictionary of active categories
    category_dict = models.Category.get_active_categories()
    # Need to create a list with the string version, since wtf freaks and thinks it's invalid if it's an int
    category_list = [(str(id), category_name) for id, category_name in category_dict.items()]
    category = SelectField('Category', choices=category_list)
