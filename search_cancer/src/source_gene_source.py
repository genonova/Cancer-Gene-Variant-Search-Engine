import logging, traceback

class GeneSource:
    logger = logging.getLogger('search_cancer')

    @staticmethod
    def search_variant(variant):
        GeneSource.logger.warning('Call to unimplemented search_variant method \n %s' % traceback.format_stack())
        return {}

    @staticmethod
    def search_gene(gene):
        GeneSource.logger.warning('Call to unimplemented search_gene method \n %s' % traceback.format_stack())
        return {}

    @staticmethod
    def search_transcript(transcript):
        GeneSource.logger.warning('Call to unimplemented search_transcript method \n %s' % traceback.format_stack())
        return {}

    @staticmethod
    def update_source():
        return False