# Save as 'check_and_launch.py' - Dependency Checker & App Launcher

import subprocess
import sys
import os

def check_and_install_dependencies():
    """Check for required dependencies and offer to install them"""
    print("🔧 CHECKING DEPENDENCIES FOR ENHANCED ALD BOOK MANAGER")
    print("=" * 60)
    
    required_packages = {
        'pandas': 'pandas>=1.5.0',
    }
    
    optional_packages = {
        'PIL': 'pillow>=9.0.0',
        'barcode': 'python-barcode>=0.13.0', 
        'fpdf': 'fpdf2>=2.7.0'
    }
    
    missing_required = []
    missing_optional = []
    
    # Check required packages
    print("\n📦 CHECKING REQUIRED PACKAGES...")
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            print(f"   ✅ {package} - Installed")
        except ImportError:
            print(f"   ❌ {package} - Missing")
            missing_required.append(pip_name)
    
    # Check optional packages  
    print("\n📦 CHECKING OPTIONAL PACKAGES...")
    for package, pip_name in optional_packages.items():
        try:
            __import__(package)
            print(f"   ✅ {package} - Installed (for PDF/barcode features)")
        except ImportError:
            print(f"   ⚠️  {package} - Missing (PDF/barcode features disabled)")
            missing_optional.append(pip_name)
    
    # Install missing required packages
    if missing_required:
        print(f"\n🚨 MISSING REQUIRED PACKAGES: {', '.join(missing_required)}")
        install = input("📥 Install missing required packages? (y/n): ")
        
        if install.lower() == 'y':
            print("🔄 Installing required packages...")
            for package in missing_required:
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                    print(f"   ✅ {package} installed successfully")
                except subprocess.CalledProcessError as e:
                    print(f"   ❌ Failed to install {package}: {e}")
                    return False
        else:
            print("❌ Cannot run app without required packages")
            return False
    
    # Offer to install optional packages
    if missing_optional:
        print(f"\n📋 OPTIONAL PACKAGES MISSING: {', '.join(missing_optional)}")
        print("   These enable PDF generation with barcodes")
        install_optional = input("📥 Install optional packages for full features? (y/n): ")
        
        if install_optional.lower() == 'y':
            for package in missing_optional:
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                    print(f"   ✅ {package} installed successfully")
                except subprocess.CalledProcessError as e:
                    print(f"   ⚠️  Failed to install optional package {package}: {e}")
    
    return True

def verify_files():
    """Verify all required files exist"""
    print("\n📁 CHECKING REQUIRED FILES...")
    
    required_files = {
        'ald_book_app.py': 'Main application',
        'enhanced_code_browser.py': 'Enhanced code browser',
        'book_gallery.py': 'Book gallery',
        'code_management.py': 'Code management',
        'utils/enhanced_file_io.py': 'Enhanced data handler',
        'ALD_CDS.csv': 'Enhanced codes data'
    }
    
    all_files_present = True
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            print(f"   ✅ {description}: {file_path}")
        else:
            print(f"   ❌ {description}: {file_path} - MISSING")
            all_files_present = False
    
    return all_files_present

def test_imports():
    """Test that all imports work"""
    print("\n🔧 TESTING IMPORTS...")
    
    try:
        # Test pandas
        import pandas as pd
        print(f"   ✅ pandas {pd.__version__}")
        
        # Test enhanced data handler
        sys.path.append('utils')
        from enhanced_file_io import load_enhanced_codes, get_categories
        print("   ✅ Enhanced data handler")
        
        # Test enhanced browser
        from enhanced_code_browser import EnhancedCodeBrowserScreen
        print("   ✅ Enhanced code browser")
        
        # Test data loading
        codes = load_enhanced_codes()
        categories = get_categories()
        print(f"   ✅ Data system: {len(codes)} codes, {len(categories)} categories")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import test failed: {e}")
        return False

def launch_app():
    """Launch the enhanced ALD app"""
    print("\n🚀 LAUNCHING ENHANCED ALD BOOK MANAGER...")
    print("=" * 60)
    
    try:
        import ald_book_app
        print("✅ App launched successfully!")
        
    except Exception as e:
        print(f"❌ App launch failed: {e}")
        input("\nPress Enter to continue...")

def main():
    """Main function"""
    print("🎉 ENHANCED ALD BOOK MANAGER - SETUP & LAUNCHER")
    print("=" * 60)
    
    # Step 1: Check and install dependencies
    if not check_and_install_dependencies():
        input("\nPress Enter to exit...")
        return
    
    # Step 2: Verify files
    if not verify_files():
        print("\n❌ Missing required files - complete setup first")
        input("\nPress Enter to exit...")
        return
    
    # Step 3: Test imports
    if not test_imports():
        print("\n❌ Import tests failed - check dependencies")
        input("\nPress Enter to exit...")
        return
    
    # Step 4: Launch app
    print("\n🎉 ALL SYSTEMS READY!")
    launch_choice = input("\n🚀 Launch Enhanced ALD Book Manager? (y/n): ")
    
    if launch_choice.lower() == 'y':
        launch_app()
    else:
        print("👍 Setup complete - run 'python ald_book_app.py' when ready!")

if __name__ == "__main__":
    main()
