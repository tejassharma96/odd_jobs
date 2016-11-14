from flask import render_template, redirect, url_for, abort, request, session, flash
from app import app, db, models
from .forms import JobForm, LoginForm, SignupForm, AcceptForm
import hashlib
import groupy


@app.route('/')
@app.route('/index')
def index():
	"""
	The base level of information
	"""
	return render_template("index.html",
						   logged_in='user_id' in session)


@app.route('/job_submit', methods=['GET', 'POST'])
def job_submit():
	"""
	The form where the jobs are submitted
	"""

	user = models.User.query.get(session['user_id']) if 'user_id' in session else None
	if user is None:
		return redirect(url_for('login_required', reason='job_submit'))

	form = JobForm()
	if form.validate_on_submit():
		job = models.Job(employer_id=user.id,
						 group_id=int(form.group.data),
						 description=form.description.data,
						 compensation=form.compensation.data,
						 location=form.location.data,
						 category_id=int(form.category.data))
		db.session.add(job)
		db.session.commit()
		group = models.Group.query.get(job.group_id)
		add_job_to_group(job, group)
		return redirect(url_for('job_info', job_id=job.id))
	else:
		for field, errors in form.errors.items():
			for error in errors:
				print("Error in the {} field - {}".format(getattr(form, field).label.text, error))

	return render_template("job_submit.html",
						   form=form,
						   logged_in='user_id' in session)


@app.route('/job_info/<job_id>')
def job_info(job_id):
	"""
	The page where a successful submission shows up
	"""

	job = models.Job.query.get(job_id)

	# Make sure the job actually exists
	if job is None:
		flash("No job with that id")
		abort(404)


	employer = models.User.query.get(job.employer_id)

	return render_template("job_info.html",
						   job=job,
						   categories=models.get_active_categories(),
						   employer=employer,
						   logged_in='user_id' in session)


@app.route('/login', methods=['GET', 'POST'])
def login():
	"""
	The login page
	"""

	form = LoginForm()
	if form.validate_on_submit():
		username = form.username.data
		password_hash = hashlib.sha256(form.password.data.encode()).hexdigest()
		user = models.User.query.filter_by(username=username).filter_by(password_hash=password_hash).first()
		if user is None:
			flash('Login failed, please recheck your username and password')
			return redirect(url_for('login'))
		else:
			session['user_id'] = user.id
			return redirect(url_for('submitted_jobs'))

	return render_template("login.html",
						   form=form,
						   logged_in='user_id' in session)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
	"""
	The signup page
	"""

	form = SignupForm()
	if form.validate_on_submit():
		user = models.User(username=form.username.data,
						   password_hash = hashlib.sha256(form.password.data.encode()).hexdigest(),
						   email = form.email.data,
						   name = form.name.data)
		db.session.add(user)
		try:
			db.session.commit()
			session['user_id'] = user.id
		except sqlalchemy.exc.IntegrityError:
			print('u idiot')
		return redirect(url_for('index'))

	return render_template("signup.html",
						   form=form,
						   logged_in='user_id' in session)


@app.route('/submitted_jobs')
def submitted_jobs():
	"""
	Shows the status of all submitted jobs
	"""

	user = models.User.query.get(session['user_id']) if 'user_id' in session else None
	if user is None:
		return redirect(url_for('login_required', reason='submitted_jobs'))
	
	jobs = user.submitted_jobs
	return render_template("submitted_jobs.html",
						   user=user,
						   jobs=jobs,
						   logged_in='user_id' in session)

@app.route('/accepted_jobs')
def accepted_jobs():
	"""
	Shows the status of all submitted jobs
	"""

	user = models.User.query.get(session['user_id']) if 'user_id' in session else None
	if user is None:
		return redirect(url_for('login_required', reason='submitted_jobs'))
	
	jobs = user.accepted_jobs
	return render_template("submitted_jobs.html",
						   user=user,
						   jobs=jobs,
						   logged_in='user_id' in session)


@app.route('/login_required/<reason>')
def login_required(reason):
	"""
	Shows a login required page with a basic message
	"""

	reasons_dict = {
			'job_submit': 'submit a job',
			'submitted_jobs': 'view your submitted jobs',
			'logout': 'logout',
			'accept_job': 'accept a job'
	}
	reason_str = reasons_dict[reason] if reason in reasons_dict else None

	if reason_str is None:
		abort(404)

	return render_template('login_required.html',
						   reason=reason_str,
						   logged_in='user_id' in session)

@app.route('/accept_job/<job_id>')
def accept_job(job_id):
	"""
	Shows a page to accept a job
	"""

	user = models.User.query.get(session['user_id']) if 'user_id' in session else None
	if user is None:
		return redirect(url_for('login_required', reason='accept_job'))

	job = models.Job.query.get(job_id)

	# Make sure the job actually exists
	if job is None:
		flash("No job with that id")
		abort(404)

	form = AcceptForm()
	if form.validate_on_submit():
		job.employee_id = user.id
		db.session.commit()

	return render_template('accept_job.html',
						   form=form,
						   job=job,
						   categories=models.get_active_categories(),
						   user=user,
						   employer=job.employer,
						   accepted=job.employee is not None,
						   logged_in='user_id' in session)

@app.route('/logout')
def logout():
	"""
	Log out the current user
	"""

	if 'user_id' in session:
		session.pop('user_id', None)
		return render_template('logout.html',
							   logged_in='user_id' in session)
	else:
		return redirect(url_for('login_required', reason='logout'))


@app.errorhandler(404)
def page_not_found(error):
	"""
	404 Error Handler
	"""
	return render_template("404.html"), 404

def add_job_to_group(job, group):
	"""
	Takes a Job and a Group (as defined in models.py)
	and adds the job to the group
	"""
	categories=models.get_active_categories()
	employer = models.User.query.get(job.employer_id)
	bot = groupy.Bot.list().filter(bot_id=group.bot_id).first
	if bot is None or employer is None:
		return False

	message_string = '''Hey everyone! A new job has been posted.
{} would like you to do something.
Location: {}
Description: {}
Compensation: {}
Category: {}
Please visit 127.0.0.1:5000{} to accept this job'''.format(employer.name,
					  						 job.location,
					  						 job.description,
					  						 job.compensation,
					  						 categories[job.category_id],
					  						 url_for('accept_job', job_id=job.id))
	
	bot.post(message_string)
	return True

# ANYTHING BELOW THIS WILL BE DELETED IN THE FINAL VERSION
# THEY ARE JUST HERE FOR TESTING
@app.route('/generic')
def generic():
	return render_template("generic.html")


@app.route('/elements')
def elements():
	return render_template("elements.html")

