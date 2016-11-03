from app import db
import datetime


class Job(db.Model):
    """
    Used to represent a job in the database
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employer_name = db.Column(db.String())
    employer_email = db.Column(db.String())
    employee = db.Column(db.String(), default=None)
    description = db.Column(db.String())
    compensation = db.Column(db.String())
    location = db.Column(db.String())
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    accept_time = db.Column(db.DateTime, default=None)

    def __repr__(self):
        repr_str = "{}: {}({}) requested someone to {} in {}, with a compensation of {} at {}".format(self.id,
                                                                                         self.employer_name,
                                                                                         self.employer_email,
                                                                                         self.description,
                                                                                         self.location,
                                                                                         self.compensation,
                                                                                         self.timestamp)
        if self.employee:
            return "{}. It was accepted by {} at {}.".format(repr_str, self.employee, self.accept_time)

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

    @staticmethod
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