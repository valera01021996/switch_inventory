import re
from base import NetmikoBase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class H3C(NetmikoBase):
    def get_version(self):
        pass

    def get_serial(self):
        pass
    
    def get_interfaces(self):
        pass