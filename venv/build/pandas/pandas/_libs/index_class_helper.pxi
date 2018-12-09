"""
Template for functions of IndexEngine subclasses.

WARNING: DO NOT edit .pxi FILE directly, .pxi is generated from .pxi.in
"""

#----------------------------------------------------------------------
# IndexEngine Subclass Methods
#----------------------------------------------------------------------


cdef class Float64Engine(IndexEngine):

    def _call_monotonic(self, values):
        return algos.is_monotonic_float64(values, timelike=False)

    def get_backfill_indexer(self, other, limit=None):
        return algos.backfill_float64(self._get_index_values(),
                                        other, limit=limit)

    def get_pad_indexer(self, other, limit=None):
        return algos.pad_float64(self._get_index_values(),
                                   other, limit=limit)

    cdef _make_hash_table(self, n):
        return _hash.Float64HashTable(n)
    cdef _get_index_values(self):
        return algos.ensure_float64(self.vgetter())

    cdef _maybe_get_bool_indexer(self, object val):
        cdef:
            ndarray[uint8_t, ndim=1, cast=True] indexer
            ndarray[intp_t, ndim=1] found
            ndarray[float64_t] values
            int count = 0


        # A view is needed for some subclasses, such as PeriodEngine:
        values = self._get_index_values().view('float64')
        indexer = values == val
        found = np.where(indexer)[0]
        count = len(found)

        if count > 1:
            return indexer
        if count == 1:
            return int(found[0])

        raise KeyError(val)



cdef class UInt64Engine(IndexEngine):

    def _call_monotonic(self, values):
        return algos.is_monotonic_uint64(values, timelike=False)

    def get_backfill_indexer(self, other, limit=None):
        return algos.backfill_uint64(self._get_index_values(),
                                        other, limit=limit)

    def get_pad_indexer(self, other, limit=None):
        return algos.pad_uint64(self._get_index_values(),
                                   other, limit=limit)

    cdef _make_hash_table(self, n):
        return _hash.UInt64HashTable(n)
    cdef _check_type(self, object val):
        hash(val)
        if util.is_bool_object(val):
            raise KeyError(val)
        elif util.is_float_object(val):
            raise KeyError(val)
    cdef _get_index_values(self):
        return algos.ensure_uint64(self.vgetter())

    cdef _maybe_get_bool_indexer(self, object val):
        cdef:
            ndarray[uint8_t, ndim=1, cast=True] indexer
            ndarray[intp_t, ndim=1] found
            ndarray[uint64_t] values
            int count = 0

        if not util.is_integer_object(val):
            raise KeyError(val)

        # A view is needed for some subclasses, such as PeriodEngine:
        values = self._get_index_values().view('uint64')
        indexer = values == val
        found = np.where(indexer)[0]
        count = len(found)

        if count > 1:
            return indexer
        if count == 1:
            return int(found[0])

        raise KeyError(val)



cdef class Int64Engine(IndexEngine):

    def _call_monotonic(self, values):
        return algos.is_monotonic_int64(values, timelike=False)

    def get_backfill_indexer(self, other, limit=None):
        return algos.backfill_int64(self._get_index_values(),
                                        other, limit=limit)

    def get_pad_indexer(self, other, limit=None):
        return algos.pad_int64(self._get_index_values(),
                                   other, limit=limit)

    cdef _make_hash_table(self, n):
        return _hash.Int64HashTable(n)
    cdef _check_type(self, object val):
        hash(val)
        if util.is_bool_object(val):
            raise KeyError(val)
        elif util.is_float_object(val):
            raise KeyError(val)
    cdef _get_index_values(self):
        return algos.ensure_int64(self.vgetter())

    cdef _maybe_get_bool_indexer(self, object val):
        cdef:
            ndarray[uint8_t, ndim=1, cast=True] indexer
            ndarray[intp_t, ndim=1] found
            ndarray[int64_t] values
            int count = 0

        if not util.is_integer_object(val):
            raise KeyError(val)

        # A view is needed for some subclasses, such as PeriodEngine:
        values = self._get_index_values().view('int64')
        indexer = values == val
        found = np.where(indexer)[0]
        count = len(found)

        if count > 1:
            return indexer
        if count == 1:
            return int(found[0])

        raise KeyError(val)



cdef class ObjectEngine(IndexEngine):

    def _call_monotonic(self, values):
        return algos.is_monotonic_object(values, timelike=False)

    def get_backfill_indexer(self, other, limit=None):
        return algos.backfill_object(self._get_index_values(),
                                        other, limit=limit)

    def get_pad_indexer(self, other, limit=None):
        return algos.pad_object(self._get_index_values(),
                                   other, limit=limit)

    cdef _make_hash_table(self, n):
        return _hash.PyObjectHashTable(n)
