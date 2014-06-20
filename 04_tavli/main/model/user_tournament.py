# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

import model


class UserTournament(model.Base):
  user_key = ndb.KeyProperty(kind=model.User, required=True)
  tournament_key = ndb.KeyProperty(kind=model.Tournament, required=True)
  position = ndb.IntegerProperty(default=0)
