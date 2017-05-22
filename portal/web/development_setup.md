# Setting up your Development Environment

These instructions will walk you through setting up a development environment
for django projects using our usual setup. It also covers some of our process
and best practices for our development environment.


## One-time Setup

Perform these steps when first setting up a new development environment for a
new or existing project.

1. Clone the repository into a new directory. e.g.:

   ```$ git clone git@github.com:ITNG/django-skeleton.git```

   and then `cd` into the new directory that was created. e.g.

   ```$ cd django-skeleton```

   (obviously your repo and directory name will be different for existing
   projects)

2. Create a virtual environment with the `virtualenv` command.

   ```$ virtualenv -p python3 env```

   Replacing `python3` with the name of the python binary you want to use. I
   assume python3 for this, which uses the default version of Python 3 on
   your system.

   This creates a virtual environment in the directory `env`. This is where
   locally installed python dependencies will live.

   Now activate your virtualenv with:

   ```$ source env/bin/activate```

3. Install dependencies

   The python dependencies are listed in requirements.txt, and can be
   installed with:

   ```$ pip install -r requirements.txt```

   If some python dependencies require compiled C extensions, you will need
   to install a C compiler and the Python development headers first or the
   install command will error.

   If some C extension modules depend on other libraries, you may need to
   install development headers for those as well.

4. Create your .env ([dotenv](project#the-dotenv-convention)) file

   Our Django setup has the project files in a directory called "project". From
   there, copy the example env file to the base directory.

   ```$ cp project/develop/env .env```

   For development you shouldn't need to edit this file at all. The default
   settings use an sqlite database called "db.sqlite3" and have reasonable
   defaults for the rest of the settings for development.

5. Create the database tables

   Run this command to create your database and database tables

   ```./manage.py migrate```

   You will also need to migrate after any changes to the migration files
   (for example, if you pull some changes that include changes to the
   database models and migrations)

6. Create a superuser

   Before you can log in to your app, you have to create a superuser in the
   users table. This can be done with the createsuperuser management command:

   ```./manage.py createsuperuser```

   The command will ask you for a username, email, and password. The email
   can be anything, it doesn't matter for development.

   I like to use simple passwords for local development, but the default
   django settings disallow weak passwords such as "password". You can add
   this line to your settings.py to disable all password validators:

   ```AUTH_PASSWORD_VALIDATORS = []```

That's all the one-time setup! Some projects may have additional steps or
values to fill in in your settings.py file.

Once ready, Move on to the "running the test server" section below.


## Setting up your environment

You'll need to activate your virtual environment in each terminal you open.
First `cd` to your project directory and then activate the virtualenv with

```$ source env/bin/activate```

Now your terminal prompt is modified, and any python commands you run will
use the libraries installed in the virtual environment.

If you are done working or want to switch to another one, run the
`deactivate` command to return your environment to its original state.


## Running the test server

```./manage.py runserver [addrport]```

This command runs the Django test server. While the test server is running,
you will be able to access your web app. The test server automatically
restarts when you make changes to python files in the project.

By default, with no parameters after `runserver`, it listens on localhost port 8000.
If you are developing locally, this is ideal.

You can specify the port to listen: e.g. `./manage.py runserver 8001`

If you are developing on a remote server, you will need to use ssh port
forwarding to access a service listening on localhost.

Alternately, the test server can listen on the external network adapter by
explicitly specifying the "any" address to bind to, like so:

```./manage.py runserver 0.0.0.0:8000```


## Using Tmux to keep the server running

For some development situations, it can be handy to leave the test server
running in the background. Here's a quick primer on how to use the `tmux`
command.

Tmux is a terminal multiplexer. It is a terminal program that runs terminals.
It runs terminal sessions in the background and then attaches to them,
meaning your can leave a terminal session running and return to it later,
leaving your programs running in the background. ([See More](https://tmux.github.io/))

To start tmux, run `tmux`. This starts a new session and opens a new shell
within it. You can identify if you're within a tmux session by the status bar
 at the bottom.

Within the session, you can now activate your virtual environment and run
your runserver command same as before.

Within a tmux session, you can send commands to tmux using the special
keystroke `Ctrl-b` and then another key. The important one to remember is
`Ctrl-b d` to detach. Your terminal will detach from tmux, and whatever command
you were running will remain running in the background.

When you want to return to a tmux session, use the command `tmux attach`

Once you exit the shell within a tmux session, that session will exit.


## Managing new dependencies with `pip-tools`

We use [`pip-tools`](https://github.com/nvie/pip-tools) to manage dependencies
in our projects. If you need to add a dependency, do the following:

1. Add the dependency to the `requirements.in` file.
2. Activate your virtual environment.
3. Install `pip-tools` to your virtual environment if not already present.
4. Run `$ pip-compile --output-file requirements.txt requirements.in`.
5. Update your virtual environment with `$ pip install -r requirements.txt`.

To understand why this practice is beneficial, I'd recommend
reading these articles [[1](http://nvie.com/posts/pin-your-packages/),
[2](http://nvie.com/posts/better-package-management/)] from the author of `pip-tools`.


## Changing database models

When you make changes to the database models, you must create a migration.
Django migration files tell Django how to alter the database tables from the
old structure to the new structure.

After any model changes, run `./manage.py makemigrations` to auto-generate a
migration file for the changes you made. You can then run that migration with
`./manage.py migrate`.

`makemigrations` only looks at your model files and generates
migration files. It doesn't touch your database. Running `migrate` looks at
your migration files and issues the actual ALTER TABLE statements to your DBMS.

### Rolling back migrations
If you decide that migration was a mistake after you apply it but before you
commit it to git, don't just delete the migration file. You must first roll it
back to undo the changes to the database.

Use

```./manage.py migrate <appname> <migration>```

Where `appname` is the name of the Django app, and `migration` is the
migration you are rewinding to. For example, if your migrations are:
* 0001_initial.py
* 0002_some_changes.py
* 0003_more_changes.py

And you want to undo the last one, use

```./manage.py migrate appname 0002_some_changes```

And this will undo (or apply) migrations such that migration 0002 is the
latest one. View which migrations are applied with `./manage.py showmigrations`

You can now safely delete the unapplied migration file and revert (or change)
your model changes, and then start the migration process from the top.

(If you have already committed your mistake to git, then leave the mistaken
migration file, change your models back, and generate a new "undo" migration)


### Committing migrations

If the database and migration files become out of sync, it can cause
headaches for collaborators as new auto-generated migrations will contain
changes that were already changed in others' databases. For this reason,
there is one important rule to keep in mind:

**Always commit migration files in the same commit as model changes**

In other words, if you make changes to the Django models, make sure you run
makemigrations and `git add` and commit the newly generated migration files at
the same time you commit the models.

This way, when collaborators pull your changes, they only need to run `
./manage.py migrate` to update their database with your changes.

Another rule is **Never delete migration files after they have been
committed**. If people have applied a migration, and then the migration is
deleted, then there is no way to roll back those changes, and new changes
made may conflict with changes in the database that are essentially unknown
to Django.


## Pulling Changes

When you pull remote changes from the repository, the one thing to be mindful
about is if any database changes were made. If so, run

```./manage.py migrate```

to apply any changes to your local database. You can run this
unconditionally after a pull or merge, as it doesn't do anything if there are
 no unapplied migrations.

If any new dependencies were added to requirements.txt, you will also need to
 run

```pip install --upgrade -r requirements.txt```

