import os
import unittest
import logging
import sys
import time

from config import basedir
from app import app, db
from app.models import Job, Category


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

    def create_job(self, employer_name, employer_email, compensation, location, description, category_id):
        """
        Mocks creating a new job through the website
        """

        data_dict = {'employer_name': employer_name,
                     'employer_email': employer_email,
                     'compensation': compensation,
                     'location': location,
                     'description': description,
                     'category_id': str(category_id)}
        return self.app.post('/job_submit', data=data_dict, follow_redirects=True)

    def test_new_job(self):
        self.create_job('Tejas', 'tejas.s1996@gmail.com', 'nothing lol', 'here', 'description', 1)

        job_0 = Job.query.filter_by(description='description').first()
        job_1 = Job.query.filter_by(description='different description').first()

        self.assertTrue(job_0)
        self.assertEqual(None, job_1)
        self.assertEqual(job_0.description, 'Tejas')
        self.assertEqual(job_0.category_id, 1)

    def test_sql_injection(self):
        """
        Test against basic SQL injection attacks (invalidated due to methodology of SQLAlchemy)
        """

        self.create_job('Tejas', 'tejas.s1996@gmail.com', '1;DROP TABLE Job', 'here', 'description', 1)
        comment = Comment.query.filter_by(compensation="1;DROP TABLE Job").first()
        self.assertTrue(comment)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("TestDatabase.test_reply_post").setLevel(logging.DEBUG)
    unittest.main()
