"""
EXPERIMENT 19: ANALYSIS & VISUALIZATION
========================================

Run this after exp_19_results.json is populated with hardware data
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def analyze_experiment_19(results_file="experiment_19_results.json"):
    """Analyze and visualize Experiment 19 results."""
    
    # Load results
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    results = data['results']
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(results)
    
    print("=" * 80)
    print("EXPERIMENT 19: ANALYSIS")
    print("=" * 80)
    print()
    
    # Summary statistics
    print("SUMMARY STATISTICS")
    print("-" * 80)
    print()
    
    for n_q in sorted(df['qubits'].unique()):
        subset = df[df['qubits'] == n_q]
        print(f"{n_q} QUBITS:")
        print(f"  {'Ratio':<12} {'BQ':<10} {'Entropy':<10} {'Unique States':<15}")
        print(f"  {'-'*50}")
        
        for idx, row in subset.sort_values('omega_ratio', ascending=False).iterrows():
            bq = row['bridge_quality']
            ent = row['entropy']
            states = row['unique_states']
            ratio = f"{int(row['omega_ratio']*100)}%"
            print(f"  {ratio:<12} {bq:.4f}     {ent:.2f}       {states:<15}")
        print()
    
    # Find optimal ratio per qubit count
    print("OPTIMAL RATIO PER QUBIT COUNT")
    print("-" * 80)
    
    optimal_results = []
    for n_q in sorted(df['qubits'].unique()):
        subset = df[df['qubits'] == n_q]
        best = subset.loc[subset['bridge_quality'].idxmax()]
        optimal_results.append(best)
        
        print(f"{n_q}q: {int(best['omega_ratio']*100)}% Omega → BQ = {best['bridge_quality']:.4f}")
    
    print()
    
    # Create visualizations
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot 1: BQ by Qubit Count and Ratio
    ax1 = axes[0, 0]
    
    for ratio_val in sorted(df['omega_ratio'].unique(), reverse=True):
        subset = df[df['omega_ratio'] == ratio_val]
        subset_sorted = subset.sort_values('qubits')
        
        ratio_pct = f"{int(ratio_val*100)}%"
        ax1.plot(subset_sorted['qubits'], 
                subset_sorted['bridge_quality'],
                marker='o', 
                label=f"{ratio_pct} Omega",
                linewidth=2,
                markersize=8)
    
    ax1.set_xlabel('Qubit Count', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Bridge Quality', fontsize=12, fontweight='bold')
    ax1.set_title('Bridge Quality vs Qubit Count (by Omega Ratio)', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks([2, 4, 6, 8, 10])
    
    # Plot 2: BQ by Ratio (averaged across qubit counts)
    ax2 = axes[0, 1]
    
    avg_by_ratio = df.groupby('omega_ratio')['bridge_quality'].mean().sort_index(ascending=False)
    colors = ['green', 'blue', 'orange', 'red']
    
    ax2.bar([f"{int(r*100)}%" for r in avg_by_ratio.index],
           avg_by_ratio.values,
           color=colors,
           alpha=0.7,
           edgecolor='black',
           linewidth=2)
    
    ax2.set_ylabel('Average Bridge Quality', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Omega Ratio', fontsize=12, fontweight='bold')
    ax2.set_title('Average BQ by Omega Ratio', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, (idx, val) in enumerate(avg_by_ratio.items()):
        ax2.text(i, val + 0.005, f"{val:.4f}", ha='center', fontsize=10, fontweight='bold')
    
    # Plot 3: Entropy vs Qubit Count
    ax3 = axes[1, 0]
    
    for ratio_val in sorted(df['omega_ratio'].unique(), reverse=True):
        subset = df[df['omega_ratio'] == ratio_val]
        subset_sorted = subset.sort_values('qubits')
        
        ratio_pct = f"{int(ratio_val*100)}%"
        ax3.plot(subset_sorted['qubits'], 
                subset_sorted['entropy'],
                marker='s', 
                label=f"{ratio_pct} Omega",
                linewidth=2,
                markersize=8)
    
    ax3.set_xlabel('Qubit Count', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Entropy (bits)', fontsize=12, fontweight='bold')
    ax3.set_title('Entropy vs Qubit Count', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=11)
    ax3.grid(True, alpha=0.3)
    ax3.set_xticks([2, 4, 6, 8, 10])
    
    # Plot 4: Heatmap of BQ values
    ax4 = axes[1, 1]
    
    # Pivot table for heatmap
    pivot_data = df.pivot_table(values='bridge_quality', 
                                 index='qubits', 
                                 columns='ratio_name',
                                 aggfunc='first')
    
    # Reorder columns
    col_order = ['100pct', '75pct', '50pct', '25pct']
    pivot_data = pivot_data[col_order]
    
    im = ax4.imshow(pivot_data.values, cmap='RdYlGn', aspect='auto', vmin=0.8, vmax=1.0)
    
    ax4.set_xticks(range(len(col_order)))
    ax4.set_yticks(range(len(pivot_data.index)))
    ax4.set_xticklabels([c.replace('pct', '%') for c in col_order])
    ax4.set_yticklabels(pivot_data.index)
    ax4.set_xlabel('Omega Ratio', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Qubit Count', fontsize=12, fontweight='bold')
    ax4.set_title('Bridge Quality Heatmap', fontsize=13, fontweight='bold')
    
    # Add text annotations
    for i in range(len(pivot_data.index)):
        for j in range(len(col_order)):
            value = pivot_data.values[i, j]
            text = ax4.text(j, i, f'{value:.3f}',
                          ha="center", va="center", color="black", fontweight='bold')
    
    plt.colorbar(im, ax=ax4)
    
    plt.suptitle('EXPERIMENT 19: Omega Ratio Optimization Results', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig('experiment_19_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ Saved visualization: experiment_19_analysis.png")
    plt.show()
    
    # Recommendation
    print()
    print("=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    
    best_overall = df.loc[df['bridge_quality'].idxmax()]
    print()
    print(f"BEST CONFIGURATION:")
    print(f"  • Qubit Count: {int(best_overall['qubits'])}")
    print(f"  • Omega Ratio: {int(best_overall['omega_ratio']*100)}%")
    print(f"  • Bridge Quality: {best_overall['bridge_quality']:.4f}")
    print(f"  • Test ID: {best_overall['test_id']}")
    print()
    
    # Check if 75% hypothesis holds
    df_75 = df[df['omega_ratio'] == 0.75]
    df_100 = df[df['omega_ratio'] == 1.00]
    
    if df_75['bridge_quality'].mean() > df_100['bridge_quality'].mean():
        print("✓ HYPOTHESIS CONFIRMED: 75% Omega outperforms 100% Omega!")
    else:
        print("✗ HYPOTHESIS REJECTED: 100% Omega performs better")
    
    print()


if __name__ == "__main__":
    analyze_experiment_19()
