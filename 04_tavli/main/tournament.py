from flask.ext import wtf
import flask

import auth
import model
import util
import iso
import task

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
  tournament_dbs, next_cursor = model.Tournament.get_dbs(is_public=True)

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
  tournament_dbs, next_cursor = model.Tournament.get_dbs(user_key=auth.current_user_key())

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

  user_tournament_dbs, _ = tournament_db.get_user_tournament_dbs()

  return flask.render_template(
      'tournament/tournament_view.html',
      html_class='tournament-view',
      title=tournament_db.name,
      tournament_db=tournament_db,
      user_tournament_dbs=user_tournament_dbs,
  )


@app.route('/tournament/<int:tournament_id>/<register_flag>/', methods=['POST'])
@auth.login_required
def tournament_register(tournament_id, register_flag):
  tournament_db = model.Tournament.get_by_id(tournament_id)
  if not tournament_db:
    flask.abort(404)

  # TODO: Check if it's open for registrations first - george -> should we add an [open_for_registration] field ???

  user_tournament_db = model.UserTournament.get_or_insert(
      str(auth.current_user_id()),
      parent=tournament_db.key,
      tournament_key=tournament_db.key,
      user_key=auth.current_user_key(),
  )

  body = 'name: %s\nusername: %s\nemail: %s' % (
      auth.current_user_db().name,
      auth.current_user_db().username,
      auth.current_user_db().email,
  )
  creator_user_db = model.User.get_by_id(tournament_db.user_key.id())

  if register_flag == 'register':
    user_tournament_db.put()
    flask.flash('Awesome! You are in..', category='success')
    # how to send an email to -> creator_user_db.email
    # task.send_mail_notification('%s entered tournament %s' % (auth.current_user_db().name, tournament_db.name), body)
  elif register_flag == 'unregister':
    user_tournament_db.key.delete()
    flask.flash('Bummer! You are out..', category='info')
    # how to send an email to -> creator_user_db.email
    # task.send_mail_notification('%s left tournament %s' % (auth.current_user_db().name, tournament_db.name), body)

  return flask.redirect(flask.url_for('tournament_view', tournament_id=tournament_id))
