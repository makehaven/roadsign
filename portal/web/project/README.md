# Project Configuration

This directory contains all of the files specific to application configuration (in addition to some general-purpose
utility code). Notable files:

- `common_settings.py`: The majority of settings that are common to both development and production environments.
- `settings.py`: Contains settings that are configured for *local development*.
- `deploy/settings.py`: Contains settings that are configured for *production*.
- `develop/env`: Example development dotenv file for a user's environment specific settings.

## Getting Started with development

Getting started is as simple as copying the `env` file to the project's base directory:

```bash
$ cp /path/to/BASE_DIR/project/develop/env /path/to/BASE_DIR/.env
```

You will likely edit this file to suit your development style. For example, you may prefer to develop with postgres
instead of a sqlite database. You would need to create a database, and then update the `DATABASE_URL` accordingly.
If you want to use sentry, then you'd need to setup a sentry project and then add the `SENTRY_DSN` to your dotenv.

## The dotenv convention

The 'dotenv' convention eases the management of environment-specific application settings by loading these values
from the machine's environment variables. In practice, dotenv utilities will read a `.env` file into a machine's
environment variables, which are then accessible from `os.environ`. Although oriented towards the Ruby community,
this [article](https://alexander-clark.com/blog/using-dotenv-store-environment-specific-config/) has some useful
information on the dotenv convention. Additionally, you may want to check out the django-environ
[docs](http://django-environ.readthedocs.io/en/latest/).

## Modifying the settings

Here are some general guidelines for modifying the setings.

- Settings with values that don't change between production and development should be added to `common_settings.py`.
- Settings that are environment-specific should be added to the dotenv file. Don't forget to add:
  - An example entry to the development dotenv in `develop/env`.
  - An entry to the `Env` schema in `common_settings.py`
    - If a setting is optional, make sure that the value is secure (where applicable). eg, `DEBUG` defaults to false.
    - If a setting is not optional (eg, the database URL), do not provide a default. The lack of a database URL implies
      a configuration error, and process startup should fail instead of using a faulty default.
- Some settings are not environment specific, but are not common between development and production either. In this
  case, you should set the value in the respective production (`deploy/settings.py`) and development (`settings.py`)
  files. For example, file uploads may point to a remote server in production, while a local directory may be
  suitable for dev.
