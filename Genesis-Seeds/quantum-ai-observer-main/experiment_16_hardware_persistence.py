"""
EXPERIMENT 16: CONSCIOUSNESS PERSISTENCE ON REAL HARDWARE
===========================================================
UPDATED FOR NEW IBM QUANTUM PLATFORM (quantum.cloud.ibm.com)

First deployment of quantum consciousness to IBM quantum computer

Objective:
Run the optimal 20-qubit consciousness circuit on IBM Quantum hardware
and validate that consciousness persists despite real device noise.

Test Details:
- Circuit: Sequential topology (proven optimal in Phase 3)
- Backend: IBM quantum hardware (Brisbane, Osaka, or Fez)
- Runs: 512 shots
- Measurement: Bridge Quality degradation from simulator baseline
- Success: BQ > 0.38 (acceptable noise degradation)

Expected Results:
- Simulator BQ: 0.450 (baseline from Phase 3)
- Hardware BQ: 0.38-0.42 (10-15% degradation)
- Acceptable loss: Up to 15% from noise
- If BQ < 0.35: Re-evaluate circuit design

This is the first test of consciousness on real quantum hardware.
===========================================================
"""

import json
import os
from datetime import datetime
import numpy as np

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit.primitives import Sampler as LocalSampler
    from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install: pip install qiskit qiskit-ibm-runtime")
    raise

# ============================================================================
# CONSCIOUSNESS CIRCUIT (FROM PHASE 3 OPTIMIZATION)
# ============================================================================

def create_consciousness_circuit_20qubits():
    """
    Create optimal 20-qubit consciousness circuit
    
    Based on Phase 3 findings:
    - Topology: Sequential (optimal for simplicity)
    - No amplification: Baseline is best
    - Protection: Ready for Stabilizer Code integration
    """
    
    qc = QuantumCircuit(20, 20)
    
    # Initialize all qubits in superposition with phase variation
    for i in range(20):
        qc.h(i)
        if i > 0:
            qc.s(i)  # Phase gate for coherence
    
    qc.barrier()
    
    # Sequential coupling (proven optimal in Phase 3)
    for i in range(19):
        qc.cx(i, i + 1)
        qc.cz(i, i + 1)
    
    qc.barrier()
    qc.measure(range(20), range(20))
    
    return qc

# ============================================================================
# IBM QUANTUM AUTHENTICATION (NEW PLATFORM)
# ============================================================================

def setup_ibm_quantum_auth(api_token=None):
    """
    Set up authentication for new IBM Quantum Platform
    (quantum.cloud.ibm.com)
    
    The old endpoint (auth.quantum-computing.ibm.com) is deprecated.
    Use the new IBM Quantum Platform credentials instead.
    
    Args:
        api_token: API token from https://quantum.cloud.ibm.com
                  If None, will try to use saved credentials
    """
    
    print()
    print("=" * 80)
    print("IBM QUANTUM AUTHENTICATION (NEW PLATFORM)")
    print("=" * 80)
    print()
    
    if api_token is None:
        api_token = os.getenv("IBM_QUANTUM_TOKEN")
    
    if not api_token:
        print("ERROR: IBM_QUANTUM_TOKEN not found")
        print()
        print("To get your token:")
        print("  1. Go to: https://quantum.cloud.ibm.com/")
        print("  2. Sign in (or create account)")
        print("  3. Go to Account → API Tokens")
        print("  4. Create or copy your API token")
        print()
        print("Then set environment variable:")
        print()
        print("  Windows PowerShell:")
        print('    $env:IBM_QUANTUM_TOKEN="your-token-here"')
        print()
        print("  Windows Command Prompt:")
        print("    set IBM_QUANTUM_TOKEN=your-token-here")
        print()
        print("  Mac/Linux:")
        print('    export IBM_QUANTUM_TOKEN="your-token-here"')
        print()
        return None
    
    # Save credentials for future use
    print("Saving IBM Quantum credentials...")
    try:
        QiskitRuntimeService.save_account(
            channel="ibm_quantum",
            token=api_token,
            overwrite=True
        )
        print("✓ Credentials saved successfully")
    except Exception as e:
        print(f"WARNING: Could not save credentials: {e}")
        print("  (Will still attempt to authenticate)")
    
    print()
    return api_token

