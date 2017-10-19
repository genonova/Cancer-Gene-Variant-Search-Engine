import logging, traceback


class MiRNASource:
    LOGGER = logging.getLogger('search_mirna')
    META = {}

    @staticmethod
    def search_mirna(mirna):
        MiRNASource.LOGGER.warning('Call to unimplemented search_mirna method \n %s' % traceback.format_stack())
        return {}

    @staticmethod
    def update_source():
        return False
