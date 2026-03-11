import type { Metadata } from "next";
import { ScorecardApp } from "./components/ScorecardApp";

export const metadata: Metadata = {
  title: "AI Readiness Scorecard",
  description:
    "Assess your organization's readiness for AI adoption. Get your Composite Readiness Score and actionable recommendations in 5 minutes.",
  openGraph: {
    title: "AI Readiness Scorecard",
    description:
      "Free assessment: Evaluate your AI readiness across Strategy, Data, Infrastructure, Governance, and Culture.",
  },
};

export default function ScorecardPage() {
  return <ScorecardApp />;
}
