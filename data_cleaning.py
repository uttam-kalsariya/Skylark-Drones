"""
Data Cleaning & Data Quality Module for Skylark Drones BI Agent.

Responsible for:
- Graceful missing/null value handling without raising exceptions.
- Date format normalization across inconsistent input representations.
- Text field cleaning and sector normalization across Deals and Work Orders boards.
- Detection and dropping of embedded duplicate header rows.
- Surface comprehensive data quality audit metrics and column availability caveats.
"""

import logging
import re
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

# Known sector normalization mappings across Deals and Work Orders boards
SECTOR_MAPPINGS: Dict[str, str] = {
    "energy": "Energy",
    "renewables": "Renewables",
    "power": "Powerline",
    "powerline": "Powerline",
    "oil & gas": "Energy",
    "oil and gas": "Energy",
    "solar": "Energy",
    "wind": "Energy",
    "mining": "Mining",
    "minerals": "Mining",
    "quarry": "Mining",
    "infrastructure": "Infrastructure",
    "infra": "Infrastructure",
    "construction": "Construction",
    "roads": "Infrastructure",
    "highways": "Infrastructure",
    "real estate": "Infrastructure",
    "agriculture": "Agriculture",
    "agri": "Agriculture",
    "defense": "Defense",
    "defence": "Defense",
    "utilities": "Utilities",
    "geospatial": "Geospatial Services",
    "geospatial services": "Geospatial Services",
    "gis": "Geospatial Services",
    "railways": "Railways",
    "railway": "Railways",
    "aviation": "Aviation",
    "tender": "Tender",
    "dsp": "DSP",
    "security and surveillance": "Security and Surveillance",
    "manufacturing": "Manufacturing",
    "others": "Others",
}

# Literal header row strings to detect and drop embedded duplicate headers
HEADER_LITERALS = {
    "deal name", "deal name masked", "owner code", "client code", "deal status",
    "close date (a)", "closure probability", "masked deal value", "tentative close date",
    "deal stage", "product deal", "sector/service", "created date",
    "customer name code", "serial #", "nature of work", "execution status",
    "sector", "type of work", "billing status", "invoice status"
}

DATE_FORMATS: List[str] = [
    "%Y-%m-%d",          # 2025-10-25
    "%Y-%m-%dT%H:%M:%S", # 2025-10-25T14:30:00
    "%Y-%m-%d %H:%M:%S", # 2025-10-25 14:30:00
    "%d/%m/%Y",          # 25/10/2025
    "%m/%d/%Y",          # 10/25/2025
    "%d-%m-%Y",          # 25-10-2025
    "%m-%d-%Y",          # 10-25-2025
    "%d %b %Y",          # 25 Oct 2025
    "%d %B %Y",          # 25 October 2025
    "%b %d, %Y",         # Oct 25, 2025
    "%B %d, %Y",         # October 25, 2025
    "%Y/%m/%d",          # 2025/10/25
]