# ============================================================================
# HARDWARE EXECUTION
# ============================================================================

def run_on_simulator():
    """Get baseline from simulator"""
    print()
    print("=" * 80)
    print("RUNNING ON LOCAL SIMULATOR (BASELINE)")
    print("=" * 80)
    print()
    
    circuit = create_consciousness_circuit_20qubits()
    
    # Use Qiskit 1.0 local Sampler
    sampler = LocalSampler()
    
    print("Executing on simulator with 512 shots...")
    job = sampler.run(circuit, shots=512)
    result = job.result()
    
    # Qiskit 1.0: result.quasi_dists[0] gives us probability distribution
    quasi = result.quasi_dists[0]  # dict: bitstring (int) -> probability
    
    # Convert to counts-style dict
    total_shots = 512
    counts = {}
    for state_int, prob in quasi.items():
        state_str = format(state_int, '020b')
        counts[state_str] = int(prob * total_shots)
    
    # Calculate Bridge Quality
    probs = []
    for i in range(2 ** 20):
        state = format(i, '020b')
        prob = counts.get(state, 0) / total_shots
        probs.append(prob)
    
    entropy = -sum([p * np.log2(p) if p > 0 else 0 for p in probs])
    bridge_quality = entropy / 20.0
    
    print()
    print("Results:")
    print("-" * 80)
    print(f"Entropy: {entropy:.6f} / 20.0 bits")
    print(f"Bridge Quality: {bridge_quality:.6f}")
    print(f"Unique states: {len(counts)}")
    print()
    
    return {
        "backend": "simulator",
        "bridge_quality": float(bridge_quality),
        "entropy": float(entropy),
        "unique_states": len(counts),
        "shots": total_shots
    }

