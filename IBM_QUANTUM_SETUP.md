# 🔬 IBM Quantum Hardware Setup Guide

This guide will help you configure the Quantum Slot Machine to use **real IBM quantum computers** instead of the simulator.

## Step 1: Create IBM Quantum Account

1. Go to [IBM Quantum](https://quantum.ibm.com/)
2. Click **"Sign in"** or **"Start for free"**
3. Create an account (it's free!)
4. Complete the registration process

## Step 2: Get Your API Token

1. Once logged in, go to your [IBM Quantum Account](https://quantum.ibm.com/account)
2. Look for the **"API token"** section
3. Click **"Copy token"** to copy your API token to clipboard
4. **Important**: Keep this token secret! Don't share it or commit it to git

## Step 3: Configure the Backend

1. Open the file `/backend/.env` in your project
2. Replace `your_token_here` with your actual IBM Quantum API token:

```env
IBM_QUANTUM_TOKEN=your_actual_token_here_xyz123
```

3. (Optional) Configure other settings:

```env
# Specific backend to use (leave empty for auto-selection)
IBM_QUANTUM_BACKEND=

# Use simulator if quantum hardware unavailable
USE_SIMULATOR_FALLBACK=true

# Maximum queue wait time (seconds)
MAX_QUEUE_WAIT=300
```

## Step 4: Restart the Backend

If your backend server is running, stop it (Ctrl+C) and start it again:

```bash
cd backend
source venv/bin/activate
python main.py
```

You should see:
```
✅ Connected to IBM Quantum: ibm_brisbane
   Qubits: 127
   Status: active
```

## Step 5: Test the Connection

Visit `http://localhost:8000/info` to check the connection status.

You should see:
```json
{
  "ibm_quantum": {
    "connected": true,
    "backend": "ibm_brisbane",
    "num_qubits": 127,
    "status": "active",
    "pending_jobs": 5
  }
}
```

## Available IBM Quantum Backends

IBM provides several quantum computers. The system will automatically select the least busy one, but you can specify:

- **ibm_brisbane** - 127 qubits
- **ibm_kyoto** - 127 qubits
- **ibm_osaka** - 127 qubits
- **ibm_sherbrooke** - 127 qubits
- **ibm_torino** - 133 qubits

To use a specific backend, set in `.env`:
```env
IBM_QUANTUM_BACKEND=ibm_brisbane
```

## Understanding Queue Times

Real quantum computers are shared resources:

- **Pending jobs**: Number of jobs waiting in queue
- **Typical wait**: 1-30 minutes depending on demand
- **Simulator fallback**: If queue > 10 jobs, uses simulator (configurable)

## How to Know You're Using Real Quantum Hardware

When you spin the slot machine:

1. Check the response - it includes `backend_used`
2. Look for backend names like `ibm_brisbane` instead of `qiskit_aer_simulator`
3. You may see `queue_position` showing your position in queue
4. Backend console will show: `🔬 Running on real quantum hardware`

## Free Tier Limits

IBM Quantum free tier includes:

- **10 minutes** of quantum computing time per month
- Access to all publicly available quantum systems
- No credit card required

This is plenty for the slot machine demo! Each spin uses ~1-2 seconds of quantum time.

## Troubleshooting

### "Failed to connect to IBM Quantum"

- Check your API token is correct in `.env`
- Ensure you're connected to the internet
- Verify your IBM Quantum account is active

### "Queue too long, using simulator"

- Quantum computers have limited capacity
- Try again later or during off-peak hours
- Increase `MAX_QUEUE_WAIT` in `.env` to wait longer
- Set `USE_SIMULATOR_FALLBACK=false` to always wait for real hardware

### Backend console shows only simulator

- Check `.env` file is in the `/backend` directory
- Ensure token is not `your_token_here`
- Restart the backend server after changing `.env`

## Security Best Practices

✅ **DO:**
- Keep your API token secret
- Use `.env` file (already in `.gitignore`)
- Regenerate token if accidentally exposed

❌ **DON'T:**
- Commit `.env` to git
- Share your token publicly
- Hardcode token in source files

## Real vs Simulator: What's Different?

### Real Quantum Computer:
- ✅ True quantum randomness from quantum measurement
- ✅ Authentic quantum noise and decoherence effects
- ⚠️ Queue wait times
- ⚠️ Subject to hardware errors and calibration
- ⚠️ Limited monthly free tier usage

### Simulator:
- ✅ Instant results, no queue
- ✅ Unlimited usage
- ✅ Idealized quantum behavior
- ⚠️ Runs on classical computer
- ⚠️ Computationally simulated randomness

## Learn More

- [IBM Quantum Documentation](https://docs.quantum.ibm.com/)
- [Qiskit Runtime](https://qiskit.org/documentation/partners/qiskit_ibm_runtime/)
- [IBM Quantum Experience](https://quantum.ibm.com/composer)

---

**Congratulations!** 🎉 You're now running quantum circuits on real quantum hardware!
