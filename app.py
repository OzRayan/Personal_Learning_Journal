from flask import (Flask, g, render_template, flash,
                   redirect, request, url_for, abort)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
import datetime
import forms
import models

# Default values for app
DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'hgd9s8#!.*hjghjfY!^%Rhg54$'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Login required.'
login_manager.login_message_category = 'error'


@login_manager.user_loader
def load_user(userid):
    """Loads user by id
    DECORATION:
        LoginManager with user_loader from flask_login
    INPUT:
        userid
    RETURNS:
         user by user id if exist
         else None
    """
    try:
        # noinspection PyUnresolvedReferences
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request.
    DECORATION:
        before_request from Flask class
    """
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request.
    DECORATION:
        after_request from Flask class
    RETURNS:
        response
    """
    g.db.close()
    return response


@app.route('/')
def index():
    """Main page view.
    DECORATION:
        route from Flask class
    RETURNS:
         render_template from flask - renders index.html template with entries flag
    """
    entries = models.Entry.select().limit(10).order_by(models.Entry.created_at.desc())
    return render_template('index.html', entries=entries, view_all=True)


def get_object_or_404(slug):
    """Get an object or 404 request.
    INPUT:
        slug
    RETURNS:
        entry_object - entry(post) object
        """
    entry_object = None
    try:
        entry_object = models.Entry.select().where(models.Entry.slug == slug).get()
    except models.DoesNotExist:
        abort(404)
    return entry_object


@app.route('/entries')
def entry_list():
    """Entry(post) list.
    DECORATION:
        route from Flask class
        :input: entries
    RETURNS:
         render_template from flask - renders index.html template with entries flag
    """
    entries = models.Entry.select().order_by(models.Entry.created_at.desc())
    return render_template('index.html', entries=entries)


@app.route('/entries/<slug>')
def view_entry(slug):
    """Entry(post) detail view.
    DECORATION:
        route from Flask class
        :input: entries/slug
    INPUT:
        slug
    RETURNS:
        render_template from flask - renders detail.html
                        template with entries, entry_tag flags
    """
    entry_object = get_object_or_404(slug)
    # noinspection PyUnresolvedReferences
    entry_tags = (models.Tag.select()
                            .join(models.EntryTag)
                            .join(models.Entry)
                            .where(models.Entry.id == entry_object.id))
    if not entry_object:
        abort(404)
    return render_template('detail.html', entry=entry_object, entry_tags=entry_tags)


@app.route('/entries/<username>')
def user_entries(username):
    """User entry(post) view.
    DECORATION:
        route from Flask class
        :input: entries/username
    INPUT:
        username
    RETURNS:
        render_template from flask - renders index.html
                            template with entries, entry_tag flags
    """
    entries = None
    entry_list_tags = []
    try:
        entries = (models.User.select()
                              .where(models.User.username == username)
                              .get()
                              .entries
                              .order_by(models.Entry.created_at.desc()))
    except models.DoesNotExist:
        abort(404)
    return render_template('index.html',
                           entries=entries,
                           entry_tags=entry_list_tags,
                           view_all=True)


@app.route('/entries/tag/<tagid>')
def entries_tag(tagid):
    """Entries(posts) tag view.
    DECORATION:
        route from Flask class
        :input: entries/slug/tag_id
    INPUT:
        tagid
    RETURNS:
        render_template from flask - renders index.html
                        template with entries
    """
    try:
        # noinspection PyUnresolvedReferences
        # noinspection PyUnusedLocal
        tag_object = models.Tag.get(models.Tag.id == tagid)
    except models.DoesNotExist:
        abort(404)
    # noinspection PyUnresolvedReferences
    entries = (models.Entry.select()
                           .join(models.EntryTag)
                           .join(models.Tag)
                           .where(models.Tag.id == tagid))
    return render_template('index.html', entries=entries, view_all=True)


@app.route('/entry', methods=('GET', 'POST'))
@login_required
def entry():
    """Entry(post) create view.
    DECORATION:
        route from Flask class
        login_required from flask_login
        :input: entry(post) with GET and POST methods
    RETURNS:
        redirect to home page if form submit is valid
        else
        render_template from flask - renders entry.html
                        template with form
    """
    form = forms.PostEntryForm()
    if form.validate_on_submit():
        models.Entry.create_entry(
            user=g.user._get_current_object(),
            title=form.title.data.strip(),
            created_at=(form.created_at.data or datetime.datetime.now()),
            duration=form.duration.data,
            content=form.content.data.strip(),
            resources=form.resources.data.strip(),
        )
        flash("Entry created!", "success")
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/entries/edit/<slug>', methods=('GET', 'POST'))
@login_required
def edit_entry(slug):
    """Entry(post) view.
    DECORATION:
        route from Flask class
        login_required from flask_login
        :input: entries/slug/edit with GET and POST methods
    INPUT:
        slug
    RETURNS:
        redirect to home page if form submit is valid
        else
        render_template from flask - renders entry.html
                        template with entries, entry_tag flags
    """
    entry_object = get_object_or_404(slug)
    form = forms.PostEntryForm(obj=entry_object)
    if form.validate_on_submit():
        # noinspection PyUnresolvedReferences
        query = models.Entry.update(
            user=g.user._get_current_object(),
            title=form.title.data.strip(),
            created_at=(form.created_at.data or datetime.datetime.now()),
            duration=form.duration.data,
            content=form.content.data.strip(),
            resources=form.resources.data.strip(),
        ).where(models.Entry.id == entry_object.id)
        query.execute()
        flash("Entry updated!", "success")
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/tags/create', methods=('GET', 'POST'))
@login_required
def tag():
    """Tag view.
    DECORATION:
        route from Flask class
        login_required from flask_login
        :input: tags/create with GET and POST methods
    RETURNS:
        redirect to home page if form submit is valid
        else
        render_template from flask - renders tag.html with form flag
    """
    form = forms.TagForm()
    if form.validate_on_submit():
        models.Tag.create(name=form.name.data)
        flash("Tag created!", "success")
        return redirect(url_for('index'))
    return render_template('tag.html', form=form)


