.. contents::


BuildMyDocs
===========

When this app is installed to a repo, it will automatically create a readthedocs project for the repo.
It will also automatically set the "Build pull requests for this project" setting to True.

This feature is possible due to the recent change in ReadTheDocs API, where this setting gets exposed to the public API: https://github.com/readthedocs/readthedocs.org/pull/7834. Thank you readthedocs team!

This app is meant for Mariatta, since it uses Mariatta's personal ReadTheDocs Access token. Any projects
created by this App will created under Mariatta's readthedocs account.

If you would like this kind of automation for yourself, you can host this bot
on your own server of choice, and supply your own readthedocs access token.

You can sponsor Mariatta on GitHub: https://github.com/sponsors/Mariatta

Motivation
==========

I like writing documentation with Sphinx, restructuredText, and deploying them
to Readthedocs. I'm also a fan of Readthedocs' "build pull request changes"
feature.

I was finding it tedious to have to create a GitHub repo, write my docs,
and then go to Readthedocs, set up the project there, enable the "build pull request"
flag, and the go back to my GitHub repo. So I thought, surely this can be automated.

So I started experimenting with ReadTheDocs APIs and write my own API client,
which was heavily inspired by gidgethub library.

About the name
==============

I thought of calling it "BuildTheDocs" but don't want to get into conflict with
readthedocs. Since this app is building my own docs, and not other people's docs,
I chose "buildmydocs".

Sponsor
=======

If you find this useful, please do consider sponsoring me on GitHub.

https://github.com/sponsors/Mariatta


Heroku Setup
============


|Deploy|

.. |Deploy| image:: https://www.herokucdn.com/deploy/button.svg
   :target: https://heroku.com/deploy?template=https://github.com/mariatta/buildmydocs


Add the following config vars in Heroku.

``GH_SECRET``: The secret key from your GitHub App

``GH_APP_ID``: The ID of your GitHub App

``GH_PRIVATE_KEY``: The private key of your GitHub App. It looks like:

```
-----BEGIN RSA PRIVATE KEY-----
somereallylongtext
-----END RSA PRIVATE KEY-----
```

``RTD_AUTH``: Readthedocs Access Token.
