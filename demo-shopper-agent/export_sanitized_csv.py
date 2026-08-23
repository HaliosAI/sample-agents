#!/usr/bin/env python3
"""
export_sanitized_csv.py
Extracts product data from linon.db, scrubs brand names, SKUs, material numbers,
carton/cubic footage noise, and exports a clean products.csv for open-source use.
"""

import sqlite3
import csv
import json
import re
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "linon.db"
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_CSV = OUTPUT_DIR / "products.csv"

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def clean_text(text: str) -> str:
    if not text:
        return ""
    
    # Replace brand names
    text = re.sub(r'\bLinon\s+Furniture\b', 'HomeStyle Furnishings', text, flags=re.IGNORECASE)
    text = re.sub(r'\bLinon\b', 'HomeStyle', text, flags=re.IGNORECASE)
    
    # Remove SKU / Material number sentences & fragments
    text = re.sub(r'(?:The\s+)?(?:product\s+with\s+)?(?:The\s+)?(?:Material\s+Number|SKU|Kit\s+ID|Material\s+No\.?)\s*(?:\(SKU\))?\s*(?:of\s+the\s+product)?\s*(?:is|:)?\s*[A-Z0-9_-]+[.\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(SKU\)\s*(?:is|of\s+the\s+product\s+is)?\s*[A-Z0-9_-]+[.\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bSKU\s*:\s*[A-Z0-9_-]+[.\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(?:and\s+)?(?:The\s+)?(?:material\s+number|material\s+no)[^.]*?\.', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(?:and\s+)?(?:The\s+)?(?:material\s+number|material\s+no)\s*/\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(?:It\s+comes\s+under|It\s+falls\s+under|Falls\s+under)\s+[^.]*?\.', '', text, flags=re.IGNORECASE)
    text = re.sub(r',?\s*are\s+available\s+for\s+download[.\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Sold\s+in\s+\d+\s+case\s+pack[.\s]*', '', text, flags=re.IGNORECASE)
    
    # Remove packaging, case pack and carton dimension noise
    text = re.sub(r'Comes\s+in\s+\d+\s*(?:<case_pack>)?\s*box[es]*[.\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'ships\s+in\s+a\s+\d+\s*(?:</?case_pack>)?\s*case\s+pack[.\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'ships\s+in\s+a\s+single\s+box\s+with\s+dimensions\s+of\s+[^.]+\.[.\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'With\s+a\s+case\s+pack\s+of\s+\d+,?\s*(?:this\s+table\'s\s+)?(?:and\s+)?(?:has\s+)?(?:cubic\s+feet\s+of\s+[\d.]+)?[.\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Carton\s+dimensions?\s*(?:are|of)?\s*[\d.]+\s*["L]*\s*x\s*[\d.]+\s*["W]*\s*x\s*[\d.]+\s*["H]*[.\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Package\s+dimensions?\s*(?:are|of)?\s*[\d.]+\s*["L]*\s*x\s*[\d.]+\s*["W]*\s*x\s*[\d.]+\s*["H]*[.\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(?:and\s+)?(?:with\s+)?a\s+cubic\s+footage\s+of\s+[\d.]+[.\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(?:and\s+)?(?:has\s+)?(?:The\s+)?cubic\s+feet\s+(?:of\s+package\s+)?is\s+[\d.]+[.\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'resulting\s+in\s+[\d.]+\s+cubic\s+feet[.\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</?case_pack>', '', text, flags=re.IGNORECASE)
    
    # Remove scraper artifacts
    text = re.sub(r'Sorry,\s*your\s*browser\s*doesn\'?t\s*support\s*embedded\s*videos\.?Download\s*Video', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Download\s+Image', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Assembly\s+Instructions', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Geo Console BlackBird Glass Top Table', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Back to:\s*[A-Za-z\s]+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Call for price', '', text, flags=re.IGNORECASE)
    
    # Clean trailing fragments and whitespace
    text = re.sub(r'\s+and\s*\.', '.', text)
    text = re.sub(r'\s*,\s*\.', '.', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_wood_and_material(description: str, vendor_attrs_raw: str) -> tuple[str, str]:
    wood_finish = ""
    material = ""
    
    if vendor_attrs_raw:
        try:
            attrs = json.loads(vendor_attrs_raw)
            if isinstance(attrs, dict):
                wood_finish = attrs.get("Wood Finish", "")
                material = attrs.get("Fabric Content", "")
        except Exception:
            pass
            
    desc_lower = description.lower()
    if not wood_finish:
        if "black finish" in desc_lower or "black wood" in desc_lower:
            wood_finish = "Black"
        elif "white finish" in desc_lower or "white wood" in desc_lower:
            wood_finish = "White"
        elif "merlot finish" in desc_lower:
            wood_finish = "Merlot"
        elif "walnut finish" in desc_lower or "dark walnut" in desc_lower:
            wood_finish = "Dark Walnut"
        elif "espresso" in desc_lower:
            wood_finish = "Espresso"
        elif "natural finish" in desc_lower or "natural wood" in desc_lower:
            wood_finish = "Natural"
        elif "pine" in desc_lower:
            wood_finish = "Pine"
            
    if not material:
        if "vinyl" in desc_lower or "polyurethane" in desc_lower or "faux leather" in desc_lower:
            material = "Vinyl / Polyurethane (Faux Leather)"
        elif "tweed" in desc_lower:
            material = "Tweed Fabric"
        elif "polyester" in desc_lower:
            material = "Polyester Fabric"
        elif "linen" in desc_lower:
            material = "Linen"
        elif "velvet" in desc_lower:
            material = "Velvet"
        elif "fabric" in desc_lower or "upholstered" in desc_lower:
            material = "Upholstered Fabric"
        elif "wood" in desc_lower or "pine" in desc_lower:
            material = "Solid Wood / Wood Veneer"
        elif "metal" in desc_lower or "steel" in desc_lower:
            material = "Metal / Steel"
            
    return wood_finish, material

def main():
    if not DB_PATH.exists():
        print(f"Error: {DB_PATH} does not exist.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    
    cur.execute("""
        SELECT 
            id,
            title, 
            main_category, 
            category_tags, 
            enhanced_description, 
            description,
            vendor_attributes 
        FROM products 
        ORDER BY id ASC
    """)
    rows = cur.fetchall()
    print(f"Fetched {len(rows)} products from database.")

    cleaned_records = []
    seen_titles = set()

    for row in rows:
        pid, title, main_cat, cat_tags_raw, enh_desc, raw_desc, vendor_attrs = row
        
        # Clean title
        clean_title = clean_text(title)
        clean_title = re.sub(r'\s+(?:Blk|Wht|Dkw|Merlot)\b', lambda m: f" - {m.group(0).strip()}", clean_title, flags=re.IGNORECASE)
        clean_title = clean_title.replace("Blk", "Black").replace("Wht", "White").replace("Dkw", "Dark Walnut")
        
        # Deduplicate identical titles
        if clean_title.lower() in seen_titles:
            continue
        seen_titles.add(clean_title.lower())

        # Clean description (prefer enhanced_description if available, else raw_desc)
        best_desc = enh_desc if enh_desc and len(enh_desc.strip()) > 30 else raw_desc
        clean_desc = clean_text(best_desc)
        
        if not clean_desc or len(clean_desc) < 20:
            clean_desc = f"{clean_title} featuring elegant design and premium craftsmanship for modern homes."

        # Clean categories
        categories = []
        if main_cat:
            categories.append(clean_text(main_cat).title())
        if cat_tags_raw:
            try:
                tags = json.loads(cat_tags_raw)
                if isinstance(tags, list):
                    for tag in tags:
                        t = clean_text(str(tag)).title()
                        if t and t not in categories and t != "Case Goods":
                            categories.append(t)
            except Exception:
                pass
        category_str = ", ".join(categories) if categories else "Home Furniture"

        wood_finish, material = extract_wood_and_material(clean_desc, vendor_attrs)
        slug = slugify(clean_title)
        product_link = f"https://example.com/products/{slug}"

        cleaned_records.append({
            "product_id": f"prod_{len(cleaned_records) + 1:04d}",
            "product_name": clean_title,
            "category": category_str,
            "description": clean_desc,
            "wood_finish": wood_finish,
            "material": material,
            "product_link": product_link
        })

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "product_id", "product_name", "category", "description", "wood_finish", "material", "product_link"
        ])
        writer.writeheader()
        writer.writerows(cleaned_records)

    print(f"Successfully exported {len(cleaned_records)} sanitized products to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