@app.route('/entries/tags/<slug>', methods=('GET', 'POST'))
@login_required
def apply_tag(slug):
    """Apply tag view.
    DECORATION:
        route from Flask class
        login_required from flask_login
        :input: entries/slug/tags with GET and POST methods
    INPUT:
        slug
    RETURNS:
        redirect to view_entry if form submit is valid
        else
        render_template from flask - renders apply_tag.html
                            with form, tag and slug flags
    """
    form = forms.EntryTagForm(request.form)
    tags = models.Tag.select()
    entry_object = get_object_or_404(slug)
    form.tags.choices = [(x.id, x.name) for x in tags]
    if form.validate_on_submit():
        entry_tags = (models.EntryTag.select()
                                     .where(models.EntryTag.entry == entry_object.id))
        existing_entry_tags = []

        for entry_tag in entry_tags:
            existing_entry_tags += [entry_tag.tag.id]
        for selection in request.form.getlist('tags'):
            if int(selection) in existing_entry_tags:
                continue
            models.EntryTag.create(
                entry=entry_object.id,
                tag=selection
            )
        flash("Tags applied!", "success")
        return redirect(url_for('view_entry', slug=slug))
    return render_template('apply_tag.html', form=form, tags=tags, slug=slug)


@app.route('/entries/<slug>/tags/remove', methods=('GET', 'POST'))
@login_required
def remove_tag(slug):
    """Remove tag view.
    DECORATION:
        route from Flask class
        login_required from flask_login
        :input: entries/slug/tags/remove with GET and POST methods
    INPUT:
        slug
    RETURNS:
        redirect to view entry(post) if form submit is valid
        else
        render_template from flask - renders remove_tag.html
                            with form, tag and slug flags
    """
    form = forms.EntryTagForm(request.form)
    entry_object = get_object_or_404(slug)
    e_id = entry_object.id
    entry_tags = (models.EntryTag.select()
                                 .where(models.EntryTag.entry == e_id))
    entry_tag_id = [entry_tag.tag.id for entry_tag in entry_tags]
    # noinspection PyUnresolvedReferences
    tags = models.Tag.select().where(models.Tag.id << entry_tag_id)
    form.tags.choices = [(x.id, x.name) for x in tags]
    if form.validate_on_submit():
        selections = [int(x) for x in request.form.getlist('tags')]
        # noinspection PyUnresolvedReferences
        tags = models.Tag.select().where(models.Tag.id << selections)
        query = models.EntryTag.delete().where(
            (models.EntryTag.entry == entry_object) &
            (models.EntryTag.tag << tags)
        )
        query.execute()
        flash("Tags removed", "success")
        return redirect(url_for('view_entry', slug=slug))
    return render_template('remove_tag.html', form=form, tags=tags, slug=slug)


@app.route('/entries/delete/<slug>', methods=('GET', 'POST'))
@login_required
def remove_entry(slug):
    """Remove entry(post) view.
    DECORATION:
        route from Flask class
        login_required from flask_login
        :input: entries/slug/delete with GET and POST methods
    INPUT:
        slug
    RETURNS:
        redirect to view entry_list if form submit is valid
        else
        render_template from flask - renders delete.html
                            with entry, form
    """
    entry_object = get_object_or_404(slug)
    form = forms.RemoveEntryForm()
    if form.validate_on_submit():
        models.Entry.delete_instance(entry_object)
        flash("Entry deleted!", "success")
        return redirect(url_for('entry_list'))
    return render_template('delete.html', entry=entry_object, form=form)


@app.route('/register', methods=('GET', 'POST'))
def register():
    """Register view. Create an user.
    DECORATION:
        route from Flask class
        :input: register with GET and POST methods
    RETURNS:
        redirect to view home page if form submit is valid
        else
        render_template from flask - renders remove_tag.html
                                with form flag
    """
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("You registered!", "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    """Login view. Uses login_user from flask_login to login user(creates a session),
        Check the password with check_password_hash from flask_bcrypt to check password.
    DECORATION:
        route from Flask class
        :input: /login with GET and POST methods
    RETURNS:
        render_template from flask - renders login.html
                                    with form flag
    """
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """Logout view. Uses logout_user from flask_login to logout user(close the session)
    DECORATION:
        login_required from flask_login
        route from Flask class
        :input: /logout with GET and POST methods
    RETURNS:
        render_template from flask - renders index.html(home page)
    """
    logout_user()
    flash("You've been logged out!", "success")
    return redirect(url_for('index'))


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='test_user',
            email='example@mail.com',
            password='testpassword',
            admin=True
        )
    except ValueError:
        pass
    app.run(debug=DEBUG)
