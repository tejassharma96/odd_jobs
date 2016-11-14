import groupy
from app import models

class Bot:
    """
    This class will be used as a sort of wrapper for the API
    It will be used to interact with the groups
    """

    def __init__(self, bot_id):
        """
        Initializes the bot from a bot id
        Raises a ValueError if no bot with the specified id exists
        """

        self.db_group = models.Group.query
                        .filter_by(bot_id=bot_id)
                        .filter_by(active=True)
                        .first()

        if self.db_group is None:
            raise ValueError('No active group exists in the db with the specified bot id')

        self.bot = groupy.Bot.list().filter(bot_id==bot_id)
        if self.bot is None:
            raise ValueError('No bot exists for the user with the specified bot id')

        self.group = groupy.Group.list().filter(group_id==self.bot.group_id)

