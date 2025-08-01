# utils/universal_cache.py

from typing import Any, Dict, List, Optional


class UniversalCache:
    def __init__(self):
        self._raw_data: Dict[str, List[Dict]] = {}
        self._indexes: Dict[str, Dict[str, Dict[str, Dict]]] = {}

    def cache_data(self, category: str, data: List[Dict]):
        """Ham veriyi cache'e yaz (örn: 'ManagedSystems')"""
        self._raw_data[category] = data

    def get_cached_data(self, category: str) -> List[Dict]:
        """Cache'teki ham veriyi getir"""
        return self._raw_data.get(category, [])

    def build_index(self, category: str, key_field: str):
        """
        Belirli bir kategori (örn: ManagedSystems) için
        key_field'e göre index oluştur (örn: Name, IPAddress)
        """
        index_key = f"{category}:{key_field}"
        data = self.get_cached_data(category)

        self._indexes.setdefault(category, {})[key_field] = {
            str(item.get(key_field)).lower(): item
            for item in data if item.get(key_field)
        }

    def get_by_key(self, category: str, key_field: str, value: str) -> Optional[Dict]:
        """
        İndexlenmiş veriden, key_field'e göre lookup yapar.
        Örn: get_by_key("ManagedSystems", "IPAddress", "192.168.1.10")
        """
        index = self._indexes.get(category, {}).get(key_field, {})
        return index.get(str(value).lower())

    def clear(self):
        self._raw_data.clear()
        self._indexes.clear()
        
    def get_all_by_key(self, category: str) -> List[Dict]:
        """Belirtilen kategoriye ait tüm ham veriyi getirir"""
        return self._raw_data.get(category, [])