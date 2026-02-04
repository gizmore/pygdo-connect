from gdo.base.GDO_Module import GDO_Module
from gdo.ui.GDT_Link import GDT_Link
from gdo.ui.GDT_Page import GDT_Page


class module_connect(GDO_Module):

    def gdo_init_sidebar(self, page: 'GDT_Page'):
        page._left_bar.add_field(GDT_Link().text('module_connect').href(self.href('overview')))
