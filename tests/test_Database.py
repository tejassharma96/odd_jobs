import os
import unittest
import logging
import sys
import time

from config import basedir
from app import app, db
from app.models import Job, Category, User


class TestDatabase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_job(self, employer_id, compensation, location, description, category_id, group_id):
        """
        Mocks creating a new job through the website
        """

        data_dict = {'employer_id': employer_id,
                     'group_id': group_id,
                     'compensation': compensation,
                     'location': location,
                     'description': description,
                     'category_id': str(category_id)}
        return self.app.post('/job_submit', data=data_dict, follow_redirects=True)

    def create_user(self, username, password, email, name):
        """
        Mocks creating a new user through the website
        """

        data_dict = {'username': username,
                     'password': password,
                     'email': email,
                     'name': name}
        return self.app.post('/signup', data=data_dict, follow_redirects=True)

    def create_category(self, category_name):
        """
        Creates a new category
        Currently no way to do this in the website
        """
        
        category = Category(name=category_name, active=True)
        db.session.add(category)
        db.session.commit()

    def test_new_job(self):
        self.create_category('Category')
        self.create_user('teja', 'bean', 'tejas.s1996@gmail.com', 'Tejas')
        self.create_job(1, 'nothing lol', 'here', 'description', 1, 1)

        job_0 = Job.query.filter_by(description='description').first()
        job_1 = Job.query.filter_by(description='different description').first()

        self.assertTrue(job_0)
        self.assertEqual(None, job_1)
        self.assertEqual(job_0.description, 'Tejas')
        self.assertEqual(job_0.category_id, 1)

    def test_user_association(self):
        self.create_category('Category')
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
        
        self.create_category('Category')
        self.create_user('teja', 'bean', 'tejas.s1996@gmail.com', 'Tejas')
        self.create_job(1, '1;DROP TABLE Job', 'here', 'description', 1, 1)
        job = Job.query.filter_by(compensation="1;DROP TABLE Job").first()
        self.assertTrue(job)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("TestDatabase.test_reply_post").setLevel(logging.DEBUG)
    unittest.main()
