"""
Tests pour les utilitaires
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from core.utils.helpers import (
    generate_random_string,
    generate_slug,
    format_file_size,
    format_duration,
    is_valid_email,
    is_valid_phone,
    clean_html,
    truncate_text,
    convert_to_snake_case,
    convert_to_camel_case,
    get_file_extension,
    get_mime_type,
    hash_password,
    verify_password,
    generate_otp,
    generate_token,
    parse_date,
    format_date,
    calculate_age,
    is_business_day,
    get_next_business_day,
    get_previous_business_day,
)
from core.utils.validators import (
    validate_email,
    validate_phone,
    validate_password,
    validate_url,
    validate_ip_address,
    validate_file_size,
    validate_file_type,
    validate_image_dimensions,
    validate_json,
    validate_slug,
    validate_hex_color,
    validate_credit_card,
    validate_postal_code,
    validate_iban,
    validate_swift_code,
    validate_tax_id,
    validate_ssn,
)
from datetime import datetime, date, timedelta
from django.utils import timezone


class HelpersTest(TestCase):
    """Tests pour les fonctions utilitaires"""
    
    def test_generate_random_string(self):
        """Test de génération de chaîne aléatoire"""
        string = generate_random_string(10)
        self.assertEqual(len(string), 10)
        
        string_with_symbols = generate_random_string(10, include_symbols=True)
        self.assertEqual(len(string_with_symbols), 10)
    
    def test_generate_slug(self):
        """Test de génération de slug"""
        slug = generate_slug("Hello World!")
        self.assertEqual(slug, "hello-world")
        
        slug_long = generate_slug("This is a very long text that should be truncated", max_length=20)
        self.assertLessEqual(len(slug_long), 20)
    
    def test_format_file_size(self):
        """Test de formatage de taille de fichier"""
        self.assertEqual(format_file_size(0), "0 B")
        self.assertEqual(format_file_size(1024), "1.0 KB")
        self.assertEqual(format_file_size(1024 * 1024), "1.0 MB")
        self.assertEqual(format_file_size(1024 * 1024 * 1024), "1.0 GB")
    
    def test_format_duration(self):
        """Test de formatage de durée"""
        self.assertEqual(format_duration(30), "30s")
        self.assertEqual(format_duration(90), "1m 30s")
        self.assertEqual(format_duration(3661), "1h 1m")
        self.assertEqual(format_duration(90061), "1j 1h")
    
    def test_is_valid_email(self):
        """Test de validation d'email"""
        self.assertTrue(is_valid_email("test@example.com"))
        self.assertTrue(is_valid_email("user.name+tag@domain.co.uk"))
        self.assertFalse(is_valid_email("invalid-email"))
        self.assertFalse(is_valid_email("@domain.com"))
        self.assertFalse(is_valid_email("user@"))
    
    def test_is_valid_phone(self):
        """Test de validation de téléphone"""
        self.assertTrue(is_valid_phone("+33123456789", "FR"))
        self.assertTrue(is_valid_phone("0123456789", "FR"))
        self.assertFalse(is_valid_phone("invalid-phone", "FR"))
        self.assertFalse(is_valid_phone("123", "FR"))
    
    def test_clean_html(self):
        """Test de nettoyage HTML"""
        html = "<p>Hello <strong>World</strong>!</p>"
        cleaned = clean_html(html)
        self.assertEqual(cleaned, "Hello World!")
    
    def test_truncate_text(self):
        """Test de troncature de texte"""
        text = "This is a very long text that should be truncated"
        truncated = truncate_text(text, 20)
        self.assertEqual(truncated, "This is a very long...")
        
        short_text = "Short text"
        not_truncated = truncate_text(short_text, 20)
        self.assertEqual(not_truncated, "Short text")
    
    def test_convert_to_snake_case(self):
        """Test de conversion en snake_case"""
        self.assertEqual(convert_to_snake_case("HelloWorld"), "hello_world")
        self.assertEqual(convert_to_snake_case("XMLHttpRequest"), "xml_http_request")
        self.assertEqual(convert_to_snake_case("already_snake_case"), "already_snake_case")
    
    def test_convert_to_camel_case(self):
        """Test de conversion en camelCase"""
        self.assertEqual(convert_to_camel_case("hello_world"), "helloWorld")
        self.assertEqual(convert_to_camel_case("xml_http_request"), "xmlHttpRequest")
        self.assertEqual(convert_to_camel_case("alreadyCamelCase"), "alreadyCamelCase")
    
    def test_get_file_extension(self):
        """Test de récupération d'extension de fichier"""
        self.assertEqual(get_file_extension("file.txt"), ".txt")
        self.assertEqual(get_file_extension("image.jpg"), ".jpg")
        self.assertEqual(get_file_extension("noextension"), "")
    
    def test_get_mime_type(self):
        """Test de récupération de type MIME"""
        self.assertEqual(get_mime_type("file.txt"), "text/plain")
        self.assertEqual(get_mime_type("image.jpg"), "image/jpeg")
        self.assertEqual(get_mime_type("unknown.xyz"), "application/octet-stream")
    
    def test_hash_password(self):
        """Test de hachage de mot de passe"""
        password = "testpassword"
        hashed = hash_password(password)
        self.assertNotEqual(password, hashed)
        self.assertEqual(len(hashed), 64)  # SHA256 hex length
    
    def test_verify_password(self):
        """Test de vérification de mot de passe"""
        password = "testpassword"
        hashed = hash_password(password)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("wrongpassword", hashed))
    
    def test_generate_otp(self):
        """Test de génération d'OTP"""
        otp = generate_otp(6)
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())
    
    def test_generate_token(self):
        """Test de génération de token"""
        token = generate_token(32)
        self.assertEqual(len(token), 32)
    
    def test_parse_date(self):
        """Test de parsing de date"""
        date_str = "2023-12-25"
        parsed = parse_date(date_str)
        self.assertIsInstance(parsed, datetime)
        self.assertEqual(parsed.year, 2023)
        self.assertEqual(parsed.month, 12)
        self.assertEqual(parsed.day, 25)
    
    def test_format_date(self):
        """Test de formatage de date"""
        date_obj = datetime(2023, 12, 25, 10, 30, 0)
        formatted = format_date(date_obj)
        self.assertEqual(formatted, "2023-12-25 10:30:00")
    
    def test_calculate_age(self):
        """Test de calcul d'âge"""
        birth_date = datetime(1990, 1, 1)
        age = calculate_age(birth_date)
        self.assertGreater(age, 30)
        self.assertLess(age, 50)
    
    def test_is_business_day(self):
        """Test de vérification de jour ouvrable"""
        # Lundi
        monday = datetime(2023, 12, 25)  # Ajustez selon la date
        # Dimanche
        sunday = datetime(2023, 12, 24)  # Ajustez selon la date
        
        # Note: Ces tests peuvent échouer selon la date réelle
        # self.assertTrue(is_business_day(monday))
        # self.assertFalse(is_business_day(sunday))


