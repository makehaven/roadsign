# Django Skeleton

for Django 1.11. Should work with either Python 3.5+ or 2.7 (3.5 is preferred)

## Features
Adds the following on top of Django's startproject template

* A set of starter html templates using bootstrap and jquery.

  * `base.html` is a minimal bootstrap template. It also shows any pending Django
    messages from the messages framework, and shows the currently logged-in
    user, and a link to logout.
  * `login.html` has a minimal login form
  * `logout.html` has a logout message and a link to log in again
  * `password_change.html` has a minimal password change form
  * `password_change_done.html` has a success message and a link to the
    'home' view

* A settings file split into a `common_settings.py` and `settings.ex.py`.
* Settings configured for a top-level static files directory
* Settings configured for a top-level templates directory
* Settings configured with a good default logging configuration
* Settings configured to auto-generate a secret key on first invocation
* A starter `.gitignore`
* A starter `requirements.txt`
* Defined urls for django built-in authentication views (login,
  logout, and password change) and settings configured to use them
  (`LOGIN_URL`, `LOGOUT_URL`, and `LOGIN_REDIRECT_URL`).

## Getting Started
The bare minimum to get a working project is:

1. Create a virtual environment and install the requirements listed in
   `requirements.txt`

   * In this directory, run `virtualenv -p /usr/bin/python3.5 env`
   * Now run `env/bin/pip install -r requirements.txt`
   * For convenience in later commands, activate your virtualenv for this
     terminal with `source ./env/bin/activate`. You can replace
     `./env/bin/python` with just `python` in subsequent commands in an
     activated environment.

2. Unless you want an app named "appname", change the app name in the following
   places:

   * The app directory name itself
   * In `common_settings.py` the INSTALLED_APPS setting
   * The import statement in the project-wide `urls.py`

3. From the base directory, copy `project/develop/env` to `.env`. No
   changes are needed for development. See the README in the `project`
   directory for more information.

4. Create your database and initial schemas with
   `./env/bin/python manage.py migrate`. The default database is a
   sqlite-based file in the base directory of your project.

5. You now have a working development environment. Run the django test server
   with `./env/bin/python manage.py runserver`

## About base.html

The base template is a simple bootstrap-based html template. It has 4 content
blocks to override in sub-templates:

* `header` is used to insert items into the header of the page, such as
  stylesheets.
* `content` is where all your content should go. It is placed inside a
  `<div>` with class `container`
* `scripts` is a block at the very end of the body, which can be used to
  insert javascript blocks.
* `title` overrides the document title.

## Notes

* A view named 'home' is referenced in the starter templates and in the
  `LOGIN_REDIRECT_URL` setting. If you change the home view to be named
  something else, make sure you update these references.

# Deployment Guide

Our usual setup is to use Nginx, Gunicorn, and Supervisor on production deployments. For this example we assume you are deploying your code to /opt/my-deployment-dir

1. Clone a copy of your code to /opt/my-deployment-dir. This should put your
   manage.py at /opt/my-deployment-dir/manage.py
1. Install Nginx and supervisor system-wide
2. Create a Python virtualenv and install your project’s dependencies +
   gunicorn into it. For this example the base dir is /opt/my-deployment-dir and
   the virtualenv is /opt/my-deployment-dir/env
3. Create a user and group for your code to run as. For this example we use
   project-user and project-group
4. Create a supervisor config in /etc/supervisord.d/myproject.ini containing:

   ```
   [program:myproject]
   directory = /opt/my-deployment-dir
   command = /opt/my-deployment-dir/env/bin/gunicorn --env DJANGO_SETTINGS_MODULE=project.settings --pythonpath /opt/my-deployment-dir/ --bind=unix:/opt/my-deployment-dir/gunicorn.sock project.wsgi
   stdout_logfile = /opt/my-deployment-dir/stdout.log
   redirect_stderr = true
   autostart = true
   autorestart = true
   user = project-user
   group = project-group
   ```

   Note: for production deployments you may want to add e.g. `-w 4` to the
   gunicorn command to spawn multiple workers.

