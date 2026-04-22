#!/usr/bin/env python3
"""
Perfect ASCII Art Alignment Tester
Tests actual character width including emojis
"""

def measure_visual_width(text):
    """
    Measure the actual visual width of text including emojis.
    Emojis typically take 2 character widths in terminals.
    """
    width = 0
    for char in text:
        code = ord(char)
        # Emoji ranges (simplified)
        if (0x1F300 <= code <= 0x1F9FF or  # Misc Symbols and Pictographs
            0x2600 <= code <= 0x26FF or    # Misc symbols
            0x2700 <= code <= 0x27BF or    # Dingbats
            0xFE00 <= code <= 0xFE0F or    # Variation Selectors
            0x1F600 <= code <= 0x1F64F or  # Emoticons
            0x1F680 <= code <= 0x1F6FF or  # Transport and Map
            0x1F900 <= code <= 0x1F9FF):   # Supplemental Symbols
            width += 2
        else:
            width += 1
    return width

def test_box(name, box_text):
    """Test a single ASCII box for perfect alignment"""
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print('='*80)
    print(box_text)
    
    lines = box_text.strip().split('\n')
    issues = []
    
    for i, line in enumerate(lines):
        # Skip empty lines
        if not line.strip():
            continue
            
        # Check for box drawing characters
        if '║' in line:
            # Find the positions of the borders
            first_border = line.find('║')
            last_border = line.rfind('║')
            
            if first_border == -1 or last_border == -1 or first_border == last_border:
                issues.append(f"Line {i+1}: Missing or malformed borders")
                continue
            
            # Extract content between borders
            content = line[first_border+1:last_border]
            
            # Measure visual width
            visual_width = measure_visual_width(content)
            
            # Should be exactly 74 characters wide
            if visual_width != 74:
                issues.append(f"Line {i+1}: Width={visual_width} (expected 74) | Content: '{content}'")
    
    if issues:
        print("\n❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n✅ PERFECT ALIGNMENT!")
        return True

# Test all boxes
print("="*80)
print("PERFECT ASCII ART ALIGNMENT TEST")
print("="*80)

boxes = {
    "No Vulnerabilities (Plain)": """
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║    ✅ NO VULNERABILITIES FOUND!                                          ║
║                                                                          ║
║    🎉 Your code looks secure! Great job maintaining security standards.  ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""",
    
    "Scan Initiated": """
╔══════════════════════════════════════════════════════════════════════════╗
║                       🔍 SECURITY SCAN INITIATED!                        ║
║                                                                          ║
║    Scanning: /path/to/project                                            ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""",
    
    "AI Fix Generation": """
╔══════════════════════════════════════════════════════════════════════════╗
║                       🤖 AI FIX GENERATION ACTIVE                        ║
║                                                                          ║
║    Generating intelligent fix suggestions using AI...                    ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""",
    
    "Vulnerabilities Detected": """
╔══════════════════════════════════════════════════════════════════════════╗
║                        VULNERABILITIES DETECTED                          ║
║                                                                          ║
║    Total Found:   5                                                      ║
║                                                                          ║
║    🔴 CRITICAL :   2                                                     ║
║    🟠 HIGH     :   1                                                     ║
║    🟡 MEDIUM   :   2                                                     ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""",
    
    "Scan Completed": """
╔══════════════════════════════════════════════════════════════════════════╗
║                           ✅ SCAN COMPLETED                              ║
║                                                                          ║
║    Security scan finished successfully! No critical issues found.        ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""",
    
    "Build Failed": """
╔══════════════════════════════════════════════════════════════════════════╗
║                            ❌ BUILD FAILED                               ║
║                                                                          ║
║    Critical vulnerabilities detected! Please fix before proceeding.      ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""",
    
    "Posting Issue": """
╔══════════════════════════════════════════════════════════════════════════╗
║                          📝 POSTING ISSUE                                ║
║                                                                          ║
║    Title: Security vulnerability found in authentication module          ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""",
    
    "Issue Posted Successfully": """
╔══════════════════════════════════════════════════════════════════════════╗
║                       ✅ ISSUE POSTED SUCCESSFULLY                       ║
║                                                                          ║
║    Your issue has been submitted to the OpenIssue backend.               ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
}

all_perfect = True
for name, box in boxes.items():
    if not test_box(name, box):
        all_perfect = False

print("\n" + "="*80)
if all_perfect:
    print("🎉 ALL BOXES ARE PERFECTLY ALIGNED!")
else:
    print("❌ SOME BOXES NEED FIXING")
print("="*80)
