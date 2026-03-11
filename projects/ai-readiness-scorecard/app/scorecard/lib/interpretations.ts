// Result band interpretations and recommendations

import type { ResultBandInfo } from "./types";
import { bandColors } from "./brand";

// Band copy - generalized for open-source use
export const BAND_COPY = {
  foundational: {
    headline: "Your organization is at the Foundational stage of AI readiness.",
    body: "Your scores indicate that the prerequisites for successful AI adoption are not yet in place. Pursuing AI initiatives today would carry a high risk of failed pilots, wasted investment, and unmanaged exposure. This is a common starting position and a solvable one.\n\nThe productive step from here is to build the foundations AI adoption requires: data that is accessible and governed, a security posture that can absorb new technology risk, and strategic clarity about what specific outcomes AI should deliver.",
    service: "Structured Readiness Assessment",
    serviceDesc:
      "A diagnostic engagement that produces a quantified picture of where you stand and a prioritized action plan for getting ready.",
  },
  developing: {
    headline: "Your organization is at the Developing stage of AI readiness.",
    body: "You have some foundations in place, but significant gaps remain across one or more critical dimensions. AI pilots may succeed in narrow, well-controlled contexts. Scaling AI adoption without addressing the identified weaknesses will likely produce the pattern that affects most organizations at this stage: a promising experiment that cannot be replicated or sustained.\n\nThe gaps identified in your scorecard are specific and addressable. A structured assessment can sequence the prerequisite work so that when you commit AI budget, it lands on a foundation that can support it.",
    service: "Structured Readiness Assessment",
    serviceDesc:
      "Identify the specific gaps, sequence the fixes, and build a credible foundation for AI adoption.",
  },
  progressing: {
    headline: "Your organization is at the Progressing stage of AI readiness.",
    body: "You have meaningful readiness in several dimensions, but your maturity is uneven. This is a common profile among organizations that are serious about AI adoption but have not yet formalized a strategy. Some areas are strong; the gaps between your strongest and weakest dimensions create risk.\n\nAI initiatives can succeed from this position with proper scoping, architecture guidance, and governance implementation.",
    service: "Strategic AI Roadmap",
    serviceDesc:
      "A 12 to 24 month AI adoption plan aligned to your business objectives, with security and governance built in from the start.",
  },
  advanced: {
    headline: "Your organization is at the Advanced stage of AI readiness.",
    body: "You have strong foundations across most dimensions. Your organization is ready for structured AI adoption with defined initiatives, clear architecture decisions, and ongoing governance. The primary risk at this stage is execution: choosing the wrong architecture, underscoping the first initiative, or moving forward without independent validation of vendor proposals.",
    service: "Architecture & Solution Design",
    serviceDesc:
      "Technical architecture guidance for your AI initiative, with security built in from the start.",
  },
  leading: {
    headline: "Your organization is at the Leading stage of AI readiness.",
    body: "Comprehensive readiness across all assessed dimensions. Your organization can pursue ambitious AI programs, including agentic AI, multi-model architectures, and complex workflow automation, with confidence in the underlying foundations.\n\nThe opportunity at this stage is acceleration: moving from capability to competitive advantage through well-architected AI systems, advanced security posture, and ongoing strategic optimization.",
    service: "Implementation Support & Advisory",
    serviceDesc:
      "Hands-on guidance during the build phase and strategic oversight as your AI program matures.",
  },
};

