"use client";

import { useState, useEffect } from "react";
import { questions, getDimensionsInOrder, dimensionMetadata } from "../lib/questions";
import { colors } from "../lib/brand";
import { DimensionIntro } from "./DimensionIntro";
import type { Answer, Dimension } from "../lib/types";

interface QuestionFlowProps {
  answers: Answer[];
  currentIndex: number;
  onAnswer: (questionId: string, value: number) => void;
  onNext: () => void;
  onPrevious: () => void;
  onComplete: () => void;
}

export function QuestionFlow({
  answers,
  currentIndex,
  onAnswer,
  onNext,
  onPrevious,
  onComplete,
}: QuestionFlowProps) {
  const [showDimensionIntro, setShowDimensionIntro] = useState(false);
  const [selectedValue, setSelectedValue] = useState<number | null>(null);

  const currentQuestion = questions[currentIndex];
  const isFirstQuestion = currentIndex === 0;
  const isLastQuestion = currentIndex === questions.length - 1;

  // Get progress
  const progress = ((currentIndex + 1) / questions.length) * 100;

  // Check if we should show dimension intro
  useEffect(() => {
    if (currentIndex === 0) {
      setShowDimensionIntro(true);
      return;
    }

    const currentDimension = currentQuestion.dimension;
    const previousDimension = questions[currentIndex - 1]?.dimension;

    if (currentDimension !== previousDimension) {
      setShowDimensionIntro(true);
    } else {
      setShowDimensionIntro(false);
    }
  }, [currentIndex, currentQuestion.dimension]);

  // Load existing answer if any
  useEffect(() => {
    const existingAnswer = answers.find((a) => a.questionId === currentQuestion.id);
    setSelectedValue(existingAnswer?.value ?? null);
  }, [currentQuestion.id, answers]);

  const handleSelect = (value: number) => {
    setSelectedValue(value);
    onAnswer(currentQuestion.id, value);
  };

  const handleContinue = () => {
    if (isLastQuestion) {
      onComplete();
    } else {
      onNext();
    }
  };

  const handleDimensionIntroContinue = () => {
    setShowDimensionIntro(false);
  };

  if (showDimensionIntro) {
    return (
      <DimensionIntro
        dimension={currentQuestion.dimension}
        onContinue={handleDimensionIntroContinue}
      />
    );
  }

  const metadata = dimensionMetadata[currentQuestion.dimension];

  return (
    <div className="max-w-2xl mx-auto px-6 py-12">
      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium uppercase tracking-wider" style={{ color: colors.slate }}>
            Question {currentIndex + 1} of {questions.length}
          </span>
          <span className="text-xs font-medium uppercase tracking-wider" style={{ color: metadata.color }}>
            {metadata.label}
          </span>
        </div>
        <div
          className="h-1 rounded-full overflow-hidden"
          style={{ backgroundColor: colors.navyMid }}
        >
          <div
            className="h-full transition-all duration-300 ease-out"
            style={{
              width: `${progress}%`,
              backgroundColor: colors.gold,
            }}
          />
        </div>
      </div>

      {/* Question */}
      <div className="mb-8">
        <h2
          className="font-display text-2xl sm:text-3xl font-light mb-3"
          style={{ color: colors.white }}
        >
          {currentQuestion.text}
        </h2>
        {currentQuestion.description && (
          <p className="text-sm" style={{ color: colors.slate }}>
            {currentQuestion.description}
          </p>
        )}
      </div>

      {/* Options */}
      <div className="space-y-3 mb-8">
        {currentQuestion.options.map((option) => {
          const isSelected = selectedValue === option.value;

          return (
            <button
              key={option.value}
              onClick={() => handleSelect(option.value)}
              className="w-full text-left px-5 py-4 rounded-md transition-all"
              style={{
                backgroundColor: isSelected ? colors.navyMid : colors.navyLight,
                border: `2px solid ${isSelected ? metadata.color : "transparent"}`,
                color: colors.white,
              }}
            >
              <div className="flex items-start">
                {/* Radio indicator */}
                <div
                  className="flex-shrink-0 w-5 h-5 rounded-full mt-0.5 mr-3 flex items-center justify-center"
                  style={{
                    border: `2px solid ${isSelected ? metadata.color : colors.slate}`,
                    backgroundColor: isSelected ? metadata.color : "transparent",
                  }}
                >
                  {isSelected && (
                    <div
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: colors.navy }}
                    />
                  )}
                </div>

                <div className="flex-1">
                  <div className="font-medium mb-1">{option.label}</div>
                  {option.description && (
                    <div className="text-sm" style={{ color: colors.slate }}>
                      {option.description}
                    </div>
                  )}
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between gap-4">
        <button
          onClick={onPrevious}
          disabled={isFirstQuestion}
          className="px-6 py-3 rounded-md font-medium transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
          style={{
            backgroundColor: colors.navyMid,
            color: colors.white,
          }}
        >
          Previous
        </button>

        <button
          onClick={handleContinue}
          disabled={selectedValue === null}
          className="px-8 py-3 rounded-md font-semibold transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          style={{
            backgroundColor: selectedValue !== null ? colors.gold : colors.navyMid,
            color: selectedValue !== null ? colors.navy : colors.slate,
          }}
        >
          {isLastQuestion ? "See Results" : "Next"}
        </button>
      </div>
    </div>
  );
}
