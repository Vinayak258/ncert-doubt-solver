"""
Retrieval Evaluation Suite

This script tests the retrieval system for:
- Relevance (manual baseline)
- Filter correctness
- Performance (latency)
"""

import sys
import time
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from vector_store.retriever import retrieve


class RetrievalTester:
    """Test suite for retrieval system."""
    
    def __init__(self):
        """Initialize the tester."""
        self.results = []
    
    def test_relevance(self):
        """
        Test if retrieval returns relevant results.
        
        Uses manually curated query-chapter pairs.
        """
        print("\n" + "=" * 80)
        print("TEST 1: RELEVANCE")
        print("=" * 80)
        
        # Test cases: (query, expected_keywords_in_results)
        test_cases = [
            ("photosynthesis", ["photosynthesis", "plant", "chlorophyll", "light"]),
            ("Newton's laws", ["newton", "force", "motion", "law"]),
            ("water cycle", ["water", "evaporation", "condensation", "rain"]),
            ("cell structure", ["cell", "nucleus", "membrane", "cytoplasm"]),
        ]
        
        passed = 0
        total = len(test_cases)
        
        for query, expected_keywords in test_cases:
            results = retrieve(query, top_k=5)
            
            if not results:
                print(f"❌ FAIL: {query} - No results returned")
                continue
            
            # Check if any expected keyword appears in top result
            top_text = results[0]['text'].lower()
            found = any(keyword.lower() in top_text for keyword in expected_keywords)
            
            if found:
                print(f"✓ PASS: {query}")
                print(f"  Top result: {results[0]['chapter']}, Page {results[0]['page']}")
                print(f"  Score: {results[0]['similarity_score']:.3f}")
                passed += 1
            else:
                print(f"❌ FAIL: {query}")
                print(f"  Expected keywords: {expected_keywords}")
                print(f"  Got: {top_text[:100]}...")
        
        accuracy = passed / total if total > 0 else 0
        print(f"\nRelevance Accuracy: {passed}/{total} ({accuracy*100:.1f}%)")
        
        self.results.append({
            'test': 'Relevance',
            'passed': passed,
            'total': total,
            'accuracy': accuracy
        })
        
        return accuracy >= 0.75  # 75% threshold
    
    def test_class_filter(self):
        """Test if class filter works correctly."""
        print("\n" + "=" * 80)
        print("TEST 2: CLASS FILTER")
        print("=" * 80)
        
        test_classes = [6, 8, 10]
        passed = 0
        total = len(test_classes)
        
        for class_num in test_classes:
            results = retrieve(
                "science",
                top_k=10,
                class_filter=class_num
            )
            
            if not results:
                print(f"⚠️  WARNING: No results for class {class_num}")
                continue
            
            # Check if all results match the filter
            all_match = all(r['class'] == class_num for r in results)
            
            if all_match:
                print(f"✓ PASS: Class {class_num} filter - {len(results)} results")
                passed += 1
            else:
                print(f"❌ FAIL: Class {class_num} filter")
                wrong = [r['class'] for r in results if r['class'] != class_num]
                print(f"  Found wrong classes: {set(wrong)}")
        
        accuracy = passed / total if total > 0 else 0
        print(f"\nClass Filter Accuracy: {passed}/{total} ({accuracy*100:.1f}%)")
        
        self.results.append({
            'test': 'Class Filter',
            'passed': passed,
            'total': total,
            'accuracy': accuracy
        })
        
        return accuracy == 1.0
    
    def test_language_filter(self):
        """Test if language filter works correctly."""
        print("\n" + "=" * 80)
        print("TEST 3: LANGUAGE FILTER")
        print("=" * 80)
        
        test_languages = ["English", "Hindi"]
        passed = 0
        total = 0
        
        for language in test_languages:
            results = retrieve(
                "science",
                top_k=10,
                language_filter=language
            )
            
            if not results:
                print(f"⚠️  WARNING: No results for language {language}")
                continue
            
            total += 1
            
            # Check if all results match the filter
            all_match = all(r['language'] == language for r in results)
            
            if all_match:
                print(f"✓ PASS: Language {language} filter - {len(results)} results")
                passed += 1
            else:
                print(f"❌ FAIL: Language {language} filter")
                wrong = [r['language'] for r in results if r['language'] != language]
                print(f"  Found wrong languages: {set(wrong)}")
        
        accuracy = passed / total if total > 0 else 0
        print(f"\nLanguage Filter Accuracy: {passed}/{total} ({accuracy*100:.1f}%)")
        
        self.results.append({
            'test': 'Language Filter',
            'passed': passed,
            'total': total,
            'accuracy': accuracy
        })
        
        return accuracy == 1.0
    
    def test_subject_filter(self):
        """Test if subject filter works correctly."""
        print("\n" + "=" * 80)
        print("TEST 4: SUBJECT FILTER")
        print("=" * 80)
        
        test_subjects = ["Science", "Math", "SST"]
        passed = 0
        total = 0
        
        for subject in test_subjects:
            results = retrieve(
                "chapter",
                top_k=10,
                subject_filter=subject
            )
            
            if not results:
                print(f"⚠️  WARNING: No results for subject {subject}")
                continue
            
            total += 1
            
            # Check if all results match the filter
            all_match = all(r['subject'] == subject for r in results)
            
            if all_match:
                print(f"✓ PASS: Subject {subject} filter - {len(results)} results")
                passed += 1
            else:
                print(f"❌ FAIL: Subject {subject} filter")
                wrong = [r['subject'] for r in results if r['subject'] != subject]
                print(f"  Found wrong subjects: {set(wrong)}")
        
        accuracy = passed / total if total > 0 else 0
        print(f"\nSubject Filter Accuracy: {passed}/{total} ({accuracy*100:.1f}%)")
        
        self.results.append({
            'test': 'Subject Filter',
            'passed': passed,
            'total': total,
            'accuracy': accuracy
        })
        
        return accuracy == 1.0
    
    def test_latency(self):
        """Test retrieval latency."""
        print("\n" + "=" * 80)
        print("TEST 5: LATENCY")
        print("=" * 80)
        
        test_queries = [
            "photosynthesis",
            "Newton's laws",
            "water cycle",
            "cell structure",
            "gravity",
            "electricity",
            "magnetism",
            "chemical reactions",
            "solar system",
            "human body"
        ]
        
        latencies = []
        
        for query in test_queries:
            start = time.time()
            results = retrieve(query, top_k=5)
            elapsed = time.time() - start
            latencies.append(elapsed)
        
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        
        print(f"Average latency: {avg_latency*1000:.2f} ms")
        print(f"Min latency: {min_latency*1000:.2f} ms")
        print(f"Max latency: {max_latency*1000:.2f} ms")
        
        threshold = 1.0  # 1 second
        passed = avg_latency < threshold
        
        if passed:
            print(f"✓ PASS: Average latency < {threshold}s")
        else:
            print(f"❌ FAIL: Average latency >= {threshold}s")
        
        self.results.append({
            'test': 'Latency',
            'avg_latency': avg_latency,
            'max_latency': max_latency,
            'threshold': threshold,
            'passed': passed
        })
        
        return passed
    
    def test_top_k(self):
        """Test if correct number of results are returned."""
        print("\n" + "=" * 80)
        print("TEST 6: TOP-K RESULTS")
        print("=" * 80)
        
        test_cases = [1, 3, 5, 10, 20]
        passed = 0
        total = len(test_cases)
        
        for k in test_cases:
            results = retrieve("science", top_k=k)
            
            if len(results) == k or len(results) < k:  # May have fewer if not enough chunks
                print(f"✓ PASS: top_k={k} returned {len(results)} results")
                passed += 1
            else:
                print(f"❌ FAIL: top_k={k} returned {len(results)} results (expected {k})")
        
        accuracy = passed / total if total > 0 else 0
        print(f"\nTop-K Accuracy: {passed}/{total} ({accuracy*100:.1f}%)")
        
        self.results.append({
            'test': 'Top-K',
            'passed': passed,
            'total': total,
            'accuracy': accuracy
        })
        
        return accuracy == 1.0
    
    def run_all_tests(self):
        """Run all tests and print summary."""
        print("\n" + "=" * 80)
        print("NCERT RETRIEVAL EVALUATION SUITE")
        print("=" * 80)
        
        # Check if index exists
        index_dir = Path("data/vector_store")
        if not index_dir.exists():
            print(f"\n❌ ERROR: Vector index not found at {index_dir}")
            print("\nPlease build the index first:")
            print("  python embeddings/build_index.py")
            sys.exit(1)
        
        # Run tests
        tests = [
            self.test_relevance,
            self.test_class_filter,
            self.test_language_filter,
            self.test_subject_filter,
            self.test_latency,
            self.test_top_k
        ]
        
        passed_tests = 0
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                print(f"\n❌ ERROR in {test.__name__}: {e}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("EVALUATION SUMMARY")
        print("=" * 80)
        
        for result in self.results:
            test_name = result['test']
            if 'accuracy' in result:
                print(f"{test_name}: {result['accuracy']*100:.1f}% "
                      f"({result['passed']}/{result['total']})")
            elif 'avg_latency' in result:
                print(f"{test_name}: {result['avg_latency']*1000:.2f} ms "
                      f"({'PASS' if result['passed'] else 'FAIL'})")
        
        print(f"\nOverall: {passed_tests}/{len(tests)} tests passed")
        
        if passed_tests == len(tests):
            print("\n✓ ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {len(tests) - passed_tests} test(s) failed")
        
        print("=" * 80)


def main():
    """Run evaluation."""
    tester = RetrievalTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