// Dimension-specific interpretations
export const DIM_INTERP = {
  "data-infrastructure": {
    low: "Your data environment is not ready to support AI workloads. Data is fragmented, ungoverned, or inaccessible in its current form. The first step is a data quality and governance assessment that produces a realistic picture of what must change before AI investment makes sense.",
    moderate:
      "Your data infrastructure has some foundations in place, but meaningful gaps remain. AI initiatives may succeed in narrow contexts where data is clean, but scaling will require investment in data quality, governance, and architecture.",
    strong:
      "Your data infrastructure is well-positioned to support AI workloads. Data is centralized, governed, and accessible with reasonable quality. Most organizations stall at data readiness. Your priority is ensuring the data pipeline architecture can serve the specific AI systems you plan to deploy.",
  },
  "technical-capability": {
    low: "Your technology stack has limited readiness for AI workloads. Before investing in AI tools, assess whether your infrastructure can support them and what upgrades are required. The full assessment covers this dimension in depth.",
    moderate:
      "Your organization has some technical foundations (likely cloud adoption and basic integrations) but has not yet built the infrastructure specifically required for AI workloads.",
    strong:
      "Your technology environment is well-prepared for AI adoption. Your priority is architecture design for specific AI initiatives: ensuring model selection, data pipelines, and security controls are correct for your use cases.",
  },
  "organizational-maturity": {
    low: "Executive support for AI adoption is weak or absent. Technology readiness is irrelevant if the organization is not prepared to support the change that AI adoption requires. The first step is building executive understanding and commitment.",
    moderate:
      "Executive interest exists, but the organizational machinery for AI adoption is not fully in place. Formalizing executive sponsorship with defined metrics, budget, and accountability is the prerequisite for moving forward effectively.",
    strong:
      "Your organization demonstrates strong executive commitment and organizational readiness for AI adoption. Maintain this by ensuring executive engagement remains active as AI initiatives move from strategy to execution.",
  },
  "governance-risk": {
    low: "Your organization has minimal governance infrastructure for AI. AI tools may already be in use without formal oversight, creating shadow AI risk and potential data exposure. The immediate priority is establishing a baseline AI use policy and gaining visibility into current AI tool usage.",
    moderate:
      "Some governance measures exist (likely a basic AI use policy or general awareness of AI-specific risks) but significant gaps remain. Strengthening governance before expanding AI usage prevents the accumulation of unmanaged risk that becomes exponentially harder to address later.",
    strong:
      "Your governance and risk posture for AI is strong. Fewer than one in four organizations have comprehensive AI governance in place. Your priority is ensuring governance scales with the complexity and scope of your AI program.",
  },
  "strategic-alignment": {
    low: "Without strategic clarity, organizations invest in AI without knowing what they are trying to achieve. The first step is identifying 1 to 3 specific, concrete problems that AI could address and evaluating whether the investment is justified.",
    moderate:
      "Some strategic direction exists. You may have identified potential use cases or allocated initial budget, but the connection between AI investment and business outcomes is not yet rigorous.",
    strong:
      "Your AI strategy is grounded in specific business outcomes with defined use cases, measurable success criteria, and realistic budgeting. This strategic maturity positions you to move directly to architecture and implementation, with confidence that the investment is aimed at the right targets.",
  },
};

// Result band info for display
export const resultBands: Record<string, ResultBandInfo> = {
  foundational: {
    band: "foundational",
    label: "Foundational",
    range: [0, 25],
    color: bandColors.foundational,
    description: BAND_COPY.foundational.body,
    recommendations: [
      "Build data infrastructure and governance foundations",
      "Establish baseline AI use policies and security controls",
      "Define specific AI use cases aligned to business outcomes",
      "Secure executive sponsorship with clear accountability",
      "Start with low-risk pilots to build organizational capability",
    ],
  },
  developing: {
    band: "developing",
    label: "Developing",
    range: [26, 45],
    color: bandColors.developing,
    description: BAND_COPY.developing.body,
    recommendations: [
      "Address specific gaps identified in dimensional scores",
      "Strengthen data quality and governance processes",
      "Formalize AI governance framework with documented policies",
      "Build technical capability through training and hiring",
      "Sequence prerequisite work before scaling AI adoption",
    ],
  },
  progressing: {
    band: "progressing",
    label: "Progressing",
    range: [46, 65],
    color: bandColors.progressing,
    description: BAND_COPY.progressing.body,
    recommendations: [
      "Level uneven maturity across dimensions",
      "Formalize AI strategy with 12-24 month roadmap",
      "Implement governance controls for scaling AI usage",
      "Design architecture for priority AI initiatives",
      "Establish ROI measurement framework",
    ],
  },
  advanced: {
    band: "advanced",
    label: "Advanced",
    range: [66, 80],
    color: bandColors.advanced,
    description: BAND_COPY.advanced.body,
    recommendations: [
      "Validate architecture decisions with independent review",
      "Scope first initiative for demonstrable business impact",
      "Implement MLOps for automated deployment and monitoring",
      "Strengthen vendor risk management for AI systems",
      "Build internal AI center of excellence",
    ],
  },
  leading: {
    band: "leading",
    label: "Leading",
    range: [81, 100],
    color: bandColors.leading,
    description: BAND_COPY.leading.body,
    recommendations: [
      "Pursue advanced AI capabilities (agentic AI, multi-model systems)",
      "Accelerate from capability to competitive advantage",
      "Optimize governance for complexity and scale",
      "Establish thought leadership in responsible AI practices",
      "Invest in emerging AI technologies and research partnerships",
    ],
  },
};

// Get dimension interpretation based on score
export function getDimensionInsight(
  dimension: string,
  score: number
): string {
  const insights = DIM_INTERP[dimension as keyof typeof DIM_INTERP];
  if (!insights) return "";

  if (score <= 2.0) return insights.low;
  if (score <= 3.5) return insights.moderate;
  return insights.strong;
}

// Get dimension band label
export function getDimensionBandLabel(score: number): string {
  if (score <= 2.0) return "Low";
  if (score <= 3.5) return "Moderate";
  return "Strong";
}
