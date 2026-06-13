"""
db_manager.py — SQLite Database Manager for lead generation tracking
====================================================================
Handles connection, initialization, inserts, status updates, and 
geographic competitor matching for scraped businesses.
"""

import sqlite3
import os
import logging
import config

logger = logging.getLogger(__name__)

def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database schema and create required indexes."""
    logger.info("Initializing SQLite database: %s", config.DB_PATH)
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT,
                website TEXT,
                category TEXT,
                maps_url TEXT,
                priority TEXT,
                status TEXT DEFAULT 'scraped',
                competitor_name TEXT DEFAULT 'N/A',
                competitor_website TEXT DEFAULT 'N/A',
                rating REAL,
                reviews INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, address)
            )
        """)
        
        # Dynamic migration for existing databases
        try:
            conn.execute("ALTER TABLE leads ADD COLUMN rating REAL")
        except sqlite3.OperationalError:
            pass # Column already exists
            
        try:
            conn.execute("ALTER TABLE leads ADD COLUMN reviews INTEGER")
        except sqlite3.OperationalError:
            pass # Column already exists

        # Indexes for fast lookup
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_name_addr ON leads(name, address)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_category_status ON leads(category, status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)")
        conn.commit()
    logger.info("Database initialized successfully.")


def insert_lead(lead: dict) -> bool:
    """
    Insert or update a lead in the database.
    If name/address already exists, updates detail fields but preserves the 'status' 
    and 'competitor_name' / 'competitor_website' unless explicitly changed.
    """
    name = lead.get("Name", "N/A")
    address = lead.get("Address", "N/A")
    phone = lead.get("Phone", "N/A")
    website = lead.get("Website", "N/A")
    category = lead.get("Category", "N/A")
    maps_url = lead.get("Maps URL", "")
    priority = lead.get("Priority", "[LOW] Low")
    status = lead.get("status", "scraped")
    rating = lead.get("Rating")
    if rating == "N/A":
        rating = None
    reviews = lead.get("Total Reviews")
    if reviews == "N/A":
        reviews = None
    
    # If the lead has a personal website, default status is 'has_website'
    # but don't overwrite if it was already updated by user
    if website != "N/A" and not any(dom in website.lower() for dom in config.PLATFORM_DOMAINS):
        status = "has_website"

    try:
        with get_connection() as conn:
            # We use ON CONFLICT to update phone, website, category, maps_url, priority, rating, reviews
            # but we preserve status and competitor info.
            conn.execute("""
                INSERT INTO leads (name, address, phone, website, category, maps_url, priority, status, rating, reviews)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name, address) DO UPDATE SET
                    phone = excluded.phone,
                    website = excluded.website,
                    category = excluded.category,
                    maps_url = excluded.maps_url,
                    priority = excluded.priority,
                    rating = excluded.rating,
                    reviews = excluded.reviews,
                    updated_at = CURRENT_TIMESTAMP
            """, (name, address, phone, website, category, maps_url, priority, status, rating, reviews))
            conn.commit()
            return True
    except Exception as e:
        logger.error("Error inserting lead %s: %s", name, e)
        return False


