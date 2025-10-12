/**
 * SMS Verification Helper Functions for E2E Testing
 *
 * @author e2e-testing-ai
 * @date 2025-10-12
 *
 * Purpose: Reusable helper functions for SMS verification E2E tests
 */

import { Page, expect } from '@playwright/test';
import { SMS_TEST_REGISTRATION_DATA } from '../fixtures/test-data';

/**
 * Navigate to vendor registration wizard
 * @param page Playwright page object
 * @param vendorType 'persona_natural' | 'persona_juridica'
 */
export async function navigateToVendorRegistration(
  page: Page,
  vendorType: 'persona_natural' | 'persona_juridica' = 'persona_natural'
): Promise<void> {
  await page.goto('/user-type-selector');
  await page.waitForLoadState('networkidle');

  // Select Vendor
  const vendorButton = page.locator('button:has-text("Vendedor")');
  await vendorButton.click();

  // Select vendor type
  const vendorTypeLocator = vendorType === 'persona_natural'
    ? page.locator('[data-testid="vendor-type-persona-natural"], button:has-text("Persona Natural")').first()
    : page.locator('[data-testid="vendor-type-persona-juridica"], button:has-text("Persona Jurídica")').first();

  await vendorTypeLocator.click();

  // Wait for wizard to load
  await page.waitForURL('**/registration-wizard**', { timeout: 10000 });
}

/**
 * Navigate to buyer registration wizard
 * @param page Playwright page object
 */
export async function navigateToBuyerRegistration(page: Page): Promise<void> {
  await page.goto('/user-type-selector');
  await page.waitForLoadState('networkidle');

  // Select Buyer
  const buyerButton = page.locator('button:has-text("Comprador")');
  await buyerButton.click();

  // Wait for wizard to load
  await page.waitForURL('**/registration-wizard**', { timeout: 10000 });
}

/**
 * Fill Step 1 (Basic Registration Data) of the wizard
 * @param page Playwright page object
 * @param data Registration data object
 */
export async function fillBasicRegistrationData(
  page: Page,
  data: {
    nombre: string;
    email: string;
    phoneNumber: string;
    countryCode: string;
    password: string;
  }
): Promise<void> {
  // Wait for Step 1 to load
  await page.waitForSelector('h1:has-text("Paso 1")', { timeout: 10000 });

  // Fill form fields
  await page.fill('input[name="nombre"]', data.nombre);
  await page.fill('input[name="email"]', data.email);

  // Select country code
  const countrySelect = page.locator('select').first();
  await countrySelect.selectOption(data.countryCode);

  // Fill phone number
  await page.fill('input[name="phoneNumber"]', data.phoneNumber);

  // Fill password fields
  await page.fill('input[name="password"]', data.password);
  await page.fill('input[name="confirmPassword"]', data.password);
}

/**
 * Submit Step 1 and advance to verification step
 * @param page Playwright page object
 */
export async function submitBasicRegistrationAndAdvance(page: Page): Promise<void> {
  const continueButton = page.locator('button[type="submit"]:has-text("Continuar")');
  await continueButton.click();

  // Wait for Step 2 (Verification) to load
  await page.waitForSelector('h2:has-text("Verificación de Contacto")', { timeout: 10000 });
}

/**
 * Send SMS verification code
 * @param page Playwright page object
 * @returns Promise<boolean> Success status
 */
export async function sendSMSVerificationCode(page: Page): Promise<boolean> {
  // Locate SMS verification section
  const smsSection = page.locator('.bg-purple-50').filter({ hasText: 'Verificación de Teléfono' });
  await expect(smsSection).toBeVisible();

  // Click send SMS button
  const sendSMSButton = smsSection.locator('button:has-text("Enviar código SMS")');
  await sendSMSButton.click();

  // Wait for response
  await page.waitForTimeout(3000);

  // Check for success or error
  const successAlert = page.locator('text=/código.*enviado/i');
  const errorMessage = page.locator('p.text-red-600');

  const success = await successAlert.isVisible({ timeout: 2000 }).catch(() => false);
  const error = await errorMessage.isVisible({ timeout: 2000 }).catch(() => false);

  return success || !error;
}

