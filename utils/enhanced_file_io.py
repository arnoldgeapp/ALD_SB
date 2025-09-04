import os
import pandas as pd
from typing import List, Dict, Optional

# File paths
BOOKS_CSV = "ald_books.csv"
CODES_CSV = "ALD_codes.csv"
ENHANCED_CODES_CSV = "ALD_CDS.csv"  # Your enhanced codes file

def load_books():
    """Load books data with enhanced columns"""
    if os.path.exists(BOOKS_CSV):
        df = pd.read_csv(BOOKS_CSV)
        
        # Ensure all required columns exist
        required_columns = ['Book', 'Code', 'Description', 'Category', 'CustomOrder']
        for col in required_columns:
            if col not in df.columns:
                if col == 'Category':
                    df[col] = "General"
                elif col == 'CustomOrder':
                    df[col] = 0
                else:
                    df[col] = ""
        
        # Clean and normalize data
        df["Book"] = df["Book"].fillna("").astype(str)
        df["Code"] = df["Code"].fillna("").astype(str)
        df["Description"] = df["Description"].fillna("").astype(str)
        df["Category"] = df["Category"].fillna("General").astype(str)
        df["CustomOrder"] = df["CustomOrder"].fillna(0)
        
        return df
    
    # Return empty DataFrame with required structure
    return pd.DataFrame(columns=['Book', 'Code', 'Description', 'Category', 'CustomOrder'])

def save_books(df):
    """Save books data"""
    df.to_csv(BOOKS_CSV, index=False)

