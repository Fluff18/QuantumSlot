import React, { useState } from 'react';
import './App.css';

function App() {
  const [symbols, setSymbols] = useState(['❓', '❓', '❓']);
  const [theta, setTheta] = useState(Math.PI / 2);
  const [entanglement, setEntanglement] = useState(false);
  const [spinning, setSpinning] = useState(false);
  const [distribution, setDistribution] = useState({});
  const [measurements, setMeasurements] = useState([]);
  const [error, setError] = useState(null);
  const [backendUsed, setBackendUsed] = useState(null);
  const [queuePosition, setQueuePosition] = useState(null);

  const handleSpin = async () => {
    setSpinning(true);
    setError(null);

    // Animate the spin
    const spinAnimation = setInterval(() => {
      setSymbols([
        ['🍒', '🍋', '🍊', '🍇', '⭐', '💎', '7️⃣', '🔔'][Math.floor(Math.random() * 8)],
        ['🍒', '🍋', '🍊', '🍇', '⭐', '💎', '7️⃣', '🔔'][Math.floor(Math.random() * 8)],
        ['🍒', '🍋', '🍊', '🍇', '⭐', '💎', '7️⃣', '🔔'][Math.floor(Math.random() * 8)]
      ]);
    }, 100);

    try {
      const response = await fetch('/spin', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          theta: theta,
          entanglement: entanglement
        })
      });

      if (!response.ok) {
        throw new Error('Failed to spin');
      }

      const data = await response.json();

      // Stop animation after a delay
      setTimeout(() => {
        clearInterval(spinAnimation);
        setSymbols(data.symbols);
        setMeasurements(data.measurements);
        setDistribution(data.distribution);
        setBackendUsed(data.backend_used);
        setQueuePosition(data.queue_position);
        setSpinning(false);
      }, 1000);

    } catch (err) {
      clearInterval(spinAnimation);
      setError('Failed to connect to quantum backend. Make sure the backend is running on port 8000.');
      setSpinning(false);
      setSymbols(['❌', '❌', '❌']);
    }
  };

  const formatTheta = (value) => {
    if (value === 0) return '0';
    if (Math.abs(value - Math.PI / 2) < 0.01) return 'π/2';
    if (Math.abs(value - Math.PI) < 0.01) return 'π';
    return value.toFixed(2);
  };

  const calculateProbability = (theta) => {
    // For RY(θ), probability of |1⟩ is sin²(θ/2)
    const prob1 = Math.pow(Math.sin(theta / 2), 2);
    return (prob1 * 100).toFixed(1);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>⚛️ Quantum Slot Machine</h1>
        <p className="subtitle">Powered by Real Quantum Hardware</p>
        {backendUsed && (
          <div className={`backend-indicator ${backendUsed.includes('ibm_') ? 'quantum' : 'simulator'}`}>
            {backendUsed.includes('ibm_') ? (
              <>
                🔬 Running on: <strong>{backendUsed}</strong>
                {queuePosition !== null && ` (Queue: ${queuePosition} jobs)`}
              </>
            ) : (
              <>
                🖥️ Running on: <strong>Simulator</strong>
              </>
            )}
          </div>
        )}
      </header>

      <div className="slot-machine">
        <div className="reels">
          {symbols.map((symbol, index) => (
            <div key={index} className={`reel ${spinning ? 'spinning' : ''}`}>
              <div className="symbol">{symbol}</div>
            </div>
          ))}
        </div>

        {measurements.length > 0 && !spinning && (
          <div className="measurements">
            <p>Raw measurements: [{measurements.join(', ')}]</p>
          </div>
        )}

        <div className="controls">
          <button
            className="spin-button"
            onClick={handleSpin}
            disabled={spinning}
          >
            {spinning ? 'SPINNING...' : 'SPIN'}
          </button>
        </div>

        <div className="parameters">
          <div className="parameter">
            <label>
              Bias (θ): {formatTheta(theta)}
              <span className="prob-info">
                P(|1⟩) ≈ {calculateProbability(theta)}%
              </span>
            </label>
            <input
              type="range"
              min="0"
              max={Math.PI}
              step="0.01"
              value={theta}
              onChange={(e) => setTheta(parseFloat(e.target.value))}
              disabled={spinning}
            />
            <div className="slider-labels">
              <span>0</span>
              <span>π/2 (balanced)</span>
              <span>π</span>
            </div>
          </div>

          <div className="parameter">
            <label>
              <input
                type="checkbox"
                checked={entanglement}
                onChange={(e) => setEntanglement(e.target.checked)}
                disabled={spinning}
              />
              Enable Entanglement (CNOT gates)
            </label>
          </div>
        </div>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {Object.keys(distribution).length > 0 && !spinning && (
          <div className="distribution">
            <h3>Measurement Distribution (100 shots)</h3>
            <div className="distribution-bars">
              {Object.entries(distribution)
                .sort((a, b) => b[1] - a[1])
                .map(([outcome, count]) => (
                  <div key={outcome} className="distribution-item">
                    <span className="outcome-label">{outcome}</span>
                    <div className="bar-container">
                      <div
                        className="bar"
                        style={{ width: `${(count / 100) * 100}%` }}
                      >
                        <span className="bar-label">{count}</span>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>

      <footer className="info-section">
        <h3>How It Works</h3>
        <div className="info-content">
          <div className="info-box">
            <h4>Quantum Circuit</h4>
            <p>
              Each spin creates a 3-qubit quantum circuit. Each qubit starts in |0⟩ state,
              then an RY(θ) gate is applied to create superposition.
            </p>
          </div>
          <div className="info-box">
            <h4>RY Gate</h4>
            <p>
              RY(θ) rotates the qubit around the Y-axis. At θ = π/2, you get a balanced
              50/50 superposition. Adjust θ to bias the results.
            </p>
          </div>
          <div className="info-box">
            <h4>Entanglement</h4>
            <p>
              When enabled, CNOT gates entangle the qubits, creating correlations
              between their measurement outcomes.
            </p>
          </div>
          <div className="info-box">
            <h4>Measurement</h4>
            <p>
              Measuring the qubits collapses their superposition, giving truly random
              results based on quantum probability amplitudes.
            </p>
          </div>
        </div>
        <div className="disclaimer">
          <h4>⚠️ Important Information:</h4>
          <ul>
            <li>This application can run on <strong>real IBM quantum computers</strong> or a classical simulator</li>
            <li>When connected to IBM Quantum, you're using actual quantum hardware (100+ qubits)</li>
            <li>Look for the backend indicator above to see which system is being used</li>
            <li>Real quantum hardware may have queue wait times during peak usage</li>
            <li>The simulator provides instant results but is computed classically</li>
            <li>This is an educational demo - not for cryptographic or production use</li>
          </ul>
        </div>
      </footer>
    </div>
  );
}

export default App;
