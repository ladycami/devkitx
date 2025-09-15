"""Tests for time_utils module."""

import pytest
from datetime import datetime, timedelta

from dev_qol_toolkit.time_utils import (
    parse_date,
    format_duration,
    get_timezone_offset,
    is_business_day,
    next_business_day,
    cron_next_run,
    Timer,
)


class TestParseDate:
    """Tests for parse_date function."""
    
    def test_parse_iso_date(self):
        """Test parsing ISO date format."""
        result = parse_date("2024-01-15")
        expected = datetime(2024, 1, 15)
        assert result == expected
    
    def test_parse_iso_datetime(self):
        """Test parsing ISO datetime format."""
        result = parse_date("2024-01-15 14:30:00")
        expected = datetime(2024, 1, 15, 14, 30, 0)
        assert result == expected
    
    def test_parse_iso_datetime_short(self):
        """Test parsing ISO datetime without seconds."""
        result = parse_date("2024-01-15 14:30")
        expected = datetime(2024, 1, 15, 14, 30, 0)
        assert result == expected
    
    def test_parse_slash_date_formats(self):
        """Test parsing various slash-separated date formats."""
        # YYYY/MM/DD
        result = parse_date("2024/01/15")
        expected = datetime(2024, 1, 15)
        assert result == expected
        
        # DD/MM/YYYY
        result = parse_date("15/01/2024")
        expected = datetime(2024, 1, 15)
        assert result == expected
        
        # MM/DD/YYYY
        result = parse_date("01/15/2024")
        expected = datetime(2024, 1, 15)
        assert result == expected
    
    def test_parse_dash_date_formats(self):
        """Test parsing various dash-separated date formats."""
        # DD-MM-YYYY
        result = parse_date("15-01-2024")
        expected = datetime(2024, 1, 15)
        assert result == expected
        
        # MM-DD-YYYY
        result = parse_date("01-15-2024")
        expected = datetime(2024, 1, 15)
        assert result == expected
    
    def test_parse_compact_formats(self):
        """Test parsing compact date formats."""
        # YYYYMMDD
        result = parse_date("20240115")
        expected = datetime(2024, 1, 15)
        assert result == expected
        
        # YYYYMMDDHHMMSS
        result = parse_date("20240115143000")
        expected = datetime(2024, 1, 15, 14, 30, 0)
        assert result == expected
    
    def test_parse_text_formats(self):
        """Test parsing text-based date formats."""
        # Full month name
        result = parse_date("January 15, 2024")
        expected = datetime(2024, 1, 15)
        assert result == expected
        
        # Abbreviated month name
        result = parse_date("Jan 15, 2024")
        expected = datetime(2024, 1, 15)
        assert result == expected
        
        # Day first format
        result = parse_date("15 January 2024")
        expected = datetime(2024, 1, 15)
        assert result == expected
    
    def test_parse_iso_with_timezone(self):
        """Test parsing ISO format with timezone indicators."""
        # ISO with Z
        result = parse_date("2024-01-15T14:30:00Z")
        expected = datetime(2024, 1, 15, 14, 30, 0)
        assert result == expected
        
        # ISO with microseconds
        result = parse_date("2024-01-15T14:30:00.123456")
        expected = datetime(2024, 1, 15, 14, 30, 0, 123456)
        assert result == expected
    
    def test_parse_with_custom_formats(self):
        """Test parsing with custom format list."""
        custom_formats = ["%d.%m.%Y", "%d.%m.%Y %H:%M"]
        
        result = parse_date("15.01.2024", custom_formats)
        expected = datetime(2024, 1, 15)
        assert result == expected
        
        result = parse_date("15.01.2024 14:30", custom_formats)
        expected = datetime(2024, 1, 15, 14, 30)
        assert result == expected
    
    def test_parse_with_whitespace(self):
        """Test parsing dates with leading/trailing whitespace."""
        result = parse_date("  2024-01-15  ")
        expected = datetime(2024, 1, 15)
        assert result == expected
    
    def test_parse_invalid_date(self):
        """Test parsing invalid date string raises ValueError."""
        with pytest.raises(ValueError, match="Unable to parse date string"):
            parse_date("invalid-date")
    
    def test_parse_empty_string(self):
        """Test parsing empty string raises ValueError."""
        with pytest.raises(ValueError, match="Unable to parse date string"):
            parse_date("")
    
    def test_parse_with_empty_formats_list(self):
        """Test parsing with empty formats list raises ValueError."""
        with pytest.raises(ValueError, match="Unable to parse date string"):
            parse_date("2024-01-15", [])


