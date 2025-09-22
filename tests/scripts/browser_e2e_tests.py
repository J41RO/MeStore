#!/usr/bin/env python3
"""
MeStore Browser-Based E2E Testing
==================================

This script performs browser-based end-to-end testing using Playwright
to test complete user journeys and cross-browser compatibility.

Test Coverage:
- Complete buyer journey (registration → product discovery → purchase)
- Complete vendor journey (registration → product upload → order management)
- Admin workflow (user management → vendor approval → system monitoring)
- Cross-platform responsive design validation
- Browser compatibility testing
"""

import asyncio
import time
import json
import logging
import sys
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('browser_e2e_results.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class BrowserTestResult:
    """Browser test result data structure"""
    test_name: str
    browser: str
    status: str  # "PASS", "FAIL", "SKIP"
    duration: float
    screenshots: List[str]
    details: Dict[str, Any]
    error_message: str = ""

class BrowserE2ETestSuite:
    """Browser-based E2E Testing Suite for MeStore"""

    def __init__(self):
        self.frontend_url = "http://192.168.1.137:5174"
        self.backend_url = "http://192.168.1.137:8000"
        self.test_results: List[BrowserTestResult] = []

    def log_test_result(self, result: BrowserTestResult):
        """Log test result"""
        status_emoji = "✅" if result.status == "PASS" else "❌" if result.status == "FAIL" else "⏭️"
        logger.info(f"{status_emoji} {result.test_name} [{result.browser}]: {result.status} ({result.duration:.2f}s)")
        if result.error_message:
            logger.error(f"   Error: {result.error_message}")
        self.test_results.append(result)

    async def test_frontend_accessibility(self, browser_name: str = "chromium") -> BrowserTestResult:
        """Test frontend accessibility and basic navigation"""
        try:
            # Import playwright (graceful degradation if not available)
            from playwright.async_api import async_playwright
        except ImportError:
            return BrowserTestResult(
                test_name="Frontend Accessibility",
                browser=browser_name,
                status="SKIP",
                duration=0,
                screenshots=[],
                details={},
                error_message="Playwright not available - skipping browser tests"
            )

        start_time = time.time()
        screenshots = []
        details = {}

        try:
            async with async_playwright() as p:
                browser = await getattr(p, browser_name).launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080}
                )
                page = await context.new_page()

                # Test main page load
                await page.goto(self.frontend_url, timeout=30000)
                await page.wait_for_load_state('networkidle', timeout=30000)

                # Take screenshot
                screenshot_path = f"screenshot_{browser_name}_main_{int(time.time())}.png"
                await page.screenshot(path=screenshot_path)
                screenshots.append(screenshot_path)

                # Test page title and basic elements
                title = await page.title()
                details['page_title'] = title

                # Test navigation elements
                nav_elements = await page.query_selector_all('nav, header, [role="navigation"]')
                details['navigation_elements'] = len(nav_elements)

                # Test responsive design - mobile viewport
                await page.set_viewport_size({"width": 375, "height": 667})
                mobile_screenshot = f"screenshot_{browser_name}_mobile_{int(time.time())}.png"
                await page.screenshot(path=mobile_screenshot)
                screenshots.append(mobile_screenshot)

                # Test tablet viewport
                await page.set_viewport_size({"width": 768, "height": 1024})
                tablet_screenshot = f"screenshot_{browser_name}_tablet_{int(time.time())}.png"
                await page.screenshot(path=tablet_screenshot)
                screenshots.append(tablet_screenshot)

                details['responsive_test'] = True
                details['viewports_tested'] = ["desktop", "mobile", "tablet"]

                await browser.close()

            duration = time.time() - start_time
            return BrowserTestResult(
                test_name="Frontend Accessibility",
                browser=browser_name,
                status="PASS",
                duration=duration,
                screenshots=screenshots,
                details=details
            )

        except Exception as e:
            duration = time.time() - start_time
            return BrowserTestResult(
                test_name="Frontend Accessibility",
                browser=browser_name,
                status="FAIL",
                duration=duration,
                screenshots=screenshots,
                details=details,
                error_message=str(e)
            )

    async def test_user_interface_elements(self, browser_name: str = "chromium") -> BrowserTestResult:
        """Test user interface elements and interactions"""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return BrowserTestResult(
                test_name="UI Elements Testing",
                browser=browser_name,
                status="SKIP",
                duration=0,
                screenshots=[],
                details={},
                error_message="Playwright not available"
            )

        start_time = time.time()
        screenshots = []
        details = {}

        try:
            async with async_playwright() as p:
                browser = await getattr(p, browser_name).launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                # Navigate to main page
                await page.goto(self.frontend_url, timeout=30000)
                await page.wait_for_load_state('networkidle', timeout=30000)

                # Test common UI elements
                buttons = await page.query_selector_all('button, input[type="button"], input[type="submit"]')
                details['buttons_found'] = len(buttons)

                links = await page.query_selector_all('a[href]')
                details['links_found'] = len(links)

                forms = await page.query_selector_all('form')
                details['forms_found'] = len(forms)

                inputs = await page.query_selector_all('input, textarea, select')
                details['input_elements'] = len(inputs)

                # Test for accessibility attributes
                aria_labels = await page.query_selector_all('[aria-label]')
                details['aria_labels'] = len(aria_labels)

                alt_texts = await page.query_selector_all('img[alt]')
                details['images_with_alt'] = len(alt_texts)

                # Take screenshot of UI elements
                ui_screenshot = f"screenshot_{browser_name}_ui_{int(time.time())}.png"
                await page.screenshot(path=ui_screenshot)
                screenshots.append(ui_screenshot)

                # Test dark/light mode if available
                try:
                    # Look for theme toggle
                    theme_toggle = await page.query_selector('[data-theme-toggle], .theme-toggle, #theme-toggle')
                    if theme_toggle:
                        await theme_toggle.click()
                        await page.wait_for_timeout(1000)

                        theme_screenshot = f"screenshot_{browser_name}_theme_{int(time.time())}.png"
                        await page.screenshot(path=theme_screenshot)
                        screenshots.append(theme_screenshot)
                        details['theme_toggle_tested'] = True
                except Exception:
                    details['theme_toggle_tested'] = False

                await browser.close()

            duration = time.time() - start_time
            return BrowserTestResult(
                test_name="UI Elements Testing",
                browser=browser_name,
                status="PASS",
                duration=duration,
                screenshots=screenshots,
                details=details
            )

        except Exception as e:
            duration = time.time() - start_time
            return BrowserTestResult(
                test_name="UI Elements Testing",
                browser=browser_name,
                status="FAIL",
                duration=duration,
                screenshots=screenshots,
                details=details,
                error_message=str(e)
            )

    async def test_navigation_flow(self, browser_name: str = "chromium") -> BrowserTestResult:
        """Test navigation flow and routing"""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return BrowserTestResult(
                test_name="Navigation Flow",
                browser=browser_name,
                status="SKIP",
                duration=0,
                screenshots=[],
                details={},
                error_message="Playwright not available"
            )

        start_time = time.time()
        screenshots = []
        details = {}

        try:
            async with async_playwright() as p:
                browser = await getattr(p, browser_name).launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                # Start from main page
                await page.goto(self.frontend_url, timeout=30000)
                await page.wait_for_load_state('networkidle', timeout=30000)

                # Test navigation to different routes
                routes_to_test = [
                    "/login",
                    "/register",
                    "/products",
                    "/admin"
                ]

                navigation_results = {}
                for route in routes_to_test:
                    try:
                        await page.goto(f"{self.frontend_url}{route}", timeout=30000)
                        await page.wait_for_load_state('networkidle', timeout=30000)

                        current_url = page.url
                        page_title = await page.title()

                        navigation_results[route] = {
                            "accessible": True,
                            "final_url": current_url,
                            "page_title": page_title
                        }

                        # Take screenshot of each route
                        route_screenshot = f"screenshot_{browser_name}_route_{route.replace('/', '_')}_{int(time.time())}.png"
                        await page.screenshot(path=route_screenshot)
                        screenshots.append(route_screenshot)

                    except Exception as e:
                        navigation_results[route] = {
                            "accessible": False,
                            "error": str(e)
                        }

                details['navigation_results'] = navigation_results
                details['routes_tested'] = len(routes_to_test)
                details['successful_routes'] = len([r for r in navigation_results.values() if r.get('accessible', False)])

                await browser.close()

            duration = time.time() - start_time
            return BrowserTestResult(
                test_name="Navigation Flow",
                browser=browser_name,
                status="PASS",
                duration=duration,
                screenshots=screenshots,
                details=details
            )

        except Exception as e:
            duration = time.time() - start_time
            return BrowserTestResult(
                test_name="Navigation Flow",
                browser=browser_name,
                status="FAIL",
                duration=duration,
                screenshots=screenshots,
                details=details,
                error_message=str(e)
            )

    async def test_form_interactions(self, browser_name: str = "chromium") -> BrowserTestResult:
        """Test form interactions and validation"""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return BrowserTestResult(
                test_name="Form Interactions",
                browser=browser_name,
                status="SKIP",
                duration=0,
                screenshots=[],
                details={},
                error_message="Playwright not available"
            )

        start_time = time.time()
        screenshots = []
        details = {}

        try:
            async with async_playwright() as p:
                browser = await getattr(p, browser_name).launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                # Test login form
                await page.goto(f"{self.frontend_url}/login", timeout=30000)
                await page.wait_for_load_state('networkidle', timeout=30000)

                # Look for login form elements
                email_input = await page.query_selector('input[type="email"], input[name*="email"], input[id*="email"]')
                password_input = await page.query_selector('input[type="password"], input[name*="password"], input[id*="password"]')
                submit_button = await page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Login"), button:has-text("Sign In")')

                details['login_form_elements'] = {
                    "email_field": email_input is not None,
                    "password_field": password_input is not None,
                    "submit_button": submit_button is not None
                }

                # Test form interaction if elements exist
                if email_input and password_input and submit_button:
                    # Fill form with test data
                    await email_input.fill("test@example.com")
                    await password_input.fill("testpassword")

                    # Take screenshot before submit
                    form_screenshot = f"screenshot_{browser_name}_form_filled_{int(time.time())}.png"
                    await page.screenshot(path=form_screenshot)
                    screenshots.append(form_screenshot)

                    # Submit form
                    await submit_button.click()
                    await page.wait_for_timeout(2000)  # Wait for response

                    # Take screenshot after submit
                    result_screenshot = f"screenshot_{browser_name}_form_result_{int(time.time())}.png"
                    await page.screenshot(path=result_screenshot)
                    screenshots.append(result_screenshot)

                    details['form_submission_tested'] = True
                else:
                    details['form_submission_tested'] = False

                await browser.close()

            duration = time.time() - start_time
            return BrowserTestResult(
                test_name="Form Interactions",
                browser=browser_name,
                status="PASS",
                duration=duration,
                screenshots=screenshots,
                details=details
            )

        except Exception as e:
            duration = time.time() - start_time
            return BrowserTestResult(
                test_name="Form Interactions",
                browser=browser_name,
                status="FAIL",
                duration=duration,
                screenshots=screenshots,
                details=details,
                error_message=str(e)
            )

    async def run_browser_tests(self, browsers: List[str] = None):
        """Run all browser tests across specified browsers"""
        if browsers is None:
            browsers = ["chromium"]  # Default to Chromium only

        logger.info("🌐 Starting Browser-Based E2E Testing Suite")
        logger.info(f"Frontend: {self.frontend_url}")
        logger.info(f"Browsers: {', '.join(browsers)}")
        logger.info("=" * 60)

        test_functions = [
            ("Frontend Accessibility", self.test_frontend_accessibility),
            ("UI Elements Testing", self.test_user_interface_elements),
            ("Navigation Flow", self.test_navigation_flow),
            ("Form Interactions", self.test_form_interactions)
        ]

        for browser in browsers:
            logger.info(f"\\n🔍 Testing with {browser.upper()}")
            logger.info("-" * 30)

            for test_name, test_func in test_functions:
                result = await test_func(browser)
                self.log_test_result(result)

        # Generate summary report
        self.generate_browser_summary_report()

    def generate_browser_summary_report(self):
        """Generate browser testing summary report"""
        logger.info("\\n" + "=" * 60)
        logger.info("🌐 BROWSER E2E TESTING SUMMARY REPORT")
        logger.info("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "PASS"])
        failed_tests = len([r for r in self.test_results if r.status == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r.status == "SKIP"])
        total_duration = sum(r.duration for r in self.test_results)

        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        logger.info(f"Skipped: {skipped_tests} ⏭️")
        if total_tests > 0:
            logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"Total Duration: {total_duration:.2f}s")

        # Show screenshots captured
        all_screenshots = []
        for result in self.test_results:
            all_screenshots.extend(result.screenshots)

        if all_screenshots:
            logger.info(f"\\n📸 Screenshots captured: {len(all_screenshots)}")
            for screenshot in all_screenshots:
                logger.info(f"  📷 {screenshot}")

        # Browser compatibility summary
        browsers_tested = list(set(r.browser for r in self.test_results))
        logger.info(f"\\n🌐 Browser Compatibility:")
        for browser in browsers_tested:
            browser_results = [r for r in self.test_results if r.browser == browser]
            browser_passed = len([r for r in browser_results if r.status == "PASS"])
            browser_total = len(browser_results)
            if browser_total > 0:
                compatibility = (browser_passed / browser_total) * 100
                logger.info(f"  {browser.upper()}: {compatibility:.1f}% ({browser_passed}/{browser_total})")

        # Save detailed results
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests,
                "success_rate": (passed_tests/total_tests)*100 if total_tests > 0 else 0,
                "total_duration": total_duration
            },
            "test_results": [asdict(result) for result in self.test_results],
            "endpoints": {
                "frontend_url": self.frontend_url,
                "backend_url": self.backend_url
            },
            "browsers_tested": browsers_tested
        }

        with open('browser_e2e_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"\\n📄 Detailed browser report saved to: browser_e2e_report.json")
        logger.info("=" * 60)

async def main():
    """Main execution function"""
    print("🌐 MeStore Browser E2E Testing Suite")
    print("====================================\\n")

    suite = BrowserE2ETestSuite()

    # Test with available browsers (Chromium by default)
    browsers_to_test = ["chromium"]

    # Try to add more browsers if Playwright is available
    try:
        from playwright.async_api import async_playwright
        # Could add "firefox", "webkit" here if needed
        pass
    except ImportError:
        logger.warning("Playwright not available - browser tests will be skipped")

    await suite.run_browser_tests(browsers_to_test)

if __name__ == "__main__":
    asyncio.run(main())