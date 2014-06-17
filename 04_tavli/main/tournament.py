from flask.ext import wtf
import flask

import auth
import model
import util
import iso

from main import app


class TournamentUpdateForm(wtf.Form):
  TYPE_CHOICES = [(t, t.replace('-', ' ').title()) for t in model.Tournament.type._choices]
  COUNTRY_CHOICES = sorted([(k, unicode(v, 'utf-8')) for k, v in iso.ISO_3166.iteritems()], key=lambda tup: tup[1])

  name = wtf.StringField('Name', [wtf.validators.required()], filters=[util.strip_filter])
  type = wtf.SelectField('Type', [wtf.validators.optional()], choices=TYPE_CHOICES)
  timestamp = wtf.DateTimeField('Date/Time', [wtf.validators.required()], format='%Y-%m-%dT%H:%M')
  place = wtf.StringField('Place', [wtf.validators.optional()], filters=[util.strip_filter])
  address = wtf.StringField('Address', [wtf.validators.optional()], filters=[util.strip_filter])
  city = wtf.StringField('City', [wtf.validators.optional()], filters=[util.strip_filter])
  country = wtf.SelectField('Country', [wtf.validators.optional()], choices=COUNTRY_CHOICES)
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


@app.route('/_s/tournament/', endpoint='tournament_list_service')
@app.route('/tournament/')
def tournament_list():
  tournament_dbs, next_cursor = model.Tournament.get_dbs(order='-timestamp', is_public=True)

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_dbs(tournament_dbs, next_cursor)

  return flask.render_template(
      'tournament/tournament_list.html',
      html_class='tournament-list',
      title='Tournaments',
      tournament_dbs=tournament_dbs,
      next_url=util.generate_next_url(next_cursor),
    )


@app.route('/_s/my/tournament/', endpoint='my_tournament_list_service')
@app.route('/my/tournament/')
@auth.login_required
def my_tournament_list():
  tournament_dbs, next_cursor = model.Tournament.get_dbs(order='-timestamp', user_key=auth.current_user_key())

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_dbs(tournament_dbs, next_cursor)

  return flask.render_template(
      'tournament/my_tournament_list.html',
      html_class='my-tournament-list',
      title='My Tournaments',
      tournament_dbs=tournament_dbs,
      next_url=util.generate_next_url(next_cursor),
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