def update_lead_status(name: str, address: str, status: str) -> bool:
    """Update the status of a specific lead (e.g. mark as qualified or deal_cracked)."""
    valid_statuses = ['scraped', 'has_website', 'qualified', 'deal_cracked', 'disqualified']
    if status not in valid_statuses:
        logger.warning("Unknown status: %s. Proceeding anyway.", status)
        
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE leads 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE LOWER(name) = LOWER(?) AND LOWER(address) = LOWER(?)
            """, (status, name.strip(), address.strip()))
            conn.commit()
            if cur.rowcount > 0:
                logger.info("Updated status of lead '%s' to '%s'", name, status)
                return True
            else:
                logger.warning("Lead '%s' at '%s' not found for status update.", name, address)
                return False
    except Exception as e:
        logger.error("Error updating lead status for %s: %s", name, e)
        return False


def load_excluded_leads() -> set[str]:
    """
    Get a set of composite keys (name|address in lowercase) for leads that 
    are already qualified, deal_cracked, or disqualified, so the scraper skips them.
    """
    excluded_keys = set()
    try:
        with get_connection() as conn:
            # We exclude qualified, deal_cracked, and disqualified leads
            cur = conn.execute("""
                SELECT name, address FROM leads 
                WHERE status IN ('qualified', 'deal_cracked', 'disqualified')
            """)
            for row in cur.fetchall():
                key = f"{row['name'].lower()}|{row['address'].lower()}"
                excluded_keys.add(key)
    except Exception as e:
        logger.error("Error loading excluded leads: %s", e)
    return excluded_keys


def clean_address_tokens(address: str) -> list[str]:
    """Helper to tokenize an address and extract clean location words (neighborhoods, roads)."""
    if not address or address == "N/A":
        return []
    
    # Common words in Indian/Delhi addresses to filter out
    stop_words = {
        "delhi", "new", "india", "road", "gali", "phase", "sector", "block", 
        "pocket", "near", "opposite", "behind", "metro", "station", "building",
        "floor", "market", "enclave", "colony", "nagar", "bagh", "khas", "place",
        "extension", "vihar", "chowk", "marg", "west", "east", "north", "south",
        "garden", "park", "house", "complex", "plaza", "tower", "towers", "arcade",
        "centre", "center", "mall", "square", "lane", "street", "line", "highway",
        "hwy", "flyover", "village", "gate", "shop", "showroom", "main", "highstreet",
        "above", "below", "ground", "first", "second", "third"
    }
    
    # Clean and split address
    addr_clean = address.lower().replace(",", " ").replace(".", " ").replace("-", " ")
    tokens = [t.strip() for t in addr_clean.split() if t.strip()]
    
    # Filter out numeric tokens and stop words
    filtered_tokens = []
    for token in tokens:
        if token.isdigit():
            continue
        if token in stop_words:
            continue
        if len(token) < 3:
            continue
        filtered_tokens.append(token)
        
    return filtered_tokens


def find_competitor_for_lead(lead_category: str, lead_address: str) -> tuple[str, str]:
    """
    Find a local rival business that has a website (status = 'has_website') in the database.
    Matches primarily by:
      1. Category (exact match)
      2. Locality (highest token overlap of clean address keywords)
    
    Returns:
        tuple: (competitor_name, competitor_website) or ("N/A", "N/A") if none found.
    """
    if not lead_category or lead_category == "N/A":
        return "N/A", "N/A"
        
    try:
        with get_connection() as conn:
            # 1. Fetch all businesses in the same category that have websites
            cur = conn.execute("""
                SELECT name, website, address FROM leads 
                WHERE category = ? AND status = 'has_website' AND website != 'N/A'
            """, (lead_category,))
            candidates = cur.fetchall()
            
            if not candidates:
                # Fallback: search for slightly loose matches in category
                cur = conn.execute("""
                    SELECT name, website, address FROM leads 
                    WHERE category LIKE ? AND status = 'has_website' AND website != 'N/A'
                """, (f"%{lead_category}%",))
                candidates = cur.fetchall()
                
            if not candidates:
                return "N/A", "N/A"
                
            # 2. Score candidates by address token overlap
            lead_tokens = set(clean_address_tokens(lead_address))
            best_candidate = None
            max_overlap = 0
            
            for candidate in candidates:
                candidate_tokens = set(clean_address_tokens(candidate["address"]))
                # Count intersection of location keywords (e.g. both contain "lajpat")
                overlap = len(lead_tokens.intersection(candidate_tokens))
                
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_candidate = candidate
                    
            if best_candidate:
                return best_candidate["name"], best_candidate["website"]
                
    except Exception as e:
        logger.error("Error finding competitor for category %s: %s", lead_category, e)
        
    return "N/A", "N/A"


def update_lead_competitor_info(name: str, address: str, comp_name: str, comp_web: str):
    """Write matched competitor info back to the SQLite lead record."""
    try:
        with get_connection() as conn:
            conn.execute("""
                UPDATE leads 
                SET competitor_name = ?, competitor_website = ?, updated_at = CURRENT_TIMESTAMP
                WHERE LOWER(name) = LOWER(?) AND LOWER(address) = LOWER(?)
            """, (comp_name, comp_web, name.strip(), address.strip()))
            conn.commit()
    except Exception as e:
        logger.error("Error updating competitor info for %s: %s", name, e)


# Self-init db if file is run directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