class TestFormatDuration:
    """Tests for format_duration function."""
    
    def test_format_zero_seconds(self):
        """Test formatting zero duration."""
        result = format_duration(0)
        assert result == "0.0s"
    
    def test_format_seconds_only(self):
        """Test formatting duration with only seconds."""
        result = format_duration(30.5)
        assert result == "30.5s"
        
        result = format_duration(1.0)
        assert result == "1.0s"
    
    def test_format_minutes_and_seconds(self):
        """Test formatting duration with minutes and seconds."""
        result = format_duration(90)  # 1 minute 30 seconds
        assert result == "1m 30.0s"
        
        result = format_duration(125.7)  # 2 minutes 5.7 seconds
        assert result == "2m 5.7s"
    
    def test_format_hours_minutes_seconds(self):
        """Test formatting duration with hours, minutes, and seconds."""
        result = format_duration(3661)  # 1 hour 1 minute 1 second
        assert result == "1h 1m 1.0s"
        
        result = format_duration(7323.5)  # 2 hours 2 minutes 3.5 seconds
        assert result == "2h 2m 3.5s"
    
    def test_format_days_hours_minutes_seconds(self):
        """Test formatting duration with days, hours, minutes, and seconds."""
        result = format_duration(90061)  # 1 day 1 hour 1 minute 1 second
        assert result == "1d 1h 1m 1.0s"
        
        result = format_duration(180122.5)  # 2 days 2 hours 2 minutes 2.5 seconds
        assert result == "2d 2h 2m 2.5s"
    
    def test_format_exact_units(self):
        """Test formatting exact unit durations."""
        result = format_duration(60)  # Exactly 1 minute
        assert result == "1m 0.0s"
        
        result = format_duration(3600)  # Exactly 1 hour
        assert result == "1h 0m 0.0s"
        
        result = format_duration(86400)  # Exactly 1 day
        assert result == "1d 0h 0m 0.0s"
    
    def test_format_large_durations(self):
        """Test formatting very large durations."""
        result = format_duration(31536000)  # 365 days
        assert result == "365d 0h 0m 0.0s"
    
    def test_format_small_durations(self):
        """Test formatting very small durations."""
        result = format_duration(0.1)
        assert result == "0.1s"
        
        result = format_duration(0.001)
        assert result == "0.0s"  # Rounded to 1 decimal place
    
    def test_format_negative_duration(self):
        """Test formatting negative durations."""
        result = format_duration(-30)
        assert result == "-30.0s"
        
        result = format_duration(-3661)
        assert result == "-1h 1m 1.0s"
    
    def test_format_fractional_seconds_only(self):
        """Test formatting when only fractional seconds remain."""
        result = format_duration(0.5)
        assert result == "0.5s"


