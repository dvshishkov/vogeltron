import mock
import pytz
from vogeltron import bot
from vogeltron.baseball import Standing, Result, Game
from vogeltron.baseball import Team, Player, Pitcher
from nose.tools import assert_equals, assert_true, assert_false
from datetime import datetime, timezone

PACIFIC = pytz.timezone('US/Pacific')

sidebar = """
## Standings
| Team | W | L | W/L% | GB |
| ------ | ------ | ----- | ----- | ----- |
| San Francisco | 3 | 1 | .750 | -- |
| San Francisco | 3 | 1 | .750 | -- |

## Last 5 Games
| Date | vs. | W/L | Score |
| ------ | ------ | ----- | ----- |
| January 1 | LA Dodgers | W | 1-1 |

## Upcoming Games
| Date | Time | Opponent |
| ------ | ------ | ----- |
| January 2 | 12:00AM | vs LA Dodgers |

Last Updated @ 2013-04-06 12:31 AM
"""

nationals_sidebar = """**NL East Standings**

|        | W | L | PCT | GB | STRK |
| :---: |:---: | :---: | :---: | :---: | :---: |
| [](/WAS1) | 3 | 1 | .750 | -- | W2 |
| [](/NYM1) | 3 | 1 | .750 | -- | W2 |

Last Updated @ 2013-04-06 12:31 AM"""

markdown = """
[](/all_statsstart)
foo
[](/all_statsend)
"""

exp_markdown = """
[](/all_statsstart)
bar
[](/all_statsend)
"""


def test_update_description_amps():
    assert_equals("&", bot.update_standings("&amp;amp;amp;", 'bar').strip())


def test_update_description():
    assert_equals(exp_markdown.strip(),
                  bot.update_standings(markdown, 'bar').strip())


@mock.patch('vogeltron.bot.timestamp')
@mock.patch('vogeltron.baseball.current_standings')
@mock.patch('vogeltron.baseball.schedule')
def test_nationals_stats(_schedule, _standings, _timestamp):
    _timestamp.return_value = "2013-04-06 12:31 AM"
    _schedule.return_value = [mock.Mock(), mock.Mock()]
    _standings.return_value = [
        Standing('San Francisco', 'WSH', 3, 1, .75, 0.0, 'Won 2'),
        Standing('San Francisco', 'NYM', 3, 1, .75, 0.0, 'Won 2'),
    ]

    assert_equals(nationals_sidebar,
                  bot.all_stats('nationals', 'NATIONAL', 'EAST', 'foo'))


@mock.patch('vogeltron.bot.timestamp')
@mock.patch('vogeltron.baseball.current_standings')
@mock.patch('vogeltron.baseball.schedule')
def test_all_stats(_schedule, _standings, _timestamp):
    _timestamp.return_value = "2013-04-06 12:31 AM"
    _schedule.return_value = (
        [Result('LA Dodgers', datetime(2013, 1, 1), True, True, "1-1")],
        [Result('LA Dodgers', datetime(2013, 1, 2), True, None, "0-0")],
    )
    _standings.return_value = [
        Standing('San Francisco', 'SFG', 3, 1, .75, 0.0, 'Won 2'),
        Standing('San Francisco', 'SFG', 3, 1, .75, 0.0, 'Won 2'),
    ]

    assert_equals(sidebar.strip(),
                  bot.all_stats('default', 'NATIONAL', 'WEST', 'foo'))


def check_thread(start, end, opened):
    assert_equals(bot.thread_open(start, end), opened)


def test_thread_window():
    dt1 = datetime(2013, 4, 16, 12)
    dt2 = datetime(2013, 4, 17, 16)
    dt3 = datetime(2013, 4, 16, 7)
    dt4 = datetime(2013, 4, 16, 8)

    yield check_thread, dt1, dt2, False
    yield check_thread, dt1, dt3, False
    yield check_thread, dt1, dt4, True


def test_timestamp():
    zone = pytz.timezone('US/Pacific')

    assert ('PST' in bot.timestamp(zone) or
            'PDT' in bot.timestamp(zone))

teams = [
    Team('Giants', '4-2', [Player('Bar', 'P')],
         Pitcher('Zito', '1-0', 0.0)),
    Team('Rockies', '5-1', [Player('Foo', 'P')],
         Pitcher('Francis', '1-0', 1.5)),
]

game = Game(teams, datetime(2013, 4, 10, 2, 15, tzinfo=timezone.utc),
            '64 Clear')


@mock.patch('vogeltron.baseball.game_info')
def test_gameday_title(_game_info):
    _game_info.return_value = game

    title, _ = bot.gamethread_post('default', 'foo', PACIFIC)

    assert_equals(title, ("Gameday Thread 4/9/13: Rockies (Francis) "
                          "at Giants (Zito) (7:15PM)"))


@mock.patch('vogeltron.baseball.game_info')
def test_gameday_title_with_template(_game_info):
    _game_info.return_value = game

    title, _ = bot.gamethread_post('athletics', 'foo', PACIFIC)

    assert_equals(title, ("GAMEDAY THREAD 4/9/13: Rockies (5-1) @ "
                          "Giants (4-2)"))


def test_reddit_url():
    title = "Gameday Thread 4/9/13: Rockies at Giants (7:15 PM PST)"
    assert_equals(bot.post_url_prefix(title), "gameday_thread_4913")


def test_postgame_reddit_url():
    title = ("POSTGAME THREAD: 4/11 -- Giants vs Cubs -- Join the Giants "
             "game / baseball discussion and social thread!")

    assert_equals(bot.post_game_url_prefix(title),
                  "postgame_thread_411")


exp_post = """
| Giants (4-2) | Rockies (5-1) |
| ------ | ------ |
| **Zito**: 1-0 0.00 ERA | **Francis**: 1-0 1.50 ERA |
| **Giants Lineup** | **Rockies Lineup** |
| Bar P | Foo P |

| 64 Clear |
| ------ |

Last Updated @ foo
"""


exp_post_no_pitchers = """
| Giants (4-2) | Rockies (5-1) |
| ------ | ------ |
| **Giants Lineup** | **Rockies Lineup** |
| Bar P | Foo P |

| 64 Clear |
| ------ |

Last Updated @ foo
"""


@mock.patch('vogeltron.bot.timestamp')
@mock.patch('vogeltron.baseball.game_info')
def test_gameday_post(_game_info, _timestamp):
    _timestamp.return_value = 'foo'
    _game_info.return_value = game

    _, post = bot.gamethread_post('default', 'foo', PACIFIC)

    assert_equals(exp_post.strip(), post)


@mock.patch('vogeltron.bot.timestamp')
@mock.patch('vogeltron.baseball.game_info')
def test_gameday_post_no_pitchers(_game_info, _timestamp):
    teams = [
        Team('Giants', '4-2', [Player('Bar', 'P')], None),
        Team('Rockies', '5-1', [Player('Foo', 'P')], None),
    ]

    g = Game(teams,
             datetime(2013, 4, 10, 2, 15, tzinfo=timezone.utc),
             '64 Clear')

    _timestamp.return_value = 'foo'
    _game_info.return_value = g

    _, post = bot.gamethread_post('default', 'foo', PACIFIC)

    assert_equals(exp_post_no_pitchers.strip(), post)


@mock.patch.dict('os.environ', {'FOO': ''})
def test_enabled_true():
    assert_true(bot.enabled('FOO'))


@mock.patch.dict('os.environ', {'FOO': 'false'})
def test_enabled_false():
    assert_false(bot.enabled('FOO'))
