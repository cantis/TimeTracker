#!/usr/bin/env python3
"""
Simple test script to validate the time formatting fix.
"""

import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from routes.home import format_time_for_display, parse_time_to_minutes
except ImportError:
    print("Could not import functions. Make sure you're running from the TimeTracker directory.")
    sys.exit(1)


def test_time_formatting():
    """Test time parsing and formatting functions."""

    # Test cases: [(input, expected_minutes, expected_display)]
    test_cases = [
        # Integer minutes past midnight
        (480, 480, '8:00 AM'),  # 8:00 AM
        (540, 540, '9:00 AM'),  # 9:00 AM
        (720, 720, '12:00 PM'),  # 12:00 PM (noon)
        (780, 780, '1:00 PM'),  # 1:00 PM
        (1020, 1020, '5:00 PM'),  # 5:00 PM
        (525, 525, '8:45 AM'),  # 8:45 AM
        # String "HH:MM" format
        ('8:00', 480, '8:00 AM'),
        ('9:00', 540, '9:00 AM'),
        ('12:00', 720, '12:00 PM'),
        ('13:00', 780, '1:00 PM'),
        ('17:00', 1020, '5:00 PM'),
        ('8:45', 525, '8:45 AM'),
        # Edge cases
        ('0:00', 0, '12:00 AM'),  # Midnight
        ('12:00', 720, '12:00 PM'),  # Noon
        ('23:59', 1439, '11:59 PM'),  # Almost midnight
    ]

    print('Testing time parsing and formatting functions...')
    print('=' * 60)

    all_passed = True

    for i, (input_value, expected_minutes, expected_display) in enumerate(test_cases, 1):
        # Test parsing
        parsed_minutes = parse_time_to_minutes(input_value)
        if parsed_minutes != expected_minutes:
            print(f'❌ Test {i} FAILED (parsing): {input_value} -> {parsed_minutes}, expected {expected_minutes}')
            all_passed = False
        else:
            print(f'✅ Test {i} PASSED (parsing): {input_value} -> {parsed_minutes}')

        # Test formatting
        formatted_display = format_time_for_display(input_value)
        if formatted_display != expected_display:
            print(
                f'❌ Test {i} FAILED (formatting): {input_value} -> '
                f"'{formatted_display}', expected '{expected_display}'"
            )
            all_passed = False
        else:
            print(f"✅ Test {i} PASSED (formatting): {input_value} -> '{formatted_display}'")

        print()

    print('=' * 60)
    if all_passed:
        print('🎉 All tests passed! Time formatting fix is working correctly.')
    else:
        print('❌ Some tests failed. Please check the implementation.')

    return all_passed


if __name__ == '__main__':
    success = test_time_formatting()
    sys.exit(0 if success else 1)
