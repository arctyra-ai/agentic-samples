// Email validation utilities with soft validation for personal domains

const PERSONAL_EMAIL_DOMAINS = [
  "gmail.com",
  "yahoo.com",
  "hotmail.com",
  "outlook.com",
  "aol.com",
  "icloud.com",
  "me.com",
  "mac.com",
  "mail.com",
  "protonmail.com",
  "proton.me",
  "zoho.com",
  "yandex.com",
  "gmx.com",
  "live.com",
  "msn.com",
  "comcast.net",
  "verizon.net",
  "att.net",
  "cox.net",
];

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function isPersonalEmail(email: string): boolean {
  if (!email || !email.includes("@")) return false;
  const domain = email.toLowerCase().split("@")[1];
  return PERSONAL_EMAIL_DOMAINS.includes(domain);
}

export function validateBusinessEmail(email: string): {
  valid: boolean;
  isPersonal: boolean;
  error?: string;
  warning?: string;
} {
  if (!email) {
    return { valid: false, isPersonal: false, error: "Email is required" };
  }

  if (!isValidEmail(email)) {
    return {
      valid: false,
      isPersonal: false,
      error: "Please enter a valid email address",
    };
  }

  const personal = isPersonalEmail(email);

  // Soft validation: allow personal emails but show warning
  if (personal) {
    return {
      valid: true,
      isPersonal: true,
      warning:
        "Please use your work email address if possible. This helps us benchmark your results accurately against organizations in your industry.",
    };
  }

  return { valid: true, isPersonal: false };
}
