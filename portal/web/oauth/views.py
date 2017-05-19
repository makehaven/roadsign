"""This module interfaces to oauth identity providers

For information on the oauth2client library, see
https://developers.google.com/api-client-library/python/guide/aaa_oauth
"""

import os
import uuid

import django.contrib.auth.backends
import django.contrib.auth.forms
from django.contrib import messages
from django.core.exceptions import SuspiciousOperation
from django.core.urlresolvers import reverse
from django.db.transaction import atomic
from django.forms import modelform_factory
from django.http import Http404, HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.shortcuts import render, resolve_url
from django.conf import settings

from . import models
from . import flows

def secure_uuid4():
    return uuid.UUID(bytes=os.urandom(16), version=4)

def login(request, provider):
    """A view that returns a redirect to the given identity provider's
    authorization url.

    If you specify a GET parameter called "next", it will be set to the
    oauth_next_url session variable. This lets you embed links to this view
    in other views and have the user directed anywhere you like after login.

    """
    next_url = request.GET.get("next")
    if next_url:
        request.session['oauth_next_url'] = next_url

    if provider == "google":
        flow = flows.get_google_flow(request)
    else:
        raise Http404()

    state = str(secure_uuid4())
    request.session['_oauth_state'] = state
    return HttpResponseRedirect(flow.step1_get_authorize_url(state=state))

def complete(request, provider):
    """A view that the user is redirected to after identifying with an
    identity provider with Oauth.

    This view will create a new OAuthUser model object if one does not exist
    for the given user/provider pair.

    This view will also attempt to authenticate and login the newly identified
    oauth user with Django's authenticate() and login() functions. This works
    with the OAuthBackend class if installed as a Django authentication
    backend. If authentication is not successful, possibly because the oauth
    user does not have an associated local Django user, the request is
    redirected to the associate view (see below).

    On successful oauth identification and authentication, this view redirects
    the user to the url in the session variable "oauth_next_url", or the
    view named in the setting LOGIN_REDIRECT_VIEW if that session variable is
    not defined.

    On unsuccessful oauth identification, the _failure() function is called
    to redirect the user to a failure page.

    """
    # Each branch of this if statement should set an "oauthuser" variable
    if provider == "google":
        error = request.GET.get("error")
        if error is not None:
            if error == "access_denied":
                msg = "You have denied access. Try again, or go back"
            else:
                msg = "An error occurred: {}".format(error)
            return _failure(request, msg)
        flow = flows.get_google_flow(request)
        credentials = flow.step2_exchange(request.GET['code'])
        #http = httplib2.Http()
        #http = credentials.authorize(http)
        # use the credentials to retrieve more user info here, if necessary
        # (not needed with google openid connect; we get the email in the
        # id_token)

        state = request.session.get('_oauth_state')
        if state is None or state != request.GET.get("state"):
            raise SuspiciousOperation("Oauth2 state did not match!")

        oauthuser, created = models.OAuthUser.objects.get_or_create(
            uid=credentials.id_token['sub'],
            provider="google",
        )

        # The docs aren't clear, but the email you get from google's identity
        # token isn't necessarily a unique or verified email, and it could
        # change. The docs say to use the "sub" field as a unique identifier
        # and key, but we still want to identify users by email for the
        # purposes of our whitelist.
        email = credentials.id_token.get("email")
        if email and credentials.id_token.get("email_verified", False):
            if oauthuser.email != email:
                oauthuser.email = email
                oauthuser.save(update_fields=['email'])
    else:
        raise Http404()

    assert isinstance(oauthuser, models.OAuthUser)

    # Try and log in the oauth user if there is an associated django user.
    # New oauth users won't have a local django user yet and authenticate()
    # will return None
    user = django.contrib.auth.authenticate(oauthuser=oauthuser)
    if user is not None:
        django.contrib.auth.login(request, user)
    else:
        # The oauth user does not have an associated local user.
        # Redirect to the oauth_associate view to make that association and
        # log the user in.
        request.session['oauth_associate_id'] = oauthuser.pk
        return HttpResponseRedirect(reverse("oauth_associate"))

    return _finish(request, oauthuser)

