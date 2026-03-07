import type { Metadata } from 'next';
import { AppProvider } from '@/context/AppContext';
import './globals.css';

export const metadata: Metadata = {
  title: 'Business Plan Generator',
  description: 'AI-powered business plan generator with multi-stage pipeline',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 antialiased">
        <AppProvider>
          {children}
        </AppProvider>
      </body>
    </html>
  );
}