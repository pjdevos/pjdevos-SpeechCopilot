import React, { useState } from 'react';
import './App.css';

// API helper functions
const API_BASE_URL = 'https://pjdevos-speechcopilot-production.up.railway.app';

const speechAPI = {
  testConnection: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return await response.json();
    } catch (error) {
      console.error('API connection failed:', error);
      throw error;
    }
  },

  generateSpeech: async (wizardData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/generate-speech`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          occasion: wizardData.occasion,
          audience: wizardData.audience,
          tone: wizardData.tone,
          length: wizardData.length,
          template: wizardData.template,
          topic: wizardData.topic || '',
          additional_context: wizardData.additionalContext || '',
          language: wizardData.language
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Speech generation failed:', error);
      throw error;
    }
  }
};

function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [wizardData, setWizardData] = useState({
    occasion: '',
    audience: '',
    tone: 'formal',
    length: '5',
    template: '',
    topic: '',
    additionalContext: '',
    language: 'english'
  });
  const [generatedSpeech, setGeneratedSpeech] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateSpeech = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Sending data to API:', wizardData);
      
      const result = await speechAPI.generateSpeech(wizardData);
      
      console.log('API response:', result);
      
      setGeneratedSpeech({
        speech: result.speech,
        structure: result.structure,
        suggestions: result.suggestions,
        metadata: {
          occasion: wizardData.occasion,
          audience: wizardData.audience,
          tone: wizardData.tone,
          length: wizardData.length,
          template: wizardData.template,
          language: wizardData.language
        }
      });
      
      setCurrentStep(4);
      
    } catch (error) {
      console.error('Error generating speech:', error);
      setError(`Failed to generate speech: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const testAPI = async () => {
    try {
      const health = await speechAPI.testConnection();
      console.log('API Health:', health);
      alert('API connection successful!');
    } catch (error) {
      alert(`API connection failed: ${error.message}`);
    }
  };

  const resetWizard = () => {
    setCurrentStep(0);
    setWizardData({
      occasion: '',
      audience: '',
      tone: 'formal',
      length: '5',
      template: '',
      topic: '',
      additionalContext: ''
    });
    setGeneratedSpeech(null);
    setError(null);
  };

  const nextStep = () => {
    if (currentStep < 4) setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    if (currentStep > 0) setCurrentStep(currentStep - 1);
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="step-container">
            <h2>Context & Occasion</h2>
            <div className="form-group">
              <label>Occasion</label>
              <select 
                value={wizardData.occasion} 
                onChange={(e) => setWizardData({...wizardData, occasion: e.target.value})}
              >
                <option value="">Select occasion...</option>
                <option value="conference">Conference/Summit</option>
                <option value="press-conference">Press Conference</option>
                <option value="corporate-event">Corporate Event</option>
                <option value="diplomatic-meeting">Diplomatic Meeting</option>
                <option value="commemoration">Commemoration</option>
                <option value="policy-announcement">Policy Announcement</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Primary Audience</label>
              <select 
                value={wizardData.audience} 
                onChange={(e) => setWizardData({...wizardData, audience: e.target.value})}
              >
                <option value="">Select audience...</option>
                <option value="diplomats">Diplomats</option>
                <option value="business-leaders">Business Leaders</option>
                <option value="media">Media/Press</option>
                <option value="general-public">General Public</option>
                <option value="government-officials">Government Officials</option>
                <option value="academic-audience">Academic Audience</option>
              </select>
            </div>

            <div className="form-group">
              <label>Speech Topic/Subject</label>
              <input 
                type="text"
                placeholder="e.g., Climate change policy, Trade agreement..."
                value={wizardData.topic}
                onChange={(e) => setWizardData({...wizardData, topic: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label>Speech Length</label>
              <select 
                value={wizardData.length} 
                onChange={(e) => setWizardData({...wizardData, length: e.target.value})}
              >
                <option value="2">2 minutes</option>
                <option value="5">5 minutes</option>
                <option value="10">10 minutes</option>
                <option value="15">15 minutes</option>
                <option value="20">20 minutes</option>
                <option value="25">25 minutes</option>
                <option value="30">30 minutes</option>
                <option value="35">35 minutes</option>
                <option value="40">40 minutes</option>
              </select>
            </div>
            <div className="form-group">
              <label>Speech Language</label>
              <select 
                value={wizardData.language} 
                onChange={(e) => setWizardData({...wizardData, language: e.target.value})}
              >
                <option value="english">🇺🇸 English</option>
                <option value="dutch">🇳🇱 Nederlands (Dutch)</option>
                <option value="french">🇫🇷 Français (French)</option>
              </select>
            </div>
          </div>
        );

      case 1:
        return (
          <div className="step-container">
            <h2>Tone & Style</h2>
            <div className="form-group">
              <label>Overall Tone</label>
              <select 
                value={wizardData.tone} 
                onChange={(e) => setWizardData({...wizardData, tone: e.target.value})}
              >
                <option value="formal">Formal</option>
                <option value="conversational">Conversational</option>
                <option value="inspiring">Inspiring</option>
                <option value="urgent">Urgent</option>
                <option value="conciliatory">Conciliatory</option>
                <option value="celebratory">Celebratory</option>
              </select>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="step-container">
            <h2>Template Selection</h2>
            <div className="template-grid">
              {[
                { id: 'crisis-response', name: 'Crisis Response', desc: 'Address urgent situations with clarity and action' },
                { id: 'policy-announcement', name: 'Policy Announcement', desc: 'Present new policies with context and benefits' },
                { id: 'diplomatic-keynote', name: 'Diplomatic Keynote', desc: 'Formal international address' },
                { id: 'commemorative', name: 'Commemorative', desc: 'Honor events, people, or achievements' },
                { id: 'persuasive', name: 'Persuasive', desc: 'Convince audience of a position or action' },
                { id: 'informational', name: 'Informational', desc: 'Educate audience on complex topics' }
              ].map(template => (
                <div 
                  key={template.id}
                  className={`template-card ${wizardData.template === template.id ? 'selected' : ''}`}
                  onClick={() => setWizardData({...wizardData, template: template.id})}
                >
                  <h3>{template.name}</h3>
                  <p>{template.desc}</p>
                </div>
              ))}
            </div>
          </div>
        );

      case 3:
        return (
          <div className="step-container">
            <h2>Review & Generate</h2>
            <div className="review-section">
              <h3>Speech Configuration:</h3>
              <ul>
                <li><strong>Occasion:</strong> {wizardData.occasion}</li>
                <li><strong>Audience:</strong> {wizardData.audience}</li>
                <li><strong>Topic:</strong> {wizardData.topic}</li>
                <li><strong>Length:</strong> {wizardData.length} minutes</li>
                <li><strong>Tone:</strong> {wizardData.tone}</li>
                <li><strong>Template:</strong> {wizardData.template}</li>
                <li><strong>Language:</strong> {wizardData.language}</li>
              </ul>
            </div>
            
            <div className="form-group">
              <label>Additional Context (Optional)</label>
              <textarea 
                placeholder="Any specific points, quotes, or context you'd like included..."
                value={wizardData.additionalContext}
                onChange={(e) => setWizardData({...wizardData, additionalContext: e.target.value})}
                rows="4"
              />
            </div>
            
            <button 
              className="generate-btn"
              onClick={generateSpeech}
              disabled={isLoading}
            >
              {isLoading ? 'Generating Speech...' : 'Generate Speech'}
            </button>
          </div>
        );

      case 4:
        return (
          <div className="step-container">
            <h2>Generated Speech</h2>
            {generatedSpeech && (
              <div className="speech-result">
                <div className="speech-content">
                  <pre style={{whiteSpace: 'pre-wrap', fontFamily: 'inherit'}}>
                    {generatedSpeech.speech}
                  </pre>
                </div>
                
                <div className="speech-actions">
                  <button onClick={() => navigator.clipboard.writeText(generatedSpeech.speech)}>
                    Copy to Clipboard
                  </button>
                  <button onClick={prevStep}>
                    Go Back & Edit
                  </button>
                  <button onClick={resetWizard}>Generate New Speech</button>
                </div>
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🎤 Speech Copilot</h1>
        <p>AI-powered speech generation for professionals</p>
        
        {/* Debug buttons */}
        <div className="debug-section">
          <button onClick={testAPI} className="test-btn">
            Test API Connection
          </button>
          <span className="step-indicator">Step {currentStep + 1} of 5</span>
        </div>
      </header>

      <main className="main-content">
        {/* Error display */}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {/* Loading indicator */}
        {isLoading && (
          <div className="loading-message">
            <div className="spinner"></div>
            Generating your speech with Claude AI...
          </div>
        )}

        {/* Wizard content */}
        <div className="wizard-container">
          {renderStep()}
          
          {/* Navigation */}
          {currentStep < 4 && (
            <div className="wizard-navigation">
              {currentStep > 0 && (
                <button onClick={prevStep} className="nav-btn prev">
                  Previous
                </button>
              )}
              {currentStep < 3 && (
                <button 
                  onClick={nextStep} 
                  className="nav-btn next"
                  disabled={
                    (currentStep === 0 && (!wizardData.occasion || !wizardData.audience)) ||
                    (currentStep === 2 && !wizardData.template)
                  }
                >
                  Next
                </button>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
