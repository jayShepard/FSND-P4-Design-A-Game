#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import MineSweeperApi

from models import User


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with unfinished games to come play
        . Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        games = Game.query(Game.game_over == False)
        users = []
        for game in games:
            user = User.query(User.name == game.user)
            if user.email:
                users.append(user)

        for user in users:
            subject = 'This is a reminder!'
            body = 'Hello {}, come finish your game!'.format(user.name)
            # This will send test emails, the arguments to send_mail are:
            # from, to, subject, body
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)


class UpdateAverageTilesRemaining(webapp2.RequestHandler):
    def post(self):
        """Update game listing announcement in memcache."""
        MineSweeperApi._cache_average_tiles()
        self.response.set_status(204)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_average_tiles', UpdateAverageTilesRemaining),
], debug=True)
