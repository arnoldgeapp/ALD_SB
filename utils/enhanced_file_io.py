# This should already be working based on your test, but here's the complete version

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
    
    return pd.DataFrame(columns=['Book', 'Code', 'Description', 'Category', 'CustomOrder'])

def save_books(df):
    """Save books data"""
    df.to_csv(BOOKS_CSV, index=False)

def load_enhanced_codes():
    """Load enhanced codes with hierarchical categories and features"""
    if os.path.exists(ENHANCED_CODES_CSV):
        try:
            df = pd.read_csv(ENHANCED_CODES_CSV, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(ENHANCED_CODES_CSV, encoding='cp1252')
            except UnicodeDecodeError:
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
    
    # Fallback to basic codes
    if os.path.exists(CODES_CSV):
        df = pd.read_csv(CODES_CSV)
        df['Category'] = 'Uncategorized'
        df['SubCategory'] = 'General'
        df['DefaultFavorite'] = False
        df['Notes'] = ''
        df['Code'] = df['Code'].fillna("").astype(str)
        df['Description'] = df['Description'].fillna("").astype(str)
        return df
    
    return pd.DataFrame(columns=['Code', 'Description', 'Category', 'SubCategory', 'DefaultFavorite', 'Notes'])

def save_enhanced_codes(df):
    """Save enhanced codes"""
    df.to_csv(ENHANCED_CODES_CSV, index=False, encoding='utf-8')

def get_categories() -> List[Dict]:
    """Get all main categories with their metadata"""
    df = load_enhanced_codes()
    if 'Category' not in df.columns:
        return [{'name': 'Uncategorized', 'color': '#64748b', 'count': len(df), 'subcategories': []}]
    
    # Define colors for your 15 categories
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
        return df

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