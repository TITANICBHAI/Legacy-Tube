#!/usr/bin/env python3
"""
Live Functional Test - Real Conversions
Tests actual video conversions on localhost
"""

import requests
import time
import os
import subprocess

BASE_URL = "http://localhost:5000"

def test_conversion(name, url, expected_status='success', max_wait=120):
    """Test a real conversion"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"URL: {url}")
    print('='*60)
    
    # Submit conversion
    print("📤 Submitting conversion...")
    try:
        response = requests.post(
            f"{BASE_URL}/convert",
            data={"url": url},
            allow_redirects=False,
            timeout=10
        )
        
        if response.status_code not in [302, 303]:
            print(f"❌ FAILED: Got status {response.status_code}")
            return False
            
        location = response.headers.get('Location', '')
        if '/status/' not in location:
            print(f"❌ FAILED: No redirect to status page")
            return False
            
        file_id = location.split('/status/')[-1]
        print(f"✅ Submitted! File ID: {file_id}")
        
    except Exception as e:
        print(f"❌ FAILED to submit: {e}")
        return False
    
    # Monitor status
    print("\n📊 Monitoring conversion status...")
    start_time = time.time()
    last_status = ""
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{BASE_URL}/status/{file_id}", timeout=10)
            html = response.text
            
            # Check for completion
            if 'Conversion Complete!' in html:
                elapsed = time.time() - start_time
                print(f"\n✅ SUCCESS! Completed in {elapsed:.1f} seconds")
                
                # Try to get file info
                try:
                    file_path = f"/tmp/downloads/{file_id}.3gp"
                    if os.path.exists(file_path):
                        size = os.path.getsize(file_path)
                        print(f"📁 File size: {size/1024/1024:.2f} MB")
                        
                        # Check video properties with ffprobe
                        result = subprocess.run([
                            'ffprobe', '-v', 'error',
                            '-select_streams', 'v:0',
                            '-show_entries', 'stream=width,height,codec_name',
                            '-of', 'csv=p=0',
                            file_path
                        ], capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            info = result.stdout.strip()
                            print(f"🎥 Video info: {info}")
                            
                            # Verify it's 176x144
                            if '176' in info and '144' in info:
                                print("✅ Resolution correct: 176x144")
                            else:
                                print(f"⚠️  Resolution unexpected: {info}")
                        
                except Exception as e:
                    print(f"⚠️  Could not read file: {e}")
                
                return True
            
            # Check for failure
            elif 'Conversion Failed' in html or 'Status unknown' in html:
                # Extract error message
                if 'Error:' in html:
                    error_start = html.find('Error:')
                    error_end = html.find('</p>', error_start)
                    error = html[error_start:error_end] if error_start > 0 else "Unknown error"
                    print(f"\n❌ FAILED: {error[:100]}")
                else:
                    print(f"\n❌ FAILED: Conversion failed")
                
                if expected_status == 'error':
                    print("✅ Expected failure - test passed!")
                    return True
                return False
            
            # Still processing
            elif 'Processing...' in html or 'Converting' in html or 'Downloading' in html:
                # Extract progress
                if '<p>' in html:
                    progress_start = html.find('<p>') + 3
                    progress_end = html.find('</p>', progress_start)
                    progress = html[progress_start:progress_end] if progress_start > 3 else "Processing..."
                    
                    if progress != last_status:
                        elapsed = time.time() - start_time
                        print(f"  [{elapsed:.0f}s] {progress[:70]}...")
                        last_status = progress
                
                time.sleep(5)  # Check every 5 seconds
                continue
        
        except Exception as e:
            print(f"⚠️  Error checking status: {e}")
            time.sleep(5)
            continue
    
    print(f"\n⏱️  TIMEOUT after {max_wait} seconds")
    return False

# Run tests
print("="*60)
print("🧪 LIVE FUNCTIONAL TESTING")
print("="*60)

tests = [
    {
        'name': 'Short Music Video (2-3 min)',
        'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'max_wait': 180
    },
    {
        'name': 'Invalid URL',
        'url': 'https://www.youtube.com/watch?v=INVALID_URL_TEST',
        'expected_status': 'error',
        'max_wait': 60
    },
    {
        'name': 'Short URL Format (youtu.be)',
        'url': 'https://youtu.be/dQw4w9WgXcQ',
        'max_wait': 180
    },
    {
        'name': 'Very Short Video (30 sec)',
        'url': 'https://www.youtube.com/watch?v=jNQXAC9IVRw',
        'max_wait': 120
    },
]

passed = 0
failed = 0

for test in tests:
    result = test_conversion(
        test['name'],
        test['url'],
        test.get('expected_status', 'success'),
        test['max_wait']
    )
    
    if result:
        passed += 1
    else:
        failed += 1
    
    time.sleep(3)  # Pause between tests

print("\n" + "="*60)
print("📊 TEST SUMMARY")
print("="*60)
print(f"Total Tests: {passed + failed}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"Success Rate: {(passed/(passed+failed)*100) if passed+failed > 0 else 0:.1f}%")
print("="*60)
