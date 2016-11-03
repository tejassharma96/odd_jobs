from flask import render_template, redirect, url_for, abort, request, flash
from app import app, db, models
from .forms import JobForm


@app.route('/')
@app.route('/index')
def index():
	"""
	The base level of information
	"""
	return render_template("index.html")


@app.route('/job_submit', methods=['GET', 'POST'])
def jobsubmit():
	"""
	The form where the jobs are submitted
	"""

	form = JobForm()
	if form.validate_on_submit():
		job = models.Job(employer_name=form.employer_name.data,
						 employer_email=form.employer_email.data,
						 description=form.description.data,
						 compensation=form.compensation.data,
						 location=form.location.data,
						 category_id=int(form.category.data))
		db.session.add(job)
		db.session.commit()
		return redirect(url_for('submit_success', job_id=job.id))
	else:
		for field, errors in form.errors.items():
			for error in errors:
				print("Error in the {} field - {}".format(getattr(form, field).label.text, error))

	return render_template("job_submit.html",
							form = form)


@app.route('/submit_success/<job_id>')
def submit_success(job_id):
	"""
	The page where a successful submission shows up
	"""

	job = models.Job.query.get(job_id)

	# Make sure the job actually exists
	if job is None:
		abort(404)

	print(job)

	return render_template("submit_success.html",
						   job=job,
						   categories=models.Category.get_active_categories())


@app.errorhandler(404)
def page_not_found(error):
	"""
	404 Error Handler
	"""
	return render_template("404.html"), 404


# ANYTHING BELOW THIS WILL BE DELETED IN THE FINAL VERSION
# THEY ARE JUST HERE FOR TESTING
@app.route('/generic')
def generic():
	return render_template("generic.html")


@app.route('/elements')
def elements():
	return render_template("elements.html")
