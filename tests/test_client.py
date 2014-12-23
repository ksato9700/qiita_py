#
# Copyright 2014 Kenichi Sato <ksato9700@gmail.com>
#
from __future__ import print_function

from qiita_v2.client import QiitaClient
from qiita_v2.exception import QiitaApiException
import responses
import simplejson as json

from nose.tools import eq_, ok_

@responses.activate
def test_get_user():
    user_body = {
        u'items_count': 100,
        u'description': "my description",
        u'name': u'My Name',
        u'twitter_screen_name': u'my_twitter_screen_name',
        u'profile_image_url': u'https://0.gravatar.com/avatar/myusername.png',
        u'followees_count': 10,
        u'followers_count': 20,
        u'location': u'my location',
        u'github_login_name': u'my_github_login_name',
        u'facebook_id': u'my_facebook_id',
        u'organization': u'my_organization',
        u'id': u'myusername',
        u'website_url': 'http://example.com/my_website_url',
        u'linkedin_id': 'my_linkedin_id',
    }

    responses.add(responses.GET,
                  "https://qiita.com/api/v2/users/myusername",
                  status=200,
                  body = json.dumps(user_body),
                  content_type="application/json")

    access_token = 'my_access_token'
    client = QiitaClient(access_token=access_token)
    res = client.get_user('myusername')
    eq_(res.to_json(), user_body)

@responses.activate
def test_get_user_not_found():
    not_found_error = {
        u'message': u'Not found',
        u'type': u'not_found',
    }
    responses.add(responses.GET,
                  "https://qiita.com/api/v2/users/nobody",
                  status=404,
                  body = json.dumps(not_found_error),
                  content_type="application/json")

    access_token = 'my_access_token'
    client = QiitaClient(access_token=access_token)
    try:
        res = client.get_user('nobody')
    except QiitaApiException as e:
        eq_(e.args[0], not_found_error)
    else:
        ok_(False)

@responses.activate
def test_get_users():
    def gen_user(uid):
        return {
            u'items_count': 100+uid,
            u'description': "my description {}".format(uid),
            u'name': u'My Name {}'.format(uid),
            u'twitter_screen_name': u'my_twitter_screen_name_{}'.format(uid),
            u'profile_image_url': u'https://0.gravatar.com/avatar/myusername{}.png'.format(uid),
            u'followees_count': 10+uid,
            u'followers_count': 20+uid,
            u'location': u'my location {}'.format(uid),
            u'github_login_name': u'my_github_login_name_{}'.format(uid),
            u'facebook_id': u'my_facebook_id_{}'.format(uid),
            u'organization': u'my_organization_{}'.format(uid),
            u'id': u'myusername{}'.format(uid),
            u'website_url': 'http://example.com/my_website_url_{}'.format(uid),
            u'linkedin_id': 'my_linkedin_id_{}'.format(uid),
        }
    users = [gen_user(uid) for uid in range(20)]

    total_count = 60004
    link = {
        u'first': u'https://qiita.com/api/v2/users?page=1',
        u'next': u'https://qiita.com/api/v2/users?page=2',
        u'last': u'https://qiita.com/api/v2/users?page={}'.format(1+total_count/20),
    }
    link_string = u", ".join(['<{}>; rel="{}"'.format(link[key], key) for key in link.keys()])

    responses.add(responses.GET,
                  "https://qiita.com/api/v2/users",
                  status=200,
                  body = json.dumps(users),
                  adding_headers={
                      u'Link': link_string,
                      u'Total-Count': str(total_count),
                  },
                  content_type="application/json")

    access_token = 'my_access_token'
    client = QiitaClient(access_token=access_token)
    res = client.list_users()
    eq_(res.to_json(), users)
    eq_(res.result_count, str(total_count))
    eq_(res.links, link)

