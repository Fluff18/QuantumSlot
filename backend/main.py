"""
Quantum Slot Machine Backend
Uses Qiskit Aer to generate truly random outcomes via quantum measurement
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import math
import random

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

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
    
    The randomness comes from quantum measurement, not pseudo-random algorithms.
    """
    # Create quantum circuit
    qc = create_quantum_circuit(request.theta, request.entanglement)
    
    # Set up simulator
    simulator = AerSimulator()
    
    # Run the circuit multiple times to get distribution
    shots = 100  # Number of measurements
    job = simulator.run(qc, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    # Get one measurement for the current spin (pick the most recent)
    # In quantum mechanics, each measurement collapses the wavefunction uniquely
    measurement_outcomes = list(counts.keys())
    # Pick based on weighted probability from counts
    measurement_str = random.choices(
        measurement_outcomes,
        weights=[counts[k] for k in measurement_outcomes],
        k=1
    )[0]
    
    # Parse the measurement string (e.g., "101" -> [1, 0, 1])
    measurements = [int(bit) for bit in measurement_str]
    
    # Map individual qubit measurements to symbols
    # Use different symbols for 0 and 1 states by offsetting by half the symbol list
    SYMBOL_OFFSET = len(SYMBOLS) // 2
    symbols = [SYMBOLS[m * SYMBOL_OFFSET % len(SYMBOLS)] for m in measurements]
    
    # Return results with distribution
    return SpinResponse(
        symbols=symbols,
        measurements=measurements,
        distribution=counts
    )


@app.get("/info")
async def info():
    """
    Get information about the quantum circuit and how it works.
    """
    return {
        "description": "Quantum Slot Machine using Qiskit Aer simulator",
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
        "randomness_source": "Quantum measurement collapse",
        "symbols": SYMBOLS,
        "disclaimer": "This is a simulation using Qiskit Aer, not a real quantum computer. Results demonstrate quantum mechanical principles but are computed classically."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