def load_enhanced_codes():
    """
    Load enhanced codes with hierarchical categories and features.
    Your structure: Code, Description, Category, SubCategory, DefaultFavorite, Notes
    """
    if os.path.exists(ENHANCED_CODES_CSV):
        try:
            # Try UTF-8 first
            df = pd.read_csv(ENHANCED_CODES_CSV, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                # Fallback to cp1252
                df = pd.read_csv(ENHANCED_CODES_CSV, encoding='cp1252')
            except UnicodeDecodeError:
                # Final fallback
                df = pd.read_csv(ENHANCED_CODES_CSV, encoding='latin-1')
        
        # Ensure all expected columns exist
        expected_columns = ['Code', 'Description', 'Category', 'SubCategory', 'DefaultFavorite', 'Notes']
        for col in expected_columns:
            if col not in df.columns:
                if col == 'DefaultFavorite':
                    df[col] = False
                elif col == 'Notes':
                    df[col] = ''
                elif col == 'Category':
                    df[col] = 'Uncategorized'
                elif col == 'SubCategory':
                    df[col] = 'General'
                else:
                    df[col] = ''
        
        # Clean data types
        df['Code'] = df['Code'].fillna("").astype(str)
        df['Description'] = df['Description'].fillna("").astype(str)
        df['Category'] = df['Category'].fillna("Uncategorized").astype(str)
        df['SubCategory'] = df['SubCategory'].fillna("General").astype(str)
        df['DefaultFavorite'] = df['DefaultFavorite'].fillna(False).astype(bool)
        df['Notes'] = df['Notes'].fillna("").astype(str)
        
        return df
    
    # Fallback to basic codes and enhance them
    if os.path.exists(CODES_CSV):
        df = pd.read_csv(CODES_CSV)
        # Add enhanced columns to match your structure
        df['Category'] = 'Uncategorized'
        df['SubCategory'] = 'General'
        df['DefaultFavorite'] = False
        df['Notes'] = ''
        
        # Clean data
        df['Code'] = df['Code'].fillna("").astype(str)
        df['Description'] = df['Description'].fillna("").astype(str)
        
        return df
    
    # Return empty enhanced structure
    return pd.DataFrame(columns=['Code', 'Description', 'Category', 'SubCategory', 'DefaultFavorite', 'Notes'])

def save_enhanced_codes(df):
    """Save enhanced codes"""
    df.to_csv(ENHANCED_CODES_CSV, index=False, encoding='utf-8')

def get_categories() -> List[Dict]:
    """Get all main categories with their metadata"""
    df = load_enhanced_codes()
    if 'Category' not in df.columns:
        return [{'name': 'Uncategorized', 'color': '#64748b', 'count': len(df), 'subcategories': []}]
    
    # Define colors for different categories
    category_colors = {
        'Defective': '#ef4444',           # Red
        'Damaged': '#dc2626',             # Dark red  
        'Assembled Wrong': '#f97316',     # Orange
        'Missing': '#7c3aed',             # Purple
        'Loose': '#eab308',               # Yellow
        'Wrong Part': '#8b5cf6',          # Light purple
        'Unplugged': '#06b6d4',           # Cyan
        'Drawer Defect': '#10b981',       # Green
        'Miscellaneous': '#64748b',       # Gray
        'Hipot': '#f59e0b',               # Amber
        'Alignment': '#14b8a6',           # Teal
        'Cross Wired': '#0ea5e9',         # Sky blue
        'Dirty': '#84cc16',               # Lime
        'No Functional Repair': '#6366f1', # Indigo
        'Leak': '#ec4899'                 # Pink
    }
    
    categories = []
    for category_name in sorted(df['Category'].unique()):
        if pd.notna(category_name) and category_name != '':
            category_data = df[df['Category'] == category_name]
            subcategories = []
            if 'SubCategory' in df.columns:
                subcategories = sorted(category_data['SubCategory'].unique())
            
            categories.append({
                'name': category_name,
                'color': category_colors.get(category_name, '#3b82f6'),
                'count': len(category_data),
                'subcategories': subcategories
            })
    
    return categories

def get_subcategories(category_name: str = None) -> List[str]:
    """Get subcategories for a given category"""
    df = load_enhanced_codes()
    
    if category_name and 'Category' in df.columns:
        filtered_df = df[df['Category'] == category_name]
        if 'SubCategory' in filtered_df.columns:
            return sorted(filtered_df['SubCategory'].unique())
    elif 'SubCategory' in df.columns:
        return sorted(df['SubCategory'].unique())
    
    return ['General']

def get_codes_by_category(category_name: str = None, subcategory_name: str = None, favorites_only: bool = False):
    """Get codes filtered by category, subcategory, and/or favorites"""
    df = load_enhanced_codes()
    
    if favorites_only and 'DefaultFavorite' in df.columns:
        df = df[df['DefaultFavorite'] == True]
    
    if category_name is None or category_name == 'All':
        if subcategory_name and subcategory_name != 'All':
            return df[df['SubCategory'] == subcategory_name] if 'SubCategory' in df.columns else df
        return df
    
    if 'Category' in df.columns:
        df = df[df['Category'] == category_name]
        
        if subcategory_name and subcategory_name != 'All' and 'SubCategory' in df.columns:
            df = df[df['SubCategory'] == subcategory_name]
            
        return df
    else:
        return df  # Return all if no categories exist

def get_favorite_codes():
    """Get all codes marked as favorites"""
    df = load_enhanced_codes()
    
    if 'DefaultFavorite' in df.columns:
        return df[df['DefaultFavorite'] == True]
    else:
        return pd.DataFrame()

def toggle_code_favorite(code: str) -> bool:
    """Toggle favorite status for a code"""
    df = load_enhanced_codes()
    
    mask = df['Code'] == code
    if mask.any():
        if 'DefaultFavorite' in df.columns:
            current_status = df.loc[mask, 'DefaultFavorite'].iloc[0]
            df.loc[mask, 'DefaultFavorite'] = not current_status
        else:
            df['DefaultFavorite'] = False
            df.loc[mask, 'DefaultFavorite'] = True
        
        save_enhanced_codes(df)
        return df.loc[mask, 'DefaultFavorite'].iloc[0]
    return False

def update_code_notes(code: str, notes: str) -> bool:
    """Update notes for a specific code"""
    df = load_enhanced_codes()
    
    mask = df['Code'] == code
    if mask.any():
        df.loc[mask, 'Notes'] = notes
        save_enhanced_codes(df)
        return True
    return False

def assign_codes_to_category(codes: List[str], category_name: str, subcategory_name: str = 'General'):
    """Assign multiple codes to a category and subcategory"""
    df = load_enhanced_codes()
    
    for code in codes:
        mask = df['Code'] == code
        if mask.any():
            df.loc[mask, 'Category'] = category_name
            if 'SubCategory' in df.columns:
                df.loc[mask, 'SubCategory'] = subcategory_name
    
    save_enhanced_codes(df)

def search_codes(search_term: str, category: str = None, subcategory: str = None, favorites_only: bool = False) -> pd.DataFrame:
    """Search codes by term, optionally within a category/subcategory"""
    df = load_enhanced_codes()
    
    if favorites_only and 'DefaultFavorite' in df.columns:
        df = df[df['DefaultFavorite'] == True]
    
    if category and category != 'All':
        df = df[df['Category'] == category]
        
    if subcategory and subcategory != 'All' and 'SubCategory' in df.columns:
        df = df[df['SubCategory'] == subcategory]
    
    if search_term:
        search_term = search_term.lower()
        mask = (
            df['Code'].astype(str).str.lower().str.contains(search_term, na=False) |
            df['Description'].astype(str).str.lower().str.contains(search_term, na=False) |
            df['Notes'].astype(str).str.lower().str.contains(search_term, na=False)
        )
        df = df[mask]
    
    return df

def get_category_colors():
    """Get predefined colors for categories"""
    return {
        'Defective': '#ef4444',           # Red
        'Damaged': '#dc2626',             # Dark red  
        'Assembled Wrong': '#f97316',     # Orange
        'Missing': '#7c3aed',             # Purple
        'Loose': '#eab308',               # Yellow
        'Wrong Part': '#8b5cf6',          # Light purple
        'Unplugged': '#06b6d4',           # Cyan
        'Drawer Defect': '#10b981',       # Green
        'Miscellaneous': '#64748b',       # Gray
        'Hipot': '#f59e0b',               # Amber
        'Alignment': '#14b8a6',           # Teal
        'Cross Wired': '#0ea5e9',         # Sky blue
        'Dirty': '#84cc16',               # Lime
        'No Functional Repair': '#6366f1', # Indigo
        'Leak': '#ec4899'                 # Pink
    }

def migrate_existing_data():
    """
    Migrate existing data to enhanced format
    This should be run once to upgrade existing installations
    """
    print("Migrating existing data to enhanced format...")
    
    # Load existing codes and enhance them
    if os.path.exists(CODES_CSV) and not os.path.exists(ENHANCED_CODES_CSV):
        df = pd.read_csv(CODES_CSV)
        df['Category'] = 'General'  # Default category
        df['SubCategory'] = 'General'  # Default subcategory
        df['DefaultFavorite'] = False
        df['Notes'] = ''
        
        save_enhanced_codes(df)
        print(f"Migrated {len(df)} codes to enhanced format")
    
    # Update books to ensure they have Category column
    books_df = load_books()
    if len(books_df) > 0:
        save_books(books_df)
        print(f"Updated {len(books_df)} book entries")
    
    print("Migration complete!")

if __name__ == "__main__":
    # Test the enhanced data loading with your actual structure
    print("Testing enhanced data system with your ALD_CDS.csv structure...")
    
    try:
        # Try loading enhanced codes
        codes_df = load_enhanced_codes()
        print(f"✅ Loaded {len(codes_df)} codes")
        print(f"📋 Columns: {list(codes_df.columns)}")
        
        if len(codes_df) > 0:
            print(f"📄 Sample data:")
            sample = codes_df.head(2)[['Code', 'Description', 'Category', 'SubCategory', 'DefaultFavorite']].to_string()
            print(f"   {sample}")
        
        # Show categories (your main grouping system)
        categories = get_categories()
        print(f"\n🏷️  Found {len(categories)} categories:")
        for category in categories[:5]:  # Show first 5
            print(f"   📂 {category['name']}: {category['count']} codes (Color: {category['color']})")
            if category['subcategories']:
                subcats = ', '.join(category['subcategories'][:3])
                more = f" (+{len(category['subcategories'])-3} more)" if len(category['subcategories']) > 3 else ""
                print(f"      └── Subcategories: {subcats}{more}")
        
        # Show favorites
        favorites = get_favorite_codes()
        favorite_count = len(favorites)
        print(f"\n⭐ Found {favorite_count} favorite codes")
        if favorite_count > 0:
            for _, fav in favorites.head(3).iterrows():
                print(f"   ⭐ {fav['Code']} - {fav['Description']}")
        
        print("✅ Enhanced data system ready for your hierarchical structure!")
        
    except Exception as e:
        print(f"❌ Error testing data system: {e}")
        import traceback
        traceback.print_exc()