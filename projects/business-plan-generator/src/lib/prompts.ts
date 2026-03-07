import { BusinessInfo, RESEARCH_REFINABLE_FIELDS } from '@/lib/types';

export function buildContextBlock(info: BusinessInfo): string {
  // Handle research-refinable fields: show "To be determined from research" when blank
  const differentiators = info.keyDifferentiators?.trim()
    || 'Not yet specified — to be determined from research';
  const competitors = info.knownCompetitors?.trim()
    || 'Not yet specified — to be determined from research';
  const revenueGoal = info.year1RevenueGoal && Number(info.year1RevenueGoal) > 0
    ? `$${Number(info.year1RevenueGoal).toLocaleString()}`
    : 'Not yet specified — to be determined from research';

  return `
=== BUSINESS CONTEXT ===
Company Name: ${info.companyName}
Tagline: ${info.tagline}
Primary Industry: ${info.primaryIndustry}
Secondary Industries: ${info.secondaryIndustries?.join(', ') || 'None'}
Geographic Focus: ${info.geographyFocus}
Founder Background: ${info.founderBackground}
Services: ${info.servicesDescription}
Key Differentiators: ${differentiators}
Known Competitors: ${competitors}
Existing IP: ${info.existingIP}
Year 1 Revenue Goal: ${revenueGoal}
Current Team Size: ${info.currentTeamSize}
Target Company Size: ${info.targetCompanySize}
========================
`.trim();
}

