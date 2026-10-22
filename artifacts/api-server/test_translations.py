import unittest

from translations import SUPPORTED_LANGUAGES, UI_TRANSLATIONS


class TranslationCompletenessTest(unittest.TestCase):
    def test_every_locale_has_every_interface_key(self):
        expected = set(UI_TRANSLATIONS['en'])
        for language in SUPPORTED_LANGUAGES:
            with self.subTest(language=language):
                self.assertEqual(set(UI_TRANSLATIONS[language]), expected)

    def test_no_locale_ships_placeholder_copy(self):
        for language, copy in UI_TRANSLATIONS.items():
            for key, value in copy.items():
                with self.subTest(language=language, key=key):
                    self.assertTrue(value.strip() or key in {'ui_title_before', 'ui_title_after'})
                    self.assertNotEqual(value.split(': ', 1)[-1], key[3:].replace('_', ' '))
                    self.assertTrue(all(ord(ch) < 0x0400 or ord(ch) > 0x04FF for ch in value), 'Cyrillic character in copy')


if __name__ == '__main__':
    unittest.main()
