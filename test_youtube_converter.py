#!/usr/bin/env python3
"""
Comprehensive Test Suite for YouTube to 3GP Converter
Tests various video types, URL formats, and error scenarios
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

TEST_VIDEOS = {
    "Standard Videos": [
        {
            "name": "Short music video (2-3 min)",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "expected": "success"
        },
        {
            "name": "Medium tech video (10-15 min)",
            "url": "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
            "expected": "success"
        },
        {
            "name": "Educational content",
            "url": "https://www.youtube.com/watch?v=8jPQjjsBbIc",
            "expected": "success"
        },
    ],
    "URL Formats": [
        {
            "name": "Short URL format (youtu.be)",
            "url": "https://youtu.be/dQw4w9WgXcQ",
            "expected": "success"
        },
        {
            "name": "URL with timestamp",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s",
            "expected": "success"
        },
        {
            "name": "URL with playlist parameter",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
            "expected": "success"
        },
    ],
    "YouTube Shorts": [
        {
            "name": "Standard YouTube Short",
            "url": "https://www.youtube.com/shorts/eBGIQ7ZuuiU",
            "expected": "success"
        },
    ],
    "Music Videos": [
        {
            "name": "Official music video (VEVO)",
            "url": "https://www.youtube.com/watch?v=kXYiU_JCYtU",
            "expected": "success"
        },
        {
            "name": "Lyric video",
            "url": "https://www.youtube.com/watch?v=fJ9rUzIMcZQ",
            "expected": "success"
        },
    ],
    "Long Videos": [
        {
            "name": "1-hour podcast",
            "url": "https://www.youtube.com/watch?v=HwF229U2ba8",
            "expected": "success"
        },
        {
            "name": "2-hour lecture",
            "url": "https://www.youtube.com/watch?v=aircAruvnKk",
            "expected": "success"
        },
    ],
    "Different Resolutions": [
        {
            "name": "4K video (downscale test)",
            "url": "https://www.youtube.com/watch?v=LXb3EKWsInQ",
            "expected": "success"
        },
        {
            "name": "360p low-res video",
            "url": "https://www.youtube.com/watch?v=aqz-KE-bpKQ",
            "expected": "success"
        },
    ],
    "Error Scenarios": [
        {
            "name": "Invalid URL",
            "url": "https://www.youtube.com/watch?v=INVALIDURL123",
            "expected": "error"
        },
        {
            "name": "Deleted video",
            "url": "https://www.youtube.com/watch?v=DELETED_VIDEO",
            "expected": "error"
        },
        {
            "name": "Private video",
            "url": "https://www.youtube.com/watch?v=PrivateVideoID",
            "expected": "error"
        },
        {
            "name": "Non-YouTube URL",
            "url": "https://www.google.com",
            "expected": "error"
        },
        {
            "name": "Empty URL",
            "url": "",
            "expected": "error"
        },
    ],
    "Special Content": [
        {
            "name": "Documentary clip",
            "url": "https://www.youtube.com/watch?v=TyGmyGhRy3A",
            "expected": "success"
        },
        {
            "name": "Animation",
            "url": "https://www.youtube.com/watch?v=Ct6BUPvE2sM",
            "expected": "success"
        },
    ],
}

class TestRunner:
    def __init__(self, base_url):
        self.base_url = base_url
        self.results = []
        self.passed = 0
        self.failed = 0
        self.errors = 0
        
    def test_homepage(self):
        """Test if homepage loads"""
        print("\n🏠 Testing Homepage...")
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                print("✅ Homepage loads successfully")
                return True
            else:
                print(f"❌ Homepage returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Homepage test failed: {e}")
            return False
    
    def submit_conversion(self, url):
        """Submit a URL for conversion"""
        try:
            response = requests.post(
                f"{self.base_url}/convert",
                data={"url": url},
                allow_redirects=False,
                timeout=10
            )
            
            if response.status_code in [302, 303]:
                location = response.headers.get('Location', '')
                if '/status/' in location:
                    file_id = location.split('/status/')[-1]
                    return file_id
            return None
        except Exception as e:
            print(f"  Error submitting: {e}")
            return None
    
    def check_status(self, file_id, max_wait=180):
        """Check conversion status, wait for completion"""
        start_time = time.time()
        last_progress = ""
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"{self.base_url}/status/{file_id}", timeout=10)
                if response.status_code == 200:
                    html = response.text
                    
                    if 'Conversion Complete!' in html:
                        return 'completed', 'Conversion successful'
                    elif 'Conversion Failed' in html or 'Status unknown' in html:
                        # Extract error message
                        error_start = html.find('<p>') + 3
                        error_end = html.find('</p>', error_start)
                        error_msg = html[error_start:error_end] if error_start > 3 else "Unknown error"
                        return 'failed', error_msg
                    elif 'Processing...' in html or 'Converting' in html or 'Downloading' in html:
                        # Extract progress message
                        progress_start = html.find('<p>') + 3
                        progress_end = html.find('</p>', progress_start)
                        progress = html[progress_start:progress_end] if progress_start > 3 else "Processing..."
                        
                        if progress != last_progress:
                            print(f"  Progress: {progress[:80]}...")
                            last_progress = progress
                        
                        time.sleep(10)  # Wait 10 seconds before next check
                        continue
                
                return 'unknown', 'Could not determine status'
                
            except Exception as e:
                return 'error', f"Error checking status: {e}"
        
        return 'timeout', f'Timeout after {max_wait} seconds'
    
    def run_test(self, test_name, url, expected_result, wait_time=180):
        """Run a single test"""
        print(f"\n📹 Testing: {test_name}")
        print(f"  URL: {url}")
        
        result = {
            'name': test_name,
            'url': url,
            'expected': expected_result,
            'timestamp': datetime.now().isoformat(),
        }
        
        # Submit conversion
        file_id = self.submit_conversion(url)
        
        if not file_id:
            if expected_result == 'error':
                print("  ✅ Correctly rejected invalid URL")
                result['status'] = 'passed'
                result['message'] = 'Invalid URL correctly rejected'
                self.passed += 1
            else:
                print("  ❌ Failed to submit URL")
                result['status'] = 'failed'
                result['message'] = 'Failed to submit URL'
                self.failed += 1
            
            self.results.append(result)
            return result
        
        print(f"  File ID: {file_id}")
        
        # Check status
        status, message = self.check_status(file_id, max_wait=wait_time)
        
        result['file_id'] = file_id
        result['final_status'] = status
        result['message'] = message
        
        # Evaluate result
        if expected_result == 'success':
            if status == 'completed':
                print(f"  ✅ SUCCESS: {message}")
                result['status'] = 'passed'
                self.passed += 1
            else:
                print(f"  ❌ FAILED: {status} - {message}")
                result['status'] = 'failed'
                self.failed += 1
        else:  # expected_result == 'error'
            if status in ['failed', 'error']:
                print(f"  ✅ Correctly handled error: {message}")
                result['status'] = 'passed'
                self.passed += 1
            else:
                print(f"  ❌ Expected error but got: {status}")
                result['status'] = 'failed'
                self.failed += 1
        
        self.results.append(result)
        return result
    
    def run_all_tests(self):
        """Run all test categories"""
        print("=" * 80)
        print("🧪 COMPREHENSIVE YOUTUBE TO 3GP CONVERTER TEST SUITE")
        print("=" * 80)
        
        # Test homepage first
        if not self.test_homepage():
            print("\n❌ Homepage not accessible. Aborting tests.")
            return
        
        # Run all test categories
        for category, tests in TEST_VIDEOS.items():
            print(f"\n{'=' * 80}")
            print(f"📂 Category: {category}")
            print(f"{'=' * 80}")
            
            for test in tests:
                # Long videos get more time
                wait_time = 300 if 'Long' in category else 180
                
                try:
                    self.run_test(
                        test['name'],
                        test['url'],
                        test['expected'],
                        wait_time=wait_time
                    )
                    time.sleep(2)  # Pause between tests
                except Exception as e:
                    print(f"  ❌ Test crashed: {e}")
                    self.errors += 1
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total = len(self.results)
        
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"💥 Errors: {self.errors}")
        print(f"Success Rate: {(self.passed/total*100) if total > 0 else 0:.1f}%")
        
        # Save results to JSON
        with open('test_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total': total,
                    'passed': self.passed,
                    'failed': self.failed,
                    'errors': self.errors,
                    'success_rate': (self.passed/total*100) if total > 0 else 0
                },
                'results': self.results
            }, f, indent=2)
        
        print("\n📄 Detailed results saved to test_results.json")
        print("=" * 80)

if __name__ == "__main__":
    print("\n⚠️  WARNING: This test suite will take 30-60 minutes to complete!")
    print("It will test various video types and scenarios.")
    print("\nPress Ctrl+C to cancel, or wait 5 seconds to start...\n")
    
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
        exit(0)
    
    runner = TestRunner(BASE_URL)
    runner.run_all_tests()