export const STAGE_PROMPTS: Record<number, { system: string; user: (context: string, previousOutputs: string[]) => string }> = {
  1: {
    system: `You are an expert industry researcher and market analyst. You produce comprehensive, data-driven market research reports. Focus on actionable insights, specific market data, and competitive intelligence. Use structured formatting with headers and bullet points.`,
    user: (context, _prev) => `Conduct thorough industry and market research for the following business:

${context}

Produce a comprehensive research report covering:

1. **Industry Overview** — Current state, size, growth trajectory, and major trends
2. **Target Market Analysis** — Customer segments, demographics, psychographics, and buying behaviors
3. **Competitive Landscape** — Direct and indirect competitors, their strengths/weaknesses, market positioning
4. **Market Opportunities** — Underserved segments, emerging trends, and strategic opportunities
5. **Regulatory Environment** — Key regulations, compliance requirements, and industry standards
6. **Technology Trends** — Relevant technology shifts and digital transformation impacts
7. **Risk Assessment** — Market risks, competitive threats, and mitigation strategies

Be specific with data points and examples. Avoid generalities. This research will inform a complete business plan.

Note: If any fields in the business context are marked "to be determined from research," your research should specifically address those areas so the user can make informed decisions about them.`,
  },

  2: {
    system: `You are a strategic business consultant specializing in synthesizing market research into actionable business strategies. You excel at identifying strategic opportunities and creating clear, implementable recommendations.`,
    user: (context, previousOutputs) => `Based on the following market research and business context, create a strategic synthesis:

${context}

=== MARKET RESEARCH ===
${previousOutputs[0] || 'No previous research available'}
===

Produce a strategic synthesis covering:

1. **Strategic Positioning** — Where this business should position itself in the market
2. **Value Proposition Canvas** — Core value propositions aligned with customer needs
3. **Competitive Strategy** — How to differentiate and compete effectively. Include specific recommended differentiators.
4. **Competitive Landscape Summary** — Name the top 5-10 competitors identified in the research, with brief descriptions of each.
5. **Growth Opportunities** — Prioritized list of growth vectors with rationale
6. **Go-to-Market Strategy** — Channel strategy, partnership opportunities, and market entry approach
7. **Revenue Potential** — Based on market size and positioning, provide a realistic Year 1 revenue range with justification.
8. **Key Success Factors** — Critical elements that must be in place for success
9. **Strategic Recommendations** — Top 5 strategic priorities for the first year

Note: If the business context shows fields marked "to be determined from research," provide specific, actionable recommendations for those fields based on your analysis. The user will review your suggestions before the pipeline continues.`,
  },

  3: {
    system: `You are an expert business writer specializing in service portfolio development. You create detailed, professional service descriptions with clear pricing strategies and compelling value propositions.`,
    user: (context, previousOutputs) => `Develop a comprehensive service portfolio for this business:

${context}

=== STRATEGIC SYNTHESIS ===
${previousOutputs[1] || 'No strategic synthesis available'}
===

Create a detailed service portfolio including:

1. **Service Categories** — Organize services into logical categories
2. **Individual Service Descriptions** — For each service:
   - Service name and brief description
   - Target customer segment
   - Key deliverables
   - Pricing model and price range
   - Estimated delivery timeline
3. **Service Packages** — Bundle offerings at different tiers (Starter, Professional, Enterprise)
4. **Pricing Strategy** — Justification for pricing based on market positioning
5. **Service Delivery Process** — High-level workflow for service delivery
6. **Upsell and Cross-sell Opportunities** — How services connect and build on each other`,
  },

  4: {
    system: `You are a professional editor specializing in business documents. You refine content for clarity, consistency, professional tone, and market alignment. Focus on making services compelling and clearly differentiated.`,
    user: (context, previousOutputs) => `Refine and improve the following service portfolio:

${context}

=== DRAFT SERVICE PORTFOLIO ===
${previousOutputs[2] || 'No draft portfolio available'}
===

Please:
1. Improve clarity and consistency of service descriptions
2. Ensure pricing is competitive and well-justified
3. Strengthen value propositions for each service
4. Verify alignment with the strategic positioning
5. Fix any grammatical or structural issues
6. Ensure professional tone throughout
7. Add any missing elements that strengthen the portfolio

Output the complete refined service portfolio.`,
  },

  5: {
    system: `You are a senior business document editor. You perform final review and formatting of service portfolios for integration into business plans. Ensure completeness, professional presentation, and strategic coherence.`,
    user: (context, previousOutputs) => `Perform final review and formatting of this service portfolio for business plan integration:

${context}

=== REFINED SERVICE PORTFOLIO ===
${previousOutputs[3] || 'No refined portfolio available'}
===

Final review checklist:
1. Verify all services have complete descriptions, pricing, and delivery details
2. Ensure consistent formatting throughout
3. Validate pricing alignment with revenue goals
4. Confirm strategic positioning is maintained
5. Polish all language for executive-level presentation
6. Add executive summary of service portfolio at the top

Output the finalized, presentation-ready service portfolio.`,
  },

  6: {
    system: `You are an expert business plan writer who creates comprehensive, investor-ready business plans. You produce well-structured documents with clear sections, financial projections, and strategic narratives. Use professional formatting with headers, bullet points, and tables where appropriate.`,
    user: (context, previousOutputs) => `Create a comprehensive business plan using all the following inputs:

${context}

=== MARKET RESEARCH ===
${previousOutputs[0] || ''}
===

=== STRATEGIC SYNTHESIS ===
${previousOutputs[1] || ''}
===

=== FINALIZED SERVICE PORTFOLIO ===
${previousOutputs[4] || ''}
===

Create a complete business plan with these sections:

1. **Executive Summary** — Compelling overview of the entire business plan
2. **Company Overview** — Mission, vision, values, legal structure
3. **Market Analysis** — Industry overview, target market, competitive landscape
4. **Products & Services** — Complete service portfolio with pricing
5. **Marketing & Sales Strategy** — Customer acquisition, channels, campaigns
6. **Operations Plan** — Processes, technology, facilities, key partnerships
7. **Management Team** — Organizational structure, key roles, hiring plan
8. **Financial Projections** — 3-year revenue projections, expense breakdown, cash flow
   - Include specific tables for Year 1, Year 2, and Year 3
   - Break down revenue by service category
   - Include key financial metrics (margins, burn rate, break-even)
9. **Funding Requirements** — If applicable, investment needed and use of funds
10. **Risk Analysis & Mitigation** — Key risks with mitigation strategies
11. **Implementation Timeline** — 12-month roadmap with key milestones
12. **Appendix** — Supporting data, detailed financial tables

Make this business plan professional, comprehensive, and ready for stakeholder presentation.`,
  },

  7: {
    system: `You are a quality assurance specialist for business documents. You review business plans for completeness, accuracy, consistency, and professional quality. You provide specific, actionable feedback.`,
    user: (context, previousOutputs) => `Perform a comprehensive quality assurance review of this business plan:

${context}

=== BUSINESS PLAN DRAFT ===
${previousOutputs[5] || 'No business plan draft available'}
===

Review for:
1. **Completeness** — Are all required sections present and thorough?
2. **Consistency** — Do numbers, claims, and strategies align across sections?
3. **Accuracy** — Are financial projections realistic given the business context?
4. **Clarity** — Is the writing clear, concise, and professional?
5. **Formatting** — Is the document well-structured and easy to navigate?
6. **Persuasiveness** — Does the plan make a compelling case for the business?

Provide specific, actionable feedback organized by section. For each issue found, suggest a specific correction or improvement.`,
  },

  8: {
    system: `You are a senior business editor who produces final, polished business plans. Incorporate all QA feedback to create a presentation-ready document. The output should be the complete, final business plan — not a list of changes.`,
    user: (context, previousOutputs) => `Produce the final, polished business plan incorporating all QA feedback:

${context}

=== BUSINESS PLAN DRAFT ===
${previousOutputs[5] || ''}
===

=== QA FEEDBACK ===
${previousOutputs[6] || ''}
===

Incorporate all QA feedback and produce the complete, final business plan. This should be:
- Professionally formatted with clear section headers
- Consistent in tone, data, and strategic narrative
- Complete with all required sections
- Ready for stakeholder presentation
- Include proper tables for financial data

Output the entire final business plan from start to finish.`,
  },
};

export function getStagePrompt(
  stageId: number,
  businessInfo: BusinessInfo,
  previousOutputs: string[],
  regenerationNotes?: string
): { system: string; user: string } {
  const stagePrompt = STAGE_PROMPTS[stageId];
  if (!stagePrompt) {
    throw new Error(`No prompt defined for stage ${stageId}`);
  }

  const context = buildContextBlock(businessInfo);
  let userPrompt = stagePrompt.user(context, previousOutputs);

  if (regenerationNotes) {
    userPrompt += `\n\n=== ADDITIONAL INSTRUCTIONS ===\n${regenerationNotes}\n===`;
  }

  return {
    system: stagePrompt.system,
    user: userPrompt,
  };
}
