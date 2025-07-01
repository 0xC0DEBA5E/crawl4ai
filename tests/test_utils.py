import unittest

from crawl4ai.utils import is_external_url, normalize_url, get_base_domain


class TestNormalizeUrl(unittest.TestCase):
    def test_normalize_url(self):
        test_cases = [
            # href, base_url, expected_result
            ("https://example.com", "https://example.com", "https://example.com/"),
            ("http://example.com", "https://otherdomain.com", "http://example.com/"),
            ("https://example.com:443", "https://otherdomain.com", "https://example.com/"),
            ("https://example.com:8443", "https://otherdomain.com", "https://example.com:8443/"),
            ("http://example.com:80", "https://otherdomain.com", "http://example.com/"),
            ("https://example.com/path?query=1", "https://otherdomain.com", "https://example.com/path?query=1"),
            ("?q", "https://example.com", "https://example.com/?q="),
            ("?b=1&a=0&c=2", "https://example.com", "https://example.com/?a=0&b=1&c=2"),
            ("?multi=2&multi=1", "https://example.com", "https://example.com/?multi=2&multi=1"),
            ("?multi=2,1", "https://example.com", "https://example.com/?multi=2%2C1"),
            ("?multi[0]=2&multi[1]=1", "https://example.com", "https://example.com/?multi%5B0%5D=2&multi%5B1%5D=1"),
            ("?multi%5B0%5D=2&multi%5B1%5D=1", "https://example.com", "https://example.com/?multi%5B0%5D=2&multi%5B1%5D=1"),
            ("?query=1#fragment", "https://example.com", "https://example.com/?query=1#fragment"),
            ("?query=1#fragment", "https://example.com/page.html", "https://example.com/page.html?query=1#fragment"),
            ("?query=1#fragment", "https://example.com/path/", "https://example.com/path/?query=1#fragment"),
            ("https://example.com/path#fragment", "https://otherdomain.com", "https://example.com/path#fragment"),
            ("https://user:password@example.com", "https://otherdomain.com", "https://user:password@example.com/"),
            ("https://user:password@example.com:8443", "https://otherdomain.com", "https://user:password@example.com:8443/"),
            ("https://example.com:8080/path", "https://otherdomain.com", "https://example.com:8080/path"),
            ("http://example.com:8888/path/", "https://otherdomain.com", "http://example.com:8888/path/"),
            ("//example.com/path", "https://otherdomain.com", "https://example.com/path"),
            ("#fragment", "https://example.com/page", "https://example.com/page#fragment"),
            ("relative/path", "https://example.com/", "https://example.com/relative/path"),
            ("./relative/path", "https://example.com/base/", "https://example.com/base/relative/path"),
            ("../parent/path", "https://example.com/base/current/", "https://example.com/base/parent/path"),
            # Special protocols test cases
            ("tel:+1234567890", "https://example.com", "tel:+1234567890"),
            ("ftp://ftp.example.com/file.txt", "https://example.com", "ftp://ftp.example.com/file.txt"),
            ("file:///path/to/local/file.txt", "https://example.com", "file:///path/to/local/file.txt"),
            ("data:text/plain;base64,SGVsbG8sIFdvcmxkIQ==", "https://example.com",
             "data:text/plain;base64,SGVsbG8sIFdvcmxkIQ=="),
            ("javascript:alert('Hello')", "https://example.com", "javascript:alert('Hello')"),
            ("  tel:+1234567890  ", "https://example.com", "tel:+1234567890"),
            ("FTP://ftp.example.com", "https://example.com", "ftp://ftp.example.com/"),
            ("javascript:", "https://example.com", "javascript:"),
            ("tel:+1234567890?ext=123", "https://example.com", "tel:+1234567890?ext=123"),
            ("mailto:user@example.com", "https://example.com", "mailto:user@example.com"),
        ]
        for href, base_url, expected in test_cases:
            with self.subTest():
                result = normalize_url(href=href, base_url=base_url)
                self.assertEqual(expected, result,
                                 f"For href='{href}' base_url='{base_url}': expected {expected}, got {result}")
        # test for removing query parameters
        with self.subTest():
            href = "https://example.com/path?query=1&b=2&c=3"
            base_url = "https://example.com"
            expected = "https://example.com/path?query=1"
            result = normalize_url(href=href, base_url=base_url, params_to_remove=['b', 'c'])
            self.assertEqual(expected, result,
                             f"For href='{href}' base_url='{base_url}': expected {expected}, got {result}")
        # test for removing query parameters and fragments
        with self.subTest():
            href = "https://example.com/path?query=1&b=2&c=3#fragment"
            base_url = "https://example.com"
            expected = "https://example.com/path?query=1"
            result = normalize_url(href=href, base_url=base_url, params_to_remove=['b', 'c'], remove_fragments=True)
            self.assertEqual(expected, result,
                             f"For href='{href}' base_url='{base_url}': expected {expected}, got {result}")

class TestIsExternalUrl(unittest.TestCase):
    def test_is_external_url(self):
        test_cases = [
            # base_url, url, expected_result
            ("example.com", "https://otherdomain.com", True),
            ("www.example.com", "http://example.com", True),
            ("example.com", "//otherdomain.com/path", True),
            ("example.com", "mailto:user@example.com", True),

            ("example.com", "https://example.com/page", False),
            ("example.com", "https://www.example.com/page", False),
            ("example.com", "https://sub.example.com", False),
            ("example.com", "https://user:password@example.com", False),
            ("example.com", "http://example.com", False),
            ("example.com", "http://www.example.com", False),
            ("example.com", "http://example.com:80", False),
            ("localhost", "http://localhost", False),
            ("example.com", "/relative/path", False),
            ("example.com", "//example.com/path", False),
            ("example.com", "https://example.com:8080/page", False),
            ("example.com", "https://example.com:8888", False),
            ("example.com", "https://example.com/page", False),
            ("example.com", "#fragment", False),
        ]

        for base_url, url, expected in test_cases:
            with self.subTest(base_url=base_url, url=url):
                result = is_external_url(url=url, base_domain=base_url)
                self.assertEqual(expected, result,
                                 f"For base_url='{base_url}', url='{url}': expected {expected}, got {result}")


class TestGetBaseDomain(unittest.TestCase):
    def test_get_base_domain(self):
        test_cases = [
            # url, expected_base_domain
            ("https://example.com/path/to/page", "example.com"),
            ("http://sub.example.com", "example.com"),
            ("http://sub2.sub.example.com", "example.com"),
            ("https://www.example.com", "example.com"),
            ("https://example.com:8080", "example.com"),
            ("http://localhost:8080", "localhost"),
            ("ftp://ftp.example.com/file.txt", "example.com"),
            ("//example.com/path", "example.com"),
            # relative links and special protocols
            ("relative/path", ""),
            ("#fragment", ""),
            ("./relative/path", ""),
            ("../parent/path", ""),
            ("mailto:user@example.com", ""),
            ("tel:+1234567890", ""),
            ("data:text/plain;base64,SGVsbG8sIFdvcmxkIQ==", ""),
            ("javascript:alert('Hello')", ""),
        ]
        for url, expected in test_cases:
            with self.subTest(url=url):
                result = get_base_domain(url)
                self.assertEqual(expected, result,
                                 f"For url='{url}': expected {expected}, got {result}")

if __name__ == "__main__":
    unittest.main()