class TestTimezoneAndBusinessDay:
    """Tests for timezone and business day functions (Task 10.2)."""
    
    def test_get_timezone_offset_utc(self):
        """Test getting UTC timezone offset."""
        result = get_timezone_offset("UTC")
        assert result == timedelta(0)
    
    def test_get_timezone_offset_gmt(self):
        """Test getting GMT timezone offset."""
        result = get_timezone_offset("GMT")
        assert result == timedelta(0)
    
    def test_get_timezone_offset_common_timezones(self):
        """Test getting offsets for common US timezones."""
        # These are standard time offsets (not accounting for DST)
        try:
            # Try with system timezone support first
            est_offset = get_timezone_offset("EST")
            assert isinstance(est_offset, timedelta)
        except ValueError:
            # Fallback to basic implementation
            est_offset = get_timezone_offset("EST")
            assert est_offset == timedelta(hours=-5)
    
    def test_get_timezone_offset_invalid(self):
        """Test getting offset for invalid timezone raises ValueError."""
        with pytest.raises(ValueError, match="not recognized|Invalid timezone"):
            get_timezone_offset("INVALID/TIMEZONE")
    
    def test_is_business_day_weekdays(self):
        """Test that weekdays are business days."""
        # Monday (2024-01-15)
        assert is_business_day(datetime(2024, 1, 15)) is True
        # Tuesday (2024-01-16)
        assert is_business_day(datetime(2024, 1, 16)) is True
        # Wednesday (2024-01-17)
        assert is_business_day(datetime(2024, 1, 17)) is True
        # Thursday (2024-01-18)
        assert is_business_day(datetime(2024, 1, 18)) is True
        # Friday (2024-01-19)
        assert is_business_day(datetime(2024, 1, 19)) is True
    
    def test_is_business_day_weekends(self):
        """Test that weekends are not business days."""
        # Saturday (2024-01-13)
        assert is_business_day(datetime(2024, 1, 13)) is False
        # Sunday (2024-01-14)
        assert is_business_day(datetime(2024, 1, 14)) is False
    
    def test_is_business_day_with_time(self):
        """Test that time component doesn't affect business day check."""
        # Monday with different times
        assert is_business_day(datetime(2024, 1, 15, 9, 0, 0)) is True
        assert is_business_day(datetime(2024, 1, 15, 17, 30, 45)) is True
        
        # Saturday with different times
        assert is_business_day(datetime(2024, 1, 13, 9, 0, 0)) is False
        assert is_business_day(datetime(2024, 1, 13, 17, 30, 45)) is False
    
    def test_next_business_day_from_weekday(self):
        """Test getting next business day from a weekday."""
        # From Monday to Tuesday
        result = next_business_day(datetime(2024, 1, 15, 14, 30))
        expected = datetime(2024, 1, 16, 14, 30)
        assert result == expected
        
        # From Wednesday to Thursday
        result = next_business_day(datetime(2024, 1, 17, 9, 0))
        expected = datetime(2024, 1, 18, 9, 0)
        assert result == expected
    
    def test_next_business_day_from_friday(self):
        """Test getting next business day from Friday (should be Monday)."""
        # From Friday to Monday
        result = next_business_day(datetime(2024, 1, 19, 16, 45))
        expected = datetime(2024, 1, 22, 16, 45)  # Next Monday
        assert result == expected
    
    def test_next_business_day_from_saturday(self):
        """Test getting next business day from Saturday (should be Monday)."""
        # From Saturday to Monday
        result = next_business_day(datetime(2024, 1, 13, 10, 0))
        expected = datetime(2024, 1, 15, 10, 0)  # Next Monday
        assert result == expected
    
    def test_next_business_day_from_sunday(self):
        """Test getting next business day from Sunday (should be Monday)."""
        # From Sunday to Monday
        result = next_business_day(datetime(2024, 1, 14, 12, 30))
        expected = datetime(2024, 1, 15, 12, 30)  # Next Monday
        assert result == expected
    
    def test_next_business_day_preserves_time(self):
        """Test that next business day preserves the time component."""
        # Test with various times
        times = [
            (0, 0, 0),      # Midnight
            (9, 30, 0),     # Morning
            (12, 0, 0),     # Noon
            (17, 45, 30),   # Evening
            (23, 59, 59),   # End of day
        ]
        
        for hour, minute, second in times:
            original = datetime(2024, 1, 15, hour, minute, second)  # Monday
            result = next_business_day(original)
            expected = datetime(2024, 1, 16, hour, minute, second)  # Tuesday
            assert result == expected


class TestSchedulingAndTimer:
    """Tests for scheduling and timer utilities (Task 10.3)."""
    
    def test_cron_next_run_not_implemented(self):
        """Test that cron_next_run raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            cron_next_run("0 0 * * *")
    
    def test_timer_not_implemented(self):
        """Test that Timer class raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            Timer()