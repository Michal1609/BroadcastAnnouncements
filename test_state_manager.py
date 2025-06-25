import unittest
import os
import tempfile
import json
from datetime import datetime, timedelta
import state_manager


class TestStateManager(unittest.TestCase):
    """
    Unit testy pro state_manager.py s podporou více hlášení za den.
    Testuje novou logiku ukládání sady zpracovaných URL místo posledního souboru.
    """
    
    def setUp(self):
        """Nastavení testovacího prostředí před každým testem."""
        # Vytvoříme dočasný soubor pro testy
        self.test_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.test_file.close()
        
        # Vytvoříme dočasný soubor i pro starý formát
        self.test_file_old = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
        self.test_file_old.close()
        
        # Změníme cesty k souboru pro testy
        self.original_state_file = state_manager.STATE_FILE_NEW
        self.original_state_file_old = state_manager.STATE_FILE
        state_manager.STATE_FILE_NEW = self.test_file.name
        state_manager.STATE_FILE = self.test_file_old.name
    
    def tearDown(self):
        """Úklid po každém testu."""
        state_manager.STATE_FILE_NEW = self.original_state_file
        state_manager.STATE_FILE = self.original_state_file_old
        
        # Smažeme testovací soubory
        if os.path.exists(self.test_file.name):
            os.unlink(self.test_file.name)
        if os.path.exists(self.test_file_old.name):
            os.unlink(self.test_file_old.name)
    
    def test_get_processed_urls_empty_file(self):
        """Test čtení prázdného/neexistujícího souboru."""
        # Ujistíme se, že testovací soubor neexistuje
        if os.path.exists(self.test_file.name):
            os.unlink(self.test_file.name)
            
        urls = state_manager.get_processed_urls()
        self.assertIsInstance(urls, set)
        self.assertEqual(len(urls), 0)
    
    def test_save_and_get_single_url(self):
        """Test uložení a načtení jednoho URL."""
        test_url = "https://rozhlas.milesovice.cz/rozhlas/Hlášení 25.6.2.ogg"
        
        state_manager.save_processed_url(test_url)
        urls = state_manager.get_processed_urls()
        
        self.assertIn(test_url, urls)
        self.assertEqual(len(urls), 1)
    
    def test_save_multiple_urls_same_day(self):
        """Test uložení více URL za stejný den - hlavní test pro opravu."""
        test_urls = [
            "https://rozhlas.milesovice.cz/rozhlas/Hlášení 25.6.1.ogg",
            "https://rozhlas.milesovice.cz/rozhlas/Hlášení 25.6.2.ogg",
            "https://rozhlas.milesovice.cz/rozhlas/Hlášení 25.6.3.ogg"
        ]
        
        for url in test_urls:
            state_manager.save_processed_url(url)
        
        urls = state_manager.get_processed_urls()
        
        for url in test_urls:
            self.assertIn(url, urls)
        self.assertEqual(len(urls), 3)
    
    def test_duplicate_url_handling(self):
        """Test, že se neduplikují URL při opakovaném uložení."""
        test_url = "https://rozhlas.milesovice.cz/rozhlas/Hlášení 25.6.2.ogg"
        
        state_manager.save_processed_url(test_url)
        state_manager.save_processed_url(test_url)  # Duplikát
        state_manager.save_processed_url(test_url)  # Další duplikát
        
        urls = state_manager.get_processed_urls()
        self.assertEqual(len(urls), 1)
        self.assertIn(test_url, urls)
    
    def test_cleanup_old_urls(self):
        """Test mazání starých záznamů."""
        # Simulujeme staré záznamy
        old_data = {
            "processed_urls": [
                {
                    "url": "https://rozhlas.milesovice.cz/rozhlas/Hlášení 1.1.1.ogg",
                    "processed_at": (datetime.now() - timedelta(days=40)).isoformat()
                },
                {
                    "url": "https://rozhlas.milesovice.cz/rozhlas/Hlášení 25.6.1.ogg",
                    "processed_at": datetime.now().isoformat()
                }
            ]
        }
        
        with open(self.test_file.name, 'w', encoding='utf-8') as f:
            json.dump(old_data, f)
        
        state_manager.cleanup_old_urls(days=30)
        urls = state_manager.get_processed_urls()
        
        # Starý záznam by měl být smazán, nový zůstat
        self.assertEqual(len(urls), 1)
        self.assertIn("https://rozhlas.milesovice.cz/rozhlas/Hlášení 25.6.1.ogg", urls)
        self.assertNotIn("https://rozhlas.milesovice.cz/rozhlas/Hlášení 1.1.1.ogg", urls)
    
    def test_migrate_from_old_format(self):
        """Test migrace ze starého formátu (last_processed.txt) na nový."""
        # Vytvoříme starý soubor s ASCII textem
        old_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
        old_file.write("Hlaseni 25.6.1.ogg")  # Použijeme ASCII verzi
        old_file.close()
        
        try:
            # Test migrace
            migrated_urls = state_manager.migrate_from_old_format(old_file.name)
            
            self.assertIsInstance(migrated_urls, set)
            self.assertEqual(len(migrated_urls), 1)
            
            # URL by mělo být rekonstruováno z filename
            expected_url = "https://rozhlas.milesovice.cz/rozhlas/Hlaseni 25.6.1.ogg"
            self.assertIn(expected_url, migrated_urls)
        
        finally:
            os.unlink(old_file.name)


if __name__ == '__main__':
    unittest.main() 