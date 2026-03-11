"use client";

import { useState } from "react";
import { colors } from "../lib/brand";
import { validateBusinessEmail } from "../lib/email-validation";
import type { EmailFormData } from "../lib/types";

interface EmailGateProps {
  onSubmit: (data: EmailFormData) => void;
}

const COMPANY_SIZES = [
  "1-49",
  "50-150",
  "151-500",
  "501-1,000",
  "1,001-2,500",
  "2,500+",
];

const INDUSTRIES = [
  "Technology/SaaS",
  "Financial Services",
  "Insurance",
  "Healthcare",
  "Manufacturing",
  "Professional Services",
  "Government/Public Sector",
  "Education",
  "Retail/E-Commerce",
  "Other",
];

export function EmailGate({ onSubmit }: EmailGateProps) {
  const [formData, setFormData] = useState<EmailFormData>({
    firstName: "",
    lastName: "",
    email: "",
    company: "",
    jobTitle: "",
    industry: "",
    companySize: "",
  });

  const [errors, setErrors] = useState<Partial<Record<keyof EmailFormData, string>>>({});
  const [warnings, setWarnings] = useState<Partial<Record<keyof EmailFormData, string>>>({});
  const [touched, setTouched] = useState<Partial<Record<keyof EmailFormData, boolean>>>({});
  const [isPersonalEmail, setIsPersonalEmail] = useState(false);

  const validateField = (
    name: keyof EmailFormData,
    value: string
  ): { error?: string; warning?: string } => {
    if (!value.trim()) {
      return { error: "This field is required" };
    }

    if (name === "email") {
      const validation = validateBusinessEmail(value);
      if (!validation.valid) {
        return { error: validation.error };
      }
      setIsPersonalEmail(validation.isPersonal);
      if (validation.warning) {
        return { warning: validation.warning };
      }
    }

    return {};
  };

  const handleBlur = (name: keyof EmailFormData) => {
    // Skip non-string fields
    if (name === "isPersonalEmail") return;

    setTouched({ ...touched, [name]: true });
    const value = formData[name];
    if (typeof value !== "string") return;

    const validation = validateField(name, value);

    const newErrors = { ...errors };
    const newWarnings = { ...warnings };

    if (validation.error) {
      newErrors[name] = validation.error;
    } else {
      delete newErrors[name];
    }

    if (validation.warning) {
      newWarnings[name] = validation.warning;
    } else {
      delete newWarnings[name];
    }

    setErrors(newErrors);
    setWarnings(newWarnings);
  };

  const handleChange = (name: keyof EmailFormData, value: string) => {
    setFormData({ ...formData, [name]: value });

    // Clear error/warning when user starts typing
    if (touched[name]) {
      const validation = validateField(name, value);

      const newErrors = { ...errors };
      const newWarnings = { ...warnings };

      if (validation.error) {
        newErrors[name] = validation.error;
      } else {
        delete newErrors[name];
      }

      if (validation.warning) {
        newWarnings[name] = validation.warning;
      } else {
        delete newWarnings[name];
      }

      setErrors(newErrors);
      setWarnings(newWarnings);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate all fields
    const newErrors: Partial<Record<keyof EmailFormData, string>> = {};
    const newWarnings: Partial<Record<keyof EmailFormData, string>> = {};
    let hasErrors = false;

    (Object.keys(formData) as Array<keyof EmailFormData>).forEach((key) => {
      // Skip non-string fields
      if (key === "isPersonalEmail") return;

      const value = formData[key];
      if (typeof value !== "string") return;

      const validation = validateField(key, value);
      if (validation.error) {
        newErrors[key] = validation.error;
        hasErrors = true;
      }
      if (validation.warning) {
        newWarnings[key] = validation.warning;
      }
    });

    setErrors(newErrors);
    setWarnings(newWarnings);
    setTouched({
      firstName: true,
      lastName: true,
      email: true,
      company: true,
      jobTitle: true,
      industry: true,
      companySize: true,
    });

    // Submit even if there are warnings (soft validation)
    if (!hasErrors) {
      onSubmit({ ...formData, isPersonalEmail } as any);
    }
  };

  // Check if form is valid (all required fields filled, no errors)
  const isFormValid =
    formData.firstName.trim() &&
    formData.lastName.trim() &&
    formData.email.trim() &&
    formData.company.trim() &&
    formData.jobTitle.trim() &&
    formData.industry &&
    formData.companySize &&
    Object.keys(errors).length === 0;

  const inputClasses = "w-full px-4 py-3 rounded-md text-sm transition-colors";
  const errorClasses = "text-xs mt-1";

  return (
    <div className="max-w-xl mx-auto px-6 py-12">
      <div className="text-center mb-8">
        <h2
          className="font-display text-3xl sm:text-4xl font-light mb-3"
          style={{ color: colors.white }}
        >
          Tell us about your organization
        </h2>
        <p style={{ color: colors.slate }}>
          We use this information to deliver your results and benchmark your
          scores against organizations of similar size and industry.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* First Name & Last Name */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label
              htmlFor="firstName"
              className="block text-xs font-medium uppercase tracking-wider mb-2"
              style={{ color: colors.slate }}
            >
              First Name *
            </label>
            <input
              type="text"
              id="firstName"
              value={formData.firstName}
              onChange={(e) => handleChange("firstName", e.target.value)}
              onBlur={() => handleBlur("firstName")}
              className={inputClasses}
              style={{
                backgroundColor: colors.navyLight,
                color: colors.white,
                border: `1px solid ${errors.firstName && touched.firstName ? colors.red : colors.navyMid}`,
              }}
            />
            {errors.firstName && touched.firstName && (
              <div className={errorClasses} style={{ color: colors.red }}>
                {errors.firstName}
              </div>
            )}
          </div>

          <div>
            <label
              htmlFor="lastName"
              className="block text-xs font-medium uppercase tracking-wider mb-2"
              style={{ color: colors.slate }}
            >
              Last Name *
            </label>
            <input
              type="text"
              id="lastName"
              value={formData.lastName}
              onChange={(e) => handleChange("lastName", e.target.value)}
              onBlur={() => handleBlur("lastName")}
              className={inputClasses}
              style={{
                backgroundColor: colors.navyLight,
                color: colors.white,
                border: `1px solid ${errors.lastName && touched.lastName ? colors.red : colors.navyMid}`,
              }}
            />
            {errors.lastName && touched.lastName && (
              <div className={errorClasses} style={{ color: colors.red }}>
                {errors.lastName}
              </div>
            )}
          </div>
        </div>

        {/* Work Email */}
        <div>
          <label
            htmlFor="email"
            className="block text-xs font-medium uppercase tracking-wider mb-2"
            style={{ color: colors.slate }}
          >
            Work Email *
          </label>
          <input
            type="email"
            id="email"
            value={formData.email}
            onChange={(e) => handleChange("email", e.target.value)}
            onBlur={() => handleBlur("email")}
            className={inputClasses}
            style={{
              backgroundColor: colors.navyLight,
              color: colors.white,
              border: `1px solid ${errors.email && touched.email ? colors.red : colors.navyMid}`,
            }}
          />
          {errors.email && touched.email && (
            <div className={errorClasses} style={{ color: colors.red }}>
              {errors.email}
            </div>
          )}
          {!errors.email && warnings.email && touched.email && (
            <div className={errorClasses} style={{ color: colors.orange }}>
              {warnings.email}
            </div>
          )}
        </div>

        {/* Company Name */}
        <div>
          <label
            htmlFor="company"
            className="block text-xs font-medium uppercase tracking-wider mb-2"
            style={{ color: colors.slate }}
          >
            Company Name *
          </label>
          <input
            type="text"
            id="company"
            value={formData.company}
            onChange={(e) => handleChange("company", e.target.value)}
            onBlur={() => handleBlur("company")}
            className={inputClasses}
            style={{
              backgroundColor: colors.navyLight,
              color: colors.white,
              border: `1px solid ${errors.company && touched.company ? colors.red : colors.navyMid}`,
            }}
          />
          {errors.company && touched.company && (
            <div className={errorClasses} style={{ color: colors.red }}>
              {errors.company}
            </div>
          )}
        </div>

        {/* Job Title */}
        <div>
          <label
            htmlFor="jobTitle"
            className="block text-xs font-medium uppercase tracking-wider mb-2"
            style={{ color: colors.slate }}
          >
            Job Title *
          </label>
          <input
            type="text"
            id="jobTitle"
            value={formData.jobTitle}
            onChange={(e) => handleChange("jobTitle", e.target.value)}
            onBlur={() => handleBlur("jobTitle")}
            className={inputClasses}
            style={{
              backgroundColor: colors.navyLight,
              color: colors.white,
              border: `1px solid ${errors.jobTitle && touched.jobTitle ? colors.red : colors.navyMid}`,
            }}
          />
          {errors.jobTitle && touched.jobTitle && (
            <div className={errorClasses} style={{ color: colors.red }}>
              {errors.jobTitle}
            </div>
          )}
        </div>

        {/* Company Size & Industry */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label
              htmlFor="companySize"
              className="block text-xs font-medium uppercase tracking-wider mb-2"
              style={{ color: colors.slate }}
            >
              Company Size *
            </label>
            <select
              id="companySize"
              value={formData.companySize}
              onChange={(e) => handleChange("companySize", e.target.value)}
              onBlur={() => handleBlur("companySize")}
              className={inputClasses}
              style={{
                backgroundColor: colors.navyLight,
                color: formData.companySize ? colors.white : colors.slateDark,
                border: `1px solid ${errors.companySize && touched.companySize ? colors.red : colors.navyMid}`,
              }}
            >
              <option value="">Select...</option>
              {COMPANY_SIZES.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
            {errors.companySize && touched.companySize && (
              <div className={errorClasses} style={{ color: colors.red }}>
                {errors.companySize}
              </div>
            )}
          </div>

          <div>
            <label
              htmlFor="industry"
              className="block text-xs font-medium uppercase tracking-wider mb-2"
              style={{ color: colors.slate }}
            >
              Industry *
            </label>
            <select
              id="industry"
              value={formData.industry}
              onChange={(e) => handleChange("industry", e.target.value)}
              onBlur={() => handleBlur("industry")}
              className={inputClasses}
              style={{
                backgroundColor: colors.navyLight,
                color: formData.industry ? colors.white : colors.slateDark,
                border: `1px solid ${errors.industry && touched.industry ? colors.red : colors.navyMid}`,
              }}
            >
              <option value="">Select...</option>
              {INDUSTRIES.map((industry) => (
                <option key={industry} value={industry}>
                  {industry}
                </option>
              ))}
            </select>
            {errors.industry && touched.industry && (
              <div className={errorClasses} style={{ color: colors.red }}>
                {errors.industry}
              </div>
            )}
          </div>
        </div>

        {/* Submit Button */}
        <div className="pt-4">
          <button
            type="submit"
            disabled={!isFormValid}
            className="w-full px-8 py-4 rounded-md font-semibold transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            style={{
              backgroundColor: isFormValid ? colors.gold : colors.navyMid,
              color: isFormValid ? colors.navy : colors.slate,
            }}
            onMouseEnter={(e) => {
              if (isFormValid) {
                e.currentTarget.style.backgroundColor = colors.goldLight;
              }
            }}
            onMouseLeave={(e) => {
              if (isFormValid) {
                e.currentTarget.style.backgroundColor = colors.gold;
              }
            }}
          >
            Continue to Assessment
          </button>
        </div>

        {/* Privacy microcopy */}
        <p className="text-xs text-center pt-2" style={{ color: colors.slateDark }}>
          Your information is used to deliver your scorecard results and provide relevant benchmarking. We do not share your information with third parties.
        </p>
      </form>
    </div>
  );
}
