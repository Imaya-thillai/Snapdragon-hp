import React, { useState, useRef, useEffect } from 'react';

const App = () => {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const fileInputRef = useRef(null);
  const [claimType, setClaimType] = useState('tree_planting');

  // Listen to network status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // Fetch initial queue
    fetchQueue();
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const fetchQueue = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/queue_status');
      const data = await res.json();
      setQueue(data.queue);
    } catch (e) {
      console.error("Backend not running");
    }
  };

  const triggerFileInput = (type) => {
    setClaimType(type);
    fileInputRef.current.click();
  };

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('image', file);
    formData.append('claim_type', claimType);

    try {
        const response = await fetch(`http://127.0.0.1:8000/api/verify_eco_claim`, {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        if (data.status === 'success') {
           alert("AI Verified! Claim added to offline queue.");
           fetchQueue();
        } else {
           alert("AI Verification Failed: " + data.message);
        }
    } catch (error) {
        alert("Connection Error to Local AI Backend.");
    } finally {
        setLoading(false);
        event.target.value = null;
    }
  };

  const handleSync = async () => {
    if (!isOnline) {
      alert("You are offline. Please connect to the internet to sync with Hedera.");
      return;
    }
    
    setSyncing(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/sync_hedera`, { method: 'POST' });
      const data = await response.json();
      alert(data.message);
      fetchQueue();
    } catch (e) {
      alert("Error syncing to Hedera.");
    } finally {
      setSyncing(false);
    }
  };

  const pendingCount = queue.filter(q => q.status === 'pending_sync').length;

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ margin: 0, color: '#064e3b' }}>🐢 Project Turtle</h1>
          <p style={{ margin: 0, color: '#4b5563' }}>AI Sustainability Agent & Hedera Network</p>
        </div>
        <div style={{ 
          padding: '0.5rem 1rem', 
          borderRadius: '999px', 
          backgroundColor: isOnline ? '#d1fae5' : '#fee2e2',
          color: isOnline ? '#065f46' : '#991b1b',
          fontWeight: 'bold',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <div style={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: isOnline ? '#10b981' : '#ef4444' }}></div>
          {isOnline ? 'Network Online' : 'Operating Offline'}
        </div>
      </div>

      {/* Hidden file input */}
      <input type="file" ref={fileInputRef} style={{ display: 'none' }} accept="image/*" onChange={handleFileChange} />

      {/* Actions */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <button 
          onClick={() => triggerFileInput('tree_planting')}
          disabled={loading}
          style={{ flex: 1, padding: '1.5rem', fontSize: '1.1rem', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer' }}>
          {loading ? 'Processing AI...' : '🌳 Log Tree Planting (Photo)'}
        </button>
        
        <button 
          onClick={() => triggerFileInput('ocean_cleanup')}
          disabled={loading}
          style={{ flex: 1, padding: '1.5rem', fontSize: '1.1rem', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer' }}>
          {loading ? 'Processing AI...' : '🌊 Log Ocean Cleanup (Photo)'}
        </button>
      </div>

      {/* Queue View */}
      <div style={{ backgroundColor: '#f9fafb', padding: '1.5rem', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 style={{ margin: 0, fontSize: '1.2rem' }}>Local Agent Queue</h2>
          <button 
            onClick={handleSync}
            disabled={syncing || pendingCount === 0 || !isOnline}
            style={{ 
              padding: '0.75rem 1.5rem', 
              backgroundColor: (!isOnline || pendingCount === 0) ? '#d1d5db' : '#8b5cf6', 
              color: (!isOnline || pendingCount === 0) ? '#6b7280' : 'white', 
              border: 'none', 
              borderRadius: '8px', 
              cursor: (!isOnline || pendingCount === 0) ? 'not-allowed' : 'pointer',
              fontWeight: 'bold'
            }}>
            {syncing ? 'Syncing...' : `Sync ${pendingCount} Claims to Hedera`}
          </button>
        </div>

        {queue.length === 0 ? (
          <p style={{ color: '#6b7280', textAlign: 'center', padding: '2rem 0' }}>No ecological claims logged yet.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {queue.slice().reverse().map((item, idx) => (
              <div key={idx} style={{ 
                padding: '1rem', 
                backgroundColor: 'white', 
                borderRadius: '8px', 
                borderLeft: `4px solid ${item.status === 'synced' ? '#8b5cf6' : '#f59e0b'}`,
                boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <strong style={{ textTransform: 'capitalize' }}>{item.claim_type.replace('_', ' ')}</strong>
                  <span style={{ fontSize: '0.9rem', color: item.status === 'synced' ? '#6d28d9' : '#b45309', backgroundColor: item.status === 'synced' ? '#ede9fe' : '#fef3c7', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                    {item.status === 'synced' ? '✓ Synced to DLT' : '⏳ Pending Sync'}
                  </span>
                </div>
                <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', color: '#4b5563' }}>AI Analysis: {item.ai_analysis}</p>
                {item.hedera_tx_id && (
                  <p style={{ margin: 0, fontSize: '0.8rem', color: '#059669', wordBreak: 'break-all' }}>
                    <strong>Hedera TX:</strong> {item.hedera_tx_id} | <strong>Reward:</strong> {item.tokens_minted} Eco-Tokens
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
