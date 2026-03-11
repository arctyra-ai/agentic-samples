// Scorecard brand colors - customize these to match your brand
// This color palette uses navy/gold theme by default

export const colors = {
  // Navy backgrounds
  navy: "#0B1120",
  navyLight: "#131B2E",
  navyMid: "#1A2540",

  // Gold accents
  gold: "#C9A84C",
  goldLight: "#E0C872",

  // Slate text
  slate: "#8B95A8",
  slateDark: "#7B8698",

  // White/off-white
  white: "#F5F5F0",
  offWhite: "#E8E6E0",

  // Semantic colors
  red: "#C44B4B",
  orange: "#D4883C",
  green: "#4B8B6E",
  greenLight: "#6AAF8B",
} as const;

// Dimension colors for the chart
export const dimensionColors = {
  "data-infrastructure": colors.greenLight, // 25% weight
  "technical-capability": "#6B9BD1", // Blue shade, 20% weight
  "organizational-maturity": "#D98B5C", // Warm orange, 15% weight
  "governance-risk": "#8B7AB8", // Purple shade, 25% weight
  "strategic-alignment": colors.gold, // 15% weight
} as const;

// Result band colors
export const bandColors = {
  foundational: colors.red, // #C44B4B
  developing: colors.orange, // #D4883C
  progressing: colors.gold, // #C9A84C
  advanced: colors.green, // #4B8B6E
  leading: colors.greenLight, // #6AAF8B
} as const;
