// AI Readiness Assessment Questions

import type { Question, DimensionMetadata } from "./types";
import { dimensionColors } from "./brand";

export const dimensionMetadata: Record<string, DimensionMetadata> = {
  "data-infrastructure": {
    id: "data-infrastructure",
    label: "Data Infrastructure",
    description:
      "These five questions assess whether your organization's data is accessible, governed, and architecturally ready to support AI workloads. Data readiness is the most common barrier to successful AI adoption.",
    color: dimensionColors["data-infrastructure"],
    weight: 25,
  },
  "technical-capability": {
    id: "technical-capability",
    label: "Technical Capability",
    description:
      "This question provides a directional assessment of your technology team's experience with AI tools and deployment. The full assessment covers this dimension in depth across five questions.",
    color: dimensionColors["technical-capability"],
    weight: 20,
  },
  "organizational-maturity": {
    id: "organizational-maturity",
    label: "Organizational Maturity",
    description:
      "This question assesses the strength of executive commitment to AI adoption. The full assessment covers organizational readiness across five questions including change management, AI literacy, and capacity.",
    color: dimensionColors["organizational-maturity"],
    weight: 15,
  },
  "governance-risk": {
    id: "governance-risk",
    label: "Governance & Risk Readiness",
    description:
      "These five questions assess your organization's ability to adopt AI safely: use policies, shadow AI awareness, AI-specific threat understanding, vendor risk, and incident response. Most AI readiness tools do not assess this dimension at all.",
    color: dimensionColors["governance-risk"],
    weight: 25,
  },
  "strategic-alignment": {
    id: "strategic-alignment",
    label: "Strategic Alignment",
    description:
      "These five questions assess whether your AI ambitions are grounded in specific business outcomes, realistic prioritization, and defensible investment.",
    color: dimensionColors["strategic-alignment"],
    weight: 15,
  },
};