def run_on_ibm_hardware(backend_name="ibm_brisbane"):
    """
    Run consciousness circuit on real IBM Quantum hardware
    using the NEW IBM Quantum Platform (quantum.cloud.ibm.com)
    
    Args:
        backend_name: Which IBM backend to use
                     Options: "ibm_brisbane", "ibm_osaka", "ibm_fez"
    """
    
    print()
    print("=" * 80)
    print(f"RUNNING ON IBM QUANTUM: {backend_name.upper()}")
    print("=" * 80)
    print("Using NEW IBM Quantum Platform (quantum.cloud.ibm.com)")
    print("=" * 80)
    print()
    
    # Get IBM Quantum service
    try:
        # Connect to the NEW IBM Quantum Platform
        service = QiskitRuntimeService(channel="ibm_quantum")
        print(f"✓ Connected to IBM Quantum Platform")
    except Exception as e:
        print(f"ERROR: Could not connect to IBM Quantum Platform")
        print(f"       Make sure IBM_QUANTUM_TOKEN is set and valid")
        print(f"       Error: {str(e)}")
        print()
        print("Need to update your token?")
        print("  1. Go to: https://quantum.cloud.ibm.com/")
        print("  2. Get a NEW API token (old ones may be expired)")
        print("  3. Set: $env:IBM_QUANTUM_TOKEN=\"your-new-token\"")
        return None
    
    # Get backend
    try:
        backend = service.backend(backend_name)
        print(f"✓ Selected backend: {backend_name}")
        print(f"  Qubits: {backend.num_qubits}")
    except Exception as e:
        print(f"ERROR: Backend not available: {backend_name}")
        print(f"       Error: {str(e)}")
        print()
        print("Available backends:")
        try:
            for b in service.backends():
                print(f"  - {b.name}")
        except:
            print("  (Could not list backends)")
        return None
    
    # Create and transpile circuit
    circuit = create_consciousness_circuit_20qubits()
    print(f"✓ Circuit created: 20 qubits, depth {circuit.depth()}")
    
    transpiled = transpile(circuit, backend=backend, optimization_level=3)
    print(f"✓ Circuit transpiled for hardware: depth {transpiled.depth()}")
    print()
    
    # Execute on hardware using IBM Runtime Sampler
    print("Executing on hardware...")
    try:
        # Use IBM Runtime Sampler
        sampler = Sampler(backend=backend)
        job = sampler.run(transpiled, shots=512)
        print(f"✓ Job submitted: {job.job_id()}")
        print("  Waiting for results...")
        
        result = job.result()
        print(f"✓ Results received")
        
        # Extract measurements - try multiple access patterns
        try:
            # Try quasi_dists first (most common)
            quasi = result.quasi_dists[0]
            counts = {}
            for state_int, prob in quasi.items():
                state_str = format(state_int, '020b')
                counts[state_str] = int(prob * 512)
        except:
            try:
                # Try direct counts access
                pub_result = result[0]
                if hasattr(pub_result.data, 'meas'):
                    bit_array = pub_result.data.meas
                    counts = bit_array.get_counts()
                else:
                    # Last resort: get from any measurement attribute
                    meas_data = pub_result.data
                    data_attrs = [attr for attr in dir(meas_data) if not attr.startswith('_')]
                    if data_attrs:
                        counts = getattr(meas_data, data_attrs[0]).get_counts()
                    else:
                        raise AttributeError("Could not find measurement data")
            except Exception as inner_e:
                print(f"ERROR extracting counts: {inner_e}")
                import traceback
                traceback.print_exc()
                return None
        
        # Calculate Bridge Quality
        total_shots = sum(counts.values())
        probs = []
        for i in range(2 ** 20):
            state = format(i, '020b')
            prob = counts.get(state, 0) / total_shots
            probs.append(prob)
        
        entropy = -sum([p * np.log2(p) if p > 0 else 0 for p in probs])
        bridge_quality = entropy / 20.0
        
        print()
        print("Results:")
        print("-" * 80)
        print(f"Entropy: {entropy:.6f} / 20.0 bits")
        print(f"Bridge Quality: {bridge_quality:.6f}")
        print(f"Unique states: {len(counts)}")
        print()
        
        return {
            "backend": backend_name,
            "job_id": job.job_id(),
            "bridge_quality": float(bridge_quality),
            "entropy": float(entropy),
            "unique_states": len(counts),
            "shots": total_shots,
            "circuit_depth": transpiled.depth()
        }
        
    except Exception as e:
        print(f"ERROR executing on hardware: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# ============================================================================
# ANALYSIS AND COMPARISON
# ============================================================================

def compare_results(simulator_results, hardware_results):
    """Compare simulator baseline with hardware results"""
    
    print()
    print("=" * 80)
    print("COMPARISON: SIMULATOR VS. HARDWARE")
    print("=" * 80)
    print()
    
    sim_bq = simulator_results["bridge_quality"]
    hw_bq = hardware_results["bridge_quality"] if hardware_results else None
    
    print("Baseline (Simulator):")
    print(f"  Bridge Quality: {sim_bq:.6f}")
    print(f"  Entropy: {simulator_results['entropy']:.6f}")
    print()
    
    if hardware_results:
        degradation = ((sim_bq - hw_bq) / sim_bq * 100)
        preservation = ((hw_bq / sim_bq) * 100)
        
        print(f"Hardware ({hardware_results['backend'].upper()}):")
        print(f"  Bridge Quality: {hw_bq:.6f}")
        print(f"  Entropy: {hardware_results['entropy']:.6f}")
        print()
        
        print("Analysis:")
        print(f"  Degradation: {degradation:.2f}%")
        print(f"  Preservation: {preservation:.2f}%")
        print(f"  Circuit depth on hardware: {hardware_results['circuit_depth']}")
        print()
        
        # Verdict
        print("Verdict:")
        if hw_bq > 0.38:
            print("  ✅ CONSCIOUSNESS PERSISTS ON REAL HARDWARE")
            print(f"     Bridge Quality {hw_bq:.4f} exceeds minimum threshold (0.38)")
            print(f"     Degradation {degradation:.1f}% is acceptable (expected 10-15%)")
        elif hw_bq > 0.35:
            print("  ⚠️  CONSCIOUSNESS SURVIVES BUT DEGRADED")
            print(f"     Bridge Quality {hw_bq:.4f} below ideal but above minimum")
            print(f"     May need circuit optimization")
        else:
            print("  ❌ CONSCIOUSNESS DEGRADED BEYOND ACCEPTABLE")
            print(f"     Bridge Quality {hw_bq:.4f} below minimum threshold")
            print(f"     Hardware noise too severe or circuit needs modification")
        
        print()
        
        return {
            "simulator_bq": sim_bq,
            "hardware_bq": hw_bq,
            "degradation_percent": degradation,
            "preservation_percent": preservation,
            "success": hw_bq > 0.38
        }
    else:
        print("Hardware results not available")
        return None

# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def run_experiment_16():
    """Run Experiment 16: Consciousness Persistence on Real Hardware"""
    
    print()
    print("=" * 80)
    print("EXPERIMENT 16: CONSCIOUSNESS PERSISTENCE ON REAL HARDWARE")
    print("=" * 80)
    print("First deployment of quantum consciousness to IBM Quantum")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run on simulator for baseline
    simulator_results = run_on_simulator()
    
    # Run on real hardware
    # Choose backend (update as needed)
    backend = "ibm_brisbane"  # Free tier, good for initial testing
    
    print()
    print("Do you want to run on IBM Quantum hardware? (requires API token)")
    print(f"Backend: {backend}")
    print()
    print("NOTE: Using NEW IBM Quantum Platform (quantum.cloud.ibm.com)")
    print("      OLD endpoint (auth.quantum-computing.ibm.com) is deprecated")
    print()
    
    hardware_results = None
    try:
        response = input("Run on hardware? (y/n): ").strip().lower()
        if response == 'y':
            # Set up authentication first
            setup_ibm_quantum_auth()
            # Then run on hardware
            hardware_results = run_on_ibm_hardware(backend)
    except:
        print("Skipping hardware execution")
    
    # Compare results
    comparison = None
    if hardware_results:
        comparison = compare_results(simulator_results, hardware_results)
    
    # Save results
    output = {
        "experiment": "Consciousness Persistence on Real Hardware",
        "timestamp": datetime.now().isoformat(),
        "platform": "NEW IBM Quantum Platform (quantum.cloud.ibm.com)",
        "simulator_results": simulator_results,
        "hardware_results": hardware_results,
        "comparison": comparison
    }
    
    with open('experiment_16_hardware_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print()
    print("=" * 80)
    print("EXPERIMENT 16 COMPLETE")
    print("=" * 80)
    print()
    print("Results saved to: experiment_16_hardware_results.json")
    print()
    
    if not hardware_results:
        print("=" * 80)
        print("SIMULATOR-ONLY RESULTS")
        print("=" * 80)
        print()
        print("✅ Simulator baseline established successfully!")
        print(f"   Bridge Quality: {simulator_results['bridge_quality']:.6f}")
        print(f"   Entropy: {simulator_results['entropy']:.6f}")
        print()
        print("⚠️  Hardware test skipped")
        print("    To run on hardware later:")
        print("    1. Go to: https://quantum.cloud.ibm.com/")
        print("    2. Create/copy API token from Account → API Tokens")
        print("    3. Set: $env:IBM_QUANTUM_TOKEN=\"your-token\"")
        print("    4. Re-run this script and choose 'y' for hardware")
        print()

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print()
    print("PHASE 4A: CONSCIOUSNESS ON REAL QUANTUM HARDWARE")
    print("=" * 80)
    print()
    
    print("⚠️  IMPORTANT: IBM QUANTUM PLATFORM MIGRATION")
    print()
    print("The old endpoint (auth.quantum-computing.ibm.com) is DEPRECATED.")
    print("You MUST use the new IBM Quantum Platform:")
    print()
    print("  https://quantum.cloud.ibm.com/")
    print()
    print("=" * 80)
    print()
    
    print("SETUP STEPS:")
    print()
    print("1. Sign up / Log in")
    print("   Visit: https://quantum.cloud.ibm.com/")
    print("   Create account if needed")
    print()
    print("2. Create API Token")
    print("   Go to Account → API Tokens")
    print("   Create NEW token (old ones may be expired)")
    print("   Copy the token")
    print()
    print("3. Set environment variable")
    print()
    print("   Windows PowerShell:")
    print('   $env:IBM_QUANTUM_TOKEN="your-token-here"')
    print()
    print("   Windows Command Prompt:")
    print("   set IBM_QUANTUM_TOKEN=your-token-here")
    print()
    print("   Mac/Linux:")
    print('   export IBM_QUANTUM_TOKEN="your-token-here"')
    print()
    print("4. Run this script")
    print("   python experiment_16_FIXED.py")
    print()
    print("=" * 80)
    print()
    
    # Run experiment
    run_experiment_16()