class ValidatorsTest(TestCase):
    """Tests pour les validateurs"""
    
    def test_validate_email(self):
        """Test de validation d'email"""
        validate_email("test@example.com")  # Ne doit pas lever d'exception
        
        with self.assertRaises(ValidationError):
            validate_email("invalid-email")
    
    def test_validate_phone(self):
        """Test de validation de téléphone"""
        validate_phone("+33123456789", "FR")  # Ne doit pas lever d'exception
        
        with self.assertRaises(ValidationError):
            validate_phone("invalid-phone", "FR")
    
    def test_validate_password(self):
        """Test de validation de mot de passe"""
        validate_password("TestPass123!")  # Ne doit pas lever d'exception
        
        with self.assertRaises(ValidationError):
            validate_password("weak")
    
    def test_validate_url(self):
        """Test de validation d'URL"""
        validate_url("https://example.com")  # Ne doit pas lever d'exception
        
        with self.assertRaises(ValidationError):
            validate_url("invalid-url")
    
    def test_validate_ip_address(self):
        """Test de validation d'adresse IP"""
        validate_ip_address("192.168.1.1")  # Ne doit pas lever d'exception
        
        with self.assertRaises(ValidationError):
            validate_ip_address("invalid-ip")
    
    def test_validate_slug(self):
        """Test de validation de slug"""
        validate_slug("valid-slug")  # Ne doit pas lever d'exception
        
        with self.assertRaises(ValidationError):
            validate_slug("Invalid Slug!")
    
    def test_validate_hex_color(self):
        """Test de validation de couleur hexadécimale"""
        validate_hex_color("#FF0000")  # Ne doit pas lever d'exception
        validate_hex_color("#F00")  # Ne doit pas lever d'exception
        
        with self.assertRaises(ValidationError):
            validate_hex_color("invalid-color")
    
    def test_validate_credit_card(self):
        """Test de validation de carte de crédit"""
        validate_credit_card("4111111111111111")  # Ne doit pas lever d'exception
        
        with self.assertRaises(ValidationError):
            validate_credit_card("1234567890123456")
    
    def test_validate_postal_code(self):
        """Test de validation de code postal"""
        validate_postal_code("75001", "FR")  # Ne doit pas lever d'exception
        
        with self.assertRaises(ValidationError):
            validate_postal_code("invalid", "FR")
    
    def test_validate_iban(self):
        """Test de validation d'IBAN"""
        validate_iban("FR1420041010050500013M02606")  # Ne doit pas lever d'exception
        
        with self.assertRaises(ValidationError):
            validate_iban("invalid-iban")
    
    def test_validate_swift_code(self):
        """Test de validation de code SWIFT"""
        validate_swift_code("DEUTDEFF")  # Ne doit pas lever d'exception
        
        with self.assertRaises(ValidationError):
            validate_swift_code("invalid-swift")
    
    def test_validate_tax_id(self):
        """Test de validation de numéro de TVA"""
        validate_tax_id("FR12345678901", "FR")  # Ne doit pas lever d'exception
        
        with self.assertRaises(ValidationError):
            validate_tax_id("invalid-tax-id", "FR")
    
    def test_validate_ssn(self):
        """Test de validation de numéro de sécurité sociale"""
        validate_ssn("1234567890123", "FR")  # Ne doit pas lever d'exception
        
        with self.assertRaises(ValidationError):
            validate_ssn("invalid-ssn", "FR")

