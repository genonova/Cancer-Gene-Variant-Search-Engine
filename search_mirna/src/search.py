from source_mirna_source import MiRNASource
from source_microrna import MicroRNA
from source_target_scan import TargetScan

import redis, json

REDIS_SEARCH = redis.StrictRedis(host='localhost', port=6379, db=7)
MIRNA_SOURCES = [MicroRNA, TargetScan]


def search_mirnas(mirnas):
    res = {}
    for mirna in mirnas:
        res[mirna] = search_mirna(mirna)
    return res


def search_mirna(mirna):
    search_result = REDIS_SEARCH.get(mirna)
    if search_result:
        print 'READ FROM REDIS CACHE'
        return json.loads(search_result)
    search_result = {}
    for source in MIRNA_SOURCES:
        search_result[source.__name__.lower()] = {
            'meta': source.META,
            'result': source.search_mirna(mirna)
        }
    # save to redis
    REDIS_SEARCH.set(mirna, json.dumps(search_result), ex=2073600)  # TODO: Current: 1day
    return search_result
