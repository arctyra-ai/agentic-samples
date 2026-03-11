# AI Readiness Scorecard

A 17-question self-assessment tool that evaluates organizational readiness to adopt AI across five dimensions: Data Infrastructure, Technical Capability, Organizational Maturity, Governance & Risk Readiness, and Strategic Alignment.

Built as a training project demonstrating agentic AI development patterns: multi-step form orchestration, weighted scoring engines, dynamic content rendering, and client-side PDF generation.

## What It Does

- Collects respondent information (name, email, company, role, industry, size)
- Presents 17 questions across 5 weighted dimensions with section transitions
- Calculates a Composite Readiness Score (0-100) with dimensional breakdown
- Displays results with score interpretation, dimensional analysis, and priority actions
- Generates a downloadable PDF report

## Methodology

The scoring uses weighted dimensions:
- Data Infrastructure: 25%
- Technical Capability: 20% (signal question)
- Organizational Maturity: 15% (signal question)
- Governance & Risk Readiness: 25%
- Strategic Alignment: 15%

Five interpretation bands: Foundational (0-25), Developing (26-45), Progressing (46-65), Advanced (66-80), Leading (81-100).

The methodology draws from NIST AI RMF, CSA/Google Cloud AI Security Survey findings, Gartner AI Maturity models, and practitioner experience in AI adoption consulting.

## Getting Started

```bash
cd ai-readiness-scorecard
pnpm install
pnpm dev
```

Open http://localhost:3000/scorecard

## Customization

To adapt this for your own practice:

1. **Branding**: Update colors in `app/scorecard/lib/brand.ts` and fonts in `app/layout.tsx`
2. **Questions**: Modify questions in `app/scorecard/lib/questions.ts`
3. **Scoring**: Adjust dimension weights and band thresholds in `app/scorecard/lib/scoring.ts`
4. **Interpretations**: Edit copy in `app/scorecard/lib/interpretations.ts`
5. **Integrations**: Add CRM and email integrations via API routes
6. **PDF**: Customize the layout in the `ScorecardResults.tsx` component's `handleDownloadPDF` function

## Tech Stack

- Next.js 16 (App Router)
- React 19 with TypeScript
- Tailwind CSS 4
- jsPDF (client-side PDF generation)
- Fully client-side scoring — no server or external services required

## Project Structure

```
ai-readiness-scorecard/
├── app/
│   ├── layout.tsx                    # Root layout with fonts
│   ├── page.tsx                      # Homepage (redirects to /scorecard)
│   ├── globals.css                   # Global styles
│   └── scorecard/
│       ├── page.tsx                  # Scorecard page route
│       ├── components/
│       │   ├── ScorecardApp.tsx      # Main orchestration component
│       │   ├── ScorecardLanding.tsx  # Landing page
│       │   ├── EmailGate.tsx         # Email/company info collection
│       │   ├── QuestionFlow.tsx      # Question presentation logic
│       │   ├── DimensionIntro.tsx    # Section transition screens
│       │   ├── ScorecardResults.tsx  # Results display + PDF generation
│       │   ├── ScoreGauge.tsx        # Circular score visualization
│       │   └── DimensionalChart.tsx  # Bar chart for dimensions
│       └── lib/
│           ├── brand.ts              # Color palette and design tokens
│           ├── types.ts              # TypeScript type definitions
│           ├── questions.ts          # All 17 questions + metadata
│           ├── scoring.ts            # Scoring engine and formulas
│           ├── interpretations.ts    # Result band and dimension copy
│           ├── email-validation.ts   # Email validation utilities
│           └── analytics.ts          # Analytics stub (customize)
├── public/                           # Static assets
├── package.json                      # Dependencies
├── tsconfig.json                     # TypeScript config
├── tailwind.config.ts                # Tailwind CSS config
└── README.md                         # This file
```

## Scoring Algorithm

### Composite Readiness Score (CRS)

The CRS is calculated as a weighted average of the five dimensional scores:

```typescript
rawCRS = (
  data * 0.25 +
  technical * 0.20 +
  organizational * 0.15 +
  governance * 0.25 +
  strategic * 0.15
) * 20

displayCRS = Math.round(((rawCRS - 20) / 80) * 100)
```

