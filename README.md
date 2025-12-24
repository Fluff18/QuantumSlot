# ⚛️ Quantum Slot Machine

A demonstration web application that uses quantum computing principles to generate random outcomes for a slot machine. Built with Python (FastAPI + Qiskit Aer) backend and React frontend.

## 🎯 What This Demo Does

This application demonstrates how quantum mechanics can be used to generate random numbers through quantum measurement. Each "spin" of the slot machine:

1. **Prepares 3 qubits** in the |0⟩ state
2. **Applies RY(θ) rotation gates** to create quantum superposition
3. **Optionally entangles** qubits using CNOT gates
4. **Measures the qubits** to collapse the superposition
5. **Maps measurements** to slot machine symbols

The key feature is that **randomness comes from quantum measurement**, not from pseudo-random number generators.

## 🔬 How the Quantum Circuit Works

### Basic Circuit (No Entanglement)

```
q0: ─RY(θ)─┤M├
q1: ─RY(θ)─┤M├
q2: ─RY(θ)─┤M├
```

Each qubit undergoes:
- **RY(θ) Gate**: Rotates the qubit around the Y-axis by angle θ
  - The gate transforms: `|0⟩ → cos(θ/2)|0⟩ + sin(θ/2)|1⟩`
  - At θ = 0: 100% probability of measuring |0⟩
  - At θ = π/2: 50/50 superposition (balanced randomness)
  - At θ = π: 100% probability of measuring |1⟩

### With Entanglement

```
q0: ─RY(θ)─■─────┤M├
q1: ─RY(θ)─X──■──┤M├
q2: ─RY(θ)────X──┤M├
```

CNOT (controlled-NOT) gates create quantum entanglement:
- Qubit 0 controls qubit 1
- Qubit 1 controls qubit 2
- This creates correlations between measurement outcomes

### Measurement Process

When a qubit in superposition is measured:
1. The superposition **collapses** to either |0⟩ or |1⟩
2. The probability is determined by the quantum state amplitudes
3. For RY(θ): P(|1⟩) = sin²(θ/2)
4. Each measurement is fundamentally random according to quantum mechanics

The outcomes are mapped to slot symbols: 🍒 🍋 🍊 🍇 ⭐ 💎 7️⃣ 🔔

## ⚠️ What This Demo Does NOT Claim

**Important Disclaimers:**

1. **This uses a classical simulator (Qiskit Aer)**, not a real quantum computer
   - The quantum circuit is simulated on classical hardware
   - Results accurately model quantum behavior but are computed deterministically

2. **Not cryptographically secure**
   - This is an educational demonstration
   - Do not use for security-critical applications
   - Classical simulation can be predictable with knowledge of the seed

3. **Simulation vs. Reality**
   - Real quantum computers have noise, decoherence, and error rates
   - This simulator provides idealized quantum behavior
   - Actual quantum hardware would show different characteristics

4. **Educational Purpose**
   - Designed to teach quantum computing concepts
   - Demonstrates superposition, measurement, and entanglement
   - Not intended for gambling or financial applications

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 14+** (for frontend)
- **pip** (Python package manager)
- **npm** (Node package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Fluff18/QuantumSlot.git
   cd QuantumSlot
   ```

2. **Set up the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Quick Start (Automated)

Use the provided script to start both servers automatically:

```bash
chmod +x start.sh
./start.sh
```

This will:
- Start the backend API on `http://localhost:8000`
- Start the frontend UI on `http://localhost:3000`
- Open your browser automatically

Press `Ctrl+C` to stop both servers.

### Manual Start

If you prefer to run the servers separately:

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```
The API will be available at `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```
The web app will open at `http://localhost:3000`

### Using the Application

1. **Spin Button**: Click to run a quantum measurement and get random symbols
2. **Bias Slider (θ)**: Adjust the rotation angle
   - Left (0): Bias toward |0⟩
   - Center (π/2): Balanced 50/50
   - Right (π): Bias toward |1⟩
3. **Entanglement Toggle**: Enable CNOT gates to entangle the qubits
4. **Distribution Chart**: Shows the measurement outcomes from 100 shots

## 📚 Technical Details

### Backend (Python + FastAPI + Qiskit)

- **FastAPI**: Modern, fast web framework for building APIs
- **Qiskit**: IBM's quantum computing SDK
- **Qiskit Aer**: High-performance quantum circuit simulator
- **Endpoints**:
  - `POST /spin`: Execute quantum circuit and return results
  - `GET /info`: Get information about the quantum circuit

### Frontend (React)

- **React 18**: Modern UI library for building interactive interfaces
- **Fetch API**: Communicates with backend
- **CSS**: Custom styling with gradients and animations
- **Real-time updates**: Shows spinning animation and measurement results

### Quantum Randomness vs. Pseudo-Random

Traditional random number generators use algorithms that are:
- Deterministic (same seed → same sequence)
- Predictable if the algorithm is known
- "Pseudo-random" not truly random

Quantum randomness (in theory) is:
- Based on fundamental uncertainty in quantum mechanics
- Truly random according to current physics understanding
- Unpredictable even with complete knowledge of initial conditions

**Note**: Since this demo uses a simulator, the randomness is still computational, but it accurately models the quantum probabilities.

## 🧪 API Examples

### Spin the Quantum Slot

```bash
curl -X POST http://localhost:8000/spin \
  -H "Content-Type: application/json" \
  -d '{"theta": 1.5708, "entanglement": false}'
```

Response:
```json
{
  "symbols": ["🍒", "💎", "🍋"],
  "measurements": [0, 1, 0],
  "distribution": {
    "000": 23,
    "001": 27,
    "010": 25,
    "011": 25
  }
}
```

### Get Circuit Information

```bash
curl http://localhost:8000/info
```

## 📖 Learn More

### Quantum Computing Concepts

- **Superposition**: A qubit can be in a combination of |0⟩ and |1⟩ simultaneously
- **Measurement**: Observing a qubit collapses it to either |0⟩ or |1⟩
- **Entanglement**: Qubits become correlated; measuring one affects the other
- **Quantum Gates**: Operations that manipulate quantum states

### Resources

- [Qiskit Documentation](https://qiskit.org/documentation/)
- [Qiskit Textbook](https://qiskit.org/textbook/preface.html)
- [IBM Quantum Experience](https://quantum-computing.ibm.com/)
- [Quantum Computing for Computer Scientists](https://www.youtube.com/watch?v=F_Riqjdh2oM)

## 🛠️ Development

### Project Structure

```
QuantumSlot/
├── backend/
│   ├── main.py              # FastAPI application with quantum circuit
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── public/
│   │   └── index.html       # HTML template
│   ├── src/
│   │   ├── App.js           # Main React component
│   │   ├── App.css          # Styling
│   │   ├── index.js         # React entry point
│   │   └── index.css        # Global styles
│   └── package.json         # Node dependencies
└── README.md                # This file
```

### Extending the Demo

Ideas for enhancements:
- Add more quantum gates (Hadamard, X, Z)
- Implement different measurement bases
- Add visualization of quantum states
- Connect to real IBM quantum hardware
- Add more complex entanglement patterns
- Implement quantum error correction

## 📄 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

- **IBM Qiskit**: For the excellent quantum computing framework
- **FastAPI**: For the modern Python web framework
- **React**: For the powerful UI library

---

**Remember**: This is a demonstration of quantum principles using classical simulation. While it accurately models quantum behavior, it's not running on actual quantum hardware and should be used for educational purposes only.
