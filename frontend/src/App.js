import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  updateFormField,
  submitInteractionForm,
  sendChatMessage,
  addUserMessage,
  resetForm,
} from './features/interaction/interactionSlice';
import './App.css';

function App() {
  const dispatch = useDispatch();
  const form = useSelector((state) => state.interaction.form);
  const chatMessages = useSelector((state) => state.interaction.chatMessages);
  const loading = useSelector((state) => state.interaction.loading);

  const [chatInput, setChatInput] = useState('');

  const handleFieldChange = (field, value) => {
    dispatch(updateFormField({ field, value }));
  };

  const handleFormSubmit = () => {
    if (!form.hcpName) {
      alert('Please enter HCP name');
      return;
    }
    // Note: form ke hcpName ko backend hcp_id chahiye — simplified demo ke liye
    // hum yahan seedha topics/sentiment save kar rahe hain via /interactions endpoint
    dispatch(
      submitInteractionForm({
        hcp_id: 1, // demo ke liye fixed; real app mein HCP search/select se aayega
        interaction_type: form.interactionType,
        interaction_date: form.date || null,
        interaction_time: form.time || null,
        attendees: form.attendees,
        topics_discussed: form.topicsDiscussed,
        sentiment: form.sentiment,
        outcomes: form.outcomes,
        followup_actions: form.followupActions,
      })
    );
    alert('Interaction logged successfully!');
  };

  const handleChatSend = () => {
    if (!chatInput.trim()) return;
    dispatch(addUserMessage(chatInput));
    dispatch(sendChatMessage(chatInput));
    setChatInput('');
  };

  return (
    <div className="app-container">
      <h2 className="page-title">Log HCP Interaction</h2>
      <div className="main-grid">
        {/* LEFT: Structured Form */}
        <div className="form-panel">
          <h3>Interaction Details</h3>

          <div className="form-row">
            <div className="form-group">
              <label>HCP Name</label>
              <input
                type="text"
                placeholder="Search or select HCP..."
                value={form.hcpName}
                onChange={(e) => handleFieldChange('hcpName', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Interaction Type</label>
              <select
                value={form.interactionType}
                onChange={(e) => handleFieldChange('interactionType', e.target.value)}
              >
                <option>Meeting</option>
                <option>Call</option>
                <option>Email</option>
                <option>Conference</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Date</label>
              <input
                type="date"
                value={form.date}
                onChange={(e) => handleFieldChange('date', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Time</label>
              <input
                type="time"
                value={form.time}
                onChange={(e) => handleFieldChange('time', e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label>Attendees</label>
            <input
              type="text"
              placeholder="Enter names or search..."
              value={form.attendees}
              onChange={(e) => handleFieldChange('attendees', e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Topics Discussed</label>
            <textarea
              placeholder="Enter key discussion points..."
              value={form.topicsDiscussed}
              onChange={(e) => handleFieldChange('topicsDiscussed', e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Observed / Inferred HCP Sentiment</label>
            <div className="sentiment-options">
              {['Positive', 'Neutral', 'Negative'].map((s) => (
                <label key={s} className="radio-label">
                  <input
                    type="radio"
                    name="sentiment"
                    checked={form.sentiment === s}
                    onChange={() => handleFieldChange('sentiment', s)}
                  />
                  {s}
                </label>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Outcomes</label>
            <textarea
              placeholder="Key outcomes or agreements..."
              value={form.outcomes}
              onChange={(e) => handleFieldChange('outcomes', e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Follow-up Actions</label>
            <textarea
              placeholder="Enter next steps or tasks..."
              value={form.followupActions}
              onChange={(e) => handleFieldChange('followupActions', e.target.value)}
            />
          </div>

          <button className="log-btn" onClick={handleFormSubmit}>
            Log Interaction
          </button>
        </div>

        {/* RIGHT: AI Chat Panel */}
        <div className="chat-panel">
          <h3>🤖 AI Assistant</h3>
          <p className="chat-subtitle">Log interaction via chat</p>

          <div className="chat-messages">
            {chatMessages.length === 0 && (
              <div className="chat-placeholder">
                Log interaction details here (e.g., "Met Dr. Smith, discussed
                Product X efficacy, positive sentiment, shared brochure") or
                ask for help.
              </div>
            )}
            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`chat-bubble ${msg.role}`}>
                {msg.text}
              </div>
            ))}
            {loading && <div className="chat-bubble ai">Thinking...</div>}
          </div>

          <div className="chat-input-row">
            <input
              type="text"
              placeholder="Describe interaction..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleChatSend()}
            />
            <button onClick={handleChatSend} disabled={loading}>
              Log
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;