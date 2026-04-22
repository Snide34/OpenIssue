#!/usr/bin/env python3
"""Test script to verify ASCII art alignment"""

# Test all ASCII art boxes
boxes = [
    # Box 1: No vulnerabilities
    """
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║    ✅ NO VULNERABILITIES FOUND!                                         ║
║                                                                          ║
║    🎉 Your code looks secure! Great job maintaining security standards. ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """,
    
    # Box 2: Scan initiated
    """
╔══════════════════════════════════════════════════════════════════════════╗
║                       🔍 SECURITY SCAN INITIATED!                        ║
║                                                                          ║
║    Scanning: /path/to/project                                           ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """,
    
    # Box 3: AI Fix Generation
    """
╔══════════════════════════════════════════════════════════════════════════╗
║                       🤖 AI FIX GENERATION ACTIVE                        ║
║                                                                          ║
║    Generating intelligent fix suggestions using AI...                   ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """,
    
    # Box 4: Vulnerabilities detected
    """
╔══════════════════════════════════════════════════════════════════════════╗
║                        VULNERABILITIES DETECTED                          ║
║                                                                          ║
║    Total Found:   5                                                     ║
║                                                                          ║
║    🔴 CRITICAL :   2                                                     ║
║    🟠 HIGH     :   1                                                     ║
║    🟡 MEDIUM   :   2                                                     ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """,
    
    # Box 5: Scan completed
    """
╔══════════════════════════════════════════════════════════════════════════╗
║                           ✅ SCAN COMPLETED                              ║
║                                                                          ║
║    Security scan finished successfully! No critical issues found.       ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """,
    
    # Box 6: Build failed
    """
╔══════════════════════════════════════════════════════════════════════════╗
║                            ❌ BUILD FAILED                               ║
║                                                                          ║
║    Critical vulnerabilities detected! Please fix before proceeding.     ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """,
    
    # Box 7: Posting issue
    """
╔══════════════════════════════════════════════════════════════════════════╗
║                          📝 POSTING ISSUE                                ║
║                                                                          ║
║    Title: Security vulnerability found in authentication module         ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """,
    
    # Box 8: Issue posted successfully
    """
╔══════════════════════════════════════════════════════════════════════════╗
║                       ✅ ISSUE POSTED SUCCESSFULLY                       ║
║                                                                          ║
║    Your issue has been submitted to the OpenIssue backend.              ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """
]

def check_box_alignment(box_text, box_num):
    """Check if a box is properly aligned"""
    lines = box_text.strip().split('\n')
    issues = []
    
    for i, line in enumerate(lines):
        # Count actual characters (emojis count as 1 in string length but display as 2)
        if '║' in line:
            # Check if line starts and ends with ║
            if not line.strip().startswith('║') or not line.strip().endswith('║'):
                issues.append(f"  Line {i+1}: Missing border characters")
            
            # Get content between borders
            content = line.strip()[1:-1] if line.strip().startswith('║') and line.strip().endswith('║') else line
            
            # Count visual width (rough estimate)
            visual_width = len(content)
            emoji_count = sum(1 for c in content if ord(c) > 127 and ord(c) not in range(0x2500, 0x2600))
            visual_width += emoji_count  # Emojis take ~2 spaces
            
            if visual_width > 76:  # 76 chars + 2 borders = 78 total
                issues.append(f"  Line {i+1}: Too wide ({visual_width} chars, max 76)")
    
    return issues

print("=" * 80)
print("ASCII ART ALIGNMENT TEST")
print("=" * 80)

for i, box in enumerate(boxes, 1):
    print(f"\n📦 Box {i}:")
    print(box)
    
    issues = check_box_alignment(box, i)
    if issues:
        print(f"⚠️  Issues found:")
        for issue in issues:
            print(issue)
    else:
        print("✅ Alignment looks good!")

print("\n" + "=" * 80)
print("Test complete!")
print("=" * 80)
