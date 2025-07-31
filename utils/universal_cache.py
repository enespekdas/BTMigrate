class UniversalCache:
    def __init__(self):
        self._raw_data = {}   # Örn: { "ManagedSystem": [...] }
        self._indexes = {}    # Örn: { "ManagedSystem:Name": { name: obj }, "ManagedAccount:Username": { ... } }

    def cache_data(self, category: str, data: list):
        self._raw_data[category] = data

    def get_cached_data(self, category: str):
        return self._raw_data.get(category, [])

    def build_index(self, category: str, key_field: str):
        key = f"{category}:{key_field}"
        data = self.get_cached_data(category)
        self._indexes[key] = {
            str(item.get(key_field)).lower(): item
            for item in data if item.get(key_field)
        }

    def get_by_key(self, category: str, key_field: str, value: str):
        index_key = f"{category}:{key_field}"
        return self._indexes.get(index_key, {}).get(value.lower())

    def clear(self):
        self._raw_data.clear()
        self._indexes.clear()


# ✅ Global cache nesnesi (tüm projede ortak kullanılmalı)
GLOBAL_CACHE = UniversalCache()
