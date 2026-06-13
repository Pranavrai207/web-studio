"""
manage_leads.py — Command Line Interface to manage lead statuses in SQLite
==========================================================================
Usage:
  python manage_leads.py --stats
  python manage_leads.py --list --status qualified
  python manage_leads.py --update --name "Aroma Spa" --address "Hauz Khas" --status qualified
"""

import argparse
import sys
import logging
import db_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def show_stats():
    """Print lead summary statistics from the SQLite database."""
    print("\n==============================================")
    print("         LEADS DATABASE STATISTICS            ")
    print("==============================================")
    
    try:
        with db_manager.get_connection() as conn:
            # Total counts
            total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
            print(f"Total leads in database: {total}")
            print("----------------------------------------------")
            
            # Status breakdown
            cur = conn.execute("SELECT status, COUNT(*) as cnt FROM leads GROUP BY status")
            rows = cur.fetchall()
            if not rows:
                print("No leads in database yet.")
            for row in rows:
                status = row["status"]
                cnt = row["cnt"]
                icon = "[Q]" if status == "qualified" else ("[W]" if status == "deal_cracked" else ("[C]" if status == "has_website" else ("[X]" if status == "disqualified" else "[S]")))
                print(f"  {icon} {status:<15}: {cnt}")
            
            # Category breakdown (top 5)
            print("----------------------------------------------")
            print("Top Categories:")
            cur = conn.execute("SELECT category, COUNT(*) as cnt FROM leads GROUP BY category ORDER BY cnt DESC LIMIT 5")
            for row in cur.fetchall():
                print(f"  - {row['category']:<25}: {row['cnt']}")
                
            print("==============================================\n")
    except Exception as e:
        logger.error("Failed to fetch statistics: %s", e)


def list_leads(status_filter=None):
    """List leads filtered by status."""
    print(f"\n==============================================")
    print(f"  LISTING LEADS (Filter: {status_filter or 'All'})")
    print(f"==============================================")
    
    query = "SELECT name, address, phone, website, status, category, competitor_name FROM leads"
    params = []
    
    if status_filter:
        query += " WHERE status = ?"
        params.append(status_filter)
        
    query += " ORDER BY category, name LIMIT 50"
    
    try:
        with db_manager.get_connection() as conn:
            cur = conn.execute(query, params)
            rows = cur.fetchall()
            if not rows:
                print("No leads matching filter found.")
                return
                
            for idx, row in enumerate(rows, 1):
                print(f"{idx}. {row['name']} | Category: {row['category']}")
                print(f"   Address: {row['address']}")
                print(f"   Phone  : {row['phone']} | Website: {row['website']}")
                print(f"   Status : {row['status'].upper()}")
                if row['competitor_name'] and row['competitor_name'] != 'N/A':
                    print(f"   Rival  : {row['competitor_name']}")
                print("-" * 46)
    except Exception as e:
        logger.error("Failed to list leads: %s", e)


def update_status(name, address, status):
    """Update a specific lead's status."""
    if not name or not address:
        print("[ERROR] Both --name and --address are required to locate a unique lead.")
        sys.exit(1)
        
    db_manager.init_db()  # Ensure database exists
    
    # We do a substring search to find the exact lead if they didn't specify the exact address
    # Find matching lead
    try:
        with db_manager.get_connection() as conn:
            cur = conn.execute(
                "SELECT name, address, status FROM leads WHERE LOWER(name) LIKE ? AND LOWER(address) LIKE ?", 
                (f"%{name.lower().strip()}%", f"%{address.lower().strip()}%")
            )
            matches = cur.fetchall()
            
            if not matches:
                print(f"[ERROR] No lead found matching Name: '{name}' and Address: '{address}'")
                return
            
            if len(matches) > 1:
                print("[WARNING] Multiple leads matched. Please be more specific:")
                for idx, m in enumerate(matches, 1):
                    print(f"  [{idx}] Name: {m['name']} | Address: {m['address']}")
                return
            
            # Exact update
            matched_name = matches[0]["name"]
            matched_address = matches[0]["address"]
            success = db_manager.update_lead_status(matched_name, matched_address, status)
            if success:
                print(f"[SUCCESS] Updated status of '{matched_name}' to '{status}'")
            else:
                print(f"[ERROR] Failed to update status of '{matched_name}'")
                
    except Exception as e:
        logger.error("Failed to query and update lead: %s", e)


def main():
    parser = argparse.ArgumentParser(description="Manage Google Maps lead statuses in SQLite")
    parser.add_argument("--stats", action="store_true", help="Show summary statistics")
    parser.add_argument("--list", action="store_true", help="List leads")
    parser.add_argument("--status", type=str, default=None, help="Filter for listing leads, or new status for update")
    parser.add_argument("--update", action="store_true", help="Update status of a lead")
    parser.add_argument("--name", type=str, help="Name of the lead to update")
    parser.add_argument("--address", type=str, help="Address of the lead to update")
    
    args = parser.parse_args()
    
    if args.stats:
        show_stats()
    elif args.list:
        list_leads(args.status)
    elif args.update:
        if not args.status:
            print("[ERROR] --status is required for update action.")
            sys.exit(1)
        update_status(args.name, args.address, args.status)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
