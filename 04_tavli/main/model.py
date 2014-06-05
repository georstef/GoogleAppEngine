# coding: utf-8

from google.appengine.ext import ndb

import config
import modelq
import modelx
import util
import iso


class Base(ndb.Model, modelq.Base):
  created = ndb.DateTimeProperty(auto_now_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)
  version = ndb.IntegerProperty(default=config.CURRENT_VERSION_TIMESTAMP)

  _PROPERTIES = {
      'key',
      'id',
      'version',
      'created',
      'modified',
    }


class Config(Base, modelx.Config):
  analytics_id = ndb.StringProperty(default='')
  announcement_html = ndb.TextProperty(default='')
  announcement_type = ndb.StringProperty(default='info', choices=[
      'info', 'warning', 'success', 'danger',
    ])
  brand_name = ndb.StringProperty(default=config.APPLICATION_ID)
  facebook_app_id = ndb.StringProperty(default='')
  facebook_app_secret = ndb.StringProperty(default='')
  feedback_email = ndb.StringProperty(default='')
  flask_secret_key = ndb.StringProperty(default=util.uuid())
  notify_on_new_user = ndb.BooleanProperty(default=True)
  twitter_consumer_key = ndb.StringProperty(default='')
  twitter_consumer_secret = ndb.StringProperty(default='')
  google_public_api_key = ndb.StringProperty(default='')

  _PROPERTIES = Base._PROPERTIES.union({
      'analytics_id',
      'announcement_html',
      'announcement_type',
      'brand_name',
      'facebook_app_id',
      'facebook_app_secret',
      'feedback_email',
      'flask_secret_key',
      'notify_on_new_user',
      'twitter_consumer_key',
      'twitter_consumer_secret',
      'google_public_api_key',
    })


class User(Base, modelx.User, modelq.User):
  name = ndb.StringProperty(required=True)
  username = ndb.StringProperty(required=True)
  email = ndb.StringProperty(default='')
  birthdate = ndb.DateProperty()
  auth_ids = ndb.StringProperty(repeated=True)
  active = ndb.BooleanProperty(default=True)
  admin = ndb.BooleanProperty(default=False)
  permissions = ndb.StringProperty(repeated=True)

  _PROPERTIES = Base._PROPERTIES.union({
      'active',
      'admin',
      'auth_ids',
      'avatar_url',
      'email',
      'birthdate',
      'name',
      'username',
      'permissions',
    })


class Tournament(Base, modelx.TournamentX):
  user_key = ndb.KeyProperty(kind=User, required=True)
  name = ndb.StringProperty(required=True)
  type = ndb.StringProperty(default='single-elimination', choices=['single-elimination', 'double-elimination'])
  timestamp = ndb.DateTimeProperty(default='')
  place = ndb.StringProperty(default='')
  address = ndb.StringProperty(default='')
  city = ndb.StringProperty(default='')
  country = ndb.StringProperty(default='', choices=iso.ISO_3166.keys())
  rules = ndb.TextProperty(default='')
  is_closed = ndb.BooleanProperty(default=False)
  is_public = ndb.BooleanProperty(default=False)

  _PROPERTIES = Base._PROPERTIES.union({
      'name',
      'type',
      'timestamp',
      'place',
      'address',
      'city',
      'country',
      'rules',
      'is_closed',
      'is_public',
    })
