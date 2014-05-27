from flask.ext import wtf
import flask
import datetime

import auth
import model
import util

from main import app


class TournamentUpdateForm(wtf.Form):
  TYPE_CHOICES = [(t, t.replace('-', ' ').title()) for t in model.Tournament.type._choices]

  name = wtf.StringField('Name', [wtf.validators.required()], filters=[util.strip_filter])
  type = wtf.SelectField('Type', [wtf.validators.optional()], choices=TYPE_CHOICES)
  timestamp = wtf.DateField('Date', [wtf.validators.required()])
  place = wtf.StringField('Place', [wtf.validators.optional()], filters=[util.strip_filter])
  address = wtf.StringField('Address', [wtf.validators.optional()], filters=[util.strip_filter])
  city = wtf.StringField('City', [wtf.validators.optional()], filters=[util.strip_filter])
  rules = wtf.TextAreaField('Rules', [wtf.validators.optional()], filters=[util.strip_filter])
  is_closed = wtf.BooleanField(default=False)
  is_public = wtf.BooleanField(default=False)


@app.route('/my/tournament/create/', methods=['GET', 'POST'], endpoint='tournament_create')
@app.route('/my/tournament/<int:tournament_id>/update/', methods=['GET', 'POST'])
@auth.login_required
def tournament_update(tournament_id=0):
  if tournament_id == 0:
    tournament_db = model.Tournament(user_key=auth.current_user_key(), name='')
  else:
    tournament_db = model.Tournament.get_by_id(tournament_id)
  if not tournament_db or tournament_db.user_key != auth.current_user_key():
    flask.abort(404)

  form = TournamentUpdateForm(obj=tournament_db)
  if form.validate_on_submit():
    form.timestamp.data = datetime.datetime.combine(form.timestamp.data, datetime.time(00, 00))
    form.populate_obj(tournament_db)
    tournament_db.put()
    return flask.redirect(flask.url_for('my_tournament_list'))
  return flask.render_template(
      'tournament/tournament_update.html',
      html_class='tournament-update',
      title='%s' % ('Create Tournament' if tournament_id == 0 else tournament_db.name),
      form=form,
      tournament_db=tournament_db,
    )


@app.route('/tournament/')
def tournament_list():
  tournament_dbs, more_cursor = util.retrieve_dbs(
      model.Tournament.query(),
      limit=util.param('limit', int),
      cursor=util.param('cursor'),
      order=util.param('order') or '-timestamp',
      is_public=True,
    )
  return flask.render_template(
      'tournament/tournament_list.html',
      html_class='tournament-list',
      title='Tournaments',
      tournament_dbs=tournament_dbs,
      more_url=util.generate_more_url(more_cursor),
    )


@app.route('/my/tournament/')
@auth.login_required
def my_tournament_list():
  tournament_dbs, more_cursor = util.retrieve_dbs(
      model.Tournament.query(),
      limit=util.param('limit', int),
      cursor=util.param('cursor'),
      order=util.param('order') or '-timestamp',
      user_key=auth.current_user_key(),
    )
  return flask.render_template(
      'tournament/my_tournament_list.html',
      html_class='my-tournament-list',
      title='My Tournaments',
      tournament_dbs=tournament_dbs,
      more_url=util.generate_more_url(more_cursor),
    )


@app.route('/tournament/<int:tournament_id>/')
def tournament_view(tournament_id):
  tournament_db = model.Tournament.get_by_id(tournament_id)
  if not tournament_db:
    flask.abort(404)
  return flask.render_template(
      'tournament/tournament_view.html',
      html_class='tournament-view',
      title=tournament_db.name,
      tournament_db=tournament_db,
    )