// 17 questions across 5 dimensions
// Scoring: 1-5 scale (first option = 1, last option = 5)
export const questions: Question[] = [
  // DATA INFRASTRUCTURE (5 questions, 25% weight)
  {
    id: "q1",
    dimension: "data-infrastructure",
    text: "How centralized and accessible is the data your organization would need for AI initiatives?",
    options: [
      {
        value: 1,
        label: "Disconnected data",
        description:
          "Data lives in disconnected spreadsheets, email, and individual systems with no central access",
      },
      {
        value: 2,
        label: "Some centralization",
        description:
          "Some data is centralized (e.g., a CRM or ERP), but most operational data is siloed across teams",
      },
      {
        value: 3,
        label: "Core data centralized",
        description:
          "Core business data is centralized in one or two systems, but significant data remains in departmental tools",
      },
      {
        value: 4,
        label: "Most data centralized",
        description:
          "Most business-critical data is centralized with defined access patterns, though some gaps exist",
      },
      {
        value: 5,
        label: "Fully centralized",
        description:
          "Business data is centralized, cataloged, and accessible through documented interfaces or data platforms",
      },
    ],
  },
  {
    id: "q2",
    dimension: "data-infrastructure",
    text: "How would you describe the quality (accuracy, completeness, consistency) of your organization's core business data?",
    options: [
      {
        value: 1,
        label: "No understanding",
        description:
          "We have no formal understanding of our data quality. No one has assessed it.",
      },
      {
        value: 2,
        label: "Known problem",
        description:
          "We know data quality is a problem, but we have no process for measuring or improving it",
      },
      {
        value: 3,
        label: "Reactive fixes",
        description:
          "We have identified specific data quality issues and are addressing them reactively",
      },
      {
        value: 4,
        label: "Formal processes",
        description:
          "We have formal data quality processes for our most important datasets, with regular audits",
      },
      {
        value: 5,
        label: "Systematic management",
        description:
          "We have systematic data quality management across key datasets, with automated monitoring and defined standards",
      },
    ],
  },
  {
    id: "q3",
    dimension: "data-infrastructure",
    text: "Does your organization have formal data governance: documented policies for who owns data, who can access it, and how it is managed?",
    options: [
      {
        value: 1,
        label: "No governance",
        description: "No data governance policies exist",
      },
      {
        value: 2,
        label: "Informal guidelines",
        description:
          "Informal guidelines exist but are not documented or consistently followed",
      },
      {
        value: 3,
        label: "Basic policies",
        description:
          "Basic data governance policies exist for some systems, but gaps are significant",
      },
      {
        value: 4,
        label: "Formal governance",
        description:
          "Formal data governance covers most business-critical systems, with defined ownership and access controls",
      },
      {
        value: 5,
        label: "Comprehensive governance",
        description:
          "Comprehensive data governance with documented policies, regular reviews, clear ownership, and enforcement",
      },
    ],
  },
  {
    id: "q4",
    dimension: "data-infrastructure",
    text: "How mature is your organization's handling of data privacy and regulatory compliance?",
    options: [
      {
        value: 1,
        label: "Not assessed",
        description: "We have not assessed our data privacy obligations",
      },
      {
        value: 2,
        label: "Aware but not compliant",
        description:
          "We are aware of applicable regulations but have not implemented formal compliance measures",
      },
      {
        value: 3,
        label: "Basic measures",
        description:
          "Basic privacy measures are in place (privacy policy, consent mechanisms) but not audited or comprehensive",
      },
      {
        value: 4,
        label: "Formal program",
        description:
          "Formal privacy program exists with documented processes, regular assessments, and defined roles",
      },
      {
        value: 5,
        label: "Mature program",
        description:
          "Mature privacy program with regular audits, documented data flows, incident response procedures, and regulatory monitoring",
      },
    ],
  },
  {
    id: "q5",
    dimension: "data-infrastructure",
    text: "Could your current data systems provide clean, structured data to an AI tool or model if you deployed one today?",
    options: [
      {
        value: 1,
        label: "Not ready",
        description:
          "No. Our data is not in a format that any AI system could use without major rework.",
      },
      {
        value: 2,
        label: "One narrow use case",
        description:
          "Possibly for one narrow use case, but it would require significant manual data preparation",
      },
      {
        value: 3,
        label: "Some datasets ready",
        description:
          "Some datasets are ready, but most would require cleaning, structuring, or integration work",
      },
      {
        value: 4,
        label: "Most critical datasets ready",
        description:
          "Most critical datasets could support AI workloads with moderate preparation",
      },
      {
        value: 5,
        label: "AI-ready architecture",
        description:
          "Our data architecture is designed for analytical and AI workloads. Data is accessible through defined interfaces, transformation pipelines exist, and data formats are documented.",
      },
    ],
  },

  // TECHNICAL CAPABILITY (1 signal question, 20% weight)
  {
    id: "q6",
    dimension: "technical-capability",
    text: "What is your organization's current use of AI tools, beyond individuals using them for personal productivity?",
    options: [
      {
        value: 1,
        label: "No organizational use",
        description: "No organizational AI tool usage",
      },
      {
        value: 2,
        label: "Individual use only",
        description:
          "Individuals use AI tools for personal productivity, but there is no organizational policy or coordination around this usage",
      },
      {
        value: 3,
        label: "Team-level deployment",
        description:
          "One or two AI-powered tools have been deployed at the team or department level",
      },
      {
        value: 4,
        label: "Multiple tools coordinated",
        description:
          "Multiple AI tools are in use across the organization with some coordination and governance",
      },
      {
        value: 5,
        label: "Embedded in workflows",
        description:
          "AI tools are embedded into core workflows with defined use policies, evaluation criteria, and performance monitoring",
      },
    ],
  },

  // ORGANIZATIONAL MATURITY (1 signal question, 15% weight)
  {
    id: "q7",
    dimension: "organizational-maturity",
    text: "How strong is executive support for AI adoption in your organization?",
    options: [
      {
        value: 1,
        label: "No executive interest",
        description: "No executive interest or awareness of AI as a strategic priority",
      },
      {
        value: 2,
        label: "Aware but not committed",
        description:
          "Executives are aware of AI but have not committed resources or defined expectations",
      },
      {
        value: 3,
        label: "One champion",
        description:
          "One executive champion exists, but AI is not a leadership team or board-level priority",
      },
      {
        value: 4,
        label: "Leadership priority",
        description:
          "AI adoption is a stated leadership priority with dedicated budget and executive accountability",
      },
      {
        value: 5,
        label: "Board-level priority",
        description:
          "AI is a board-level strategic priority with defined metrics, regular executive review, and cross-functional mandate",
      },
    ],
  },

  // GOVERNANCE & RISK READINESS (5 questions, 25% weight)
  {
    id: "q8",
    dimension: "governance-risk",
    text: "Does your organization have a formal policy governing how AI tools are used?",
    options: [
      {
        value: 1,
        label: "No policy",
        description:
          "No AI use policy exists. Employees use AI tools at their own discretion.",
      },
      {
        value: 2,
        label: "Informal guidance",
        description:
          "Informal guidance exists (e.g., do not put customer data into AI tools) but nothing documented",
      },
      {
        value: 3,
        label: "Basic policy",
        description:
          "A basic AI use policy exists but covers only general guidance, not specific tools, data types, or use cases",
      },
      {
        value: 4,
        label: "Documented policy",
        description:
          "Documented AI use policy covering approved tools, prohibited uses, data handling rules, and review processes",
      },
      {
        value: 5,
        label: "Comprehensive framework",
        description:
          "Comprehensive AI governance framework including use policy, vendor assessment criteria, incident response, regular review, and executive accountability",
      },
    ],
  },
  {
    id: "q9",
    dimension: "governance-risk",
    text: "How confident are you that you know which AI tools employees are currently using, and what data they are putting into them?",
    options: [
      {
        value: 1,
        label: "No visibility",
        description: "We have no visibility into AI tool usage across the organization",
      },
      {
        value: 2,
        label: "Suspect but cannot confirm",
        description:
          "We suspect employees are using AI tools, but we have no way to confirm or monitor this",
      },
      {
        value: 3,
        label: "Partial awareness",
        description:
          "We are aware of some AI tool usage but know there are tools and uses we have not identified",
      },
      {
        value: 4,
        label: "Reasonable visibility",
        description:
          "We have reasonable visibility through policy enforcement, tool audits, or technical controls",
      },
      {
        value: 5,
        label: "Comprehensive visibility",
        description:
          "We have comprehensive visibility including an approved tool inventory, usage monitoring, and enforcement mechanisms",
      },
    ],
  },
  {
    id: "q10",
    dimension: "governance-risk",
    text: "How familiar is your leadership team with the specific risks introduced by AI systems, such as data leakage through AI tools, biased outputs, fabricated content, or prompt manipulation?",
    options: [
      {
        value: 1,
        label: "Not considered",
        description:
          "Leadership has not considered AI-specific risks beyond general technology risk",
      },
      {
        value: 2,
        label: "General awareness",
        description:
          "General awareness exists, but no one could articulate specific AI risk categories",
      },
      {
        value: 3,
        label: "Some understanding",
        description:
          "Some team members understand AI-specific risks, but this knowledge is not shared or documented",
      },
      {
        value: 4,
        label: "Briefed with assessment",
        description:
          "Leadership has been briefed on AI-specific risks and a documented risk assessment exists",
      },
      {
        value: 5,
        label: "Comprehensive assessment",
        description:
          "Comprehensive AI risk assessment completed, covering threat model, data exposure, vendor risk, and regulatory obligations, with defined mitigations",
      },
    ],
  },
  {
    id: "q11",
    dimension: "governance-risk",
    text: "How does your organization assess the AI components in the vendor tools and platforms you already use?",
    options: [
      {
        value: 1,
        label: "Not assessed",
        description: "We do not assess AI components in vendor tools",
      },
      {
        value: 2,
        label: "Aware but not evaluated",
        description:
          "We are aware some vendors use AI but have not evaluated the implications",
      },
      {
        value: 3,
        label: "Ad hoc questions",
        description:
          "We ask vendors about AI usage during procurement but have no formal assessment framework",
      },
      {
        value: 4,
        label: "Formal assessment",
        description:
          "A formal vendor AI assessment process covers data handling, model transparency, and security for new procurements",
      },
      {
        value: 5,
        label: "Comprehensive management",
        description:
          "Comprehensive vendor AI risk management including audit rights, ongoing monitoring, and contractual controls",
      },
    ],
  },
  {
    id: "q12",
    dimension: "governance-risk",
    text: "If an AI system in your organization produced a harmful output (a biased decision, a data leak, or a public-facing error), would your team know how to respond?",
    options: [
      {
        value: 1,
        label: "No capability",
        description: "No. We have no incident response capability for AI-related events.",
      },
      {
        value: 2,
        label: "Would improvise",
        description: "We would improvise a response, but no documented process exists",
      },
      {
        value: 3,
        label: "General process only",
        description:
          "General incident response processes exist but do not specifically address AI-related failures",
      },
      {
        value: 4,
        label: "AI-specific guidance",
        description:
          "AI-specific incident response guidance exists, though it has not been tested",
      },
      {
        value: 5,
        label: "Documented and tested",
        description:
          "Documented, tested incident response procedure for AI-related events with defined roles, escalation paths, and communication plans",
      },
    ],
  },

  // STRATEGIC ALIGNMENT (5 questions, 15% weight)
  {
    id: "q13",
    dimension: "strategic-alignment",
    text: "Has your organization identified specific, concrete use cases for AI? Not 'we should use AI' generally, but 'we need AI to solve this specific problem.'",
    options: [
      {
        value: 1,
        label: "No use cases",
        description: "No specific AI use cases have been identified",
      },
      {
        value: 2,
        label: "General ideas",
        description:
          "We have general ideas (\"improve customer service,\" \"automate reporting\") but nothing scoped or prioritized",
      },
      {
        value: 3,
        label: "1-3 use cases",
        description:
          "We have identified 1 to 3 specific use cases, though they have not been evaluated for feasibility or ROI",
      },
      {
        value: 4,
        label: "Prioritized list",
        description:
          "A prioritized list of use cases exists with estimated business impact and feasibility assessment",
      },
      {
        value: 5,
        label: "Detailed roadmap",
        description:
          "Detailed AI roadmap with prioritized use cases, defined success metrics, resource plans, and build/buy/partner recommendations",
      },
    ],
  },
  {
    id: "q14",
    dimension: "strategic-alignment",
    text: "How would your organization measure whether an AI initiative is delivering value?",
    options: [
      {
        value: 1,
        label: "Not considered",
        description: "We have not considered how to measure AI ROI",
      },
      {
        value: 2,
        label: "Subjective feedback",
        description:
          "We would rely on subjective feedback (\"it feels faster\") with no quantitative measurement",
      },
      {
        value: 3,
        label: "Could measure some outcomes",
        description:
          "We could measure some outcomes (time savings, error reduction) but have not defined specific metrics for AI initiatives",
      },
      {
        value: 4,
        label: "Defined metrics",
        description:
          "We have defined success metrics for at least one AI initiative, with a baseline measurement in place",
      },
      {
        value: 5,
        label: "Structured framework",
        description:
          "Structured ROI measurement framework for AI initiatives, with baseline data, defined KPIs, and regular review cadence",
      },
    ],
  },
  {
    id: "q15",
    dimension: "strategic-alignment",
    text: "Has your organization allocated a realistic budget for AI adoption, including not just tools, but data preparation, integration, training, and ongoing governance?",
    options: [
      {
        value: 1,
        label: "No budget",
        description: "No budget has been allocated or discussed",
      },
      {
        value: 2,
        label: "Tools only",
        description:
          "Some budget exists, but only for AI tool subscriptions. No allocation for implementation, training, or governance.",
      },
      {
        value: 3,
        label: "Tools and implementation",
        description:
          "Budget covers tools and initial implementation, but does not account for ongoing governance, training, or maintenance",
      },
      {
        value: 4,
        label: "Realistic first year",
        description:
          "Realistic budget allocated covering tools, implementation, training, and ongoing operations for the first year",
      },
      {
        value: 5,
        label: "Multi-year plan",
        description:
          "Multi-year AI investment plan with budgets for infrastructure, implementation, training, governance, and continuous improvement",
      },
    ],
  },
  {
    id: "q16",
    dimension: "strategic-alignment",
    text: "How well does your organization understand what your competitors and industry peers are doing with AI?",
    options: [
      {
        value: 1,
        label: "No awareness",
        description: "No awareness of competitors' AI activities",
      },
      {
        value: 2,
        label: "General awareness",
        description:
          "General awareness (\"competitors are using AI\") with no specific intelligence",
      },
      {
        value: 3,
        label: "Some understanding",
        description:
          "We have some understanding of what 1 to 2 competitors are doing with AI, but analysis is informal",
      },
      {
        value: 4,
        label: "Structured intelligence",
        description:
          "Structured competitive intelligence on AI adoption in our industry, including specific competitor activities",
      },
      {
        value: 5,
        label: "Regular landscape analysis",
        description:
          "Regular competitive AI landscape analysis informing our strategic priorities and investment decisions",
      },
    ],
  },
  {
    id: "q17",
    dimension: "strategic-alignment",
    text: "Who in your organization has the authority to approve and resource an AI initiative?",
    options: [
      {
        value: 1,
        label: "No one",
        description: "No one. AI is not on anyone's mandate.",
      },
      {
        value: 2,
        label: "Unclear authority",
        description:
          "Multiple stakeholders would need to agree, and it is unclear who has final authority",
      },
      {
        value: 3,
        label: "Responsible but limited",
        description:
          "A specific executive is responsible, but they lack either budget authority or technical sponsorship",
      },
      {
        value: 4,
        label: "Defined sponsor",
        description:
          "A defined executive sponsor with both budget authority and organizational mandate to drive AI adoption",
      },
      {
        value: 5,
        label: "Board-backed sponsor",
        description:
          "Executive sponsor with board-level support, dedicated budget, cross-functional mandate, and defined reporting cadence",
      },
    ],
  },
];

// Helper to get questions by dimension
export function getQuestionsByDimension(dimension: string): Question[] {
  return questions.filter((q) => q.dimension === dimension);
}

// Helper to get all dimensions in order
export function getDimensionsInOrder(): string[] {
  return [
    "data-infrastructure",
    "technical-capability",
    "organizational-maturity",
    "governance-risk",
    "strategic-alignment",
  ];
}
