// QA FIX: 3 — Improve DOCX markdown parsing for complex structures
import { Document, Paragraph, TextRun, Table, TableRow, TableCell, HeadingLevel, AlignmentType } from 'docx';

interface MarkdownElement {
  type: 'paragraph' | 'heading' | 'list' | 'table' | 'code';
  content: string;
  level?: number;
  items?: string[];
  rows?: string[][];
}

export function parseMarkdownToDocxChildren(markdown: string) {
  const elements = parseMarkdownElements(markdown);
  const children: any[] = [];

  for (const element of elements) {
    switch (element.type) {
      case 'heading':
        children.push(createHeading(element.content, element.level || 1));
        break;
      case 'list':
        if (element.items) {
          children.push(...createList(element.items));
        }
        break;
      case 'table':
        if (element.rows) {
          children.push(createTable(element.rows));
        }
        break;
      case 'code':
        children.push(createCodeBlock(element.content));
        break;
      default:
        children.push(createParagraph(element.content));
    }
  }

  return children.length > 0 ? children : [new Paragraph({ text: 'No content available' })];
}

function parseMarkdownElements(markdown: string): MarkdownElement[] {
  const lines = markdown.split('\n');
  const elements: MarkdownElement[] = [];
  let currentElement: MarkdownElement | null = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    if (!trimmed) {
      if (currentElement) {
        elements.push(currentElement);
        currentElement = null;
      }
      if (elements.length > 0 && elements[elements.length - 1].type !== 'paragraph') {
        elements.push({ type: 'paragraph', content: '' });
      }
      continue;
    }

    // Headers
    const headerMatch = trimmed.match(/^(#{1,6})\s+(.+)$/);
    if (headerMatch) {
      if (currentElement) {
        elements.push(currentElement);
      }
      currentElement = {
        type: 'heading',
        content: headerMatch[2],
        level: headerMatch[1].length,
      };
      continue;
    }

    // List items
    const listMatch = trimmed.match(/^[-*+]\s+(.+)$/) || trimmed.match(/^\d+\.\s+(.+)$/);
    if (listMatch) {
      if (!currentElement || currentElement.type !== 'list') {
        if (currentElement) {
          elements.push(currentElement);
        }
        currentElement = { type: 'list', content: '', items: [] };
      }
      currentElement.items!.push(listMatch[1]);
      continue;
    }

    // Table rows
    if (trimmed.includes('|')) {
      if (!currentElement || currentElement.type !== 'table') {
        if (currentElement) {
          elements.push(currentElement);
        }
        currentElement = { type: 'table', content: '', rows: [] };
      }
      const cells = trimmed.split('|').map(cell => cell.trim()).filter(cell => cell);
      // Skip separator rows like |---|---|
      if (cells.length > 0 && !cells.every(c => /^[-:]+$/.test(c))) {
        currentElement.rows!.push(cells);
      }
      continue;
    }

    // Code blocks
    if (trimmed.startsWith('```')) {
      if (currentElement && currentElement.type === 'code') {
        elements.push(currentElement);
        currentElement = null;
      } else {
        if (currentElement) {
          elements.push(currentElement);
        }
        currentElement = { type: 'code', content: '' };
      }
      continue;
    }

    // Regular content
    if (currentElement && currentElement.type === 'code') {
      currentElement.content += (currentElement.content ? '\n' : '') + line;
    } else {
      if (currentElement && currentElement.type === 'paragraph') {
        currentElement.content += ' ' + trimmed;
      } else {
        if (currentElement) {
          elements.push(currentElement);
        }
        currentElement = { type: 'paragraph', content: trimmed };
      }
    }
  }

  if (currentElement) {
    elements.push(currentElement);
  }

  return elements;
}

function createHeading(text: string, level: number): Paragraph {
  const headingLevels = [
    HeadingLevel.HEADING_1,
    HeadingLevel.HEADING_2,
    HeadingLevel.HEADING_3,
    HeadingLevel.HEADING_4,
    HeadingLevel.HEADING_5,
    HeadingLevel.HEADING_6,
  ];

  return new Paragraph({
    text,
    heading: headingLevels[Math.min(level - 1, 5)],
  });
}

function createParagraph(text: string): Paragraph {
  if (!text.trim()) {
    return new Paragraph({ text: '' });
  }

  const runs = renderInlineRuns(text);
  return new Paragraph({ children: runs });
}

function createList(items: string[]): Paragraph[] {
  return items.map(item => new Paragraph({
    children: renderInlineRuns(`• ${item}`),
    indent: { left: 720 },
  }));
}

function createTable(rows: string[][]): Table {
  if (rows.length === 0) {
    return new Table({
      rows: [
        new TableRow({
          children: [
            new TableCell({
              children: [new Paragraph({ text: 'Empty table' })],
            }),
          ],
        }),
      ],
    });
  }

  const tableRows = rows.map((row, index) =>
    new TableRow({
      children: row.map(cell =>
        new TableCell({
          children: [new Paragraph({
            children: renderInlineRuns(cell),
          })],
        })
      ),
    })
  );

  return new Table({ rows: tableRows });
}

function createCodeBlock(content: string): Paragraph {
  return new Paragraph({
    children: [new TextRun({
      text: content,
      font: 'Courier New',
      size: 20,
    })],
    indent: { left: 720 },
  });
}

export function renderInlineRuns(text: string): TextRun[] {
  const runs: TextRun[] = [];
  let remaining = text;

  // Parse inline formatting
  const regex = /(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`)/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(remaining)) !== null) {
    // Add text before the match
    if (match.index > lastIndex) {
      runs.push(new TextRun({ text: remaining.substring(lastIndex, match.index) }));
    }

    if (match[2]) {
      // Bold
      runs.push(new TextRun({ text: match[2], bold: true }));
    } else if (match[3]) {
      // Italic
      runs.push(new TextRun({ text: match[3], italics: true }));
    } else if (match[4]) {
      // Code
      runs.push(new TextRun({ text: match[4], font: 'Courier New', size: 20 }));
    }

    lastIndex = match.index + match[0].length;
  }

  // Add remaining text
  if (lastIndex < remaining.length) {
    runs.push(new TextRun({ text: remaining.substring(lastIndex) }));
  }

  if (runs.length === 0) {
    runs.push(new TextRun({ text }));
  }

  return runs;
}

export function buildTableFromMarkdown(markdownTable: string): Table {
  const rows = markdownTable.split('\n')
    .map(line => line.split('|').map(cell => cell.trim()).filter(cell => cell))
    .filter(row => row.length > 0 && !row.every(c => /^[-:]+$/.test(c)));

  return createTable(rows);
}