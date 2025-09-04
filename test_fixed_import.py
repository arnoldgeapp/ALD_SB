# Save as 'test_fixed_import.py' and run to verify the fix

import sys
import os

def test_fixed_imports():
    print("=== 🔧 TESTING FIXED IMPORTS ===\n")
    
    # Check if the file exists
    if not os.path.exists('utils/enhanced_file_io.py'):
        print("❌ utils/enhanced_file_io.py not found")
        print("📝 Make sure you saved the corrected version")
        return
    
    file_size = os.path.getsize('utils/enhanced_file_io.py')
    print(f"✅ utils/enhanced_file_io.py found ({file_size:,} bytes)")
    
    # Test imports
    try:
        sys.path.append('utils')
        from enhanced_file_io import (
            load_enhanced_codes, 
            get_categories, 
            get_subcategories,
            get_favorite_codes,
            get_category_colors
        )
        print("✅ All imports successful!")
        
        # Test data loading
        print("\n📊 Testing data loading...")
        codes_df = load_enhanced_codes()
        categories = get_categories()
        favorites = get_favorite_codes()
        colors = get_category_colors()
        
        print(f"✅ Loaded {len(codes_df)} codes")
        print(f"✅ Found {len(categories)} categories")
        print(f"✅ Found {len(favorites)} favorite codes")
        print(f"✅ Loaded {len(colors)} category colors")
        
        # Show some categories
        print(f"\n🏷️  Top Categories:")
        for i, cat in enumerate(categories[:5]):
            color = cat['color']
            print(f"   {i+1}. {cat['name']}: {cat['count']} codes (Color: {color})")
        
        # Show some favorites
        if len(favorites) > 0:
            print(f"\n⭐ Favorite Codes:")
            for _, fav in favorites.head(3).iterrows():
                print(f"   ⭐ {fav['Code']} - {fav['Description']} ({fav['Category']})")
        
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"🚀 Ready to proceed with integration!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"📝 Check that you saved the complete corrected version")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_imports()