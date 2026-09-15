import React, { useState, useRef } from 'react';

const App = () => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);
  const [checkType, setCheckType] = useState(null);

  // Opens the file dialog
  const triggerFileInput = (type) => {
    setCheckType(type);
    fileInputRef.current.click();
  };

  // Handles the file selection and sends it to the FastAPI backend
  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file || !checkType) return;

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    // The FastAPI backend expects 'image' for message/document, and 'audio' for call
    const fieldName = checkType === 'call' ? 'audio' : 'image';
    formData.append(fieldName, file);

    try {
        // Send a real HTTP POST request to the local Python server
        const response = await fetch(`http://127.0.0.1:8000/api/check_${checkType}`, {
            method: 'POST',
            body: formData,
        });
        
        const data = await response.json();
        setResult(data);
    } catch (error) {
        console.error("Error communicating with backend:", error);
        setResult({ 
            verdict: "Connection Error", 
            explanation: "Failed to connect to the local AI backend. Make sure your Python server is running on port 8000!" 
        });
    } finally {
        setLoading(false);
        // Clear the input so the same file can be selected again
        event.target.value = null;
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto', textAlign: 'center', fontFamily: 'sans-serif' }}>
      <h1>SatyaShield AI</h1>
      <p style={{ color: '#4b5563', marginBottom: '2rem' }}>Offline Scam & Document Verification</p>
      
      {/* Hidden file input */}
      <input 
        type="file" 
        ref={fileInputRef} 
        style={{ display: 'none' }} 
        accept={checkType === 'call' ? "audio/*" : "image/*"}
        onChange={handleFileChange}
      />

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <button 
          onClick={() => triggerFileInput('message')}
          style={{ padding: '1.5rem', fontSize: '1.2rem', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', transition: 'transform 0.1s' }}
          onMouseOver={(e) => e.target.style.transform = 'scale(1.02)'}
          onMouseOut={(e) => e.target.style.transform = 'scale(1)'}>
          📷 Check a Message (Upload Screenshot)
        </button>
        
        <button 
          onClick={() => triggerFileInput('call')}
          style={{ padding: '1.5rem', fontSize: '1.2rem', backgroundColor: '#8b5cf6', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', transition: 'transform 0.1s' }}
          onMouseOver={(e) => e.target.style.transform = 'scale(1.02)'}
          onMouseOut={(e) => e.target.style.transform = 'scale(1)'}>
          🎤 Check a Call (Upload Audio)
        </button>
        
        <button 
          onClick={() => triggerFileInput('document')}
          style={{ padding: '1.5rem', fontSize: '1.2rem', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', transition: 'transform 0.1s' }}
          onMouseOver={(e) => e.target.style.transform = 'scale(1.02)'}
          onMouseOut={(e) => e.target.style.transform = 'scale(1)'}>
          📄 Check a Document (Upload Photo)
        </button>
      </div>

      {loading && (
        <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#f3f4f6', borderRadius: '8px' }}>
          <p style={{ fontSize: '1.2rem', margin: 0, fontWeight: 'bold', color: '#374151' }}>⚙️ Analyzing on-device...</p>
        </div>
      )}

      {result && (
        <div style={{ 
          marginTop: '2rem', 
          padding: '1.5rem', 
          borderRadius: '12px', 
          backgroundColor: result.verdict === 'Likely Scam' ? '#fee2e2' : result.verdict.includes('Error') ? '#fef3c7' : '#d1fae5',
          border: `2px solid ${result.verdict === 'Likely Scam' ? '#ef4444' : result.verdict.includes('Error') ? '#f59e0b' : '#10b981'}`
        }}>
          <h2 style={{ 
            color: result.verdict === 'Likely Scam' ? '#dc2626' : result.verdict.includes('Error') ? '#d97706' : '#059669', 
            margin: '0 0 1rem 0' 
          }}>
            {result.verdict}
          </h2>
          <p style={{ fontSize: '1.1rem', margin: 0, color: '#1f2937' }}>{result.explanation}</p>
          
          {result.pattern_matched && (
            <p style={{ fontSize: '0.9rem', marginTop: '1rem', fontWeight: 'bold', color: '#7f1d1d' }}>
              Detected Pattern: {result.pattern_matched}
            </p>
          )}
          {result.scheme_matched && (
            <p style={{ fontSize: '0.9rem', marginTop: '1rem', fontWeight: 'bold', color: '#064e3b' }}>
              Matched Scheme: {result.scheme_matched}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default App;
