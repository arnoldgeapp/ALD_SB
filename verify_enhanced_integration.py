# Save as 'verify_enhanced_integration.py' and run to verify everything is ready

import os
import sys

def verify_integration():
    print("🔍 VERIFYING ENHANCED INTEGRATION...")
    print("=" * 50)
    
    all_ready = True
    
    # Check if enhanced_code_browser.py exists
    if os.path.exists('enhanced_code_browser.py'):
        size = os.path.getsize('enhanced_code_browser.py')
        print(f"✅ enhanced_code_browser.py ({size:,} bytes)")
        
        # Quick import test
        try:
            from enhanced_code_browser import EnhancedCodeBrowserScreen
            print("✅ Enhanced browser imports successfully")
        except Exception as e:
            print(f"❌ Enhanced browser import failed: {e}")
            all_ready = False
    else:
        print("❌ enhanced_code_browser.py - MISSING")
        print("📝 Save the Enhanced Code Browser from the artifact!")
        all_ready = False
    
    # Check data handler
    if os.path.exists('utils/enhanced_file_io.py'):
        print("✅ utils/enhanced_file_io.py exists")
        try:
            sys.path.append('utils')
            from enhanced_file_io import load_enhanced_codes, get_categories
            codes = load_enhanced_codes()
            categories = get_categories()
            print(f"✅ Data system: {len(codes)} codes, {len(categories)} categories")
        except Exception as e:
            print(f"❌ Data system error: {e}")
            all_ready = False
    else:
        print("❌ utils/enhanced_file_io.py - MISSING")
        all_ready = False
    
    # Check main app
    if os.path.exists('ald_book_app.py'):
        print("✅ ald_book_app.py updated correctly")
    else:
        print("❌ ald_book_app.py - MISSING")
        all_ready = False
    
    print("=" * 50)
    
    if all_ready:
        print("🎉 INTEGRATION COMPLETE!")
        print("🚀 READY TO LAUNCH!")
        print("\n📋 To launch your enhanced app:")
        print("   python ald_book_app.py")
        print("\n✨ You should see:")
        print("   • 3 cards in the main menu")
        print("   • Green 'Enhanced Code Browser' card")
        print("   • Click it to see your 941 codes organized!")
        
        return True
    else:
        print("⚠️  INTEGRATION NOT COMPLETE")
        print("\n📝 Still needed:")
        if not os.path.exists('enhanced_code_browser.py'):
            print("   • Save enhanced_code_browser.py from artifact")
        print("\n🔧 Complete the missing items and run this test again")
        
        return False

if __name__ == "__main__":
    ready = verify_integration()
    
    if ready:
        launch = input("\n🚀 Launch the app now? (y/n): ")
        if launch.lower() == 'y':
            print("🎉 Launching your Enhanced ALD Book Manager...")
            os.system('python ald_book_app.py')
    else:
        input("\nPress Enter to continue...")