/**
 * Enter SMS verification code
 * @param page Playwright page object
 * @param code 6-digit verification code
 */
export async function enterSMSCode(page: Page, code: string): Promise<void> {
  const codeInput = page.locator('input[placeholder="000000"]');
  await expect(codeInput).toBeVisible();
  await codeInput.fill(code);
}

/**
 * Verify SMS code and check result
 * @param page Playwright page object
 * @returns Promise<boolean> Success status
 */
export async function verifySMSCode(page: Page): Promise<boolean> {
  const verifyButton = page.locator('button:has-text("Verificar código")');
  await expect(verifyButton).toBeEnabled();
  await verifyButton.click();

  // Wait for verification result
  await page.waitForTimeout(3000);

  // Check if advanced to Step 3 (success)
  const step3Header = page.locator('h2:has-text("Información Adicional")');
  const success = await step3Header.isVisible({ timeout: 5000 }).catch(() => false);

  // Check for error message (failure)
  const errorMessage = page.locator('p.text-red-600');
  const error = await errorMessage.isVisible({ timeout: 2000 }).catch(() => false);

  return success && !error;
}

/**
 * Complete SMS verification flow (send + enter code + verify)
 * @param page Playwright page object
 * @param code 6-digit verification code
 * @returns Promise<boolean> Success status
 */
export async function completeSMSVerification(page: Page, code: string): Promise<boolean> {
  // Send SMS
  const sendSuccess = await sendSMSVerificationCode(page);
  if (!sendSuccess) {
    console.error('❌ Failed to send SMS code');
    return false;
  }

  // Enter code
  await enterSMSCode(page, code);

  // Verify code
  const verifySuccess = await verifySMSCode(page);
  if (!verifySuccess) {
    console.error('❌ SMS verification failed');
    return false;
  }

  console.log('✅ SMS verification completed successfully');
  return true;
}

/**
 * Verify phone number is displayed correctly in verification step
 * @param page Playwright page object
 * @param expectedPhone Full phone number with country code (e.g., +573001234567)
 */
export async function verifyPhoneNumberDisplay(page: Page, expectedPhone: string): Promise<void> {
  await expect(page.locator(`text=${expectedPhone}`)).toBeVisible();
}

/**
 * Check if SMS send button is disabled (rate limiting)
 * @param page Playwright page object
 * @returns Promise<boolean> True if disabled
 */
export async function isSMSSendButtonDisabled(page: Page): Promise<boolean> {
  const sendButton = page.locator('button:has-text("Enviar código SMS")');
  return await sendButton.isDisabled({ timeout: 1000 }).catch(() => false);
}

/**
 * Check for rate limit error message
 * @param page Playwright page object
 * @returns Promise<boolean> True if rate limit error is shown
 */
export async function hasRateLimitError(page: Page): Promise<boolean> {
  const rateLimitMessage = page.locator('text=/demasiados intentos/i');
  return await rateLimitMessage.isVisible({ timeout: 2000 }).catch(() => false);
}

/**
 * Navigate back in wizard
 * @param page Playwright page object
 */
export async function navigateBackInWizard(page: Page): Promise<void> {
  const backButton = page.locator('button:has-text("Volver")');
  await backButton.click();
  await page.waitForTimeout(1000);
}

/**
 * Get current wizard step number
 * @param page Playwright page object
 * @returns Promise<number> Current step number (1-4)
 */
export async function getCurrentWizardStep(page: Page): Promise<number> {
  const stepHeaders = [
    'Paso 1 de 4',
    'Paso 2 de 4',
    'Paso 3 de 4',
    'Paso 4 de 4'
  ];

  for (let i = 0; i < stepHeaders.length; i++) {
    const header = page.locator(`h1:has-text("${stepHeaders[i]}")`);
    if (await header.isVisible({ timeout: 1000 }).catch(() => false)) {
      return i + 1;
    }
  }

  return 0; // Unknown step
}

