#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Validator - Comprehensive validation for venue data

Provides validation for:
- Phone numbers (Taiwan format)
- Email addresses
- URLs
- Capacity ranges
- Area measurements
- Required fields
- Data consistency
"""
import re
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class ValidationResult:
    """Validation result for a single field"""
    is_valid: bool
    field_name: str
    errors: List[str]
    warnings: List[str]


class DataValidator:
    """
    Comprehensive data validator for venue data

    Validation rules:
    - Phone: Taiwan format (+886-9-1234-5678 or 0912-345-678)
    - Email: Valid format, not a spam address
    - URL: Valid HTTP/HTTPS URL
    - Capacity: 5-5000 people
    - Area: 1-10000坪 or sqm
    """

    # Regex patterns
    PHONE_PATTERN = re.compile(
        r'^(\+886-)?\d{1,4}-\d{3,4}-\d{3,4}$|^0\d{1,3}-\d{3,4}-\d{3,4}$|^09\d{2}-\d{3}-\d{3}$'
    )
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    URL_PATTERN = re.compile(
        r'^https?://[^\s/$.?#].[^\s]*$'
    )

    # Spam email patterns
    SPAM_EMAIL_PATTERNS = [
        'no-reply',
        'noreply',
        'donotreply',
        '@spam.',
        '@temp.'
    ]

    # Validation ranges
    MIN_CAPACITY = 5
    MAX_CAPACITY = 5000
    MIN_AREA = 1
    MAX_AREA = 10000

    def __init__(self, strict: bool = True):
        """
        Initialize validator

        Args:
            strict: If True, all errors must be fixed
        """
        self.strict = strict

    def validate_all(self, venues: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Validate all venues

        Args:
            venues: List of venue dictionaries

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        all_errors = []

        for venue in venues:
            venue_id = venue.get('id', 'unknown')
            is_valid, errors, warnings = self.validate_venue(venue)

            if not is_valid:
                for error in errors:
                    all_errors.append(f"Venue {venue_id}: {error}")

            if warnings and self.strict:
                for warning in warnings:
                    all_errors.append(f"Venue {venue_id} (WARNING): {warning}")

        return len(all_errors) == 0, all_errors

    def validate_venue(self, venue: Dict) -> Tuple[bool, List[str], List[str]]:
        """
        Validate single venue

        Args:
            venue: Venue dictionary

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        # Check required fields
        required_fields = ['id', 'name', 'venueType', 'url']
        for field in required_fields:
            if field not in venue:
                errors.append(f"Missing required field: {field}")

        # Validate URL
        if 'url' in venue:
            is_valid, error = self.validate_url(venue['url'])
            if not is_valid:
                errors.append(error)

        # Validate contact (Phase 2: 支援新舊欄位)
        # 新欄位: contact.phone, contact.email
        # 舊欄位: contactPhone, contactEmail

        phone_found = False
        email_found = False

        # 先檢查新欄位
        if 'contact' in venue:
            contact = venue['contact']

            # Phone (new field)
            if 'phone' in contact:
                is_valid, error, warning = self.validate_phone(contact['phone'])
                if not is_valid:
                    errors.append(error)
                elif warning:
                    warnings.append(warning)
                phone_found = True

            # Email (new field)
            if 'email' in contact:
                is_valid, error = self.validate_email(contact['email'])
                if not is_valid:
                    errors.append(error)
                email_found = True

        # 如果新欄位沒有，檢查舊欄位（向後相容）
        if not phone_found and 'contactPhone' in venue:
            is_valid, error, warning = self.validate_phone(venue['contactPhone'])
            if not is_valid:
                errors.append(error)
            elif warning:
                warnings.append(warning)

        if not email_found and 'contactEmail' in venue:
            is_valid, error = self.validate_email(venue['contactEmail'])
            if not is_valid:
                errors.append(error)

        # Validate capacity
        if 'capacity' in venue:
            is_valid, error = self.validate_capacity(venue['capacity'])
            if not is_valid:
                errors.append(error)

        # Validate rooms
        if 'rooms' in venue:
            for i, room in enumerate(venue['rooms']):
                room_errors = self._validate_room(room, i)
                errors.extend(room_errors)

        # Validate address
        if 'address' in venue:
            is_valid, error = self.validate_address(venue['address'])
            if not is_valid:
                errors.append(error)

        return len(errors) == 0, errors, warnings

    def validate_phone(
        self,
        phone: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate phone number (Taiwan format)

        Valid formats:
        - +886-2-3366-4504
        - 02-3366-4504
        - 0912-345-678

        Args:
            phone: Phone number string

        Returns:
            Tuple of (is_valid, error_message, warning_message)
        """
        if not phone:
            return False, "Phone number is empty", None

        # Remove whitespace
        phone = phone.strip()

        # Check pattern
        if not self.PHONE_PATTERN.match(phone):
            return False, f"Invalid phone format: {phone}", None

        # Check for common issues
        if phone.startswith('0') and len(phone.replace('-', '')) < 10:
            return True, None, "Phone number might be incomplete"

        return True, None, None

    def validate_email(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email address

        Checks:
        - Valid format
        - Not a spam address

        Args:
            email: Email address

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email is empty"

        email = email.strip().lower()

        # Check pattern
        if not self.EMAIL_PATTERN.match(email):
            return False, f"Invalid email format: {email}"

        # Check spam patterns
        for spam_pattern in self.SPAM_EMAIL_PATTERNS:
            if spam_pattern in email:
                return False, f"Email appears to be spam/temporary: {email}"

        return True, None

    def validate_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate URL

        Args:
            url: URL string

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url:
            return False, "URL is empty"

        url = url.strip()

        # Check pattern
        if not self.URL_PATTERN.match(url):
            return False, f"Invalid URL format: {url}"

        # Parse URL
        try:
            parsed = urlparse(url)

            # Check scheme
            if parsed.scheme not in ['http', 'https']:
                return False, f"URL must use HTTP or HTTPS: {url}"

            # Check domain
            if not parsed.netloc:
                return False, f"URL missing domain: {url}"

        except Exception as e:
            return False, f"URL parsing error: {e}"

        return True, None

    def validate_capacity(self, capacity: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate capacity values

        Args:
            capacity: Capacity dictionary (e.g., {'theater': 400, 'classroom': 200})

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(capacity, dict):
            return False, "Capacity must be a dictionary"

        if not capacity:
            return True, None  # Empty capacity is OK

        for layout, value in capacity.items():
            if not isinstance(value, (int, float)):
                return False, f"Capacity '{layout}' must be a number"

            if value < self.MIN_CAPACITY or value > self.MAX_CAPACITY:
                return False, (
                    f"Capacity '{layout}' ({value}) outside valid range "
                    f"({self.MIN_CAPACITY}-{self.MAX_CAPACITY})"
                )

        return True, None

    def validate_area(self, area: Any, unit: str = '坪') -> Tuple[bool, Optional[str]]:
        """
        Validate area measurement

        Args:
            area: Area value (number or string)
            unit: Unit (坪, sqm)

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Convert to float
        try:
            area_value = float(area)
        except (TypeError, ValueError):
            return False, f"Area must be a number: {area}"

        # Check range
        if area_value < self.MIN_AREA or area_value > self.MAX_AREA:
            return False, (
                f"Area ({area_value}) outside valid range "
                f"({self.MIN_AREA}-{self.MAX_AREA})"
            )

        # Validate unit
        valid_units = ['坪', 'sqm', 'sqm', 'm²', '平方公尺', '平方公尺']
        if unit not in valid_units:
            return False, f"Invalid area unit: {unit}"

        return True, None

    def validate_address(self, address: str) -> Tuple[bool, Optional[str]]:
        """
        Validate address

        Args:
            address: Address string

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not address:
            return False, "Address is empty"

        address = address.strip()

        # Minimum length check
        if len(address) < 5:
            return False, f"Address too short: {address}"

        # Should contain Chinese characters or numbers
        if not re.search(r'[\u4e00-\u9fff0-9]', address):
            return False, f"Address should contain Chinese characters or numbers: {address}"

        return True, None

    def _validate_room(self, room: Dict, index: int) -> List[str]:
        """
        Validate single room

        Args:
            room: Room dictionary
            index: Room index

        Returns:
            List of errors
        """
        errors = []

        # Required fields
        if 'name' not in room:
            errors.append(f"Room {index}: Missing name")

        # Validate capacity
        if 'capacity' in room:
            capacity = room['capacity']

            # Can be dict or single value
            if isinstance(capacity, dict):
                is_valid, error = self.validate_capacity(capacity)
                if not is_valid:
                    errors.append(f"Room {index} ({room.get('name')}): {error}")
            elif isinstance(capacity, (int, float)):
                if capacity < self.MIN_CAPACITY or capacity > self.MAX_CAPACITY:
                    errors.append(
                        f"Room {index} ({room.get('name')}): "
                        f"Capacity {capacity} outside valid range"
                    )

        # Validate area
        if 'area' in room:
            unit = room.get('areaUnit', '坪')
            is_valid, error = self.validate_area(room['area'], unit)
            if not is_valid:
                errors.append(f"Room {index} ({room.get('name')}): {error}")

        return errors

    def validate_consistency(self, venue: Dict) -> Tuple[bool, List[str]]:
        """
        Validate data consistency across fields

        Checks:
        - Venue type matches rooms presence
        - Email domain matches website (optional)
        - Phone area code matches city (optional)

        Args:
            venue: Venue dictionary

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        # Check venue type vs rooms
        venue_type = venue.get('venueType', '')
        rooms = venue.get('rooms', [])

        if venue_type and not rooms:
            errors.append(f"Venue type '{venue_type}' but no rooms defined")

        # Check URL consistency
        url = venue.get('url', '')
        contact = venue.get('contact', {})
        email = contact.get('email', '')

        if url and email:
            # Extract domain from URL
            try:
                url_domain = urlparse(url).netloc
                email_domain = email.split('@')[-1]

                # Optional: Check if domains match
                # This is a warning, not an error
                if url_domain not in email_domain and email_domain not in url_domain:
                    pass  # Could add warning here
            except:
                pass

        return len(errors) == 0, errors


if __name__ == '__main__':
    # Test usage
    validator = DataValidator()

    # Test phone validation
    print("Testing phone validation:")
    test_phones = [
        '+886-2-3366-4504',  # Valid
        '02-3366-4504',      # Valid
        '0912-345-678',      # Valid
        '123',               # Invalid
        ''                   # Invalid
    ]

    for phone in test_phones:
        is_valid, error, warning = validator.validate_phone(phone)
        status = "[OK]" if is_valid else "[FAIL]"
        print(f"  {status} {phone}: {error or warning or 'OK'}")

    # Test email validation
    print("\nTesting email validation:")
    test_emails = [
        'test@example.com',    # Valid
        'no-reply@test.com',   # Invalid (spam)
        '',                    # Invalid
        'invalid-email'        # Invalid
    ]

    for email in test_emails:
        is_valid, error = validator.validate_email(email)
        status = "[OK]" if is_valid else "[FAIL]"
        print(f"  {status} {email}: {error or 'OK'}")

    # Test venue validation
    print("\nTesting venue validation:")
    test_venue = {
        'id': 1128,
        'name': '集思台大會議中心',
        'venueType': '會議中心',
        'url': 'https://www.meeting.com.tw/ntu/',
        'contact': {
            'phone': '+886-2-3366-4504',
            'email': 'ntu.service@meeting.com.tw'
        },
        'rooms': [
            {
                'name': '國際會議廳',
                'capacity': {'theater': 400},
                'area': 253.6,
                'areaUnit': '坪'
            }
        ]
    }

    is_valid, errors, warnings = validator.validate_venue(test_venue)
    print(f"  Valid: {is_valid}")
    if errors:
        print(f"  Errors: {errors}")
    if warnings:
        print(f"  Warnings: {warnings}")
