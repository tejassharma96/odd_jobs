from groupy import Bot, Group
from app import db, models

def add_job_to_group(job, group):
    """
    Takes a Job and a Group (as defined in models.py)
    and adds the job to the group
    """
    categories=models.get_active_categories()
    employer = job.employer
    bot = Bot.list().filter(bot_id=group.bot_id).first
    if bot is None or employer is None:
        return False

    message_string = '''Hey everyone! A new job has been posted.
{} would like you to do something.
Location: {}
Description: {}
Compensation: {}
Category: {}
Please visit {} to accept this job'''.format(employer.name,
                                             job.location,
                                             job.description,
                                             job.compensation,
                                             categories[job.category_id],
                                             url_for('accept_job', job_id=job.id, _external=True))
    
    bot.post(message_string)
    return True

def create_group(group_name, creator_id):
    """
    Creates a group, and a bot for that group, and then adds the group to the app database
    """

    new_group = Group.create(group_name, share=True)
    new_bot = Bot.create("JobPostBot", new_group.group_id)
    db_group = models.Group(group_name=new_group.name,
                            group_id=new_group.group_id,
                            bot_name=new_bot.name,
                            bot_id=new_bot.bot_id,
                            active=True,
                            creator_id=creator_id)
    db.session.add(db_group)
    db.session.commit()

def get_group_share_url(group):
    """
    Takes a group from the models module, and returns the share url for that module
    """

    # Get group and make sure it exists
    group = Group.list().filter(group_id=group.group_id).first
    if group is None:
        return False

    # If the share url doesn't exist, generate it
    if group.share_url is None:
        group.update(share=True)

    return group.share_url