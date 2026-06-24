from sqlalchemy.orm import Session
from app.models import Asset, Target
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger("AssetInventory")

class AssetInventory:
    @staticmethod
    def save_discovered_assets(db: Session, target_id: int, assets: List[Dict[str, Any]]) -> int:
        """
        Saves a list of discovered assets into the database, avoiding duplicates.
        Returns the number of newly added assets.
        """
        added_count = 0
        existing_assets = db.query(Asset.url, Asset.method, Asset.asset_type).filter(
            Asset.target_id == target_id
        ).all()
        
        # Build cache for fast lookups
        cache = {(url, method, atype) for url, method, atype in existing_assets}
        
        for asset in assets:
            url = asset.get("url", "")
            method = asset.get("method", "GET")
            asset_type = asset.get("asset_type", "page")
            
            if (url, method, asset_type) in cache:
                continue
                
            db_asset = Asset(
                target_id=target_id,
                url=url,
                asset_type=asset_type,
                method=method,
                parameters=asset.get("parameters", "[]"),
                headers=asset.get("headers", "{}"),
                cookies=asset.get("cookies", "{}")
            )
            db.add(db_asset)
            cache.add((url, method, asset_type))
            added_count += 1
            
        try:
            db.commit()
            logger.info(f"Saved {added_count} new assets to inventory for target {target_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving assets to database: {e}")
            
        return added_count

    @staticmethod
    def get_assets_by_target(db: Session, target_id: int) -> List[Asset]:
        return db.query(Asset).filter(Asset.target_id == target_id).all()
