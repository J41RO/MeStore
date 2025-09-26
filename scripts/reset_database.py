#!/usr/bin/env python3
"""
Database Reset CLI Script

Easy-to-use command-line script for database reset operations during development.
Provides interactive prompts and safety confirmations to prevent accidental data loss.

Usage Examples:
    python scripts/reset_database.py --help
    python scripts/reset_database.py --quick
    python scripts/reset_database.py --user test@example.com
    python scripts/reset_database.py --stats
    python scripts/reset_database.py --full-reset --confirm

Features:
- Interactive prompts with safety confirmations
- Multiple reset levels and scopes
- Environment validation
- Detailed operation logging
- Test user creation utilities

Author: Backend Framework AI
Created: 2025-09-25
Version: 1.0.0
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path
from typing import List, Optional
import logging
from datetime import datetime
import json

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import our modules
from app.services.database_reset_service import (
    DatabaseResetService,
    ResetLevel,
    ResetResult,
    quick_user_reset,
    quick_test_data_reset
)
from app.core.config import settings
from app.models.user import UserType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_colored(text: str, color: str = Colors.ENDC):
    """Print colored text to terminal."""
    print(f"{color}{text}{Colors.ENDC}")


def print_header(text: str):
    """Print formatted header."""
    print_colored(f"\n{'='*60}", Colors.HEADER)
    print_colored(f" {text.center(58)} ", Colors.HEADER)
    print_colored(f"{'='*60}", Colors.HEADER)


def print_result(result: ResetResult, operation: str):
    """Print formatted reset result."""
    if result.success:
        print_colored(f"\n✅ {operation} completed successfully!", Colors.OKGREEN)
        print_colored(f"   Execution time: {result.execution_time:.2f}s", Colors.OKCYAN)

        if result.affected_users:
            print_colored(f"   Affected users: {len(result.affected_users)}", Colors.OKCYAN)
            for user in result.affected_users[:5]:  # Show first 5
                print_colored(f"     - {user}", Colors.OKCYAN)
            if len(result.affected_users) > 5:
                print_colored(f"     ... and {len(result.affected_users) - 5} more", Colors.OKCYAN)

        if result.deleted_records:
            print_colored("   Deleted records:", Colors.OKCYAN)
            for table, count in result.deleted_records.items():
                print_colored(f"     {table}: {count}", Colors.OKCYAN)

        if result.warnings:
            print_colored("   Warnings:", Colors.WARNING)
            for warning in result.warnings:
                print_colored(f"     • {warning}", Colors.WARNING)
    else:
        print_colored(f"\n❌ {operation} failed!", Colors.FAIL)
        for error in result.errors:
            print_colored(f"   Error: {error}", Colors.FAIL)


def confirm_action(prompt: str, default: bool = False) -> bool:
    """Get user confirmation for actions."""
    default_text = "Y/n" if default else "y/N"
    response = input(f"{Colors.WARNING}{prompt} [{default_text}]: {Colors.ENDC}")

    if not response:
        return default

    return response.lower() in ['y', 'yes', 'true', '1']


def get_user_input(prompt: str, default: str = "") -> str:
    """Get user input with default value."""
    full_prompt = f"{prompt}"
    if default:
        full_prompt += f" [{default}]"
    full_prompt += ": "

    response = input(full_prompt)
    return response if response else default


async def show_database_stats():
    """Show current database statistics."""
    print_header("DATABASE STATISTICS")

    try:
        async with DatabaseResetService() as service:
            stats = await service.get_reset_statistics()

        print_colored(f"Environment: {stats['environment']['current']}", Colors.OKCYAN)
        print_colored(f"Database: {stats['environment']['database_url']}", Colors.OKCYAN)
        print_colored(f"Reset allowed: {'Yes' if stats['environment']['reset_allowed'] else 'No'}", Colors.OKCYAN)

        print_colored("\nUser Statistics:", Colors.OKBLUE)
        for user_type, counts in stats['users'].items():
            print_colored(f"  {user_type}: {counts['total']} total, {counts['active']} active", Colors.OKCYAN)

        print_colored(f"\nTest users identified: {stats['test_users']}", Colors.OKCYAN)

        print_colored("\nTable Sizes (top 10):", Colors.OKBLUE)
        for table in stats['table_sizes'][:10]:
            print_colored(f"  {table['table']}: {table['live_tuples']} records", Colors.OKCYAN)

    except Exception as e:
        print_colored(f"Failed to get database statistics: {str(e)}", Colors.FAIL)


async def reset_single_user(email: str, level: ResetLevel, force: bool = False):
    """Reset a single user."""
    print_header(f"RESET USER: {email}")

    if not force:
        safe_domains = {"@test.com", "@testing.com", "@dev.com", "@example.com"}
        is_safe = any(domain in email for domain in safe_domains)

        if not is_safe:
            print_colored(f"⚠️  Email '{email}' doesn't appear to be a test user.", Colors.WARNING)
            if not confirm_action("Continue with reset anyway?"):
                print_colored("Reset cancelled.", Colors.WARNING)
                return

    if not confirm_action(f"Reset user '{email}' with level '{level.value}'?"):
        print_colored("Reset cancelled.", Colors.WARNING)
        return

    try:
        result = await quick_user_reset(email)
        print_result(result, f"User reset ({email})")

    except Exception as e:
        print_colored(f"Reset failed: {str(e)}", Colors.FAIL)


async def reset_all_test_users(level: ResetLevel, patterns: Optional[List[str]] = None):
    """Reset all test users."""
    print_header("RESET ALL TEST USERS")

    # Show what will be affected first
    try:
        async with DatabaseResetService() as service:
            test_users = await service._identify_test_users(patterns)

        if not test_users:
            print_colored("No test users found to reset.", Colors.WARNING)
            return

        print_colored(f"Found {len(test_users)} test users:", Colors.OKCYAN)
        for user in test_users[:10]:  # Show first 10
            print_colored(f"  - {user.email} ({user.user_type.value})", Colors.OKCYAN)
        if len(test_users) > 10:
            print_colored(f"  ... and {len(test_users) - 10} more", Colors.OKCYAN)

        if not confirm_action(f"Reset {len(test_users)} test users with level '{level.value}'?"):
            print_colored("Reset cancelled.", Colors.WARNING)
            return

        result = await quick_test_data_reset()
        print_result(result, "Test users reset")

    except Exception as e:
        print_colored(f"Reset failed: {str(e)}", Colors.FAIL)


async def full_database_reset(preserve_admins: bool = True):
    """Perform full database reset with multiple confirmations."""
    print_header("FULL DATABASE RESET")

    print_colored("⚠️  WARNING: THIS WILL DELETE ALL DATA IN THE DATABASE! ⚠️", Colors.FAIL)
    print_colored("This operation cannot be undone!", Colors.FAIL)

    if not confirm_action("Do you understand this will delete ALL data?"):
        print_colored("Reset cancelled.", Colors.WARNING)
        return

    confirmation_text = "DELETE ALL DATA"
    user_input = get_user_input(f"Type '{confirmation_text}' to confirm")

    if user_input != confirmation_text:
        print_colored("Incorrect confirmation. Reset cancelled.", Colors.FAIL)
        return

    print_colored(f"Admin users will be {'preserved' if preserve_admins else 'deleted'}.", Colors.WARNING)

    if not confirm_action("This is your final confirmation. Proceed with FULL RESET?"):
        print_colored("Reset cancelled.", Colors.WARNING)
        return

    try:
        async with DatabaseResetService() as service:
            result = await service.full_database_reset(
                confirm_dangerous=True,
                preserve_admin_users=preserve_admins
            )

        print_result(result, "Full database reset")

    except Exception as e:
        print_colored(f"Full reset failed: {str(e)}", Colors.FAIL)


async def create_test_user_interactive():
    """Interactive test user creation."""
    print_header("CREATE TEST USER")

    # Get user details
    email = get_user_input("Email (must use test domain)")

    # Validate test domain
    safe_domains = {"@test.com", "@testing.com", "@dev.com", "@example.com"}
    if not any(domain in email for domain in safe_domains):
        print_colored(f"Email must use a test domain: {', '.join(safe_domains)}", Colors.FAIL)
        return

    password = get_user_input("Password", "testpass123")

    # User type selection
    print_colored("\nUser types:", Colors.OKCYAN)
    user_types = list(UserType)
    for i, user_type in enumerate(user_types, 1):
        print_colored(f"  {i}. {user_type.value}", Colors.OKCYAN)

    type_choice = get_user_input("Select user type (1-5)", "1")
    try:
        selected_type = user_types[int(type_choice) - 1]
    except (ValueError, IndexError):
        selected_type = UserType.BUYER

    # Optional fields
    nombre = get_user_input("First name (optional)")
    apellido = get_user_input("Last name (optional)")
    telefono = get_user_input("Phone (optional)")
    ciudad = get_user_input("City (optional)")

    if not confirm_action(f"Create test user '{email}' as {selected_type.value}?"):
        print_colored("User creation cancelled.", Colors.WARNING)
        return

    try:
        async with DatabaseResetService() as service:
            extra_fields = {}
            if nombre: extra_fields["nombre"] = nombre
            if apellido: extra_fields["apellido"] = apellido
            if telefono: extra_fields["telefono"] = telefono
            if ciudad: extra_fields["ciudad"] = ciudad

            user = await service.create_test_user(
                email=email,
                password=password,
                user_type=selected_type,
                **extra_fields
            )

        print_colored(f"✅ Test user created successfully!", Colors.OKGREEN)
        print_colored(f"   ID: {user.id}", Colors.OKCYAN)
        print_colored(f"   Email: {user.email}", Colors.OKCYAN)
        print_colored(f"   Type: {user.user_type.value}", Colors.OKCYAN)
        print_colored(f"   Password: {password}", Colors.OKCYAN)

    except Exception as e:
        print_colored(f"User creation failed: {str(e)}", Colors.FAIL)


async def interactive_menu():
    """Show interactive menu for database operations."""
    while True:
        print_header("DATABASE RESET TOOL")

        print_colored("Available operations:", Colors.OKBLUE)
        print_colored("1. Show database statistics", Colors.OKCYAN)
        print_colored("2. Quick reset (all test users)", Colors.OKCYAN)
        print_colored("3. Reset specific user", Colors.OKCYAN)
        print_colored("4. Create test user", Colors.OKCYAN)
        print_colored("5. Full database reset (DANGEROUS)", Colors.FAIL)
        print_colored("6. Exit", Colors.OKCYAN)

        choice = get_user_input("\nSelect operation (1-6)")

        try:
            if choice == "1":
                await show_database_stats()
            elif choice == "2":
                await reset_all_test_users(ResetLevel.USER_CASCADE)
            elif choice == "3":
                email = get_user_input("User email to reset")
                if email:
                    await reset_single_user(email, ResetLevel.USER_CASCADE)
            elif choice == "4":
                await create_test_user_interactive()
            elif choice == "5":
                await full_database_reset()
            elif choice == "6":
                print_colored("Goodbye!", Colors.OKGREEN)
                break
            else:
                print_colored("Invalid choice. Please select 1-6.", Colors.WARNING)

        except KeyboardInterrupt:
            print_colored("\n\nOperation cancelled by user.", Colors.WARNING)
        except Exception as e:
            print_colored(f"Operation failed: {str(e)}", Colors.FAIL)

        if choice in ["1", "2", "3", "4", "5"]:
            input("\nPress Enter to continue...")


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Database Reset CLI Tool for MeStore",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/reset_database.py --quick
  python scripts/reset_database.py --user test@example.com
  python scripts/reset_database.py --stats
  python scripts/reset_database.py --create-user test@dev.com
  python scripts/reset_database.py --full-reset --confirm
  python scripts/reset_database.py --interactive
        """
    )

    parser.add_argument("--quick", action="store_true", help="Quick reset of all test users")
    parser.add_argument("--user", type=str, help="Reset specific user by email")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("--create-user", type=str, help="Create test user with specified email")
    parser.add_argument("--full-reset", action="store_true", help="Full database reset (DANGEROUS)")
    parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompts")
    parser.add_argument("--force", action="store_true", help="Force operations even for non-test users")
    parser.add_argument("--preserve-admins", action="store_true", default=True, help="Preserve admin users in full reset")
    parser.add_argument("--interactive", action="store_true", help="Start interactive menu")
    parser.add_argument("--level", type=str, default="user_cascade",
                        choices=[level.value for level in ResetLevel],
                        help="Reset level (default: user_cascade)")

    args = parser.parse_args()

    # Validate environment
    try:
        allowed_environments = {"development", "testing", "dev", "test"}
        current_env = settings.ENVIRONMENT.lower()

        if current_env not in allowed_environments:
            print_colored(f"❌ Database reset not allowed in environment: {current_env}", Colors.FAIL)
            print_colored(f"Only allowed in: {', '.join(allowed_environments)}", Colors.FAIL)
            sys.exit(1)

        print_colored(f"✅ Environment check passed: {settings.ENVIRONMENT}", Colors.OKGREEN)

    except Exception as e:
        print_colored(f"❌ Environment validation failed: {str(e)}", Colors.FAIL)
        sys.exit(1)

    # Parse reset level
    try:
        reset_level = ResetLevel(args.level)
    except ValueError:
        print_colored(f"Invalid reset level: {args.level}", Colors.FAIL)
        sys.exit(1)

    # Execute operations
    try:
        if args.interactive:
            await interactive_menu()

        elif args.stats:
            await show_database_stats()

        elif args.quick:
            if not args.confirm:
                if not confirm_action("Quick reset all test users?"):
                    print_colored("Reset cancelled.", Colors.WARNING)
                    return

            result = await quick_test_data_reset()
            print_result(result, "Quick test data reset")

        elif args.user:
            if not args.confirm:
                if not confirm_action(f"Reset user '{args.user}'?"):
                    print_colored("Reset cancelled.", Colors.WARNING)
                    return

            await reset_single_user(args.user, reset_level, args.force)

        elif args.create_user:
            if not args.confirm:
                await create_test_user_interactive()
            else:
                try:
                    async with DatabaseResetService() as service:
                        user = await service.create_test_user(
                            email=args.create_user,
                            password="testpass123",
                            user_type=UserType.BUYER
                        )
                    print_colored(f"✅ Created test user: {user.email}", Colors.OKGREEN)
                except Exception as e:
                    print_colored(f"Failed to create user: {str(e)}", Colors.FAIL)

        elif args.full_reset:
            if args.confirm:
                try:
                    async with DatabaseResetService() as service:
                        result = await service.full_database_reset(
                            confirm_dangerous=True,
                            preserve_admin_users=args.preserve_admins
                        )
                    print_result(result, "Full database reset")
                except Exception as e:
                    print_colored(f"Full reset failed: {str(e)}", Colors.FAIL)
            else:
                await full_database_reset(args.preserve_admins)

        else:
            # No specific command, start interactive mode
            await interactive_menu()

    except KeyboardInterrupt:
        print_colored("\n\nOperation cancelled by user.", Colors.WARNING)
    except Exception as e:
        print_colored(f"Unexpected error: {str(e)}", Colors.FAIL)
        logger.exception("Unexpected error in CLI")
        sys.exit(1)


if __name__ == "__main__":
    # Ensure we can import asyncio and run
    if sys.version_info < (3, 7):
        print("This script requires Python 3.7 or higher.")
        sys.exit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)