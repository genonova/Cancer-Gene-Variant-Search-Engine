from source_microrna import MicroRNA
from source_target_scan import TargetScan

from functools import partial

import redis, json, time, multiprocessing.pool, multiprocessing

REDIS_SEARCH = redis.StrictRedis(host='localhost', port=6379, db=7)
MIRNA_SOURCES = [MicroRNA, TargetScan]

class NoDaemonProcess(multiprocessing.Process):
    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
class Pool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess

def search_mirnas(mirnas):
    p = Pool(3)
    res = multiprocessing.Manager().dict()
    search_partial = partial(search_mirna, res)
    p.map(search_partial, mirnas)
    # for mirna in mirnas:
    #     res[mirna] = search_mirna(mirna)
    p.close()
    p.join()
    return res


def search_mirna(res, mirna):
    res[mirna] = {}
    if mirna:
        p = Pool(3)
        search_result = multiprocessing.Manager().dict()
        search_partial = partial(search_mirna_source, mirna, search_result)
        p.map(search_partial, MIRNA_SOURCES)
        p.close()
        p.join()
        # REDIS_SEARCH.set(mirna, json.dumps(search_result), ex=20736000)  # TODO: Current: 1day
        res[mirna] = search_result.copy()


def search_mirna_source(mirna, search_result, source):
    result = {
        'meta': source.META,
        'result': '',
        'down_grade': False,
        'down_grade_mirna': ''
    }
    source_name = source.__name__.lower()
    mirna_no_dash = mirna.split('_')[0]
    mirna_array = mirna_no_dash.split('-')
    for i in range(len(mirna_array) - 1, 1, -1):
        mirna_fixed = '-'.join(mirna_array[0:i + 1])
        source_key = source_name + mirna_fixed
        cached_source = REDIS_SEARCH.get(source_key)
        if cached_source:
            print 'READ FROM REDIS CACHE'
            arr = json.loads(cached_source)
            if arr:
                result['result'] = json.loads(cached_source)
                break
            else:
                continue
        tmp = source.search_mirna(mirna_fixed)
        result['result'] = tmp
        if tmp:
            REDIS_SEARCH.set(source_key, json.dumps(tmp))
            if mirna != mirna_fixed:
                result['down_grade'] = True
                result['down_grade_mirna'] = mirna_fixed
            else:
                result['down_grade'] = False
            break
        else:
            REDIS_SEARCH.set(source_key, '[]')
        time.sleep(3)
    search_result[source_name] = result