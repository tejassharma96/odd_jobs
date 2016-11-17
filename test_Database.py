from config import basedir
from app import app, db
from app.models import Job, Category, User, Group

from flask import Flask
from flask_testing import TestCase
import unittest
import os
import logging
import sys
import time

class TestDatabase(TestCase):

    def create_app(self):

        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        return app

    def setUp(self):

        db.create_all()
        duplicate_check = Group.query.filter_by(bot_name='OddJobBot').first()
        if duplicate_check is not None:
            return
        group = Group(bot_name='OddJobBot', group_name='oddjobs', group_id=26687080, bot_id='41a362cc6509e68c26a9483529', active=True)
        db.session.add(group)
        db.session.commit()

    def tearDown(self):

        db.session.remove()
        db.drop_all()

    def create_job(self, employer_id, compensation, location, description, category_id, group_id):
        """
        Creates a new job and adds it to the db
        """

        job = Job(employer_id=employer_id, group_id=group_id, compensation=compensation, location=location, category_id=category_id, description=description) 
        db.session.add(job)
        db.session.commit()

    def create_user(self, username, password, email, name):
        """
        Creates a new job and adds  it to the db
        """

        duplicate_check = User.query.filter_by(username=username).first()
        if duplicate_check is not None:
            return
        user = User(username=username, password=password, email=email, name=name)
        db.session.add(user)
        db.session.commit()

    def create_category(self, category_name):
        """
        Creates a new category and adds it to the db
        """
        
        duplicate_check = Category.query.filter_by(name=category_name).first()
        if duplicate_check is not None:
            return
        category = Category(name=category_name, active=True)
        db.session.add(category)
        db.session.commit()

    def test_new_job(self):
        self.create_category('Gardening')
        self.create_user('teja', 'bean', 'tejas.s1996@gmail.com', 'Tejas')
        self.create_job(1, 'nothing lol', 'here', 'description', 1, 1)

        job_0 = Job.query.filter_by(description='description').first()
        job_1 = Job.query.filter_by(description='different description').first()

        self.assertTrue(job_0)
        self.assertEqual(None, job_1)
        self.assertEqual(job_0.description, 'Tejas')
        self.assertEqual(job_0.category_id, 1)

    def test_user_association(self):
        self.create_category('Gardening')
        self.create_user('teja', 'bean', 'tejas.s1996@gmail.com', 'Tejas')
        self.create_job(1, 'nothing lol', 'here', 'description', 1, 1)
        
        job_0 = Job.query.filter_by(description='description').first()
        teja = User.query.filter_by(username='username').first()

        self.assertTrue(job_0)
        self.assertTrue(teja)

        job_1 = teja.submitted_jobs.first()
        self.assertTrue(job_1)
        self.assertEqual(job_0.description, job_1.description)

    def test_sql_injection(self):
        """
        Test against basic SQL injection attacks (invalidated due to methodology of SQLAlchemy)
        """

        self.create_job('Tejas', 'tejas.s1996@gmail.com', '1;DROP TABLE Job', 'here', 'description', 1)
        comment = Comment.query.filter_by(compensation="1;DROP TABLE Job").first()
        self.assertTrue(comment)

if __name__ == '__main__':
    unittest.main()