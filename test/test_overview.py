import unittest
from unittest.mock import patch

from gdo.connect.method.overview import overview


class ConnectOverviewTest(unittest.TestCase):

    @patch('gdo.connect.method.overview.overview.render_autojoin_channels', return_value='')
    @patch('gdo.connect.method.overview.t', side_effect=lambda key, *_: key)
    def test_connector_card_explains_the_gateway_and_escapes_its_name(self, translate, _):
        class Connector:
            def get_name(self):
                return 'irc'

            def render_user_connect_help(self):
                return 'ircs://irc.example.test:6697'

            def render_user_command_help(self):
                return '$help'

        class Server:
            def get_connector(self):
                return Connector()

            def get_name(self):
                return '<test-network>'

            def get_username(self):
                return 'Mira'

            def get_trigger(self):
                return '$'

            def get_connector_name(self):
                return 'irc'

        card = overview.render_server_card(Server())
        self.assertIn('&lt;test-network&gt;', card)
        translate.assert_any_call('connect_card_identity', ('Mira', '$'))
        self.assertIn('<code>$help</code>', card)

    @patch('gdo.connect.method.overview.overview.render_autojoin_channels', return_value='')
    @patch('gdo.connect.method.overview.t', side_effect=lambda key, *_: key)
    def test_connector_card_omits_an_empty_command_hint(self, _, __):
        class Connector:
            def get_name(self):
                return 'web'

            def render_user_connect_help(self):
                return 'Use this website'

            def render_user_command_help(self):
                return ''

        class Server:
            def get_connector(self):
                return Connector()

            def get_name(self):
                return 'Web'

            def get_username(self):
                return 'Dog'

            def get_trigger(self):
                return '!'

            def get_connector_name(self):
                return 'web'

        card = overview.render_server_card(Server())
        self.assertNotIn('<code>', card)

    @patch('gdo.connect.method.overview.t', side_effect=lambda key, *_: key)
    def test_connector_group_has_one_explanation_and_all_its_servers(self, _):
        class Connector:
            def get_name(self):
                return 'irc'

            def render_user_connect_help(self):
                return 'ircs://irc.example.test:6697'

            def render_user_command_help(self):
                return '$help'

        class Server:
            def __init__(self, name):
                self.name = name

            def get_connector(self):
                return Connector()

            def get_name(self):
                return self.name

            def get_username(self):
                return 'Mira'

            def get_trigger(self):
                return '$'

            def get_connector_name(self):
                return 'irc'

            def query_channels(self):
                return []

        group = overview.render_connector_group('irc', [Server('One'), Server('Two')])
        self.assertEqual(1, group.count('connect_description_irc'))
        self.assertIn('One', group)
        self.assertIn('Two', group)

    @patch('gdo.connect.method.overview.t', side_effect=lambda key, *_: key)
    def test_autojoin_channels_render_as_a_server_scoped_list(self, _):
        class Channel:
            def __init__(self, name):
                self.name = name

            def get_name(self):
                return self.name

            def render_name(self):
                return f'Display {self.name}'

        with patch.object(overview, 'autojoin_channels', return_value=[Channel('#alpha'), Channel('#beta')]):
            rendered = overview.render_autojoin_channels(object())
        self.assertIn('connect_autojoin', rendered)
        self.assertIn('Display #alpha', rendered)
        self.assertIn('Display #beta', rendered)

    def test_autojoin_channels_read_the_channel_database_field_for_every_connector(self):
        class Channel:
            def __init__(self, enabled):
                self.enabled = enabled

            def gdo_val(self, key):
                self.key = key
                return self.enabled

        class Server:
            def get_connector_name(self):
                return 'telegram'

            def query_channels(self):
                return [Channel('1'), Channel('0')]

        channels = overview.autojoin_channels(Server())
        self.assertEqual(1, len(channels))
        self.assertEqual('1', channels[0].enabled)

    @patch('gdo.connect.method.overview.t', side_effect=lambda key, *_: key)
    def test_discord_shows_all_known_channels(self, _):
        class Channel:
            def __init__(self, name):
                self.name = name

            def get_name(self):
                return self.name

        class Server:
            def get_connector_name(self):
                return 'discord'

            def query_channels(self):
                return [Channel('general'), Channel('quiet-room')]

        rendered = overview.render_autojoin_channels(Server())
        self.assertIn('connect_known_channels', rendered)
        self.assertIn('general', rendered)
        self.assertIn('quiet-room', rendered)
