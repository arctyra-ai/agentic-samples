import { BusinessInfo } from '@/lib/types';

interface ValidationError {
  field: string;
  message: string;
}

interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
}

export function validateBusinessInfo(info: BusinessInfo): ValidationResult {
  const errors: ValidationError[] = [];

  if (!info.companyName?.trim()) {
    errors.push({ field: 'companyName', message: 'Company name is required' });
  } else if (info.companyName.length > 100) {
    errors.push({ field: 'companyName', message: 'Company name must be 100 characters or fewer' });
  }

  if (!info.tagline?.trim()) {
    errors.push({ field: 'tagline', message: 'Tagline is required' });
  } else if (info.tagline.length > 200) {
    errors.push({ field: 'tagline', message: 'Tagline must be 200 characters or fewer' });
  }

  if (!info.primaryIndustry) {
    errors.push({ field: 'primaryIndustry', message: 'Primary industry is required' });
  }

  if (!info.geographyFocus) {
    errors.push({ field: 'geographyFocus', message: 'Geographic focus is required' });
  }

  if (!info.founderBackground?.trim()) {
    errors.push({ field: 'founderBackground', message: 'Founder background is required' });
  } else if (info.founderBackground.length > 1000) {
    errors.push({ field: 'founderBackground', message: 'Founder background must be 1000 characters or fewer' });
  }

  if (!info.servicesDescription?.trim()) {
    errors.push({ field: 'servicesDescription', message: 'Services description is required' });
  } else if (info.servicesDescription.length > 1000) {
    errors.push({ field: 'servicesDescription', message: 'Services description must be 1000 characters or fewer' });
  }

  if (!info.keyDifferentiators?.trim()) {
    errors.push({ field: 'keyDifferentiators', message: 'Key differentiators are required' });
  } else if (info.keyDifferentiators.length > 500) {
    errors.push({ field: 'keyDifferentiators', message: 'Key differentiators must be 500 characters or fewer' });
  }

  if (!info.existingIP?.trim()) {
    errors.push({ field: 'existingIP', message: 'Please describe existing IP or enter "None"' });
  } else if (info.existingIP.length > 500) {
    errors.push({ field: 'existingIP', message: 'Existing IP must be 500 characters or fewer' });
  }

  if (info.knownCompetitors && info.knownCompetitors.length > 500) {
    errors.push({ field: 'knownCompetitors', message: 'Known competitors must be 500 characters or fewer' });
  }

  const revenue = Number(info.year1RevenueGoal);
  if (!revenue || revenue <= 0) {
    errors.push({ field: 'year1RevenueGoal', message: 'Revenue goal must be greater than 0' });
  }

  const teamSize = Number(info.currentTeamSize);
  if (teamSize < 0) {
    errors.push({ field: 'currentTeamSize', message: 'Team size cannot be negative' });
  }

  if (!info.targetCompanySize) {
    errors.push({ field: 'targetCompanySize', message: 'Target company size is required' });
  }

  if (info.secondaryIndustries && info.secondaryIndustries.length > 3) {
    errors.push({ field: 'secondaryIndustries', message: 'Please select no more than 3 secondary industries' });
  }

  return { valid: errors.length === 0, errors };
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US').format(num);
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

export function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}