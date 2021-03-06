import os
from os import environ
import dj_database_url
from boto.mturk import qualification

import otree.settings

CHANNEL_ROUTING = 'italian_routing.channel_routing'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# the usual is : CHANNEL_ROUTING = 'italian_routing.channel_routing'


# the environment variable OTREE_PRODUCTION controls whether Django runs in
# DEBUG mode. If OTREE_PRODUCTION==1, then DEBUG=False


if environ.get('OTREE_PRODUCTION') not in {None, '', '0'}:
    DEBUG = False
else:
    DEBUG = True

ADMIN_USERNAME = 'admin'

# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

# don't share this with anybody.
SECRET_KEY = 'ksm@zv_ht*zw@lp-h6u_4%&g)sxiu16bykd_6+_$63+8-la+ma'

DATABASES = {
    'default': dj_database_url.config(
        # Rather than hardcoding the DB parameters here,
        # it's recommended to set the DATABASE_URL environment variable.
        # This will allow you to use SQLite locally, and postgres/mysql
        # on the server
        # Examples:
        # export DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
        # export DATABASE_URL=mysql://USER:PASSWORD@HOST:PORT/NAME

        # fall back to SQLite if the DATABASE_URL env var is missing
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
    )
}

# AUTH_LEVEL:
# If you are launching a study and want visitors to only be able to
# play your app if you provided them with a start link, set the
# environment variable OTREE_AUTH_LEVEL to STUDY.
# If you would like to put your site online in public demo mode where
# anybody can play a demo version of your game, set OTREE_AUTH_LEVEL
# to DEMO. This will allow people to play in demo mode, but not access
# the full admin interface.

AUTH_LEVEL = environ.get('OTREE_AUTH_LEVEL')

# setting for integration with AWS Mturk
AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY')


# e.g. EUR, CAD, GBP, CHF, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True


# e.g. en, de, fr, it, ja, zh-hans
# see: https://docs.djangoproject.com/en/1.9/topics/i18n/#term-language-code
LANGUAGE_CODE = 'en'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree', 'radiogrid']

# SENTRY_DSN = ''

DEMO_PAGE_INTRO_TEXT = """
oTree games
"""

# from here on are qualifications requirements for workers
# see description for requirements on Amazon Mechanical Turk website:
# http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_QualificationRequirementDataStructureArticle.html
# and also in docs for boto:
# https://boto.readthedocs.org/en/latest/ref/mturk.html?highlight=mturk#module-boto.mturk.qualification

mturk_hit_settings = {
    'keywords': ['easy', 'bonus', 'choice', 'study'],
    'title': 'Title for your experiment',
    'description': 'Description for your experiment',
    'frame_height': 500,
    'preview_template': 'global/MTurkPreview.html',
    'minutes_allotted_per_assignment': 60,
    'expiration_hours': 7*24,  # 7 days
    # 'grant_qualification_id': 'YOUR_QUALIFICATION_ID_HERE',# to prevent retakes
    'qualification_requirements': [
        # qualification.LocaleRequirement("EqualTo", "US"),
        # qualification.PercentAssignmentsApprovedRequirement("GreaterThanOrEqualTo", 50),
        # qualification.NumberHitsApprovedRequirement("GreaterThanOrEqualTo", 5),
        # qualification.Requirement('YOUR_QUALIFICATION_ID_HERE', 'DoesNotExist')
    ]
}
# ROOM
ROOM_DEFAULTS = {}

ROOMS = [
    {
        'name': 'Bologna_lab',
        'display_name': 'BLESS',
        'participant_label_file': 'labels.txt',
    },
    {
        'name': 'econ_lab',
        'display_name': 'Experimental Economics Lab',
    },
]




# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = {
    'real_world_currency_per_point': 0.100,
    'participation_fee': 5.00,
    'doc': "",
    'mturk_hit_settings': mturk_hit_settings,
}


SESSION_CONFIGS = [
{
        'name': 'endsurvey',
        'display_name': 'endsurvey',
        'num_demo_participants': 12,
        'app_sequence': ['endsurvey', ],
},
    {
        'name': 'italianwage',
        'display_name': 'italianwage',
        'num_demo_participants': 12,
        'app_sequence': ['italianwage', 'endsurvey'],
        'treatment': 'all_taxes',
        # the allowed treatments are 'no_taxes', 'worker_tax', 'employer_tax', and 'all_taxes'
    },
    {
        'name': 'italiandirect',
        'display_name': 'italiandirect',
        'num_demo_participants': 12,
        'app_sequence': ['italiandirect', 'endsurvey'],
        'treatment': 'all_taxes',
        # the allowed treatments are 'no_taxes', 'worker_tax', 'employer_tax', and 'all_taxes'
    },
    {
        'name': 'italiantutorial',
        'display_name': 'italiantutorial',
        'num_demo_participants': 12,
        'treatment': 'all_taxes',
        # the allowed treatments are 'no_taxes', 'worker_tax', 'employer_tax', and 'all_taxes'
        'timeline': 'direct',
        # allowed timelines are 'direct' and 'wage' and they must correspond
        #  to the applications in the sequence, directauction and wageauction
        'app_sequence': ['italiantutorial', 'italiandirect', 'endsurvey'],
    },

]
SENTRY_DSN = 'http://168f82a499d74f10962bac1044751c17:acec14636580498f8d76c0f07e398cf5@sentry.otree.org/245'

# anything you put after the below line will override
# oTree's default settings. Use with caution.
otree.settings.augment_settings(globals())
