# Quick analysis of your actual ALD_CDS.csv structure
import pandas as pd

def analyze_your_data():
    print("=== 📊 YOUR ALD_CDS.csv ANALYSIS ===\n")
    
    # Load your actual data
    df = pd.read_csv('ALD_CDS.csv', encoding='utf-8')
    
    print(f"🎯 Total codes: {len(df)}")
    print(f"📋 Columns: {list(df.columns)}")
    print()
    
    # Analyze main categories
    print("🏷️ MAIN CATEGORIES:")
    categories = df['Category'].value_counts()
    for category, count in categories.items():
        print(f"   📁 {category}: {count} codes")
    print()
    
    # Analyze subcategories for top categories
    print("🔍 SUBCATEGORIES (Top 3 categories):")
    for category in categories.head(3).index:
        subcats = df[df['Category'] == category]['SubCategory'].value_counts()
        print(f"\n   📁 {category}:")
        for subcat, count in subcats.head(5).items():  # Show top 5 subcategories
            print(f"      └── {subcat}: {count} codes")
    
    # Analyze favorites
    print(f"\n⭐ FAVORITES:")
    favorites = df[df['DefaultFavorite'] == True]
    print(f"   🌟 {len(favorites)} codes marked as favorites")
    
    if len(favorites) > 0:
        print("   📋 Favorite codes:")
        for _, row in favorites.head(5).iterrows():
            print(f"      ⭐ {row['Code']} - {row['Description']} ({row['Category']} → {row['SubCategory']})")
    
    # Notes analysis
    notes_count = df['Notes'].notna().sum()
    print(f"\n📝 NOTES:")
    print(f"   ✏️  {notes_count} codes have notes")
    
    print(f"\n🎨 READY FOR ENHANCED UI!")
    print(f"   • {len(categories)} main categories")
    print(f"   • {df['SubCategory'].nunique()} unique subcategories") 
    print(f"   • {len(favorites)} favorite codes")
    print(f"   • Hierarchical browsing ready")
    print(f"   • Color coding ready")

if __name__ == "__main__":
    analyze_your_data()