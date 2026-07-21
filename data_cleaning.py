"""
Data Cleaning & Data Quality Module for Skylark Drones BI Agent.

Responsible for:
- Graceful missing/null value handling without raising exceptions.
- Date format normalization across inconsistent input representations (ISO, US, EU, epoch, relative, etc.).
- Text field cleaning and normalization (lowercasing, whitespace collapsing, sector variant mapping).
- Surface comprehensive data quality audit metrics and warnings per column/record.
"""

import logging
import re
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple, Union

# Set up logger for data cleaning module
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

# Known sector normalization mappings
SECTOR_MAPPINGS: Dict[str, str] = {
    "energy": "Energy",
    "renewables": "Energy",
    "power": "Energy",
    "oil & gas": "Energy",
    "oil and gas": "Energy",
    "solar": "Energy",
    "wind": "Energy",
    "mining": "Mining",
    "minerals": "Mining",
    "quarry": "Mining",
    "infrastructure": "Infrastructure",
    "infra": "Infrastructure",
    "construction": "Infrastructure",
    "roads": "Infrastructure",
    "highways": "Infrastructure",
    "real estate": "Infrastructure",
    "agriculture": "Agriculture",
    "agri": "Agriculture",
    "farming": "Agriculture",
    "defense": "Defense",
    "defence": "Defense",
    "military": "Defense",
    "utilities": "Utilities",
    "telecom": "Utilities",
    "geospatial": "Geospatial Services",
    "mapping": "Geospatial Services",
    "gis": "Geospatial Services",
}

# Common date formats to attempt parsing
DATE_FORMATS: List[str] = [
    "%Y-%m-%d",          # 2023-10-25
    "%Y-%m-%dT%H:%M:%S", # 2023-10-25T14:30:00
    "%Y-%m-%d %H:%M:%S", # 2023-10-25 14:30:00
    "%d/%m/%Y",          # 25/10/2023
    "%m/%d/%Y",          # 10/25/2023
    "%d-%m-%Y",          # 25-10-2023
    "%m-%d-%Y",          # 10-25-2023
    "%d %b %Y",          # 25 Oct 2023
    "%d %B %Y",          # 25 October 2023
    "%b %d, %Y",         # Oct 25, 2023
    "%B %d, %Y",         # October 25, 2023
    "%Y/%m/%d",          # 2023/10/25
]


