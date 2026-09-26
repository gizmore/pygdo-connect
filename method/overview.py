from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Trans import t
from gdo.base.Util import html
from gdo.core.GDO_Server import GDO_Server
from gdo.message.GDT_HTML import GDT_HTML
from gdo.date.Time import Time
from gdo.table.MethodQueryTable import MethodQueryTable


class overview(MethodQueryTable):

    def gdo_cached(cls) -> int:
        return Time.ONE_HOUR

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_execute(self) -> GDT:
        from gdo.net.module_net import module_net

        net = module_net.instance()
        servers = GDO_Server.table().select().where('serv_enabled').order('serv_name').exec().fetch_all()
        groups = {}
        for server in servers:
            groups.setdefault(server.get_connector_name(), []).append(server)
        cards = ''.join(
            self.render_connector_group(connector_name, connector_servers)
            for connector_name, connector_servers in groups.items()
        )
        tcp_command = f'nc {Application.config("core.domain")} {net.cfg_port()}'
        return GDT_HTML().html(f'''\
<main class="connect-overview">
  <header class="connect-overview__hero">
    <p class="connect-overview__eyebrow">{html(t('connect_eyebrow'))}</p>
    <h1>{html(t('mt_connect_overview'))}</h1>
    <p>{html(t('connect_intro'))}</p>
  </header>
  <section class="connect-overview__tcp" aria-labelledby="connect-tcp-title">
    <div>
      <p class="connect-overview__eyebrow">{html(t('title_raw_tcp'))}</p>
      <h2 id="connect-tcp-title">{html(t('connect_tcp_title'))}</h2>
      <p>{html(t('connect_tcp_intro'))}</p>
    </div>
    <code>{html(tcp_command)}</code>
  </section>
  <section class="connect-overview__networks" aria-labelledby="connect-networks-title">
    <div class="connect-overview__section-heading">
      <div>
        <p class="connect-overview__eyebrow">{html(t('connect_networks_eyebrow'))}</p>
        <h2 id="connect-networks-title">{html(t('connect_networks_title'))}</h2>
      </div>
      <p>{html(t('connect_networks_intro'))}</p>
    </div>
    <div class="connect-overview__grid">{cards}</div>
  </section>
</main>''')

    @staticmethod
    def connector_description(connector_name: str) -> str:
        descriptions = {
            'bash': 'connect_description_bash',
            'discord': 'connect_description_discord',
            'irc': 'connect_description_irc',
            'lup': 'connect_description_lup',
            'slack': 'connect_description_slack',
            'tcp': 'connect_description_tcp',
            'telegram': 'connect_description_telegram',
            'web': 'connect_description_web',
            'websocket': 'connect_description_websocket',
        }
        return t(descriptions.get(connector_name, 'connect_description_generic'))

    @classmethod
    def render_connector_group(cls, connector_name: str, servers: list[GDO_Server]) -> str:
        cards = ''.join(cls.render_server_card(server) for server in servers)
        description = cls.connector_description(connector_name)
        return f'''\
<section class="connect-overview__connector-group">
  <header>
    <div>
      <p class="connect-overview__eyebrow">{html(t('connect_connector_eyebrow'))}</p>
      <h3>{html(connector_name)}</h3>
    </div>
    <p>{html(description)}</p>
  </header>
  <div class="connect-overview__grid">{cards}</div>
</section>'''

    @staticmethod
    def autojoin_channels(server: GDO_Server) -> list:
        return [channel for channel in server.query_channels()
                if channel.gdo_val('chan_autojoin') == '1']

    @staticmethod
    def listed_channels(server: GDO_Server) -> list:
        """Return the useful public channel list for one connector.

        Discord has no IRC-style join loop: its channel records are discovered
        from gateway events, so all known channels are useful to show.  Other
        connectors expose only their opted-in autojoin channels.
        """
        if getattr(server, 'get_connector_name', lambda: '')() == 'discord':
            return list(server.query_channels())
        return overview.autojoin_channels(server)

    @classmethod
    def render_autojoin_channels(cls, server: GDO_Server) -> str:
        channels = cls.listed_channels(server)
        if not channels:
            return ''
        title = 'connect_known_channels' if getattr(server, 'get_connector_name', lambda: '')() == 'discord' else 'connect_autojoin'
        names = ''.join(
            f'<li>{html(channel.render_name() if hasattr(channel, "render_name") else channel.get_name())}</li>'
            for channel in channels
        )
        return f'''\
<div class="connect-overview__autojoin">
  <strong>{html(t(title))}</strong>
  <ul>{names}</ul>
</div>'''

    @staticmethod
    def render_server_card(server: GDO_Server) -> str:
        connector = server.get_connector()
        connector_name = connector.get_name()
        connect_help = connector.render_user_connect_help()
        command_help = connector.render_user_command_help()
        command = f'<code>{html(command_help)}</code>' if command_help else ''
        identity = t('connect_card_identity', (server.get_username(), server.get_trigger()))
        autojoin = overview.render_autojoin_channels(server)
        return f'''\
<article class="connect-overview__card">
  <header>
    <h3>{html(server.get_name())}</h3>
    <span>{html(connector_name)}</span>
  </header>
  <p class="connect-overview__identity">{html(identity)}</p>
  <div class="connect-overview__address">{connect_help}</div>
  {autojoin}
  {command}
</article>'''
