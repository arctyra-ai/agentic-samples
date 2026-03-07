'use client';

import React, { useEffect, useRef } from 'react';

interface StreamingTextProps {
  content: string;
  isStreaming: boolean;
  className?: string;
  autoScroll?: boolean;
}

export function StreamingText({
  content,
  isStreaming,
  className = '',
  autoScroll = true,
}: StreamingTextProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [content, autoScroll]);

  return (
    <div
      ref={containerRef}
      className={`bg-slate-800 rounded-lg p-4 overflow-y-auto whitespace-pre-wrap ${className}`}
      role="log"
      aria-live={isStreaming ? 'polite' : 'off'}
      aria-label="Streaming content"
    >
      <div className="text-sm text-slate-200 leading-relaxed">
        {content}
        {isStreaming && (
          <span className="typing-cursor ml-0.5" aria-hidden="true">|</span>
        )}
      </div>
      {!content && !isStreaming && (
        <p className="text-slate-500 italic">No content yet...</p>
      )}
    </div>
  );
}