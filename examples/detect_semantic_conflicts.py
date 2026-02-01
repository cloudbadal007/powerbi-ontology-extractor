"""
Example: Detect Semantic Conflicts

This example demonstrates analyzing multiple Power BI dashboards to:
1. Load multiple .pbix files
2. Extract semantic models
3. Run conflict detection
4. Display conflicts
5. Calculate semantic debt ($600K in this example)
6. Suggest canonical definition
7. Generate consolidation report

This demonstrates the "20 million dashboards with conflicting definitions" problem.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from powerbi_ontology import PowerBIExtractor, SemanticAnalyzer


def main():
    """Main example workflow."""
    print("=" * 80)
    print("Semantic Conflict Detection Example")
    print("=" * 80)
    print()
    print("Scenario: Organization has 5 dashboards defining 'Customer' differently")
    print()
    
    # Step 1: Load all 5 .pbix files
    print("Step 1: Loading Power BI dashboards...")
    pbix_files = [
        "sample_pbix/Finance_Dashboard.pbix",
        "sample_pbix/Sales_Dashboard.pbix",
        "sample_pbix/Operations_Dashboard.pbix",
        "sample_pbix/Customer_Service_Dashboard.pbix",
        "sample_pbix/Marketing_Dashboard.pbix"
    ]
    
    semantic_models = []
    for pbix_file in pbix_files:
        if Path(pbix_file).exists():
            print(f"  Loading: {pbix_file}")
            extractor = PowerBIExtractor(pbix_file)
            model = extractor.extract()
            semantic_models.append(model)
        else:
            print(f"  ⚠️  Note: {pbix_file} not found (demonstration mode)")
    
    if not semantic_models:
        print("\n  ⚠️  No .pbix files found. This is a demonstration.")
        print("  In production, this would analyze actual Power BI dashboards.")
        print()
        return
    
    print(f"  ✓ Loaded {len(semantic_models)} semantic models")
    print()
    
    # Step 2: Run conflict detection
    print("Step 2: Detecting semantic conflicts...")
    analyzer = SemanticAnalyzer(semantic_models)
    conflicts = analyzer.detect_conflicts()
    
    print(f"  ✓ Found {len(conflicts)} conflicts")
    print()
    
    # Step 3: Display conflicts
    print("Step 3: Conflict Details")
    print("-" * 80)
    for i, conflict in enumerate(conflicts[:5], 1):  # Show first 5
        print(f"\nConflict {i}: {conflict.concept}")
        print(f"  Severity: {conflict.severity}")
        print(f"  {conflict.dashboard1}:")
        print(f"    {conflict.definition1[:100]}...")
        print(f"  {conflict.dashboard2}:")
        print(f"    {conflict.definition2[:100]}...")
        print(f"  Description: {conflict.description}")
    
    if len(conflicts) > 5:
        print(f"\n  ... and {len(conflicts) - 5} more conflicts")
    print()
    
    # Step 4: Calculate semantic debt
    print("Step 4: Calculating semantic debt...")
    debt_report = analyzer.calculate_semantic_debt()
    
    print(f"  Total Conflicts: {debt_report.total_conflicts}")
    print(f"  Total Duplications: {debt_report.total_duplications}")
    print(f"  Cost per Conflict: ${debt_report.cost_per_conflict:,.0f}")
    print(f"  Total Semantic Debt: ${debt_report.total_cost:,.0f}")
    print()
    print(f"  💰 {debt_report.message}")
    print()
    
    # Step 5: Suggest canonical definitions
    print("Step 5: Suggesting canonical definitions...")
    canonical_defs = analyzer.suggest_canonical_definitions()
    
    print(f"  ✓ Suggested {len(canonical_defs)} canonical definitions")
    print()
    for canon in canonical_defs[:3]:  # Show first 3
        print(f"  Concept: {canon.name}")
        print(f"    Confidence: {canon.confidence:.0%}")
        print(f"    Dashboards using: {len(canon.dashboards_using)}")
        print(f"    Alternative definitions: {len(canon.alternative_definitions)}")
        print()
    
    # Step 6: Generate consolidation report
    print("Step 6: Generating consolidation report...")
    report_path = "output/semantic_analysis.html"
    Path("output").mkdir(exist_ok=True)
    analyzer.generate_consolidation_report(report_path)
    print(f"  ✓ Report saved to: {report_path}")
    print()
    
    print("=" * 80)
    print("✅ Analysis Complete!")
    print()
    print("Key Findings:")
    print(f"  • {len(conflicts)} semantic conflicts detected")
    print(f"  • ${debt_report.total_cost:,.0f} estimated cost to reconcile")
    print(f"  • {len(canonical_defs)} canonical definitions suggested")
    print()
    print("This demonstrates the 'semantic debt' problem from 'The Power BI Paradox' article.")
    print("=" * 80)


if __name__ == "__main__":
    main()