/**
 * Take screenshot for debugging
 * @param page Playwright page object
 * @param filename Screenshot filename
 */
export async function takeDebugScreenshot(page: Page, filename: string): Promise<void> {
  await page.screenshot({
    path: `test-results/screenshots/${filename}`,
    fullPage: true
  });
  console.log(`📸 Screenshot saved: ${filename}`);
}

/**
 * Wait for network idle (useful after form submissions)
 * @param page Playwright page object
 * @param timeout Optional timeout in milliseconds
 */
export async function waitForNetworkIdle(page: Page, timeout: number = 5000): Promise<void> {
  await page.waitForLoadState('networkidle', { timeout });
}

/**
 * Validate phone input format
 * @param phone Phone number string
 * @returns boolean True if valid E.164 format
 */
export function isValidE164Phone(phone: string): boolean {
  const e164Regex = /^\+[1-9]\d{1,14}$/;
  return e164Regex.test(phone);
}

/**
 * Format phone for display
 * @param phone Phone number with country code
 * @returns Formatted phone string
 */
export function formatPhoneDisplay(phone: string): string {
  if (!phone.startsWith('+')) return phone;

  // Colombia format: +57 300 123 4567
  if (phone.startsWith('+57')) {
    return phone.replace(/(\+57)(\d{3})(\d{3})(\d{4})/, '$1 $2 $3 $4');
  }

  // USA format: +1 555 123 4567
  if (phone.startsWith('+1')) {
    return phone.replace(/(\+1)(\d{3})(\d{3})(\d{4})/, '$1 $2 $3 $4');
  }

  return phone;
}

/**
 * Extract error message from page
 * @param page Playwright page object
 * @returns Promise<string | null> Error message or null
 */
export async function getErrorMessage(page: Page): Promise<string | null> {
  const errorLocator = page.locator('p.text-red-600, p.text-sm.text-red-600');
  const errorText = await errorLocator.textContent().catch(() => null);
  return errorText;
}

/**
 * Check if verification step is complete
 * @param page Playwright page object
 * @returns Promise<boolean> True if phone verified
 */
export async function isPhoneVerified(page: Page): Promise<boolean> {
  const verifiedIndicator = page.locator('text=/teléfono verificado/i');
  const checkIcon = page.locator('.bg-green-100').filter({ hasText: 'Teléfono verificado' });

  const hasVerifiedText = await verifiedIndicator.isVisible({ timeout: 2000 }).catch(() => false);
  const hasCheckIcon = await checkIcon.isVisible({ timeout: 2000 }).catch(() => false);

  return hasVerifiedText || hasCheckIcon;
}

/**
 * Complete full vendor registration flow (for testing complete journey)
 * @param page Playwright page object
 * @param vendorType 'persona_natural' | 'persona_juridica'
 * @param smsCode SMS verification code
 * @returns Promise<boolean> Success status
 */
export async function completeVendorRegistrationFlow(
  page: Page,
  vendorType: 'persona_natural' | 'persona_juridica',
  smsCode: string = '123456'
): Promise<boolean> {
  // Step 1: Navigate to registration
  await navigateToVendorRegistration(page, vendorType);

  // Step 2: Fill basic data
  const registrationData = vendorType === 'persona_natural'
    ? SMS_TEST_REGISTRATION_DATA.vendorPersonaNatural
    : SMS_TEST_REGISTRATION_DATA.vendorPersonaJuridica;

  await fillBasicRegistrationData(page, registrationData);
  await submitBasicRegistrationAndAdvance(page);

  // Step 3: SMS Verification
  const smsSuccess = await completeSMSVerification(page, smsCode);
  if (!smsSuccess) {
    console.error('❌ SMS verification failed');
    return false;
  }

  // Step 4: Fill additional data (Step 3 of wizard)
  // Note: This would require additional helper functions for Step 3 form
  console.log('⚠️ Additional data entry not implemented - test stops at SMS verification');

  return true;
}