def associate(request):
    """This view is called after a user has been identified via oauth but
    they do not have a local user associated.

    The complete view redirects here after setting the session variable
    oauth_associate_id, indicating which oauth user has just been created
    that needs associating.

    This implementation presents the user with two options, after which a
    local user is associated with the new oauth identity and the user logged in:
    1. Create a new account (an abbreviated new account form is presented)
    2. log in to an existing local account (a login form is presented; if the
       user is already logged in, this option is assumed)

    """
    oauthuser_pk = request.session.get("oauth_associate_id")
    if oauthuser_pk is None:
        # User navigated to this view outside of the above workflow?
        return HttpResponseBadRequest()
    oauthuser = models.OAuthUser.objects.get(pk=oauthuser_pk)

    if request.user.is_authenticated:
        # The user is logged in with a local account (perhaps they just
        # logged in with the form below). Associate it.
        messages.add_message(
            request,
            messages.INFO,
            "Your oauth identity {} is now associated with your account {}".format(
                oauthuser.email,
                request.user,
            )
        )
        oauthuser.user = request.user
        oauthuser.save(update_fields=['user'])
        del request.session["oauth_associate_id"]
        return _finish(request, oauthuser)

    UsernameForm = modelform_factory(
        django.contrib.auth.get_user_model(),
        fields=['username'],
    )

    # Note: at present we don't bother asking for the user's email address
    # or filling it in automatically from the oauth information because we
    # don't currently have a way to verify email addresses, and because there
    # are questions as to whether we can trust the email addresses we get from
    # oauth to be already verified. If we auto-associated new oauth users
    # with existing local accounts by email address, then:
    # * A malicious identity provider could return arbitrary or unverified
    #   email addresses, letting users take over existing local accounts
    # * If we don't verify email addresses and a user mis-types their own
    #   email address, A non-malicious identity provider would let the owner of
    #   the mistyped email address take over the account
    #
    # A proper fix involves implementing an actual email verification
    # system, and only auto-associating if we trust the identity provider AND
    # we verify the email address ourself.
    #
    # We may also decide to change the user model so that email is unique and
    # the primary username field, and then it will make sense to fill it in
    # from oauth and create accounts with already-verified emails. But for now
    # the user created should just have the bare minimum needed to be a valid
    # user in the system, which is only a username.

    if request.method == "POST":
        # Submitted a username request
        form = UsernameForm(data=request.POST)
        if form.is_valid():
            with atomic():
                user = form.save()

                oauthuser.user = user
                oauthuser.save(update_fields=['user'])

                django.contrib.auth.login(request, user,
                                          "oauth.authbackend.OAuthBackend")

                del request.session["oauth_associate_id"]

                return _finish(request, oauthuser)
    else:
        # Show the login form and a username signup form
        form = UsernameForm(
            initial=dict(
                username=oauthuser.email
            )
        )
    return render(request, 'oauth_associate.html',
                  {
                      "form": form,
                      "loginform": django.contrib.auth.forms.AuthenticationForm(request),
                  })

def _finish(request, oauthuser):
    """Returns a response that finishes the authentication flow.

    One of the above views should call this once we have a local user logged
    in with an associated OAuthUser
    """
    # We expect the view that initiated the process to set this
    # session variable so we can redirect back to them.
    next_url = request.session.get('oauth_next_url')
    if next_url is not None:
        return HttpResponseRedirect(next_url)

    # Fallback if there was no redirect url
    messages.add_message(
        request,
        messages.SUCCESS,
        "You are now identified as {} and logged in".format(oauthuser.email)
    )
    return HttpResponseRedirect(resolve_url(settings.LOGIN_REDIRECT_URL))


def _failure(request, msg=""):
    """Called on an unsuccessful authentication.

    Customize this function to change where the user is directed after they
    decline to authorize the app.

    """
    if msg:
        messages.add_message(
            request,
            messages.ERROR,
            msg,
        )
    return HttpResponseRedirect(settings.LOGIN_URL)