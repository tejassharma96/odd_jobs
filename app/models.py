from app import db
import datetime


class Job(db.Model):
    """
    Used to represent a job in the database
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.String())
    compensation = db.Column(db.String())
    location = db.Column(db.String())
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    accept_time = db.Column(db.DateTime, default=None)

    employer = db.relationship('User', foreign_keys=[employer_id], backref='submitted_jobs')
    employee = db.relationship('User', foreign_keys=[employee_id], backref='accepted_jobs')

    def __repr__(self):
        repr_str = "{}: {}(group {}) requested someone to {} in {}, with a compensation of {} at {}".format(self.id,
                                                                                         self.employer_id,
                                                                                         self.group_id,
                                                                                         self.description,
                                                                                         self.location,
                                                                                         self.compensation,
                                                                                         self.timestamp)
        if self.employee:
            return "{}. It was accepted by {} at {}.".format(repr_str, self.employee.name, self.accept_time)

        return repr_str


class Category(db.Model):
    """
    Used to represent a category, to allow easy adding of categories by users
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jobs = db.relationship('Job', backref='category', lazy='dynamic')
    name = db.Column(db.String(), index=True, unique=True)
    active = db.Column(db.Boolean, index=True)

    def __repr__(self):
        return "{}: {} (Active: {})".format(self.id, self.name, self.active)


class Group(db.Model):
    """
    Used to represent a groupme group, to allow different groups to be created
    e.g. based on category, location, reward level, work level etc.
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jobs = db.relationship('Job', backref='group', lazy='dynamic')
    bot_name = db.Column(db.String())
    group_name = db.Column(db.String())
    group_id = db.Column(db.Integer, index=True, unique=True)
    bot_id = db.Column(db.String(), index=True)
    active = db.Column(db.Boolean, index=True)
    creator_id = db.Column(db.Integer, default=1, db.ForeignKey('user.id'))
    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_groups')

class User(db.Model):
    """
    Used to represent an employer and store information
    Information will be received using openid
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(), unique=True)
    name = db.Column(db.String())
    email = db.Column(db.String(), unique=True)
    password_hash = db.Column(db.String())

def get_active_categories():
    """
    Gets a dict of active categories
    :return: Said dictionary
    """
    active_list = Category.query.filter_by(active=True).order_by(Category.id)
    return_dict = {}

    for cat in active_list:
        return_dict[cat.id] = cat.name

    return return_dict

def get_active_groups():
    """
    Gets a dict of active groups
    :return: Said dictionary
    """
    active_list = Group.query.filter_by(active=True).order_by(Group.id)
    return_dict = {}

    for group in active_list:
        return_dict[group.id] = group.group_name

    return return_dict