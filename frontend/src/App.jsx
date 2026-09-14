import React, { useState } from 'react';

const App = () => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const simulateCheck = async (type) => {
    setLoading(true);
    setResult(null);
    
    // In production, this hits the local FastAPI backend running on 127.0.0.1:8000
    // e.g. fetch('http://127.0.0.1:8000/api/check_message', ...)
    setTimeout(() => {
      if (type === 'message') {
        setResult({ verdict: "Likely Scam", message: "This matches a known 'Fake KYC' scam pattern. Do not click any links." });
      } else if (type === 'call') {
        setResult({ verdict: "Likely Scam", message: "This audio mentions 'Digital Arrest' which is a common fraud script." });
      } else {
        setResult({ verdict: "Looks Genuine", message: "This document matches the PM-Kisan scheme. It appears authentic." });
      }
      setLoading(false);
    }, 1500);
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto', textAlign: 'center' }}>
      <h1>SatyaShield AI</h1>
      <p>Offline Scam & Document Verification</p>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '2rem' }}>
        <button 
          onClick={() => simulateCheck('message')}
          style={{ padding: '1.5rem', fontSize: '1.2rem', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer' }}>
          📷 Check a Message
        </button>
        
        <button 
          onClick={() => simulateCheck('call')}
          style={{ padding: '1.5rem', fontSize: '1.2rem', backgroundColor: '#8b5cf6', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer' }}>
          🎤 Check a Call
        </button>
        
        <button 
          onClick={() => simulateCheck('document')}
          style={{ padding: '1.5rem', fontSize: '1.2rem', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer' }}>
          📄 Check a Document
        </button>
      </div>

      {loading && <p style={{ marginTop: '2rem', fontSize: '1.2rem' }}>Analyzing on-device...</p>}

      {result && (
        <div style={{ marginTop: '2rem', padding: '1.5rem', borderRadius: '12px', backgroundColor: result.verdict === 'Likely Scam' ? '#fee2e2' : '#d1fae5' }}>
          <h2 style={{ color: result.verdict === 'Likely Scam' ? '#dc2626' : '#059669', margin: '0 0 1rem 0' }}>{result.verdict}</h2>
          <p style={{ fontSize: '1.1rem', margin: 0 }}>{result.message}</p>
        </div>
      )}
    </div>
  );
};

export default App;
