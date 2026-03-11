// Analytics utility for scorecard event tracking
// Stubbed out - no analytics integration

/**
 * Track a custom event (no-op stub)
 * @param name Event name (e.g., "scorecard_started")
 * @param properties Optional event properties
 */
export function trackEvent(
  name: string,
  properties?: Record<string, string | number | boolean>
): void {
  // No-op: You can add your own analytics integration here
  if (process.env.NODE_ENV === "development") {
    console.log("[Analytics] Event:", name, properties);
  }
}

/**
 * Track page view (no-op stub)
 * @param path Page path
 * @param title Optional page title
 */
export function trackPageView(path: string, title?: string): void {
  // No-op: You can add your own analytics integration here
  if (process.env.NODE_ENV === "development") {
    console.log("[Analytics] Page view:", path, title);
  }
}
