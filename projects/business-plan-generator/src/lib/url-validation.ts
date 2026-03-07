// SECURITY FIX: G-1 — URL validation to prevent SSRF attacks on custom LLM endpoints

/**
 * Validates a URL to ensure it does not target internal/private networks.
 * Blocks: private IPs, localhost, link-local, cloud metadata endpoints.
 */
export function validateExternalUrl(urlString: string): { valid: boolean; error?: string } {
  if (!urlString || !urlString.trim()) {
    return { valid: false, error: 'URL is required' };
  }

  let parsed: URL;
  try {
    parsed = new URL(urlString);
  } catch {
    return { valid: false, error: 'Invalid URL format' };
  }

  // Must be HTTPS (or HTTP only for development)
  if (!['https:', 'http:'].includes(parsed.protocol)) {
    return { valid: false, error: 'Only HTTP and HTTPS protocols are allowed' };
  }

  const hostname = parsed.hostname.toLowerCase();

  // Block localhost variants
  const localhostPatterns = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '::1',
    '[::1]',
    '0177.0.0.1',      // Octal
    '2130706433',        // Decimal
    '0x7f000001',        // Hex
  ];

  if (localhostPatterns.includes(hostname)) {
    return { valid: false, error: 'Localhost addresses are not allowed' };
  }

  // Block private IP ranges
  const privateIPPatterns = [
    /^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$/,           // 10.0.0.0/8
    /^172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}$/, // 172.16.0.0/12
    /^192\.168\.\d{1,3}\.\d{1,3}$/,                 // 192.168.0.0/16
    /^169\.254\.\d{1,3}\.\d{1,3}$/,                 // Link-local
    /^100\.(6[4-9]|[7-9]\d|1[0-1]\d|12[0-7])\.\d{1,3}\.\d{1,3}$/, // Carrier-grade NAT
    /^198\.18\.\d{1,3}\.\d{1,3}$/,                  // Benchmarking
    /^198\.19\.\d{1,3}\.\d{1,3}$/,                  // Benchmarking
    /^fc[0-9a-f]{2}:/i,                              // IPv6 unique local
    /^fd[0-9a-f]{2}:/i,                              // IPv6 unique local
    /^fe80:/i,                                        // IPv6 link-local
  ];

  for (const pattern of privateIPPatterns) {
    if (pattern.test(hostname)) {
      return { valid: false, error: 'Private and internal network addresses are not allowed' };
    }
  }

  // Block cloud metadata endpoints
  const metadataHostnames = [
    '169.254.169.254',       // AWS/GCP/Azure metadata
    'metadata.google.internal',
    'metadata.google',
    '100.100.100.200',       // Alibaba Cloud metadata
  ];

  if (metadataHostnames.includes(hostname)) {
    return { valid: false, error: 'Cloud metadata endpoints are not allowed' };
  }

  // Block .internal and .local TLDs
  if (hostname.endsWith('.internal') || hostname.endsWith('.local') || hostname.endsWith('.localhost')) {
    return { valid: false, error: 'Internal domain names are not allowed' };
  }

  return { valid: true };
}

/**
 * Returns true if the URL is a known trusted provider endpoint.
 */
export function isTrustedProviderEndpoint(urlString: string): boolean {
  const trustedPrefixes = [
    'https://api.openai.com/',
    'https://api.anthropic.com/',
    'https://generativelanguage.googleapis.com/',
    'https://openrouter.ai/',
  ];

  return trustedPrefixes.some(prefix => urlString.startsWith(prefix));
}