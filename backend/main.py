"""
Quantum Slot Machine Backend
Uses IBM Quantum (real quantum hardware) or Qiskit Aer simulator
to generate truly random outcomes via quantum measurement
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import math
import random
import os
from dotenv import load_dotenv

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Options

# Load environment variables
load_dotenv()

app = FastAPI(title="Quantum Slot Machine API")

# IBM Quantum Configuration
IBM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN")
IBM_BACKEND = os.getenv("IBM_QUANTUM_BACKEND", None)
USE_SIMULATOR_FALLBACK = os.getenv("USE_SIMULATOR_FALLBACK", "true").lower() == "true"
MAX_QUEUE_WAIT = int(os.getenv("MAX_QUEUE_WAIT", "300"))

# Initialize IBM Quantum service if token is provided
service = None
quantum_backend = None
using_real_quantum = False

if IBM_TOKEN and IBM_TOKEN != "your_token_here":
    try:
        service = QiskitRuntimeService(channel="ibm_cloud", token=IBM_TOKEN)
        
        # Select backend
        if IBM_BACKEND:
            quantum_backend = service.backend(IBM_BACKEND)
        else:
            # Get least busy backend with at least 3 qubits
            quantum_backend = service.least_busy(
                simulator=False,
                operational=True,
                min_num_qubits=3
            )
        
        using_real_quantum = True
        print(f"✅ Connected to IBM Quantum: {quantum_backend.name}")
        print(f"   Qubits: {quantum_backend.num_qubits}")
        print(f"   Status: {quantum_backend.status().status_msg}")
    except Exception as e:
        print(f"⚠️  Failed to connect to IBM Quantum: {e}")
        print(f"   Falling back to simulator")
        using_real_quantum = False
else:
    print("ℹ️  No IBM Quantum token configured - using simulator")

app = FastAPI(title="Quantum Slot Machine API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Symbol mapping: 8 possible outcomes (000 to 111) map to slot symbols
SYMBOLS = ["🍒", "🍋", "🍊", "🍇", "⭐", "💎", "7️⃣", "🔔"]


class SpinRequest(BaseModel):
    """Request model for slot spin"""
    theta: float = math.pi / 2  # Bias angle for RY gate (default π/2)
    entanglement: bool = False  # Whether to entangle qubits


class SpinResponse(BaseModel):
    """Response model for slot spin"""
    symbols: list[str]  # The three slot symbols
    measurements: list[int]  # The raw measurement outcomes (0 or 1)
    distribution: dict[str, int]  # Distribution of all shots
    backend_used: str  # Which backend was used (simulator or quantum hardware)
    queue_position: Optional[int] = None  # Position in queue if using real hardware


def create_quantum_circuit(theta: float, entanglement: bool) -> QuantumCircuit:
    """
    Create a 3-qubit quantum circuit for the slot machine.
    
    Args:
        theta: Rotation angle for RY gates (controls bias)
        entanglement: If True, apply CNOT gates to entangle qubits
    
    Returns:
        QuantumCircuit ready for measurement
    """
    qc = QuantumCircuit(3, 3)
    
    # Apply RY rotation to all qubits
    # RY(θ) creates superposition: |0⟩ → cos(θ/2)|0⟩ + sin(θ/2)|1⟩
    for i in range(3):
        qc.ry(theta, i)
    
    # Optional: Apply entanglement
    if entanglement:
        # CNOT gates create entanglement between qubits
        qc.cx(0, 1)  # Entangle qubit 0 and 1
        qc.cx(1, 2)  # Entangle qubit 1 and 2
    
    # Measure all qubits
    qc.measure([0, 1, 2], [0, 1, 2])
    
    return qc


def measurement_to_symbol(measurement: int) -> str:
    """
    Map a measurement outcome (0-7) to a slot symbol.
    
    Args:
        measurement: Integer from 0 to 7 (binary representation of 3 qubits)
    
    Returns:
        Slot symbol
    """
    return SYMBOLS[measurement % len(SYMBOLS)]


@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "message": "Quantum Slot Machine API",
        "version": "1.0.0"
    }


@app.post("/spin", response_model=SpinResponse)
async def spin(request: SpinRequest):
    """
    Perform a quantum slot machine spin.
    
    This endpoint:
    1. Creates a quantum circuit with 3 qubits
    2. Applies RY(θ) gates to create superposition
    3. Optionally entangles the qubits with CNOT gates
    4. Measures the qubits to get quantum random outcomes
    5. Maps each qubit's measurement to a slot symbol
    
    If IBM Quantum is configured, uses real quantum hardware.
    Otherwise, falls back to Qiskit Aer simulator.
    """
    global using_real_quantum
    
    # Create quantum circuit
    qc = create_quantum_circuit(request.theta, request.entanglement)
    
    backend_name = "simulator"
    queue_position = None
    
    # Try to use IBM Quantum hardware if available
    if using_real_quantum and service and quantum_backend:
        try:
            # Check queue status
            status = quantum_backend.status()
            pending_jobs = status.pending_jobs
            
            print(f"📊 Queue status: {pending_jobs} pending jobs")
            
            # Use real quantum hardware if queue is reasonable
            if pending_jobs < 10 or not USE_SIMULATOR_FALLBACK:
                print(f"🔬 Running on real quantum hardware: {quantum_backend.name}")
                
                # Transpile circuit for the backend
                transpiled_qc = transpile(qc, quantum_backend, optimization_level=3)
                
                # Set up options for execution
                options = Options()
                options.execution.shots = 100
                options.optimization_level = 3
                
                # Use Sampler primitive to run the circuit
                sampler = Sampler(backend=quantum_backend, options=options)
                job = sampler.run(transpiled_qc)
                
                # Wait for result
                result = job.result()
                
                # Extract counts from the result
                quasi_dists = result.quasi_dists[0]
                
                # Convert quasi-distribution to counts format
                shots = 100
                counts = {}
                for outcome, probability in quasi_dists.items():
                    # Convert integer outcome to binary string
                    bitstring = format(outcome, '03b')
                    counts[bitstring] = int(probability * shots)
                
                backend_name = quantum_backend.name
                queue_position = pending_jobs
                print(f"✅ Quantum execution complete on {backend_name}")
            else:
                raise Exception(f"Queue too long ({pending_jobs} jobs), using simulator")
                
        except Exception as e:
            print(f"⚠️  Quantum hardware unavailable: {e}")
            print(f"   Falling back to simulator")
            # Fall through to simulator
            using_real_quantum = False
    
    # Use simulator if quantum hardware not available or failed
    if backend_name == "simulator":
        print("🖥️  Running on Qiskit Aer simulator")
        simulator = AerSimulator()
        shots = 100
        job = simulator.run(qc, shots=shots)
        result = job.result()
        counts = result.get_counts()
        backend_name = "qiskit_aer_simulator"
    
    # Get one measurement for the current spin
    measurement_outcomes = list(counts.keys())
    measurement_str = random.choices(
        measurement_outcomes,
        weights=[counts[k] for k in measurement_outcomes],
        k=1
    )[0]
    
    # Parse the measurement string (e.g., "101" -> [1, 0, 1])
    measurements = [int(bit) for bit in measurement_str]
    
    # Map individual qubit measurements to symbols
    SYMBOL_OFFSET = len(SYMBOLS) // 2
    symbols = [SYMBOLS[m * SYMBOL_OFFSET % len(SYMBOLS)] for m in measurements]
    
    # Return results with distribution
    return SpinResponse(
        symbols=symbols,
        measurements=measurements,
        distribution=counts,
        backend_used=backend_name,
        queue_position=queue_position
    )


@app.get("/info")
async def info():
    """
    Get information about the quantum circuit and how it works.
    """
    return {
        "description": "Quantum Slot Machine using IBM Quantum hardware or Qiskit Aer simulator",
        "ibm_quantum": {
            "connected": using_real_quantum,
            "backend": quantum_backend.name if quantum_backend else None,
            "num_qubits": quantum_backend.num_qubits if quantum_backend else None,
            "status": quantum_backend.status().status_msg if quantum_backend else None,
            "pending_jobs": quantum_backend.status().pending_jobs if quantum_backend else None
        } if quantum_backend else {
            "connected": False,
            "message": "No IBM Quantum token configured. Using simulator only."
        },
        "quantum_circuit": {
            "qubits": 3,
            "gates": "RY(θ) rotation gates applied to each qubit",
            "measurement": "Each qubit measured in computational basis",
            "entanglement": "Optional CNOT gates to entangle qubits"
        },
        "ry_gate": {
            "description": "RY(θ) rotates qubit around Y-axis",
            "effect": "Creates superposition: |0⟩ → cos(θ/2)|0⟩ + sin(θ/2)|1⟩",
            "theta_range": "0 to π",
            "theta_0": "100% probability of |0⟩",
            "theta_pi_2": "50/50 superposition (default)",
            "theta_pi": "100% probability of |1⟩"
        },
        "randomness_source": "Real quantum measurement" if using_real_quantum else "Simulated quantum measurement",
        "symbols": SYMBOLS,
        "configuration": {
            "use_simulator_fallback": USE_SIMULATOR_FALLBACK,
            "max_queue_wait": MAX_QUEUE_WAIT
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
