# coding: utf-8

from flask.ext import wtf
from google.appengine.api import app_identity
from google.appengine.ext import ndb
import flask

import auth
import config
import model
import util

from main import app


class ConfigUpdateForm(wtf.Form):
  analytics_id = wtf.StringField('Tracking ID', filters=[util.strip_filter])
  announcement_html = wtf.TextAreaField('Announcement HTML', filters=[util.strip_filter])
  announcement_type = wtf.SelectField('Announcement Type', choices=[(t, t.title()) for t in model.Config.announcement_type._choices])
  brand_name = wtf.StringField('Brand Name', [wtf.validators.required()], filters=[util.strip_filter])
  facebook_app_id = wtf.StringField('App ID', filters=[util.strip_filter])
  facebook_app_secret = wtf.StringField('App Secret', filters=[util.strip_filter])
  feedback_email = wtf.StringField('Feedback Email', [wtf.validators.optional(), wtf.validators.email()], filters=[util.email_filter])
  flask_secret_key = wtf.StringField('Secret Key', [wtf.validators.optional()], filters=[util.strip_filter])
  notify_on_new_user = wtf.BooleanField('Send an email notification when a user signs up')
  twitter_consumer_key = wtf.StringField('Consumer Key', filters=[util.strip_filter])
  twitter_consumer_secret = wtf.StringField('Consumer Secret', filters=[util.strip_filter])
  google_public_api_key = wtf.StringField('Public API key', filters=[util.strip_filter])


@app.route('/_s/admin/config/', endpoint='admin_config_update_service')
@app.route('/admin/config/', methods=['GET', 'POST'])
@auth.admin_required
def admin_config_update():
  config_db = model.Config.get_master_db()
  form = ConfigUpdateForm(obj=config_db)
  if form.validate_on_submit():
    form.populate_obj(config_db)
    if not config_db.flask_secret_key:
      config_db.flask_secret_key = util.uuid()
    config_db.put()
    reload(config)
    app.config.update(CONFIG_DB=config_db)
    return flask.redirect(flask.url_for('welcome'))

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_db(config_db)

  instances_url = None
  if config.PRODUCTION:
    instances_url = '%s?app_id=%s&version_id=%s' % (
        'https://appengine.google.com/instances',
        app_identity.get_application_id(),
        config.CURRENT_VERSION_ID,
      )

  return flask.render_template(
      'admin/config_update.html',
      title='Admin Config',
      html_class='admin-config',
      form=form,
      config_db=config_db,
      instances_url=instances_url,
      has_json=True,
    )


###############################################################################
# Helpers
###############################################################################
@app.route('/_s/admin/tournament/update/')
@auth.admin_required
def admin_tournament_update():
  tournament_dbs, tournament_cursor = util.get_dbs(
      model.Tournament.query(),
      limit=util.param('limit', int) or config.DEFAULT_DB_LIMIT,
      order=util.param('order'),
      cursor=util.param('cursor'),
    )

  ndb.put_multi(tournament_dbs)
  return util.jsonify_model_dbs(tournament_dbs, tournament_cursor)


@app.route('/_s/admin/user/update/')
@auth.admin_required
def admin_user_update():
  user_dbs, user_cursor = util.get_dbs(
      model.User.query(),
      limit=util.param('limit', int) or config.DEFAULT_DB_LIMIT,
      order=util.param('order'),
      cursor=util.param('cursor'),
    )

  updated_dbs = []
  for user_db in user_dbs:
    if not user_db.birthdate:
      user_db.birthdate = None
      updated_dbs.append(user_db)

  if updated_dbs:
    ndb.put_multi(updated_dbs)

  return util.jsonify_model_dbs(updated_dbs, user_cursor)
