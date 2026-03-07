'use client';

import React, { useState, useCallback } from 'react';
import { useAppContext } from '@/context/AppContext';
import { MarkdownRenderer } from '@/components/ui/MarkdownRenderer';
import { TokenDisplay } from '@/components/ui/TokenDisplay';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';

export function OutputScreen() {
  const {
    finalOutput,
    pipelineOutputs,
    businessInfo,
    llmConfig,
    totalTokenUsage,
    setCurrentStep,
  } = useAppContext();

  const [activeTab, setActiveTab] = useState<'plan' | 'stages' | 'export'>('plan');
  const [isExporting, setIsExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState<'docx' | 'markdown'>('docx');
  const [includeCovers, setIncludeCovers] = useState(true);
  const [includeTOC, setIncludeTOC] = useState(true);
  const [showExportModal, setShowExportModal] = useState(false);

  // Use the last pipeline output as the final document if finalOutput isn't set
  const displayContent = finalOutput || pipelineOutputs[pipelineOutputs.length - 1] || 'No output available.';

  const handleExportDocx = useCallback(async () => {
    setIsExporting(true);

    try {
      const response = await fetch('/api/export-docx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: displayContent,
          companyName: businessInfo.companyName || 'Business Plan',
          includeCoverPage: includeCovers,
          includeTableOfContents: includeTOC,
        }),
      });

      if (!response.ok) {
        throw new Error('Export failed');
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${(businessInfo.companyName || 'Business_Plan').replace(/[^a-zA-Z0-9\s-]/g, '')}_Business_Plan.docx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export error:', error);
    } finally {
      setIsExporting(false);
      setShowExportModal(false);
    }
  }, [displayContent, businessInfo.companyName, includeCovers, includeTOC]);

  const handleExportMarkdown = useCallback(() => {
    const blob = new Blob([displayContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(businessInfo.companyName || 'Business_Plan').replace(/[^a-zA-Z0-9\s-]/g, '')}_Business_Plan.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setShowExportModal(false);
  }, [displayContent, businessInfo.companyName]);

  const handleCopyToClipboard = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(displayContent);
    } catch {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = displayContent;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    }
  }, [displayContent]);

  const stageNames = [
    'Industry & Market Research',
    'Strategic Synthesis',
    'Service Portfolio Development',
    'Service Portfolio Refinement',
    'Service Portfolio Finalization',
    'Business Plan Development',
    'Quality Assurance Review',
    'Final Document Assembly',
  ];

  return (
    <div className="min-h-screen bg-slate-950 p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-100">
              {businessInfo.companyName || 'Your'} Business Plan
            </h1>
            <p className="text-slate-400 mt-1">
              Generated business plan ready for review and export
            </p>
          </div>
          <div className="flex space-x-3">
            <Button variant="secondary" onClick={handleCopyToClipboard}>
              📋 Copy
            </Button>
            <Button onClick={() => setShowExportModal(true)}>
              📥 Export
            </Button>
          </div>
        </div>

        {/* Token Summary */}
        <TokenDisplay
          usage={totalTokenUsage}
          model={llmConfig?.model}
          className="w-full"
        />

        {/* Tabs */}
        <div className="border-b border-slate-800">
          <nav className="flex space-x-4" role="tablist" aria-label="Output views">
            <button
              onClick={() => setActiveTab('plan')}
              className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'plan'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
              role="tab"
              aria-selected={activeTab === 'plan'}
              aria-controls="panel-plan"
            >
              Final Business Plan
            </button>
            <button
              onClick={() => setActiveTab('stages')}
              className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'stages'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
              role="tab"
              aria-selected={activeTab === 'stages'}
              aria-controls="panel-stages"
            >
              Stage Outputs ({pipelineOutputs.length})
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'plan' && (
          <div id="panel-plan" role="tabpanel" className="bg-slate-900 rounded-lg p-6 overflow-auto max-h-[70vh]">
            <MarkdownRenderer content={displayContent} />
          </div>
        )}

        {activeTab === 'stages' && (
          <div id="panel-stages" role="tabpanel" className="space-y-4">
            {pipelineOutputs.map((output, index) => (
              <details key={index} className="bg-slate-900 rounded-lg border border-slate-800">
                <summary className="p-4 cursor-pointer text-slate-100 font-medium hover:bg-slate-800/50 rounded-lg">
                  Stage {index + 1}: {stageNames[index] || `Stage ${index + 1}`}
                </summary>
                <div className="p-4 pt-0 border-t border-slate-800">
                  <MarkdownRenderer content={output || 'No output for this stage.'} />
                </div>
              </details>
            ))}
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between pt-4 border-t border-slate-800">
          <Button
            variant="secondary"
            onClick={() => setCurrentStep('pipeline')}
          >
            ← Back to Pipeline
          </Button>
          <Button
            variant="secondary"
            onClick={() => setCurrentStep('wizard')}
          >
            Start New Plan
          </Button>
        </div>

        {/* Export Modal */}
        <Modal
          isOpen={showExportModal}
          onClose={() => setShowExportModal(false)}
          title="Export Business Plan"
          size="md"
        >
          <div className="space-y-4">
            <div role="radiogroup" aria-label="Export format">
              <label className="label mb-3">Export Format</label>
              <div className="space-y-2">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    value="docx"
                    checked={exportFormat === 'docx'}
                    onChange={() => setExportFormat('docx')}
                    className="w-4 h-4 text-blue-600 bg-slate-800 border-slate-600 focus:ring-blue-500"
                  />
                  <span className="text-slate-200">Microsoft Word (.docx)</span>
                </label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    value="markdown"
                    checked={exportFormat === 'markdown'}
                    onChange={() => setExportFormat('markdown')}
                    className="w-4 h-4 text-blue-600 bg-slate-800 border-slate-600 focus:ring-blue-500"
                  />
                  <span className="text-slate-200">Markdown (.md)</span>
                </label>
              </div>
            </div>

            {exportFormat === 'docx' && (
              <div className="space-y-2">
                <label className="label">Options</label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeCovers}
                    onChange={(e) => setIncludeCovers(e.target.checked)}
                    className="w-4 h-4 text-blue-600 bg-slate-800 border-slate-600 rounded focus:ring-blue-500"
                  />
                  <span className="text-slate-200">Include Cover Page</span>
                </label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeTOC}
                    onChange={(e) => setIncludeTOC(e.target.checked)}
                    className="w-4 h-4 text-blue-600 bg-slate-800 border-slate-600 rounded focus:ring-blue-500"
                  />
                  <span className="text-slate-200">Include Table of Contents</span>
                </label>
              </div>
            )}

            <div className="flex space-x-3 pt-2">
              <Button
                variant="secondary"
                onClick={() => setShowExportModal(false)}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={exportFormat === 'docx' ? handleExportDocx : handleExportMarkdown}
                loading={isExporting}
                disabled={isExporting}
                className="flex-1"
              >
                {isExporting ? 'Exporting...' : 'Export'}
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </div>
  );
}