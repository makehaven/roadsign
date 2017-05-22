# Oauth Authentication

This Django app is a simple way to add oauth authentication to your django 
project.

## Setup

1. Uncomment the dependency in requirements.txt
2. Add the `oauth` app to your `INSTALLED_APPS` list in common_settings.py
3. Add the authentication backend `oauth.authbackend.OAuthBackend` to the 
`AUTHENTICATION_BACKENDS` list in common_settings.py
4. Run `manage.py migrate` to install the new database table
5. Include the oauth urls.py from your project urls.py
6. Fill in the `GOOGLE_OPENIDCONNECT_KEY` and `GOOGLE_OPENIDCONNECT_SECRET` 
keys in settings.py

## How to use this app

Add links to your login view template pointing to the `oauth_login` view. 
When users click the link, they will be redirected to the identity provider 
where they log in, and are then redirected back to the `oauth_complete` view 
when they are logged in.

To log in, oauth users must have a local Django user in the database. 
First-time oauth users will be redirected to the `oauth_associate` view to 
create a new local account and associate it with their oauth identity.

## Customizing

See the docstrings and comments in views.py for information on what each view
does.

Things you may wish to customize for your specific project:

* Where the user is directed to if they reject permissions on the identity 
provider. (See `views._failure()`)

* What information is required of new users on first login, or more 
generally, the behavior of oauth users that have no local account. (See
`views.associate()`)

* Add in new identity providers (Add a new function to the `flows` module, 
and add a new block in `views.login()` and `views.complete()`)

Note: this module does not perform any access list logic. It is recommended 
you use regular django permissions and authorization decorators to restrict 
views to select users, but you could also add code to `views.complete()` to 
disallow oauth users that meet or don't meet some criteria from even logging in.