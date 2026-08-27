from gdo.base.GDO import GDO
from gdo.base.Query import Query
from gdo.base.Render import Mode
from gdo.base.Application import Application
from gdo.core.GDO_Server import GDO_Server
from gdo.base.GDT import GDT
from gdo.core.GDT_String import GDT_String
from gdo.date.Time import Time
from gdo.message.GDT_Paragraph import GDT_Paragraph
from gdo.table.GDT_Table import TableMode
from gdo.table.MethodQueryTable import MethodQueryTable
from gdo.ui.GDT_Panel import GDT_Panel
from gdo.core.GDT_Container import GDT_Container


class overview(MethodQueryTable):

    def gdo_cached(cls) -> int:
        return Time.ONE_HOUR

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_table_mode(self) -> TableMode:
        return TableMode.LIST

    def gdo_table(self) -> GDO:
        return GDO_Server.table()

    def gdo_table_query(self) -> Query:
        return GDO_Server.table().select().where('serv_enabled')

    def gdo_execute(self) -> GDT:
        from gdo.net.module_net import module_net

        net = module_net.instance()
        help_ = GDT_Panel().title('title_raw_tcp').text('info_raw_tcp', (
            Application.config('core.domain'),
            net.cfg_port(),
        ))
        result = GDT_Container().vertical()
        result.add_fields(help_, super().gdo_execute())
        return result

    def render_gdo(self, gdo: GDO, mode: Mode) -> any:
        return GDT_Paragraph().add_fields(
            gdo.column('serv_id'),
            gdo.column('serv_name'),
            GDT_String().val(' - '),
            GDT_String().val(gdo.get_connector().render_user_connect_help()),
            GDT_String().val(gdo.get_connector().render_user_command_help()),
        ).render_list()
