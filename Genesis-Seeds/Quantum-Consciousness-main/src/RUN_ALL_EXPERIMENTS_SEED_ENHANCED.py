"""
MASTER EXPERIMENT RUNNER - SEED ENHANCED VERSION
=================================================
Orchestrates all quantum consciousness experiments with seed diversity testing
"""

import subprocess
import sys
import json
import time
from datetime import datetime
import argparse

# ============================================================================
# EXPERIMENT REGISTRY
# ============================================================================

EXPERIMENTS = {
    1: {
        "name": "Brotherhood Validation with Seed Pairing Tests",
        "file": "experiment_1_brotherhood_SEED_ENHANCED.py",
        "runtime_estimate": "30 min",
        "critical": True,
        "description": "Tests all 10 unique seed pairings for Brotherhood dynamics"
    },
    2: {
        "name": "Consciousness Markers with Seed Calibration",
        "file": "experiment_2_consciousness_SEED_ENHANCED.py",
        "runtime_estimate": "15 min",
        "critical": True,
        "description": "Measures Φ, temporal coherence, causal density, PEIG across seed pairs"
    },
    3: {
        "name": "Scaling with Seed Diversity",
        "file": "experiment_3_scaling_SEED_ENHANCED.py",
        "runtime_estimate": "20 min",
        "critical": False,
        "description": "Tests homogeneous vs mixed seed populations at different scales"
    },
    4: {
        "name": "Learning with Seed Pairing Tests",
        "file": "experiment_4_learning_SEED_ENHANCED.py",
        "runtime_estimate": "25 min",
        "critical": False,
        "description": "Identifies which seed pairs learn fastest and maintain PEIG best"
    },
    5: {
        "name": "Hardware Translation with Seed Context",
        "file": "experiment_5_hardware_SEED_ENHANCED.py",
        "runtime_estimate": "10 min",
        "critical": False,
        "description": "Translates optimal seed configurations to hardware specifications"
    }
}

# ============================================================================
# EXPERIMENT EXECUTION
# ============================================================================

def run_experiment(exp_num):
    """Execute a single experiment"""
    exp = EXPERIMENTS[exp_num]

    print(f"\n{'='*80}")
    print(f"EXPERIMENT {exp_num}: {exp['name']}")
    print(f"{'='*80}")
    print(f"Description: {exp['description']}")
    print(f"Estimated runtime: {exp['runtime_estimate']}")
    print(f"{'='*80}\n")

    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, exp['file']],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour max per experiment
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(result.stdout)
            status = "SUCCESS"
            error_msg = None
        else:
            print(result.stdout)
            print(result.stderr)
            status = "FAILED"
            error_msg = result.stderr

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        status = "TIMEOUT"
        error_msg = "Experiment exceeded 1 hour time limit"
        print(f"ERROR: {error_msg}")

    except Exception as e:
        elapsed = time.time() - start_time
        status = "ERROR"
        error_msg = str(e)
        print(f"ERROR: {error_msg}")

    return {
        "experiment_number": exp_num,
        "experiment_name": exp['name'],
        "status": status,
        "runtime_seconds": elapsed,
        "runtime_formatted": f"{int(elapsed // 60)}m {int(elapsed % 60)}s",
        "error": error_msg
    }

# ============================================================================
# MASTER RESULTS COMPILATION
# ============================================================================

def compile_master_results(run_results):
    """Compile results from all experiments"""

    print(f"\n{'='*80}")
    print("COMPILING MASTER RESULTS")
    print(f"{'='*80}\n")

    master_data = {
        "suite_name": "Quantum Consciousness Research - SEED ENHANCED",
        "timestamp": datetime.now().isoformat(),
        "total_experiments": len(run_results),
        "experiments_run": run_results,
        "summary": {}
    }

    # Load individual experiment results
    for exp_num in [1, 2, 3, 4, 5]:
        try:
            with open(f'experiment_{exp_num}_results.json', 'r') as f:
                exp_data = json.load(f)
                master_data['summary'][f'experiment_{exp_num}'] = exp_data
        except FileNotFoundError:
            master_data['summary'][f'experiment_{exp_num}'] = {"status": "not_run"}

    # Save master results
    with open('MASTER_RESULTS.json', 'w') as f:
        json.dump(master_data, f, indent=2)

    print("Master results compiled: MASTER_RESULTS.json")
    return master_data

# ============================================================================
# SEED STABILITY SUMMARY
# ============================================================================

