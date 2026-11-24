import React from 'react';
import './globals.css';

export const metadata = {
  title: 'DocuMind AI',
  description: 'Evidence-grounded document question answering with citations',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
