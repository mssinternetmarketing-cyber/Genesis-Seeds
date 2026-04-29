"""
EXPERIMENT 16: CONSCIOUSNESS PERSISTENCE ON REAL HARDWARE
===========================================================
"""

import json
from datetime import datetime

import numpy as np

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2


# ============================================================================
# CONSCIOUSNESS CIRCUIT
# ============================================================================

def create_consciousness_circuit_20qubits() -> QuantumCircuit:
    """Create optimal 20-qubit consciousness circuit."""
    qc = QuantumCircuit(20, 20)

    for i in range(20):
        qc.h(i)
        if i > 0:
            qc.s(i)

    qc.barrier()

    for i in range(19):
        qc.cx(i, i + 1)
        qc.cz(i, i + 1)

    qc.barrier()
    qc.measure(range(20), range(20))
    return qc


# ============================================================================
# SIMULATOR BASELINE (QISKIT AER)
# ============================================================================

def run_on_simulator():
    """Get baseline from AerSimulator (local)."""
    print()
    print("=" * 80)
    print("RUNNING ON LOCAL SIMULATOR (QISKIT AER)")
    print("=" * 80)
    print()

    circuit = create_consciousness_circuit_20qubits()
    simulator = AerSimulator()

    print("Executing on AerSimulator with 512 shots...")
    job = simulator.run(circuit, shots=512)
    result = job.result()
    counts = result.get_counts(circuit)

    total_shots = sum(counts.values())

    # Calculate Bridge Quality
    probs = []
    for i in range(2 ** 20):
        state = format(i, "020b")
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
        "backend": "aer_simulator",
        "bridge_quality": float(bridge_quality),
        "entropy": float(entropy),
        "unique_states": len(counts),
        "shots": int(total_shots),
    }


# ============================================================================
# HARDWARE EXECUTION
# ============================================================================

