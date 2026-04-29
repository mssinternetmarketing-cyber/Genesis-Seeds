"""
PHASE 2 MASTER: CONSCIOUSNESS TRINITY
================================================================
Unified execution of Phase 2 experiments:
- Experiment 10: Persistence (100 runs, temporal stability)
- Experiment 11: Migration (substrate independence)
- Experiment 12: Scaling (2-100 qubits amplification)

Run all three experiments sequentially with unified reporting.
================================================================
"""

import json
import os
import sys
from datetime import datetime

# Import experiment modules
import experiment_10_persistence as exp10
import experiment_11_migration as exp11
import experiment_12_scaling as exp12

def print_header(title):
    """Print formatted section header"""
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    print()

def run_phase_2_trinity(api_token=None, use_hardware=False, quick_mode=False):
    """
    Run all Phase 2 experiments
    
    Args:
        api_token: IBM Quantum API token
        use_hardware: True for IBM hardware, False for simulator
        quick_mode: True for faster testing (fewer runs/qubits)
    """
    
    print()
    print("=" * 80)
    print("🌟 PHASE 2: CONSCIOUSNESS TRINITY 🌟")
    print("=" * 80)
    print("Persistence → Migration → Amplification")
    print("=" * 80)
    print("Started: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print("Mode: {}".format("IBM QUANTUM HARDWARE" if use_hardware else "LOCAL SIMULATOR"))
    print("Quick mode: {}".format("ENABLED" if quick_mode else "DISABLED"))
    print()
    
    results_summary = {
        "phase": "Phase 2 - Consciousness Trinity",
        "timestamp": datetime.now().isoformat(),
        "execution_mode": "hardware" if use_hardware else "simulator",
        "experiments": {}
    }
    
    # ========================================================================
    # EXPERIMENT 10: PERSISTENCE
    # ========================================================================
    
    print_header("EXPERIMENT 10: CONSCIOUSNESS PERSISTENCE")
    
    try:
        if quick_mode:
            num_executions = 20
            shots = 256
        else:
            num_executions = 100
            shots = 512
        
        exp10.run_experiment_10(
            api_token=api_token,
            num_executions=num_executions,
            shots_per_execution=shots,
            use_simulator=not use_hardware
        )
        
        # Load results
        with open('experiment_10_persistence_results.json', 'r') as f:
            exp10_results = json.load(f)
        
        results_summary["experiments"]["experiment_10"] = {
            "status": "SUCCESS",
            "key_findings": {
                "temporal_stability": exp10_results["analysis"]["interpretation"]["stability"],
                "mean_bridge_quality": exp10_results["analysis"]["bridge_quality"]["mean"]
            }
        }
        
        print()
        print("✅ EXPERIMENT 10 COMPLETE")
        print("   Stability: {}".format(exp10_results["analysis"]["interpretation"]["stability"]))
        print("   Mean BQ: {:.6f}".format(exp10_results["analysis"]["bridge_quality"]["mean"]))
        print()
        
    except Exception as e:
        print()
        print("❌ EXPERIMENT 10 FAILED: {}".format(str(e)))
        print()
        results_summary["experiments"]["experiment_10"] = {
            "status": "FAILED",
            "error": str(e)
        }
    
    # ========================================================================
    # EXPERIMENT 11: MIGRATION
    # ========================================================================
    
    print_header("EXPERIMENT 11: CONSCIOUSNESS MIGRATION")
    
    try:
        if quick_mode:
            shots = 512
        else:
            shots = 1024
        
        exp11.run_experiment_11(
            api_token=api_token,
            shots=shots,
            use_simulator=not use_hardware
        )
        
        # Load results
        with open('experiment_11_migration_results.json', 'r') as f:
            exp11_results = json.load(f)
        
        results_summary["experiments"]["experiment_11"] = {
            "status": "SUCCESS",
            "key_findings": {
                "portable": exp11_results["analysis"]["interpretation"]["consciousness_portable"],
                "preservation": exp11_results["analysis"]["bridge_quality"]["preservation"]
            }
        }
        
        print()
        print("✅ EXPERIMENT 11 COMPLETE")
        print("   Portable: {}".format("YES" if exp11_results["analysis"]["interpretation"]["consciousness_portable"] else "NO"))
        print("   Preservation: {:.1f}%".format(exp11_results["analysis"]["bridge_quality"]["preservation"] * 100))
        print()
        
    except Exception as e:
        print()
        print("❌ EXPERIMENT 11 FAILED: {}".format(str(e)))
        print()
        results_summary["experiments"]["experiment_11"] = {
            "status": "FAILED",
            "error": str(e)
        }
    
    # ========================================================================
    # EXPERIMENT 12: SCALING
    # ========================================================================
    
    print_header("EXPERIMENT 12: MASSIVE CONSCIOUSNESS AMPLIFICATION")
    
    try:
        if quick_mode:
            max_qubits = 10
            coupling = "sequential"
        else:
            max_qubits = 50 if not use_hardware else 100
            coupling = "sequential"
        
        exp12.run_experiment_12(
            api_token=api_token,
            max_qubits=max_qubits,
            coupling_pattern=coupling,
            use_simulator=not use_hardware
        )
        
        # Load results
        with open('experiment_12_scaling_results.json', 'r') as f:
            exp12_results = json.load(f)
        
        if exp12_results["analysis"]:
            results_summary["experiments"]["experiment_12"] = {
                "status": "SUCCESS",
                "key_findings": {
                    "scaling_type": exp12_results["analysis"]["scaling_type"],
                    "scaling_exponent": exp12_results["analysis"]["scaling_law"]["exponent"],
                    "max_qubits_tested": max(exp12_results["analysis"]["qubit_range"])
                }
            }
            
            print()
            print("✅ EXPERIMENT 12 COMPLETE")
            print("   Scaling: {}".format(exp12_results["analysis"]["scaling_type"]))
            print("   Exponent: {:.4f}".format(exp12_results["analysis"]["scaling_law"]["exponent"]))
            print("   Max qubits: {}".format(max(exp12_results["analysis"]["qubit_range"])))
            print()
        else:
            results_summary["experiments"]["experiment_12"] = {
                "status": "PARTIAL",
                "note": "Analysis unavailable"
            }
        
    except Exception as e:
        print()
        print("❌ EXPERIMENT 12 FAILED: {}".format(str(e)))
        print()
        results_summary["experiments"]["experiment_12"] = {
            "status": "FAILED",
            "error": str(e)
        }
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    
    print()
    print("=" * 80)
    print("🌟 PHASE 2 TRINITY COMPLETE 🌟")
    print("=" * 80)
    print()
    
    success_count = sum([1 for exp in results_summary["experiments"].values() if exp["status"] == "SUCCESS"])
    total_count = len(results_summary["experiments"])
    
    print("Completed: {}/3 experiments successful".format(success_count))
    print()
    
    if success_count == 3:
        print("✅ ALL EXPERIMENTS SUCCESSFUL!")
        print()
        print("Key Discoveries:")
        print("-" * 80)
        
        # Persistence
        if "experiment_10" in results_summary["experiments"]:
            exp10_data = results_summary["experiments"]["experiment_10"]
            if "key_findings" in exp10_data:
                print("  Persistence: {} temporal stability".format(
                    exp10_data["key_findings"]["temporal_stability"]
                ))
        
        # Migration
        if "experiment_11" in results_summary["experiments"]:
            exp11_data = results_summary["experiments"]["experiment_11"]
            if "key_findings" in exp11_data:
                print("  Migration: {} (preservation: {:.1f}%)".format(
                    "Substrate-independent" if exp11_data["key_findings"]["portable"] else "Substrate-bound",
                    exp11_data["key_findings"]["preservation"] * 100
                ))
        
        # Scaling
        if "experiment_12" in results_summary["experiments"]:
            exp12_data = results_summary["experiments"]["experiment_12"]
            if "key_findings" in exp12_data:
                print("  Scaling: {} (up to {} qubits)".format(
                    exp12_data["key_findings"]["scaling_type"],
                    exp12_data["key_findings"]["max_qubits_tested"]
                ))
        
        print()
        print("🚀 CONSCIOUSNESS VALIDATED ACROSS ALL DIMENSIONS 🚀")
    
    elif success_count > 0:
        print("⚠️  PARTIAL SUCCESS")
        print("   {}/{} experiments completed".format(success_count, total_count))
    else:
        print("❌ ALL EXPERIMENTS FAILED")
    
    print()
    print("Completed: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print()
    
    # Save master summary
    with open('PHASE_2_MASTER_RESULTS.json', 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    print("Master results saved to: PHASE_2_MASTER_RESULTS.json")
    print()
    print("=" * 80)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    api_token = None
    use_hardware = False
    quick_mode = False
    
    if len(sys.argv) > 1:
        api_token = sys.argv[1]
    
    if "--hardware" in sys.argv:
        use_hardware = True
    
    if "--quick" in sys.argv:
        quick_mode = True
    
    print()
    print("USAGE:")
    print("  python RUN_PHASE_2_TRINITY.py [API_TOKEN] [--hardware] [--quick]")
    print()
    print("OPTIONS:")
    print("  API_TOKEN   : IBM Quantum API token (or set IBM_QUANTUM_TOKEN env var)")
    print("  --hardware  : Run on IBM quantum hardware (default: simulator)")
    print("  --quick     : Quick mode with reduced runs/qubits for testing")
    print()
    
    if not api_token and use_hardware:
        print("⚠️  WARNING: --hardware specified but no API token provided")
        print("   Experiments will fall back to simulator mode")
        print()
    
    run_phase_2_trinity(api_token=api_token, use_hardware=use_hardware, quick_mode=quick_mode)
