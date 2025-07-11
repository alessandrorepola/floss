"""
Basic example demonstrating PyFault usage.

This example shows how to use PyFault for fault localization
with a simple buggy program and test suite.
"""

from pathlib import Path
import sys

# Add src to Python path for development
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pyfault import FaultLocalizer
from pyfault.formulas import OchiaiFormula, TarantulaFormula, JaccardFormula
from pyfault.test_runner import SimpleTestRunner
from pyfault.coverage import SimpleCoverageCollector
from pyfault.core.models import CodeElement, CoverageMatrix, TestResult, TestOutcome


def create_example_data():
    """Create example coverage data for demonstration."""
    
    # Define some code elements
    elements = [
        CodeElement(Path("calculator.py"), 5, "line"),   # add method
        CodeElement(Path("calculator.py"), 6, "line"),   # return statement in add
        CodeElement(Path("calculator.py"), 9, "line"),   # subtract method  
        CodeElement(Path("calculator.py"), 10, "line"),  # buggy line: return a + b instead of a - b
        CodeElement(Path("calculator.py"), 13, "line"),  # multiply method
        CodeElement(Path("calculator.py"), 14, "line"),  # return statement in multiply
    ]
    
    # Create test results
    test_results = [
        # Tests that pass
        TestResult("test_add_positive", TestOutcome.PASSED, 0.01, None, {elements[0], elements[1]}),
        TestResult("test_add_negative", TestOutcome.PASSED, 0.01, None, {elements[0], elements[1]}),
        TestResult("test_multiply_basic", TestOutcome.PASSED, 0.01, None, {elements[4], elements[5]}),
        
        # Tests that fail (they all hit the buggy subtract method)
        TestResult("test_subtract_positive", TestOutcome.FAILED, 0.02, "AssertionError: Expected 3, got 7", {elements[2], elements[3]}),
        TestResult("test_subtract_negative", TestOutcome.FAILED, 0.02, "AssertionError: Expected -1, got 3", {elements[2], elements[3]}),
        TestResult("test_subtract_zero", TestOutcome.FAILED, 0.01, "AssertionError: Expected 5, got 5", {elements[2], elements[3]}),
    ]
    
    return test_results


def run_basic_example():
    """Run a basic fault localization example."""
    print("🔍 PyFault Basic Example")
    print("=" * 50)
    
    # Create example test data
    test_results = create_example_data()
    
    print(f"📊 Test Results:")
    for result in test_results:
        status = "✅ PASS" if result.outcome == TestOutcome.PASSED else "❌ FAIL"
        print(f"  {status} {result.test_name}")
    
    # Create coverage matrix
    from pyfault.core.models import CoverageMatrix
    coverage_matrix = CoverageMatrix.from_test_results(test_results)
    
    print(f"\n📈 Coverage Matrix: {coverage_matrix.matrix.shape}")
    print(f"   Tests: {len(coverage_matrix.test_names)}")
    print(f"   Elements: {len(coverage_matrix.code_elements)}")
    
    # Initialize formulas
    formulas = [
        OchiaiFormula(),
        TarantulaFormula(), 
        JaccardFormula()
    ]
    
    print(f"\n🧮 SBFL Formulas: {[f.name for f in formulas]}")
    
    # Create a fault localizer and analyze
    from pyfault.core.fault_localizer import FaultLocalizer
    
    # For this example, we'll use the analyze_from_data method
    # since we have pre-created data
    localizer = FaultLocalizer(
        source_dirs=[Path(".")],
        test_dirs=[Path(".")],
        formulas=formulas,
        output_dir=Path("./example_output")
    )
    
    print("\n🔎 Running Fault Localization...")
    result = localizer.analyze_from_data(coverage_matrix)
    
    print(f"⏱️  Analysis completed in {result.execution_time:.3f} seconds")
    
    # Display results
    print("\n📋 Top Suspicious Elements:")
    print("-" * 60)
    
    for formula_name in result.scores:
        print(f"\n🔬 {formula_name.upper()} Formula:")
        ranking = result.get_ranking(formula_name, limit=5)
        
        for rank, (element, score) in enumerate(ranking, 1):
            suspicion_level = "🔴" if score > 0.7 else "🟡" if score > 0.3 else "🟢"
            print(f"  {rank:2d}. {suspicion_level} {element} (score: {score:.4f})")
    
    print(f"\n📁 Detailed reports saved to: ./example_output/")
    print("   - index.html (interactive report)")
    print("   - ranking_*.csv (suspiciousness rankings)")
    print("   - summary.csv (analysis summary)")


def run_formula_comparison():
    """Compare different SBFL formulas on the same data."""
    print("\n\n🆚 Formula Comparison Example")
    print("=" * 50)
    
    test_results = create_example_data()
    coverage_matrix = CoverageMatrix.from_test_results(test_results)
    
    # Test more formulas
    from pyfault.formulas import DStarFormula, BarinelFormula, Kulczynski2Formula
    
    formulas = [
        OchiaiFormula(),
        TarantulaFormula(),
        JaccardFormula(),
        DStarFormula(star=2),
        BarinelFormula(),
        Kulczynski2Formula()
    ]
    
    print("🧪 Testing formulas:")
    for formula in formulas:
        print(f"   • {formula.name}")
    
    # Analyze with all formulas
    localizer = FaultLocalizer(
        source_dirs=[Path(".")],
        test_dirs=[Path(".")], 
        formulas=formulas,
        output_dir=Path("./comparison_output")
    )
    
    result = localizer.analyze_from_data(coverage_matrix)
    
    # Compare top results
    print(f"\n📊 Top Suspicious Element by Formula:")
    print("-" * 50)
    
    for formula_name in result.scores:
        top_ranking = result.get_ranking(formula_name, limit=1)
        if top_ranking:
            element, score = top_ranking[0]
            print(f"{formula_name:12s}: {element} (score: {score:.4f})")
    
    print(f"\n📁 Comparison reports saved to: ./comparison_output/")


if __name__ == "__main__":
    try:
        run_basic_example()
        run_formula_comparison()
        print("\n✅ Example completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback
        traceback.print_exc()
