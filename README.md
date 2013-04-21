![Vogeltron: a bot for sports subreddit](header.png)

[![Build Status](https://travis-ci.org/kyleconroy/sfgiantsbot.png?branch=master)](https://travis-ci.org/kyleconroy/vogeltron)

A Reddit bot for posting MLB game schedules, league standings, and gameday
threads. Currently serving duty in /r/SFGiants. Built to run on Python 3.3 and
Heroku.

## History

While Vogeltron was built for the [San Francisco Giants subreddit][sr], it will
work for any MLB team. 

[sr]: http://www.reddit.com/r/sfgiants

## Deploying Vogeltron

Before deploying Vogeltron, you'll need [git][git], the [Heroku
toolbet][heroku], and a [Heroku account][account].  Inside the Vogeltron
directory run

    $ heroku create

Next, you'll need to configure Vogeltron. These are the settings for the
Giants, please change them for your team.

```
$ heroku config:add VOGELTRON_USERNAME=redditbot
$ heroku config:add VOGELTRON_PASSWORD=supersecret
$ heroku config:add VOGELTRON_SUBREDDIT=SFGiants
$ heroku config:add VOGELTRON_TEAM=Giants
```

The `VOGELTRON_TEAM` value can be either the full name (San Francisco Giants)
or just the team name (Giants) as seen in [this list on ESPN][espn].

To get league standings and team schedules to show up in your subreddit's side
bar, add the following markdown to your sidebar

```markdown
[](/statsstart)
[](/statsend)
```

Add the [Heroku Scheduler Add-on][sched] to your app (Don't worry, it's free).

    $ heroku addons:add scheduler:standard

Next, [you'll need to schedule Vogeltron][setup] to run this task every 10
minutes:

    python -m vogeltron.bot

Once finished, just deploy to Heroku.

    $ git push heroku master

Your personal Vogeltron is now up and running.

[espn]: http://espn.go.com/mlb/teams
[git]: http://git-scm.com/downloads
[heroku]: https://toolbelt.herokuapp.com
[account]: https://id.heroku.com/signup
[sched]: https://addons.heroku.com/scheduler
[setup]: https://devcenter.heroku.com/articles/scheduler#scheduling-jobs


## Development

Pull requests are always welcome. Please make sure the tests pass, and any new
functionality has tests. To install and test locally, just run:

``` 
$ make install test
```


## Multiple Deployment

We have multiple subreddits using Vogeltron. Instead of having to push changes
manually to each bot, we've automated this process:

```js
{
  "raven": "SENTRY_API_KEY"
  "heroku": "HEROKU_API_KEY",
  "subreddits": [
    {
      "name": "sfgiants",
      "team": "Giants",
      "username": "bot",
      "password": "password"
    },
    ...
  ]
}
```

## Acknowledgements

- [Justin Crisostomo](justincrisostomo.com) for the awesome Vogeltron image
