"use client";

import { useState, useEffect } from "react";
import { ScorecardLanding } from "./ScorecardLanding";
import { EmailGate } from "./EmailGate";
import { QuestionFlow } from "./QuestionFlow";
import { ScorecardResults } from "./ScorecardResults";
import { calculateResults } from "../lib/scoring";
import { colors } from "../lib/brand";
import { trackEvent } from "../lib/analytics";
import type {
  ScorecardStep,
  EmailFormData,
  Answer,
  ScorecardResults as Results,
} from "../lib/types";

export function ScorecardApp() {
  const [step, setStep] = useState<ScorecardStep>("landing");
  const [emailData, setEmailData] = useState<EmailFormData | null>(null);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [results, setResults] = useState<Results | null>(null);
  const [showCalculating, setShowCalculating] = useState(false);

  // Track page view on mount
  useEffect(() => {
    trackEvent("scorecard_page_viewed");
  }, []);

  // Handle start
  const handleStart = () => {
    trackEvent("scorecard_started");
    setStep("email-gate");
  };

  // Handle email submission
  const handleEmailSubmit = (data: EmailFormData) => {
    trackEvent("scorecard_email_submitted", {
      company_size: data.companySize,
      industry: data.industry,
    });

    setEmailData(data);
    setStep("questions");

    // Email data is stored in state but not sent to any backend
    // You can add your own backend integration here
    if (process.env.NODE_ENV === "development") {
      console.log("[Client] Email data captured:", data);
    }
  };

  // Handle answer
  const handleAnswer = (questionId: string, value: number) => {
    setAnswers((prev) => {
      const existing = prev.find((a) => a.questionId === questionId);
      if (existing) {
        return prev.map((a) =>
          a.questionId === questionId ? { ...a, value } : a
        );
      }
      return [...prev, { questionId, value }];
    });
  };

  // Handle next question
  const handleNext = () => {
    setCurrentQuestionIndex((prev) => prev + 1);
  };

  // Handle previous question
  const handlePrevious = () => {
    setCurrentQuestionIndex((prev) => Math.max(0, prev - 1));
  };

  // Handle complete assessment
  const handleComplete = () => {
    setShowCalculating(true);
    setStep("calculating");

    // Simulate calculation delay
    setTimeout(() => {
      const calculatedResults = calculateResults(answers);
      setResults(calculatedResults);
      setShowCalculating(false);
      setStep("results");

      // Track completion
      trackEvent("scorecard_completed", {
        crs: calculatedResults.overallScore,
        band: calculatedResults.band,
        lowest_dimension: calculatedResults.lowestDimension,
      });

      // Results are calculated and displayed but not sent to any backend
      // You can add your own backend integration here
      if (process.env.NODE_ENV === "development" && emailData) {
        console.log("[Client] Scorecard completed:", {
          email: emailData.email,
          firstName: emailData.firstName,
          company: emailData.company,
          crs: calculatedResults.overallScore,
          band: calculatedResults.band,
          lowestDimension: calculatedResults.lowestDimension,
        });
      }
    }, 2000);
  };

  // Handle restart
  const handleRestart = () => {
    setStep("landing");
    setEmailData(null);
    setAnswers([]);
    setCurrentQuestionIndex(0);
    setResults(null);
  };

  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: colors.navy }}
    >
      {/* Logo/Brand */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <a
          href="/"
          className="inline-block font-display text-xl"
          style={{ color: colors.white }}
        >
          AI Readiness Scorecard
        </a>
      </div>

      {/* Main Content */}
      <div className="pb-16">
        {step === "landing" && <ScorecardLanding onStart={handleStart} />}

        {step === "email-gate" && <EmailGate onSubmit={handleEmailSubmit} />}

        {step === "questions" && (
          <QuestionFlow
            answers={answers}
            currentIndex={currentQuestionIndex}
            onAnswer={handleAnswer}
            onNext={handleNext}
            onPrevious={handlePrevious}
            onComplete={handleComplete}
          />
        )}

        {step === "calculating" && (
          <div className="max-w-xl mx-auto px-6 py-24 text-center">
            <div
              className="inline-block w-16 h-16 rounded-full mb-6"
              style={{
                border: `3px solid ${colors.navyMid}`,
                borderTopColor: colors.gold,
                animation: "spin 1s linear infinite",
              }}
            />
            <h2
              className="font-display text-2xl font-light mb-2"
              style={{ color: colors.white }}
            >
              Calculating Your Score
            </h2>
            <p style={{ color: colors.slate }}>
              Analyzing your responses across all dimensions...
            </p>

            <style jsx>{`
              @keyframes spin {
                to {
                  transform: rotate(360deg);
                }
              }
            `}</style>
          </div>
        )}

        {step === "results" && results && emailData && (
          <ScorecardResults
            results={results}
            emailData={emailData}
            onRestart={handleRestart}
          />
        )}
      </div>
    </div>
  );
}