5. Create an nginx config in /etc/nginx/conf.d/myproject.conf containing:

   ```
   upstream gunicorn {
       server unix:/opt/my-deployment-dir/gunicorn.sock fail_timeout=0;
   }

   server {
       listen 80;
       server_name my-hostname.example.com;

       location /static/ {
           alias /opt/my-deployment-dir/static-root/;
       }
       location / {
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_set_header Host $http_host;
           proxy_redirect off;
           proxy_pass http://gunicorn;
       }
   }
   ```

   Note: You must include the X-Forwarded-Proto line even if not using ssl,
   because gunicorn interprets this header by default, and indicates via
   enviornment variables to Django. So this must be set to make sure clients
   can't fake Django into thinking a request is secure.

   Note: it is sometimes a good idea to put the socket file in e.g.
   /opt/my-deployment-dir/run if you want to have the server run as a
   different user than the user that owns /opt/my-deployment-dir. Then only
   that one directory needs to be writable by the linux user that runs the
   server process.

   Note: If running selinux, nginx won't be able to read the socket file. You
   can give nginx read-write permissions to all files in a directory with
   these commands:

   ```
   # yum install policycoreutils-python
   # semanage fcontext -a -t httpd_sys_rw_content_t "/opt/my-deployment-dir/run(/.*)?"
   # restorecon -vR /opt/my-deployment-dir/run
   ```
   [Read more about the different context types that RedHat/CentOS uses with web servers](https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html-single/Managing_Confined_Services/#sect-Managing_Confined_Services-The_Apache_HTTP_Server-Types)

6. Copy the example settings.ex.py to settings.py and configure:

   * Configure the django project for /opt/my-deployment-dir/static-root to
   be the STATIC_ROOT and run `manage.py collectstatic`
   * Configure the database parameters and run `manage.py migrate`
   * If this is a production deployment, set DEBUG to false and set the
   ALLOWED_HOSTS array to your hostnames you're serving, e.g. "my-hostname.example.com"

7. sudo systemctl restart supervisord
8. `sudo supervisorctl status` to make sure the workers started okay.
9. test nginx config with "sudo nginx -t"
10. restart nginx with "sudo nginx -s reload"
11. sudo systemctl enable nginx
12. sudo systemctl enable supervisord

### SSL Setup

To get LetsEncrypt running on the Nginx instance you just set up, follow
these steps

(adapted from <https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04>
and <https://certbot.eff.org/#centosrhel7-nginx>)

1. `yum install certbot` (assumes CentOS7 and epel repos installed)
2. Create a directory somewhere on the filesystem such as /opt/webroot
3. Add a new location block to your nginx config that looks like this:

   ```
   location ~ /.well-known {
       root /opt/webroot;
   }
   ```
   and reload nginx with `nginx -s reload`

3. Run `certbot certonly`

   This will ask you for your domain name and web root. If successful, it
   will go ahead and issue you your cert

4. Generate strong dh parameters with

   ```openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048```

5. Modify your nginx config. Add a new server block at the top that looks
like this:

   ```
   server {
        listen 80;
        server_name my-hostname.example.com;
        return 301 https://$server_name$request_uri;
   }
   ```

   And then modify your existing server block by replacing the listen line
   with:
   ```listen 443 ssl;```

   And adding these parameters:
   ```
        ssl_certificate /etc/letsencrypt/live/my-hostname.example.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/my-hostname.example.com/privkey.pem;
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_prefer_server_ciphers on;
        ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
        ssl_ecdh_curve secp384r1;
        ssl_session_cache shared:SSL:10m;
        ssl_session_tickets off;
        ssl_stapling on;
        ssl_stapling_verify on;
        add_header Strict-Transport-Security "max-age=6307200; includeSubdomains";
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nostiff;
        ssl_dhparam /etc/ssl/certs/dhparam.pem;
   ```
   (That full set of parameters will score you an A on ssl testers, but not
   all of them may be necessary)

   Make sure this line is in your `location /` block:

   ```   proxy_set_header X-Forwarded-Proto $scheme```

   Test and reload your nginx config

   ```
   # nginx -t
   # nginx -s reload
   ```

6. Add this configuration option to your settings.py (not necessary if
   running under gunicorn; gunicorn looks for this header by
   default if nginx connects from localhost, and indicates to Django whether
   the connection is secure via wsgi environ variables, which Django trusts
   by default)

   ```SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')```

7. Configure certbot to renew certificates automatically:

   run `certbot renew --dry-run` to make sure everything looks okay

   Edit root's crontab with `sudo crontab -e` and add this line:

   ```
    RANDOM_DELAY=60
    0 7 * * * certbot renew --quiet --post-hook "nginx -s reload"
   ```
   This attempts renewal once a day at a random minute between 7 and 8am. The
   renew command only actually renews if the cert expires within 30 days. It
   is recommended to run this often in case the cert was revoked earlier
   than expected

## Deployment notes and tips:

* I like to make a git branch named for that deployment. For example, I may make a branch called "my-deployment.oscar.ncsu.edu" and check out that branch. Then I can continue to develop on the master branch, and merge changes into the deployment branch and follow the instructions below to update the deployment
* With the above technique, I can check in any deployment-specific files such as settings.py to keep revisions and backups of critical files. Only push changes back if the remote repository is not public or if there are no secrets (such as db passwords) being checked in.
* By default, Supervisor rotates the stdout log file after 50 megabytes and
  keeps 10 past backups. You may consider tweaking these parameters in the
  supervisor config.

  For some situations, it's more appropriate to change Python's logging
  configuration to have Python log to a file instead of stderr so that Python
  can handle the log rotation instead of supervisor (using the
  RotatingFileHandler or TimedRotatingFileHandler). You will need to decide
  for yourself which makes the most sense for your situation.

  It usually makes sense to have supervisor perform the logging, so any
  erroneous writes to stdout or stderr by python outside of the logging
  system go to the same file. On the other hand, you may want to
  separate them if you want your log files in a consistent format, and you're
  using some library that's being rude and doing its own writing to stderr
  instead of using python logging.

* For production deployments, using Sentry is highly recommended. Add 'raven'
  to the requirements.txt and uncomment the sentry lines from the example
  settings file.

## Deploying Changes

To update a deployment with new changes:

1. cd to /opt/my-deployment-dir
2. run "git pull --ff-only". In general, you don't want to be doing any committing or merging out of the deployment working copy.
3. run "./env/bin/python manage.py migrate" to update the database with any new schema changes
4. run "./env/bin/python manage.py collectstatic" to update the static files
5. run "sudo supervisorctl restart all" to restart all running gunicorn processes