This formula:
1. Weights each dimension (1.0-5.0 scale) according to its importance
2. Multiplies by 20 to get a 20-100 range
3. Normalizes to 0-100 for display
4. Rounds to the nearest integer

### Dimensional Scores

Each dimension score is the average of its constituent questions:

- **Data Infrastructure**: 5 questions (Q1-Q5)
- **Technical Capability**: 1 signal question (Q6)
- **Organizational Maturity**: 1 signal question (Q7)
- **Governance & Risk Readiness**: 5 questions (Q8-Q12)
- **Strategic Alignment**: 5 questions (Q13-Q17)

Each question has 5 options scored 1-5. The dimensional score is the arithmetic mean of its questions, ranging from 1.0 (lowest) to 5.0 (highest).

### Band Thresholds

**Overall CRS Bands:**
- Foundational: 0-25
- Developing: 26-45
- Progressing: 46-65
- Advanced: 66-80
- Leading: 81-100

**Dimensional Bands:**
- Low: 1.0-2.0
- Moderate: 2.1-3.5
- Strong: 3.6-5.0

## Adding Integrations

### CRM Integration (HubSpot, Salesforce, etc.)

Create an API route at `app/api/scorecard/register/route.ts`:

```typescript
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const body = await request.json();
  
  // Send to your CRM
  await createContact({
    firstName: body.firstName,
    lastName: body.lastName,
    email: body.email,
    company: body.company,
    // ... other fields
  });
  
  return NextResponse.json({ success: true });
}
```

Then modify `ScorecardApp.tsx` to call this route in `handleEmailSubmit`.

### Email Integration (Resend, SendGrid, etc.)

Create an API route at `app/api/scorecard/submit/route.ts`:

```typescript
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const { email, firstName, crs, dimScores, band } = await request.json();
  
  // Send confirmation email
  await sendEmail({
    to: email,
    subject: "Your AI Readiness Scorecard Results",
    html: `<p>Hi ${firstName}, your CRS is ${crs}...</p>`,
  });
  
  return NextResponse.json({ success: true });
}
```

### Analytics

Replace the stub in `app/scorecard/lib/analytics.ts`:

```typescript
export function trackEvent(eventName: string, properties?: Record<string, any>) {
  // Google Analytics
  if (typeof window !== "undefined" && window.gtag) {
    window.gtag("event", eventName, properties);
  }
  
  // Or Plausible
  if (typeof window !== "undefined" && window.plausible) {
    window.plausible(eventName, { props: properties });
  }
}
```

## Design Decisions

### Why Client-Side Scoring?

The scoring engine runs entirely in the browser with no server dependencies. This design:
- Eliminates server costs
- Ensures instant results (no network latency)
- Works offline (PWA-ready)
- Protects user privacy (no data leaves the device until explicitly submitted)

### Why Signal Questions?

Two dimensions (Technical Capability and Organizational Maturity) use single "signal questions" rather than 5-question deep dives. This design:
- Keeps assessment under 5 minutes
- Provides directional signal without over-surveying
- Allows upgrade path to full assessment (27 questions across all dimensions)

### Why PDF Generation?

The PDF is generated client-side using jsPDF. This design:
- Eliminates server-side rendering complexity
- Works without external PDF APIs (Puppeteer, Cloudflare Browser Rendering, etc.)
- Produces consistent output across platforms
- Allows offline PDF generation

Trade-off: Limited font support (uses built-in Helvetica). For custom fonts, consider server-side rendering with `@react-pdf/renderer`.

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Cloudflare Pages

```bash
pnpm build
```

Then deploy the `.next` directory to Cloudflare Pages with the following settings:
- Build command: `pnpm build`
- Output directory: `.next`
- Framework preset: Next.js

### Docker

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build
EXPOSE 3000
CMD ["pnpm", "start"]
```

## License

MIT

## Part of Arctyra Agentic AI Training

This project is one of several sample projects in the [Agentic Samples](https://github.com/arctyra-ai/agentic-samples) repository, demonstrating practical applications of AI-assisted development.

---

**Questions or feedback?** Open an issue in the [agentic-samples repository](https://github.com/arctyra-ai/agentic-samples).
