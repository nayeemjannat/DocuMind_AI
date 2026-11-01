import React from 'react';

export default function HomePage() {
  return (
    <main style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
      <h1>DocuMind AI</h1>
      <p>
        Upload documents (PDF, DOCX, TXT) and ask questions with verified, evidence-grounded citations.
      </p>
      <div style={{ marginTop: '1.5rem', padding: '1rem', border: '1px solid #ccc', borderRadius: '8px' }}>
        <h3>Document Search & Analysis</h3>
        <p>Ask questions and get verified, citation-backed answers from your documents.</p>
      </div>
    </main>
  );
}
