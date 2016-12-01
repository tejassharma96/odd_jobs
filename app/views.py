from flask import render_template, redirect, url_for, abort, request, session, flash, jsonify
from app import app, db, models, emails, groupme, forms
import hashlib
import groupy
import datetime


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

	# Create the form and set up validation
	form = forms.JobForm()
	forms.repopulate_group(form)
	forms.repopulate_categories(form)
	
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
		groupme.add_job_to_group(job, group)
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

	# Just redirect them to index if they are already logged in
	user = models.User.query.get(session['user_id']) if 'user_id' in session else None
	if user is not None:
		return redirect(url_for('index'))

	form = forms.LoginForm()
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

	# Just redirect them to index if they are already logged in
	user = models.User.query.get(session['user_id']) if 'user_id' in session else None
	if user is not None:
		return redirect(url_for('index'))

	form = forms.SignupForm()
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
			flash("A user with than username or email already exists")
			abort(409)
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
	return render_template("accepted_jobs.html",
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
			'accept_job': 'accept a job',
			'create_group': 'create a group',
			'request_add': 'request to be added to a group'
	}
	reason_str = reasons_dict[reason] if reason in reasons_dict else None

	if reason_str is None:
		abort(404)

	return render_template('login_required.html',
						   reason=reason_str,
						   logged_in='user_id' in session)

@app.route('/accept_job/<job_id>', methods=['GET', 'POST'])
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

	form = forms.AcceptForm()
	if form.validate_on_submit():
		# Edit job before sending email
		job.employee_id = user.id
		job.accept_time = datetime.datetime.utcnow()
		emails.send_job_email(job)
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


@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
	"""
	Uses a form to get the name of a group and then creates that group
	"""

	user = models.User.query.get(session['user_id']) if 'user_id' in session else None
	if user is None:
		return redirect(url_for('login_required', reason='create_group'))

	form = forms.GroupForm()
	if form.validate_on_submit():
		groupme.create_group(form.name.data, user.id)
		return redirect(url_for('request_add'))

	return render_template('create_group.html',
						   form=form,
						   logged_in='user_id' in session)

@app.route('/request_add', methods=['GET', 'POST'])
def request_add():
	"""
	Uses a drop-down to get the name of the group to be added to, generates a join url
	"""

	user = models.User.query.get(session['user_id']) if 'user_id' in session else None
	if user is None:
		return redirect(url_for('login_required', reason='request_add'))

	form = forms.JoinGroupForm()
	forms.repopulate_group(form)
	if form.validate_on_submit():
		return redirect(url_for('join_group_redirect', group_id=form.group.data))

	return render_template('request_add.html',
						   form=form,
						   logged_in='user_id' in session)

@app.route('/join_group_redirect/<group_id>')
def join_group_redirect(group_id):
	"""
	Redirects to the share url
	"""

	group_id = int(group_id)
	group = models.Group.query.get(group_id)
	if group is None:
		print('couldn\'t get group')
		abort(404)

	share_url = groupme.get_group_share_url(group)
	return render_template('join_group_redirect.html',
						   url=share_url)


@app.route('/create_category', methods=['GET', 'POST'])
def create_category():
	"""
	Uses a form to get the name of a category and then creates that category
	"""

	user = models.User.query.get(session['user_id']) if 'user_id' in session else None
	if user is None:
		return redirect(url_for('login_required', reason='create_category'))

	# Use the same form as a group as it's the same info; just a name
	form = forms.GroupForm()
	if form.validate_on_submit():
		category = models.Category(name=form.name.data, active=True)
		try:
			db.session.add(category)
			db.session.commit()
		except sqlalchemy.exc.IntegrityError:
			flash("A category with than name already exists")
			abort(409)
		return redirect(url_for('job_submit'))

	return render_template('create_category.html',
						   form=form,
						   logged_in='user_id' in session)	


@app.errorhandler(404)
def page_not_found(error):
	"""
	404 Error Handler
	"""
	return render_template("404.html"), 404


@app.errorhandler(409)
def page_not_found(error):
	"""
	409 Error Handler
	"""
	return render_template("409.html"), 409


@app.errorhandler(500)
def internal_error(error):
	"""
	500 Error Handler
	"""
	db.session.rollback()
	return render_template('500.html'), 500