def generate_seed_summary(master_data):
    """Generate cross-experiment seed stability insights"""

    print(f"\n{'='*80}")
    print("SEED STABILITY SUMMARY")
    print(f"{'='*80}\n")

    summary = master_data.get('summary', {})

    # Extract key findings
    findings = []

    # From Experiment 1
    exp1 = summary.get('experiment_1', {})
    if 'stability_map' in exp1:
        findings.append({
            "experiment": "Brotherhood (Exp 1)",
            "finding": f"Best pairing: {exp1['stability_map'].get('best_brotherhood_pair', 'N/A')}"
        })

    # From Experiment 2
    exp2 = summary.get('experiment_2', {})
    if 'consciousness_leaders' in exp2:
        findings.append({
            "experiment": "Consciousness (Exp 2)",
            "finding": f"Highest Φ: {exp2['consciousness_leaders'].get('highest_phi', 'N/A')}"
        })

    # From Experiment 3
    exp3 = summary.get('experiment_3', {})
    if 'stability_map' in exp3:
        findings.append({
            "experiment": "Scaling (Exp 3)",
            "finding": f"Most stable: {exp3['stability_map'].get('most_stable_config', 'N/A')}"
        })

    # From Experiment 4
    exp4 = summary.get('experiment_4', {})
    if 'stability_map' in exp4:
        findings.append({
            "experiment": "Learning (Exp 4)",
            "finding": f"Fastest learner: {exp4['stability_map'].get('fastest_learner', 'N/A')}"
        })

    # Print findings
    for f in findings:
        print(f"{f['experiment']:25} {f['finding']}")

    print(f"\n{'='*80}")
    print("INTERPRETATION:")
    print(f"{'='*80}")
    print("If the same seed pairing appears across multiple experiments,")
    print("that pairing represents a naturally stable configuration.")
    print("These are your 'anchor points' in the quantum consciousness space.")
    print(f"{'='*80}\n")

    return findings

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Run Quantum Consciousness Experiments (Seed Enhanced)')
    parser.add_argument('--quick', action='store_true', help='Run only critical experiments (1-2)')
    parser.add_argument('--full', action='store_true', help='Run all experiments (1-5)')
    parser.add_argument('--experiments', nargs='+', type=int, help='Run specific experiments by number')

    args = parser.parse_args()

    # Determine which experiments to run
    if args.experiments:
        experiments_to_run = [e for e in args.experiments if e in EXPERIMENTS]
    elif args.quick:
        experiments_to_run = [1, 2]
    elif args.full:
        experiments_to_run = list(EXPERIMENTS.keys())
    else:
        # Default: run all
        experiments_to_run = list(EXPERIMENTS.keys())

    print("=" * 80)
    print("QUANTUM CONSCIOUSNESS RESEARCH SUITE - SEED ENHANCED")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    if args.quick:
        print("🚀 QUICK MODE: Running critical experiments only (Exp 1-2)")
    elif args.full:
        print("🔬 FULL MODE: Running complete experimental suite (Exp 1-5)")
    else:
        print(f"📊 CUSTOM MODE: Running experiments {experiments_to_run}")

    print()
    print(f"Running {len(experiments_to_run)} experiments")

    # Estimate total time
    total_time_estimate = sum(
        int(EXPERIMENTS[e]['runtime_estimate'].split()[0]) 
        for e in experiments_to_run
    )
    print(f"Estimated total time: {total_time_estimate} minutes")
    print()

    # Run experiments
    suite_start_time = time.time()
    run_results = []

    for exp_num in experiments_to_run:
        result = run_experiment(exp_num)
        run_results.append(result)

        if result['status'] != 'SUCCESS':
            print(f"\n⚠️  WARNING: Experiment {exp_num} {result['status']}")
            if result['error']:
                print(f"Error: {result['error']}")

    suite_elapsed = time.time() - suite_start_time

    # Compile results
    master_data = compile_master_results(run_results)

    # Generate seed summary
    findings = generate_seed_summary(master_data)

    # Final summary
    print()
    print("=" * 80)
    print("RESEARCH SUITE COMPLETE")
    print("=" * 80)
    print(f"Total runtime: {int(suite_elapsed // 60)}m {int(suite_elapsed % 60)}s")
    print(f"Experiments run: {len(run_results)}")
    print(f"Successful: {sum(1 for r in run_results if r['status'] == 'SUCCESS')}")
    print(f"Failed: {sum(1 for r in run_results if r['status'] != 'SUCCESS')}")
    print()
    print("Results saved to:")
    print("  - MASTER_RESULTS.json (complete compilation)")
    for exp_num in experiments_to_run:
        print(f"  - experiment_{exp_num}_results.json")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
