"""Tests for time_utils module."""

import time
import pytest
from datetime import datetime, timedelta

from devtools_py.time_utils import (
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
            (0, 0, 0),  # Midnight
            (9, 30, 0),  # Morning
            (12, 0, 0),  # Noon
            (17, 45, 30),  # Evening
            (23, 59, 59),  # End of day
        ]

        for hour, minute, second in times:
            original = datetime(2024, 1, 15, hour, minute, second)  # Monday
            result = next_business_day(original)
            expected = datetime(2024, 1, 16, hour, minute, second)  # Tuesday
            assert result == expected


class TestSchedulingAndTimer:
    """Tests for scheduling and timer utilities (Task 10.3)."""

    def test_cron_next_run_daily(self):
        """Test cron expression for daily execution."""
        # Every day at 9 AM
        from_time = datetime(2024, 1, 15, 8, 0)  # 8 AM
        result = cron_next_run("0 9 * * *", from_time)
        expected = datetime(2024, 1, 15, 9, 0)  # Same day at 9 AM
        assert result == expected

        # After 9 AM, should be next day
        from_time = datetime(2024, 1, 15, 10, 0)  # 10 AM
        result = cron_next_run("0 9 * * *", from_time)
        expected = datetime(2024, 1, 16, 9, 0)  # Next day at 9 AM
        assert result == expected

    def test_cron_next_run_weekdays(self):
        """Test cron expression for weekday execution."""
        # Every weekday at 9 AM (Monday=1, Friday=5)
        # From Saturday, should be Monday
        from_time = datetime(2024, 1, 13, 10, 0)  # Saturday
        result = cron_next_run("0 9 * * 1-5", from_time)
        expected = datetime(2024, 1, 15, 9, 0)  # Next Monday
        assert result == expected

        # From Friday before 9 AM, should be same day
        from_time = datetime(2024, 1, 19, 8, 0)  # Friday 8 AM
        result = cron_next_run("0 9 * * 1-5", from_time)
        expected = datetime(2024, 1, 19, 9, 0)  # Same Friday 9 AM
        assert result == expected

        # From Friday after 9 AM, should be next Monday
        from_time = datetime(2024, 1, 19, 10, 0)  # Friday 10 AM
        result = cron_next_run("0 9 * * 1-5", from_time)
        expected = datetime(2024, 1, 22, 9, 0)  # Next Monday
        assert result == expected

    def test_cron_next_run_hourly(self):
        """Test cron expression for hourly execution."""
        # Every hour at minute 30
        from_time = datetime(2024, 1, 15, 14, 15)  # 2:15 PM
        result = cron_next_run("30 * * * *", from_time)
        expected = datetime(2024, 1, 15, 14, 30)  # 2:30 PM same day
        assert result == expected

        # After 30 minutes, should be next hour
        from_time = datetime(2024, 1, 15, 14, 45)  # 2:45 PM
        result = cron_next_run("30 * * * *", from_time)
        expected = datetime(2024, 1, 15, 15, 30)  # 3:30 PM same day
        assert result == expected

    def test_cron_next_run_specific_time(self):
        """Test cron expression for specific time."""
        # Every day at 2:30 PM
        from_time = datetime(2024, 1, 15, 10, 0)  # 10 AM
        result = cron_next_run("30 14 * * *", from_time)
        expected = datetime(2024, 1, 15, 14, 30)  # Same day 2:30 PM
        assert result == expected

    def test_cron_next_run_multiple_values(self):
        """Test cron expression with multiple values."""
        # At 9 AM and 5 PM every day
        from_time = datetime(2024, 1, 15, 12, 0)  # Noon
        result = cron_next_run("0 9,17 * * *", from_time)
        expected = datetime(2024, 1, 15, 17, 0)  # Same day 5 PM
        assert result == expected

    def test_cron_next_run_step_values(self):
        """Test cron expression with step values."""
        # Every 15 minutes
        from_time = datetime(2024, 1, 15, 14, 10)  # 2:10 PM
        result = cron_next_run("*/15 * * * *", from_time)
        expected = datetime(2024, 1, 15, 14, 15)  # 2:15 PM same day
        assert result == expected

    def test_cron_next_run_default_from_time(self):
        """Test cron expression with default from_time (now)."""
        # Should not raise an error and return a datetime
        result = cron_next_run("0 9 * * *")
        assert isinstance(result, datetime)

    def test_cron_next_run_invalid_expression(self):
        """Test invalid cron expressions raise ValueError."""
        # Too few parts
        with pytest.raises(ValueError, match="must have 5 parts"):
            cron_next_run("0 9 * *")

        # Too many parts
        with pytest.raises(ValueError, match="must have 5 parts"):
            cron_next_run("0 9 * * * *")

        # Invalid values
        with pytest.raises(ValueError, match="Invalid cron expression"):
            cron_next_run("60 9 * * *")  # Invalid minute

    def test_timer_basic_usage(self):
        """Test basic timer usage."""
        timer = Timer()

        # Timer should not be started initially
        with pytest.raises(RuntimeError, match="Timer was not started"):
            timer.elapsed()

        # Start timer
        timer.start()

        # Should be able to get elapsed time
        elapsed1 = timer.elapsed()
        assert elapsed1 >= 0

        # Wait a bit and check elapsed time increased
        time.sleep(0.01)
        elapsed2 = timer.elapsed()
        assert elapsed2 > elapsed1

        # Stop timer
        final_elapsed = timer.stop()
        assert final_elapsed >= elapsed2

        # Elapsed should remain the same after stopping
        assert timer.elapsed() == final_elapsed

    def test_timer_start_already_running(self):
        """Test starting timer when already running raises error."""
        timer = Timer()
        timer.start()

        with pytest.raises(RuntimeError, match="Timer is already running"):
            timer.start()

    def test_timer_stop_not_started(self):
        """Test stopping timer that was not started raises error."""
        timer = Timer()

        with pytest.raises(RuntimeError, match="Timer was not started"):
            timer.stop()

    def test_timer_reset(self):
        """Test timer reset functionality."""
        timer = Timer()
        timer.start()
        time.sleep(0.01)
        timer.stop()

        # Reset should clear the timer
        timer.reset()

        with pytest.raises(RuntimeError, match="Timer was not started"):
            timer.elapsed()

    def test_timer_restart(self):
        """Test timer restart functionality."""
        timer = Timer()
        timer.start()
        time.sleep(0.01)
        timer.stop()

        # Restart should reset and start again
        timer.restart()

        # Should be able to get elapsed time
        elapsed = timer.elapsed()
        assert elapsed >= 0
        assert elapsed < 0.1  # Should be small since we just restarted

    def test_timer_context_manager(self):
        """Test timer as context manager."""
        with Timer() as timer:
            time.sleep(0.01)
            elapsed_during = timer.elapsed()
            assert elapsed_during > 0

        # Timer should be stopped after context
        elapsed_after = timer.elapsed()
        assert elapsed_after >= elapsed_during

    def test_timer_context_manager_with_exception(self):
        """Test timer context manager handles exceptions."""
        timer = None
        try:
            with Timer() as timer:
                time.sleep(0.01)
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Timer should still be stopped even with exception
        assert timer is not None
        elapsed = timer.elapsed()
        assert elapsed > 0