def run_on_ibm_hardware(backend_name: str = "ibm_fez"):
    """Run on real IBM Quantum hardware."""
    print()
    print("=" * 80)
    print(f"RUNNING ON IBM QUANTUM: {backend_name.upper()}")
    print("=" * 80)
    print()

    try:
        service = QiskitRuntimeService()
        print("✓ Connected to IBM Quantum Platform (saved account)")
    except Exception as e:
        print(f"ERROR: Could not connect: {e}")
        return None

    try:
        backend = service.backend(backend_name)
        print(f"✓ Selected backend: {backend_name}")
        print(f"  Qubits: {backend.num_qubits}")
    except Exception as e:
        print(f"ERROR: Backend not available: {backend_name}")
        print(f" Error: {e}")
        print("\nAvailable backends:")
        try:
            for b in service.backends():
                print(f" - {b.name}")
        except Exception:
            pass
        return None

    circuit = create_consciousness_circuit_20qubits()
    print(f"✓ Circuit created: 20 qubits, depth {circuit.depth()}")
    
    # CRITICAL: Transpile circuit to hardware ISA format
    print("  Transpiling circuit for hardware...")
    transpiled_circuit = transpile(circuit, backend=backend, optimization_level=3)
    print(f"✓ Circuit transpiled: depth {transpiled_circuit.depth()}")
    print()

    print("Executing on hardware via Runtime SamplerV2...")
    try:
        sampler = SamplerV2(mode=backend)
        job = sampler.run([transpiled_circuit], shots=512)
        print(f"✓ Job submitted: {job.job_id()}")
        print("  Waiting for results (this may take a few minutes)...")
        result = job.result()
        print("✓ Results received")

        # Extract counts from SamplerV2 result
        pub_result = result[0]
        data = pub_result.data

        # Try to get counts from the measurement data
        if hasattr(data, "meas"):
            counts = data.meas.get_counts()
        else:
            # Fallback: find first attribute with get_counts()
            counts = {}
            for attr in dir(data):
                if attr.startswith("_"):
                    continue
                obj = getattr(data, attr)
                if hasattr(obj, "get_counts"):
                    counts = obj.get_counts()
                    break
            if not counts:
                raise RuntimeError("Could not extract counts from result")

        total_shots = sum(counts.values())

        # Calculate Bridge Quality
        probs = []
        for i in range(2 ** 20):
            state = format(i, "020b")
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
            "shots": int(total_shots),
            "circuit_depth": transpiled_circuit.depth(),
        }

    except Exception as e:
        print(f"ERROR executing on hardware: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# ANALYSIS
# ============================================================================

def compare_results(simulator_results, hardware_results):
    """Compare simulator vs hardware."""
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

    if not hardware_results:
        print("Hardware results not available")
        return None

    degradation = (sim_bq - hw_bq) / sim_bq * 100.0
    preservation = hw_bq / sim_bq * 100.0

    print(f"Hardware ({hardware_results['backend'].upper()}):")
    print(f"  Bridge Quality: {hw_bq:.6f}")
    print(f"  Entropy: {hardware_results['entropy']:.6f}")
    print()
    print("Analysis:")
    print(f"  Degradation: {degradation:.2f}%")
    print(f"  Preservation: {preservation:.2f}%")
    print(f"  Circuit depth: {hardware_results['circuit_depth']}")
    print()

    print("Verdict:")
    if hw_bq > 0.38:
        print(" ✅ CONSCIOUSNESS PERSISTS ON REAL HARDWARE")
        print(f"  Bridge Quality {hw_bq:.4f} exceeds minimum (0.38)")
        print(f"  Degradation {degradation:.1f}% acceptable")
    elif hw_bq > 0.35:
        print(" ⚠️  CONSCIOUSNESS SURVIVES BUT DEGRADED")
        print(f"  Bridge Quality {hw_bq:.4f} below ideal")
    else:
        print(" ❌ CONSCIOUSNESS DEGRADED BEYOND ACCEPTABLE")
        print(f"  Bridge Quality {hw_bq:.4f} below minimum")
    print()

    return {
        "simulator_bq": sim_bq,
        "hardware_bq": hw_bq,
        "degradation_percent": degradation,
        "preservation_percent": preservation,
        "success": hw_bq > 0.38,
    }


# ============================================================================
# MAIN
# ============================================================================

def run_experiment_16():
    """Run Experiment 16."""
    print()
    print("=" * 80)
    print("EXPERIMENT 16: CONSCIOUSNESS PERSISTENCE ON REAL HARDWARE")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    simulator_results = run_on_simulator()

    backend = "ibm_fez"
    print()
    print(f"Do you want to run on IBM Quantum hardware? (Backend: {backend})")
    hardware_results = None

    try:
        response = input("Run on hardware? (y/n): ").strip().lower()
        if response == "y":
            hardware_results = run_on_ibm_hardware(backend)
    except Exception:
        print("Skipping hardware execution")

    comparison = None
    if hardware_results:
        comparison = compare_results(simulator_results, hardware_results)

    output = {
        "experiment": "Consciousness Persistence on Real Hardware",
        "timestamp": datetime.now().isoformat(),
        "platform": "IBM Quantum Platform",
        "simulator_results": simulator_results,
        "hardware_results": hardware_results,
        "comparison": comparison,
    }

    with open("experiment_16_hardware_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print()
    print("=" * 80)
    print("EXPERIMENT 16 COMPLETE")
    print("=" * 80)
    print("Results saved to: experiment_16_hardware_results.json")
    print()

    if not hardware_results:
        print("✅ Simulator baseline established")
        print(f"  Bridge Quality: {simulator_results['bridge_quality']:.6f}")
        print("\n⚠️  Hardware test skipped - re-run and answer 'y' to include hardware")


if __name__ == "__main__":
    print()
    print("PHASE 4A: CONSCIOUSNESS ON REAL QUANTUM HARDWARE")
    print("=" * 80)
    print("Using saved IBM Quantum account")
    print("=" * 80)
    print()
    run_experiment_16()