def normalize_date(value: Any) -> Optional[str]:
    """
    Normalize various date formats into an ISO 8601 string standard format (YYYY-MM-DD).
    Returns None if unparseable or empty/null. Never raises an exception.
    """
    try:
        if value is None:
            return None
        
        # Handle datetime/date objects directly
        if isinstance(value, (datetime, date)):
            return value.strftime("%Y-%m-%d")
        
        # String processing
        val_str = str(value).strip()
        if not val_str or val_str.lower() in ("null", "none", "n/a", "na", "undefined", "", "-"):
            return None
        
        # Remove time portions if appended with timezone or timestamp ISO strings
        val_clean = val_str.split("T")[0].split(" ")[0].strip()
        
        # Try parsing standard epoch timestamps (milliseconds or seconds)
        if val_clean.isdigit():
            num = int(val_clean)
            if num > 1e11:  # Milliseconds epoch
                return datetime.fromtimestamp(num / 1000.0).strftime("%Y-%m-%d")
            elif num > 1e8:  # Seconds epoch
                return datetime.fromtimestamp(num).strftime("%Y-%m-%d")

        # Try predefined date formats
        for fmt in DATE_FORMATS:
            try:
                dt = datetime.strptime(val_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
            
            # Try matching stripped clean date string
            try:
                dt = datetime.strptime(val_clean, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass

        logger.warning(f"Could not parse date value: {value}")
        return None
    except Exception as e:
        logger.error(f"Error normalizing date '{value}': {e}")
        return None


def normalize_text(value: Any, field_name: str = "") -> Optional[str]:
    """
    Normalize text input: strip leading/trailing whitespace, lowercase, collapse internal whitespace,
    and collapse known variants (e.g. sector names like "energy", "ENERGY ", " oil & gas ").
    Never raises an exception.
    """
    try:
        if value is None:
            return None
        
        val_str = str(value).strip()
        if not val_str or val_str.lower() in ("null", "none", "n/a", "na", "undefined", "-", ""):
            return None
        
        # Collapse multiple internal spaces
        val_str = re.sub(r"\s+", " ", val_str)
        cleaned_lower = val_str.lower()
        
        # If normalizing a sector field or generic text matching known sector mapping
        if "sector" in field_name.lower() or cleaned_lower in SECTOR_MAPPINGS:
            if cleaned_lower in SECTOR_MAPPINGS:
                return SECTOR_MAPPINGS[cleaned_lower]
            # Capitalize each word for standard sector formatting
            return val_str.title()
        
        return val_str
    except Exception as e:
        logger.error(f"Error normalizing text '{value}': {e}")
        return None


def clean_records(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Takes raw monday.com items or dict records, returns (cleaned_records, quality_report).
    
    Data quality report format:
    {
        "total_records": int,
        "missing_fields": Dict[str, int],
        "malformed_fields": Dict[str, int],
        "warnings": List[str]
    }
    
    Never raises an exception — degrades gracefully.
    """
    quality_report: Dict[str, Any] = {
        "total_records": len(records) if isinstance(records, list) else 0,
        "missing_fields": {},
        "malformed_fields": {},
        "warnings": []
    }
    
    if not isinstance(records, list):
        msg = f"Invalid input to clean_records: expected list, got {type(records)}"
        logger.error(msg)
        quality_report["warnings"].append(msg)
        return [], quality_report

    cleaned_records: List[Dict[str, Any]] = []

    for idx, record in enumerate(records):
        try:
            if not isinstance(record, dict):
                quality_report["warnings"].append(f"Record at index {idx} is not a dictionary. Skipping.")
                continue

            cleaned_item: Dict[str, Any] = {}
            
            for key, raw_value in record.items():
                key_lower = str(key).lower()
                
                # Check for missing values
                if raw_value is None or str(raw_value).strip().lower() in ("", "null", "none", "n/a", "na", "-"):
                    quality_report["missing_fields"][key] = quality_report["missing_fields"].get(key, 0) + 1
                    cleaned_item[key] = None
                    continue

                # Process based on column/field type hints
                if any(date_kw in key_lower for date_kw in ["date", "created", "updated", "due", "close", "timestamp"]):
                    norm_date = normalize_date(raw_value)
                    if norm_date is None:
                        quality_report["malformed_fields"][key] = quality_report["malformed_fields"].get(key, 0) + 1
                    cleaned_item[key] = norm_date

                elif any(num_kw in key_lower for num_kw in ["val", "value", "amount", "price", "budget", "cost", "revenue"]):
                    try:
                        # Clean currency symbols or numeric strings (e.g., "$10,000" -> 10000.0)
                        cleaned_num_str = re.sub(r"[^\d.-]", "", str(raw_value))
                        cleaned_item[key] = float(cleaned_num_str) if cleaned_num_str else None
                        if cleaned_item[key] is None:
                            quality_report["malformed_fields"][key] = quality_report["malformed_fields"].get(key, 0) + 1
                    except Exception:
                        quality_report["malformed_fields"][key] = quality_report["malformed_fields"].get(key, 0) + 1
                        cleaned_item[key] = None
                else:
                    # Text / categorical normalization
                    cleaned_item[key] = normalize_text(raw_value, field_name=key)

            cleaned_records.append(cleaned_item)

        except Exception as e:
            msg = f"Unexpected error processing record index {idx}: {e}"
            logger.error(msg)
            quality_report["warnings"].append(msg)
            cleaned_records.append(record if isinstance(record, dict) else {})

    return cleaned_records, quality_report
