import { NextRequest, NextResponse } from 'next/server';
import { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak } from 'docx';
import { parseMarkdownToDocxChildren } from '@/lib/docx-utils';

// SECURITY FIX: G-4 — Server-side input length validation for export
const MAX_CONTENT_LENGTH = 500000; // 500KB of text content
const MAX_COMPANY_NAME_LENGTH = 100;

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const {
      content,
      companyName,
      includeTableOfContents,
      includeCoverPage,
    } = body as {
      content: string;
      companyName: string;
      includeTableOfContents: boolean;
      includeCoverPage: boolean;
    };

    if (!content) {
      return NextResponse.json({ error: 'No content provided' }, { status: 400 });
    }

    // SECURITY FIX: G-4 — Enforce server-side input length limits
    if (content.length > MAX_CONTENT_LENGTH) {
      return NextResponse.json(
        { error: 'Content exceeds maximum allowed length' },
        { status: 400 }
      );
    }

    const sanitizedCompanyName = (companyName || 'Business Plan').substring(0, MAX_COMPANY_NAME_LENGTH);

    const sections: any[] = [];

    // Cover page
    if (includeCoverPage) {
      sections.push({
        properties: {},
        children: [
          new Paragraph({ text: '' }),
          new Paragraph({ text: '' }),
          new Paragraph({ text: '' }),
          new Paragraph({ text: '' }),
          new Paragraph({ text: '' }),
          new Paragraph({
            children: [
              new TextRun({
                text: sanitizedCompanyName,
                bold: true,
                size: 56,
                color: '2563EB',
              }),
            ],
            alignment: AlignmentType.CENTER,
          }),
          new Paragraph({ text: '' }),
          new Paragraph({
            children: [
              new TextRun({
                text: 'Business Plan',
                size: 36,
                color: '64748B',
              }),
            ],
            alignment: AlignmentType.CENTER,
          }),
          new Paragraph({ text: '' }),
          new Paragraph({
            children: [
              new TextRun({
                text: `Generated on ${new Date().toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}`,
                size: 24,
                color: '94A3B8',
              }),
            ],
            alignment: AlignmentType.CENTER,
          }),
          new Paragraph({
            children: [new PageBreak()],
          }),
        ],
      });
    }

    // Table of contents placeholder
    if (includeTableOfContents) {
      sections.push({
        properties: {},
        children: [
          new Paragraph({
            text: 'Table of Contents',
            heading: HeadingLevel.HEADING_1,
          }),
          new Paragraph({
            text: '(Update this table of contents by right-clicking and selecting "Update Field" in Word)',
            italics: true,
          }),
          new Paragraph({
            children: [new PageBreak()],
          }),
        ],
      });
    }

    // Main content
    const docxChildren = parseMarkdownToDocxChildren(content);
    sections.push({
      properties: {},
      children: docxChildren,
    });

    const doc = new Document({
      title: `${sanitizedCompanyName} - Business Plan`,
      description: `Business plan for ${sanitizedCompanyName}`,
      creator: 'Business Plan Generator',
      sections,
    });

    const buffer = await Packer.toBuffer(doc);

    return new Response(buffer, {
      headers: {
        'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'Content-Disposition': `attachment; filename="${sanitizedCompanyName.replace(/[^a-zA-Z0-9\s-]/g, '')}_Business_Plan.docx"`,
      },
    });
  } catch (error) {
    console.error('DOCX export error:', error);
    return NextResponse.json(
      { error: 'Failed to generate DOCX file' },
      { status: 500 }
    );
  }
}