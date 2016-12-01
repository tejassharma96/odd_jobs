from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email
from app import models


class JobForm(FlaskForm):
    """
    This is the form that will be used to create a job
    """
    description = TextAreaField('Description', validators=[DataRequired()])
    compensation = StringField('Compensation', validators=[DataRequired()])
    location = StringField('Compensation', validators=[DataRequired()])

    # Get dictionary of active categories
    category_dict = models.get_active_categories()
    # Need to create a list with the string version, since wtf freaks and thinks it's invalid if it's an int
    category_list = [(str(id), category_name) for id, category_name in category_dict.items()]

    category = SelectField('Category', choices=category_list)

    # Do the same for groups
    group_dict = models.get_active_groups()
    group_list = [(str(id), group_name) for id, group_name in group_dict.items()]

    group = SelectField('Group', choices=group_list)

class LoginForm(FlaskForm):
    """
    This is the form that will be used to log in
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class SignupForm(FlaskForm):
    """
    This is the form that will be used to sign up
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class AcceptForm(FlaskForm):
    """
    This is the form an employee has to fill out to accept a job
    """
    confirm = BooleanField('Confirm', validators=[DataRequired()])

class GroupForm(FlaskForm):
    """
    This is the form someone has to fill out to create a group
    """
    name = StringField('Name', validators=[DataRequired()])

class JoinGroupForm(FlaskForm):
    """
    This is the dropdown for selecting a group to join
    """
    group_dict = models.get_active_groups()
    group_list = [(str(id), group_name) for id, group_name in group_dict.items()]

    group = SelectField('Group', choices=group_list)

def repopulate_group(form):
    """
    Updates the group field in a form from the database
    """
    group_dict = models.get_active_groups()
    group_list = [(str(id), group_name) for id, group_name in group_dict.items()]

    form.group.choices = group_list

def repopulate_categories(form):
    """
    Updates the category field in a form from the database
    """
    category_dict = models.get_active_categories()
    category_list = [(str(id), category_name) for id, category_name in category_dict.items()]

    form.category.choices = category_list