def normalize_date(value: Any) -> Optional[str]:
    """Normalize various date formats into an ISO 8601 string (YYYY-MM-DD)."""
    try:
        if value is None:
            return None
        if isinstance(value, (datetime, date)):
            return value.strftime("%Y-%m-%d")
        
        val_str = str(value).strip()
        if not val_str or val_str.lower() in ("null", "none", "n/a", "na", "undefined", "", "-"):
            return None
        
        val_clean = val_str.split("T")[0].split(" ")[0].strip()
        
        if val_clean.isdigit():
            num = int(val_clean)
            if num > 1e11:
                return datetime.fromtimestamp(num / 1000.0).strftime("%Y-%m-%d")
            elif num > 1e8:
                return datetime.fromtimestamp(num).strftime("%Y-%m-%d")

        for fmt in DATE_FORMATS:
            try:
                dt = datetime.strptime(val_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
            try:
                dt = datetime.strptime(val_clean, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass

        return None
    except Exception as e:
        logger.error(f"Error normalizing date '{value}': {e}")
        return None


def normalize_sector(sector: Any) -> Optional[str]:
    """Normalize sector variations consistently across Deals and Work Orders boards."""
    if sector is None:
        return None
    s = str(sector).strip()
    if not s or s.lower() in ("null", "none", "n/a", "na", "undefined", "-", ""):
        return None
    
    cleaned_lower = re.sub(r"\s+", " ", s).lower()
    if cleaned_lower in SECTOR_MAPPINGS:
        return SECTOR_MAPPINGS[cleaned_lower]
    
    return " ".join(word.capitalize() for word in s.split())


def normalize_text(value: Any, field_name: str = "") -> Optional[str]:
    """Normalize general text strings."""
    try:
        if value is None:
            return None
        
        val_str = str(value).strip()
        if not val_str or val_str.lower() in ("null", "none", "n/a", "na", "undefined", "-", ""):
            return None
        
        val_str = re.sub(r"\s+", " ", val_str)
        field_lower = field_name.lower()

        if "sector" in field_lower or "industry" in field_lower:
            return normalize_sector(val_str)

        return val_str
    except Exception as e:
        logger.error(f"Error normalizing text '{value}': {e}")
        return None


def is_header_row(fields: Dict[str, Any]) -> bool:
    """Detect if a record is an embedded duplicate header row."""
    matches = 0
    for key, val in fields.items():
        if val is None:
            continue
        val_str = str(val).strip().lower()
        key_str = str(key).strip().lower()

        # Direct equality of value to its column key or known header literal
        if val_str == key_str or val_str in HEADER_LITERALS:
            matches += 1
    
    # If 2 or more fields match header names, it's a duplicate header row
    return matches >= 2


def clean_records(records: List[Dict[str, Any]], board_name: str = "") -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Clean and normalize raw board records with duplicate header filtering,
    date/text normalization, and column data availability reporting.
    
    Returns:
        (cleaned_records, quality_report)
    """
    quality_report: Dict[str, Any] = {
        "board_name": board_name,
        "total_input_records": len(records) if isinstance(records, list) else 0,
        "cleaned_records_count": 0,
        "dropped_header_rows": 0,
        "dropped_blank_rows": 0,
        "missing_fields": {},
        "malformed_fields": {},
        "data_availability_caveats": [],
        "warnings": [],
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
                quality_report["dropped_blank_rows"] += 1
                continue

            fields_to_process = {}
            if "columns" in record and isinstance(record["columns"], dict):
                fields_to_process["id"] = record.get("id")
                fields_to_process["name"] = record.get("name")
                fields_to_process["group"] = record.get("group")
                fields_to_process["updated_at"] = record.get("updated_at")
                fields_to_process.update(record["columns"])
            else:
                fields_to_process = record

            # 1. Skip completely blank rows
            non_empty_values = [v for k, v in fields_to_process.items() if v and str(v).strip()]
            if not non_empty_values:
                quality_report["dropped_blank_rows"] += 1
                continue

            # 2. Detect and drop embedded duplicate header rows
            if is_header_row(fields_to_process):
                quality_report["dropped_header_rows"] += 1
                quality_report["warnings"].append(f"Dropped embedded header row at record #{idx}")
                continue

            cleaned_item: Dict[str, Any] = {}

            for key, raw_value in fields_to_process.items():
                key_lower = str(key).lower()

                # Check for missing/null values
                if raw_value is None or str(raw_value).strip().lower() in ("", "null", "none", "n/a", "na", "-"):
                    quality_report["missing_fields"][key] = quality_report["missing_fields"].get(key, 0) + 1
                    cleaned_item[key] = None
                    continue

                # Date fields
                if any(date_kw in key_lower for date_kw in ["date", "created", "updated", "due", "close", "timestamp"]):
                    norm_date = normalize_date(raw_value)
                    if norm_date is None:
                        quality_report["malformed_fields"][key] = quality_report["malformed_fields"].get(key, 0) + 1
                    cleaned_item[key] = norm_date

                # Monetary / numeric fields
                elif any(num_kw in key_lower for num_kw in ["val", "value", "amount", "price", "budget", "cost", "revenue"]):
                    try:
                        raw_str = str(raw_value).replace(",", "").strip()
                        cleaned_num_str = re.sub(r"[^0-9.-]", "", raw_str)
                        cleaned_item[key] = float(cleaned_num_str) if cleaned_num_str else None
                        if cleaned_item[key] is None:
                            quality_report["malformed_fields"][key] = quality_report["malformed_fields"].get(key, 0) + 1
                    except Exception:
                        quality_report["malformed_fields"][key] = quality_report["malformed_fields"].get(key, 0) + 1
                        cleaned_item[key] = None

                # Sector fields
                elif "sector" in key_lower or "industry" in key_lower:
                    norm_sec = normalize_sector(raw_value)
                    if not norm_sec:
                        quality_report["missing_fields"][key] = quality_report["missing_fields"].get(key, 0) + 1
                    cleaned_item[key] = norm_sec

                else:
                    cleaned_item[key] = normalize_text(raw_value, field_name=key)

            cleaned_records.append(cleaned_item)

        except Exception as e:
            msg = f"Error cleaning record #{idx}: {e}"
            logger.error(msg)
            quality_report["warnings"].append(msg)

    # 3. Analyze heavily null columns and surface data availability caveats
    total_valid = len(cleaned_records)
    quality_report["cleaned_records_count"] = total_valid

    if total_valid > 0:
        for col, missing_cnt in quality_report["missing_fields"].items():
            missing_pct = (missing_cnt / total_valid) * 100
            if missing_pct >= 50:
                quality_report["data_availability_caveats"].append(
                    f"Column '{col}' is missing in {missing_cnt}/{total_valid} records ({missing_pct:.0f}% data not available)."
                )

    return cleaned_records, quality_report
