import unittest

from zoo import catalogue, profiles_page


class ProfilesPageTest(unittest.TestCase):
    def test_shortcuts_name_real_profiles_and_specimens(self):
        self.assertEqual(profiles_page.check(catalogue.catalogue(), profiles_page.shortcuts()), [])

    def test_committed_page_is_current(self):
        page = profiles_page.render(catalogue.catalogue(), profiles_page.shortcuts())
        self.assertEqual(profiles_page.PAGE.read_text(), page,
                         'docs/PROFILES.md is stale: run python3 -m zoo.profiles_page')


if __name__ == '__main__':
    unittest.main()
