# coding: utf-8

from __future__ import absolute_import

from datetime import datetime

from google.appengine.ext import ndb

import iso
import model


class Tournament(model.Base):
  user_key = ndb.KeyProperty(kind=model.User, required=True)
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

  _PROPERTIES = model.Base._PROPERTIES.union({
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
