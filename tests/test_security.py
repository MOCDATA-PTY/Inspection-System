"""
Security Testing Script
Tests all implemented security features
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from django.test import RequestFactory
from main.middleware import SecurityHeadersMiddleware
from main.decorators import ratelimit
from main.security_utils import validate_file_upload, sanitize_filename
from django.core.files.uploadedfile import SimpleUploadedFile


def test_environment_variables():
    """Test that environment variables are properly loaded"""
    print("\n[TEST] Environment Variables")
    
    assert settings.DEBUG == False, "DEBUG should be False"
    assert 'insecure' not in settings.SECRET_KEY.lower() or len(settings.SECRET_KEY) > 50, "SECRET_KEY should be secure"
    assert '*' not in settings.ALLOWED_HOSTS, "ALLOWED_HOSTS should not contain wildcards"
    
    print("  [OK] DEBUG is False")
    print("  [OK] SECRET_KEY is configured")
    print("  [OK] ALLOWED_HOSTS is restricted")
    return True


def test_security_headers():
    """Test that security headers middleware is working"""
    print("\n[TEST] Security Headers Middleware")
    
    factory = RequestFactory()
    request = factory.get('/')
    
    # Create a simple response
    from django.http import HttpResponse
    response = HttpResponse("Test")
    
    # Apply security headers middleware
    middleware = SecurityHeadersMiddleware(lambda r: response)
    response = middleware(request)
    
    # Check headers
    assert 'Content-Security-Policy' in response, "CSP header missing"
    assert 'X-Content-Type-Options' in response, "X-Content-Type-Options missing"
    assert 'X-Frame-Options' in response, "X-Frame-Options missing"
    assert 'Referrer-Policy' in response, "Referrer-Policy missing"
    assert 'Permissions-Policy' in response, "Permissions-Policy missing"
    
    print("  [OK] Content-Security-Policy header present")
    print("  [OK] X-Content-Type-Options header present")
    print("  [OK] X-Frame-Options header present")
    print("  [OK] Referrer-Policy header present")
    print("  [OK] Permissions-Policy header present")
    return True


def test_file_upload_validation():
    """Test file upload validation"""
    print("\n[TEST] File Upload Validation")
    
    # Test valid file
    valid_file = SimpleUploadedFile("test.pdf", b"fake pdf content", content_type="application/pdf")
    valid_file.size = 1024  # 1KB
    
    try:
        validate_file_upload(valid_file)
        print("  [OK] Valid PDF file accepted")
    except Exception as e:
        print(f"  [FAIL] Valid file rejected: {e}")
        return False
    
    # Test file too large
    large_file = SimpleUploadedFile("large.pdf", b"x" * (51 * 1024 * 1024), content_type="application/pdf")
    large_file.size = 51 * 1024 * 1024  # 51MB
    
    try:
        validate_file_upload(large_file)
        print("  [FAIL] Oversized file was accepted")
        return False
    except Exception:
        print("  [OK] Oversized file rejected")
    
    # Test invalid extension
    invalid_file = SimpleUploadedFile("test.exe", b"fake exe", content_type="application/x-msdownload")
    invalid_file.size = 1024
    
    try:
        validate_file_upload(invalid_file)
        print("  [FAIL] Invalid file type was accepted")
        return False
    except Exception:
        print("  [OK] Invalid file type rejected")
    
    return True


def test_filename_sanitization():
    """Test filename sanitization"""
    print("\n[TEST] Filename Sanitization")
    
    # Test path traversal attack
    dangerous_name = "../../../etc/passwd"
    safe_name = sanitize_filename(dangerous_name)
    assert '/' not in safe_name and '\\' not in safe_name, "Path separators not removed"
    print(f"  [OK] Path traversal blocked: '{dangerous_name}' -> '{safe_name}'")
    
    # Test null bytes
    null_name = "test\x00file.pdf"
    safe_name = sanitize_filename(null_name)
    assert '\x00' not in safe_name, "Null bytes not removed"
    print(f"  [OK] Null bytes removed: '{repr(null_name)}' -> '{safe_name}'")
    
    # Test normal filename
    normal_name = "My Document.pdf"
    safe_name = sanitize_filename(normal_name)
    assert safe_name == "My Document.pdf", "Normal filename changed"
    print(f"  [OK] Normal filename preserved: '{normal_name}'")
    
    return True


def test_csrf_protection():
    """Test CSRF protection settings"""
    print("\n[TEST] CSRF Protection")
    
    assert 'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE, "CSRF middleware not enabled"
    assert settings.CSRF_COOKIE_HTTPONLY == True, "CSRF cookie should be HTTPOnly"
    assert settings.CSRF_COOKIE_SAMESITE == 'Lax', "CSRF cookie should use SameSite=Lax"
    
    print("  [OK] CSRF middleware enabled")
    print("  [OK] CSRF cookie is HTTPOnly")
    print("  [OK] CSRF cookie uses SameSite=Lax")
    return True


def test_session_security():
    """Test session security settings"""
    print("\n[TEST] Session Security")
    
    assert settings.SESSION_COOKIE_HTTPONLY == True, "Session cookie should be HTTPOnly"
    assert settings.SESSION_COOKIE_SAMESITE == 'Lax', "Session cookie should use SameSite=Lax"
    assert settings.SESSION_COOKIE_AGE == 86400, "Session timeout should be 24 hours"
    
    print("  [OK] Session cookie is HTTPOnly")
    print("  [OK] Session cookie uses SameSite=Lax")
    print("  [OK] Session timeout is 24 hours")
    return True


def test_password_validation():
    """Test password validation settings"""
    print("\n[TEST] Password Validation")
    
    validators = settings.AUTH_PASSWORD_VALIDATORS
    assert len(validators) >= 4, "Should have at least 4 password validators"
    
    validator_names = [v['NAME'] for v in validators]
    assert any('MinimumLength' in name for name in validator_names), "Minimum length validator missing"
    assert any('CommonPassword' in name for name in validator_names), "Common password validator missing"
    
    print(f"  [OK] {len(validators)} password validators configured")
    print("  [OK] Minimum length validator enabled")
    print("  [OK] Common password validator enabled")
    return True


def run_all_tests():
    """Run all security tests"""
    print("="*60)
    print("SECURITY FEATURE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Security Headers", test_security_headers),
        ("File Upload Validation", test_file_upload_validation),
        ("Filename Sanitization", test_filename_sanitization),
        ("CSRF Protection", test_csrf_protection),
        ("Session Security", test_session_security),
        ("Password Validation", test_password_validation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"  [FAILED] {test_name}")
        except Exception as e:
            failed += 1
            print(f"  [ERROR] {test_name}: {e}")
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n[SUCCESS] All security features are working correctly!")
        return True
    else:
        print(f"\n[WARNING] {failed} test(s) failed. Please review the output above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
