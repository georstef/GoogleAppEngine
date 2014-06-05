# coding: utf-8

from datetime import datetime
from google.appengine.ext import ndb
import hashlib
import iso


class Config(object):
  @classmethod
  def get_master_db(cls):
    return cls.get_or_insert('master')

  @property
  def has_facebook(self):
    return bool(self.facebook_app_id and self.facebook_app_secret)

  @property
  def has_twitter(self):
    return bool(self.twitter_consumer_key and self.twitter_consumer_secret)


class User(object):
  def has_permission(self, perm):
    return self.admin or perm in self.permissions

  def avatar_url_size(self, size=None):
    return '//gravatar.com/avatar/%(hash)s?d=identicon&r=x%(size)s' % {
        'hash': hashlib.md5(self.email or self.username).hexdigest(),
        'size': '&s=%d' % size if size > 0 else '',
      }
  avatar_url = property(avatar_url_size)


class TournamentX(object):
  @ndb.ComputedProperty
  def country_name(self):
    if self.country in iso.ISO_3166:
      return iso.ISO_3166[self.country]
    return 'N/A'

  @ndb.ComputedProperty
  def full_address(self):
    return ', '.join(x for x in [self.address, self.city, self.country_name] if x and x != 'N/A')

  @ndb.ComputedProperty
  def is_past(self):
    return self.timestamp < datetime.now()
