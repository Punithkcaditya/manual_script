#!/usr/bin/env python3
"""
Campaign Visits Export Script
Exports campaign_visits data to CSV with enriched information from related tables.
"""

import os
import sys
import psycopg2
import csv
import json
import re
import ipaddress
import mimetypes
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

INFOBIP_API_KEY = os.getenv("INFOBIP_API_KEY")
INFOBIP_BASE_URL = os.getenv("INFOBIP_BASE_URL", "https://api.infobip.com")
INFOBIP_FROM_EMAIL = os.getenv("INFOBIP_FROM_EMAIL", "no-reply@kots.world")
INFOBIP_FROM_NAME = os.getenv("INFOBIP_FROM_NAME", "KOTS")

DEFAULT_EXPORT_TO = "jayanth.m@kots.world"
DEFAULT_EXPORT_CC = "renukaprasad.s@kots.world,vijeth@kots.world"
# DEFAULT_EXPORT_CC = "renukaprasad.s@kots.world"

def connect_db():
    """Create database connection using environment variables"""
    try:
        return psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", 5432)
        )
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def get_campaign_visits_data(conn):
    """
    Query campaign_visits with all required joins and transformations.
    Returns distinct records based on lead_id.
    """
    try:
        cursor = conn.cursor()
        
        # Complex query with all joins and logic
        query = """
        WITH unique_bookings AS (
            SELECT DISTINCT ON (dummy_order_code)
                id,
                dummy_order_code,
                flat_booking_order_code,
                flat_slug,
                tenant_phone_number
            FROM flat_booking_orders
            WHERE flat_booking_order_code IS NOT NULL
              AND flat_booking_order_code <> '-'
            ORDER BY dummy_order_code, created_at DESC
        ),
        distinct_visits AS (
            SELECT DISTINCT ON (cv.ip_address)
                cv.id,
                cv.timestamp,
                cv.ip_address,
                cv.created_at,
                cv.referrer,
                cv.user_agent,
                cv.area,
                cv.city,
                cv.flat_id,
                cv.dummy_order_code,
                cv.campaign_id,
                cv.lead_id,
                cv.page,

                CASE
                    WHEN cv.campaign_id LIKE 'M00%' THEN 'META'
                    ELSE 'GOOGLE'
                END AS source,

                CASE
                    WHEN cv.page = 'whatsapp_click' THEN 'whatsapp'
                    WHEN ce.id IS NOT NULL THEN 'paidlead_form'
                    WHEN sw.id IS NOT NULL THEN 'phone_call'
                    ELSE NULL
                END AS action_type,

                CASE
                    WHEN ub.dummy_order_code IS NOT NULL THEN 'YES'
                    ELSE 'No'
                END AS bookings,

                COALESCE(flat_last.flat_id::text, cv.flat_id::text, '') AS flat_view,
                COALESCE(prop_last.property_id::text, NULLIF(cv.property_id::text, ''), '') AS property_id

            FROM public.campaign_visits cv

            LEFT JOIN unique_bookings ub
                ON cv.dummy_order_code = ub.dummy_order_code

            LEFT JOIN contact_enquiries ce
                ON ce.ip::text = cv.ip_address::text

            LEFT JOIN sales_webhook sw
                ON ub.tenant_phone_number IS NOT NULL
                AND sw.phone = CONCAT('+91', ub.tenant_phone_number)

            LEFT JOIN LATERAL (
                SELECT cv3.flat_id
                FROM campaign_visits cv3
                WHERE cv3.lead_id = cv.lead_id
                  AND cv3.page = 'flat-detail'
                  AND cv3.flat_id IS NOT NULL
                ORDER BY cv3."timestamp" DESC, cv3.id DESC
                LIMIT 1
            ) AS flat_last ON TRUE

            LEFT JOIN LATERAL (
                SELECT cv2.property_id
                FROM campaign_visits cv2
                WHERE cv2.lead_id = cv.lead_id
                  AND cv2.page = 'property-detail'
                  AND cv2.property_id IS NOT NULL
                  AND cv2.property_id <> ''
                ORDER BY cv2."timestamp" DESC, cv2.id DESC
                LIMIT 1
            ) AS prop_last ON TRUE

            WHERE cv.timestamp >= TIMESTAMPTZ '2026-02-17 18:30:00+00'
            AND cv.timestamp <  TIMESTAMPTZ '2026-02-24 18:30:00+00'
            ORDER BY cv.ip_address, cv.timestamp DESC
        )
        SELECT 
            timestamp::date AS date,
            campaign_id,
            source,
            action_type,
            page AS page_url,
            bookings,
            ip_address::text AS ip_address,
            flat_view,
            property_id,
            user_agent,
            timestamp AS time_stamp
        FROM distinct_visits
        ORDER BY timestamp DESC
        """
        
        logger.info("Executing query to fetch campaign visits data...")
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        logger.info(f"Retrieved {len(rows)} distinct records")
        cursor.close()
        
        return columns, rows
        
    except Exception as e:
        logger.error(f"Error retrieving data from database: {e}")
        raise

def get_geo_from_ip(ip_address):
    """
    Get geographical information from an IP address using ip-api.com.
    """
    try:
        if not ip_address:
            return {'error': 'Missing IP address'}

        url = f"http://ip-api.com/json/{ip_address}"
        timeout_seconds = float(os.getenv("GEO_LOOKUP_TIMEOUT_SECONDS", "2"))
        response = requests.get(url, timeout=timeout_seconds)
        response.raise_for_status()

        data = response.json()
        if data.get('status') == 'success':
            return {
                'ip': data.get('query'),
                'country': data.get('country'),
                'country_code': data.get('countryCode'),
                'region': data.get('regionName'),
                'region_code': data.get('region'),
                'city': data.get('city'),
                'district': data.get('district', ''),
                'zip_code': data.get('zip'),
                'latitude': data.get('lat'),
                'longitude': data.get('lon'),
                'timezone': data.get('timezone'),
                'isp': data.get('isp'),
                'organization': data.get('org'),
                'as_number': data.get('as')
            }

        return {'error': data.get('message', 'Unknown error')}

    except requests.exceptions.RequestException as e:
        return {'error': f'Request failed: {str(e)}'}
    except json.JSONDecodeError:
        return {'error': 'Failed to parse response'}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}

def _is_public_ip(ip_address):
    """Return True when IP is a globally routable public IP."""
    try:
        return ipaddress.ip_address(ip_address).is_global
    except ValueError:
        return False

def _format_geography(geo_data):
    """Format geography text as: district, city, region, country."""
    if not geo_data or 'error' in geo_data:
        return ''
    parts = [
        geo_data.get('district'),
        geo_data.get('city'),
        geo_data.get('region'),
        geo_data.get('country')
    ]
    return ', '.join([p for p in parts if p])

def _load_geo_cache(cache_file):
    """Load persisted IP geography cache from disk."""
    if not cache_file or not os.path.exists(cache_file):
        return {}
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            raw_cache = json.load(f)
        if not isinstance(raw_cache, dict):
            return {}
        cleaned_cache = {}
        for ip, value in raw_cache.items():
            if isinstance(value, dict):
                cleaned_cache[str(ip)] = _format_geography(value)
            else:
                cleaned_cache[str(ip)] = str(value) if value else ''
        return cleaned_cache
    except Exception as e:
        logger.warning(f"Unable to load geo cache file {cache_file}: {e}")
        return {}

def _save_geo_cache(cache_file, cache_data):
    """Persist IP geography cache to disk."""
    if not cache_file:
        return
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=True)
    except Exception as e:
        logger.warning(f"Unable to save geo cache file {cache_file}: {e}")

def _safe_int_env(name, default):
    """Get positive int env var with fallback default."""
    try:
        value = int(os.getenv(name, str(default)))
        return value if value > 0 else default
    except (TypeError, ValueError):
        return default

def _parse_emails(value):
    """Parse comma-separated emails into a clean list."""
    if not value:
        return []
    return [email.strip() for email in str(value).split(',') if email.strip()]

def _send_email_with_cc_bcc_attachment(to_email: str, subject: str, text: str, attachment_path: str, cc=None, bcc=None):
    """
    Send email using Infobip Email API with CC/BCC and one attachment.
    If Infobip config is missing, simulates email and returns success.
    """
    cc = cc or []
    bcc = bcc or []

    if not INFOBIP_API_KEY:
        logger.info("[DEV] EMAIL SIMULATED (Infobip not configured)")
        logger.info("To: %s", to_email)
        logger.info("CC: %s", ", ".join(cc) if cc else "")
        logger.info("BCC: %s", ", ".join(bcc) if bcc else "")
        logger.info("Subject: %s", subject)
        logger.info("Attachment: %s", attachment_path)
        return True, "Email simulated (Infobip not configured)."

    if not attachment_path or not os.path.exists(attachment_path):
        return False, f"Attachment not found: {attachment_path}"

    try:
        url = f"{INFOBIP_BASE_URL.rstrip('/')}/email/3/send"
        headers = {
            "Authorization": f"App {INFOBIP_API_KEY}"
        }
        payload = {
            "from": f"{INFOBIP_FROM_NAME} <{INFOBIP_FROM_EMAIL}>",
            "to": to_email,
            "subject": subject,
            "text": text
        }
        if cc:
            payload["cc"] = ", ".join(cc) if isinstance(cc, (list, tuple)) else str(cc)
        if bcc:
            payload["bcc"] = ", ".join(bcc) if isinstance(bcc, (list, tuple)) else str(bcc)

        guessed_content_type = mimetypes.guess_type(attachment_path)[0] or "application/octet-stream"
        with open(attachment_path, "rb") as attachment_file:
            files = {
                "attachment": (os.path.basename(attachment_path), attachment_file, guessed_content_type)
            }
            response = requests.post(url, headers=headers, data=payload, files=files, timeout=45)

        if 200 <= response.status_code < 300:
            return True, f"Email sent via Infobip. Response: {response.text}"
        return False, f"Infobip error {response.status_code}: {response.text}"

    except Exception as e:
        return False, f"Infobip error: {e}"

def send_export_email(output_file, record_count):
    """Send campaign export CSV to configured recipients."""
    to_email = os.getenv("CAMPAIGN_EXPORT_TO", DEFAULT_EXPORT_TO)
    cc_emails = _parse_emails(os.getenv("CAMPAIGN_EXPORT_CC", DEFAULT_EXPORT_CC))
    bcc_emails = _parse_emails(os.getenv("CAMPAIGN_EXPORT_BCC", ""))

    report_date = datetime.now().strftime("%Y-%m-%d")
    subject = f"Campaign Visits Export - {report_date}"
    text = (
        f"Hi Team,\n\n"
        f"Please find attached the campaign visits export CSV.\n"
        f"Total records: {record_count}\n"
        f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"Regards,\n"
        f"KOTS Automation"
    )

    success, message = _send_email_with_cc_bcc_attachment(
        to_email=to_email,
        subject=subject,
        text=text,
        attachment_path=output_file,
        cc=cc_emails,
        bcc=bcc_emails
    )
    if success:
        logger.info(message)
    else:
        logger.error(message)
    return success

def _parse_user_agent(user_agent_string: str):
    """
    Parse user agent string to extract device type, OS, and model.

    Returns:
        Dict with keys: device_type, device_os, device_model
    """
    if not user_agent_string:
        return {
            "device_type": "Unknown",
            "device_os": "Unknown",
            "device_model": "Unknown"
        }

    ua = user_agent_string.lower()
    device_type = "Desktop"
    device_os = "Unknown"
    device_model = "Unknown"

    if any(mobile_indicator in ua for mobile_indicator in ['mobile', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone']):
        if 'tablet' in ua or 'ipad' in ua:
            device_type = "Tablet"
        else:
            device_type = "Mobile"

    if 'windows' in ua:
        if 'windows nt 11' in ua or 'windows 11' in ua:
            device_os = "Windows 11"
        elif 'windows nt 10' in ua or 'windows 10' in ua:
            device_os = "Windows 10"
        elif 'windows nt 6.3' in ua:
            device_os = "Windows 8.1"
        elif 'windows nt 6.2' in ua:
            device_os = "Windows 8"
        elif 'windows nt 6.1' in ua:
            device_os = "Windows 7"
        else:
            device_os = "Windows"
    elif 'mac os' in ua or 'macos' in ua:
        device_os = "macOS"
    elif 'android' in ua:
        android_match = re.search(r'android\s+([\d.]+)', ua)
        if android_match:
            device_os = f"Android {android_match.group(1)}"
        else:
            device_os = "Android"
    elif 'iphone' in ua or 'ipad' in ua or 'ipod' in ua:
        ios_match = re.search(r'os\s+([\d_]+)', ua)
        if ios_match:
            version = ios_match.group(1).replace('_', '.')
            device_os = f"iOS {version}"
        else:
            device_os = "iOS"
    elif 'linux' in ua:
        device_os = "Linux"

    if device_type in ["Mobile", "Tablet"]:
        if 'iphone' in ua:
            device_model = "iPhone"
        elif 'ipad' in ua:
            device_model = "iPad"
        elif 'android' in ua:
            model_match = re.search(r';\s*([a-z0-9\s-]+)\s*\)', ua)
            if model_match:
                model = model_match.group(1).strip()
                model = re.sub(r'^(build|wv|linux|android)', '', model, flags=re.I).strip()
                if model:
                    device_model = model

    return {
        "device_type": device_type,
        "device_os": device_os,
        "device_model": device_model
    }

def export_to_csv(columns, rows, output_file='campaign_visits_export.csv'):
    """Export data to CSV file"""
    try:
        # Map database column names to CSV column names
        csv_column_mapping = {
            'date': 'Date',
            'campaign_id': 'campaign_id',
            'source': 'Source',
            'action_type': 'action_type (whatsapp / phone_call / paidlead_form)',
            'page_url': 'page_url',
            'bookings': 'Bookings',
            'ip_address': 'IP ADRESS',
            'geography': 'GEOGRAPHY',
            'device_type': 'DEVICE TYPE',
            'device_os': 'DEVICE OS',
            'device_model': 'DEVICE MODEL',
            'flat_view': 'FLAT VIEW',
            'property_id': 'PROPERTY ID',
            'time_stamp': 'Time Stamp'
        }
        
        # Create CSV with proper column order
        csv_columns = [
            'Date',
            'campaign_id',
            'Source',
            'action_type (whatsapp / phone_call / paidlead_form)',
            'page_url',
            'Bookings',
            'IP ADRESS',
            'GEOGRAPHY',
            'DEVICE TYPE',
            'DEVICE OS',
            'DEVICE MODEL',
            'FLAT VIEW',
            'PROPERTY ID',
            'Time Stamp'
        ]
        
        logger.info(f"Writing data to {output_file}...")

        row_dicts = [dict(zip(columns, row)) for row in rows]
        geo_enabled = os.getenv("ENABLE_GEO_LOOKUP", "true").strip().lower() not in {"0", "false", "no"}
        geo_cache_file = os.getenv("GEO_CACHE_FILE", "ip_geo_cache.json")
        geo_max_new_lookups = _safe_int_env("GEO_MAX_NEW_LOOKUPS", 120)
        geo_workers = _safe_int_env("GEO_LOOKUP_WORKERS", 8)

        geo_cache = _load_geo_cache(geo_cache_file) if geo_enabled else {}
        if geo_enabled:
            unique_ips = sorted({
                str(r.get('ip_address')).strip()
                for r in row_dicts
                if r.get('ip_address')
            })
            missing_ips = [
                ip for ip in unique_ips
                if ip and ip not in geo_cache and _is_public_ip(ip)
            ]
            if len(missing_ips) > geo_max_new_lookups:
                logger.info(
                    "Geography lookup limited to %s new IPs (out of %s missing). "
                    "Tune GEO_MAX_NEW_LOOKUPS for more.",
                    geo_max_new_lookups,
                    len(missing_ips)
                )
                missing_ips = missing_ips[:geo_max_new_lookups]

            if missing_ips:
                logger.info(
                    "Resolving geography for %s IPs with %s workers (cache file: %s)...",
                    len(missing_ips),
                    geo_workers,
                    geo_cache_file
                )
                with ThreadPoolExecutor(max_workers=geo_workers) as executor:
                    future_to_ip = {
                        executor.submit(get_geo_from_ip, ip): ip for ip in missing_ips
                    }
                    for future in as_completed(future_to_ip):
                        ip = future_to_ip[future]
                        try:
                            geo_data = future.result()
                        except Exception:
                            geo_data = {'error': 'lookup_failed'}
                        geo_cache[ip] = _format_geography(geo_data)
                _save_geo_cache(geo_cache_file, geo_cache)
            else:
                logger.info("No new public IPs needed for geography lookup. Using cached values.")
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            ua_cache = {}
            
            # Write header
            writer.writerow(csv_columns)
            
            # Write data rows
            for row_dict in row_dicts:
                
                # Helper function to format values
                def format_value(value):
                    if value is None:
                        return ''
                    # Handle datetime objects
                    if isinstance(value, datetime):
                        return value.strftime('%Y-%m-%d %H:%M:%S')
                    # Handle date objects (from timestamp::date)
                    if hasattr(value, 'strftime'):
                        try:
                            return value.strftime('%Y-%m-%d')
                        except:
                            return str(value)
                    return str(value)

                def get_geography_value(ip_address):
                    ip = format_value(ip_address).strip()
                    if not ip:
                        return ''
                    return geo_cache.get(ip, '')

                def get_device_info(user_agent):
                    ua = format_value(user_agent)
                    if ua not in ua_cache:
                        ua_cache[ua] = _parse_user_agent(ua)
                    return ua_cache[ua]

                device_info = get_device_info(row_dict.get('user_agent'))
                
                # Format the row according to CSV column order
                csv_row = [
                    format_value(row_dict.get('date')),  # Date
                    format_value(row_dict.get('campaign_id')),  # campaign_id
                    format_value(row_dict.get('source')),  # Source
                    format_value(row_dict.get('action_type')),  # action_type
                    format_value(row_dict.get('page_url')),  # page_url
                    format_value(row_dict.get('bookings', 'No')),  # Bookings
                    format_value(row_dict.get('ip_address')),  # IP ADRESS
                    get_geography_value(row_dict.get('ip_address')),  # GEOGRAPHY
                    format_value(device_info.get('device_type')),  # DEVICE TYPE
                    format_value(device_info.get('device_os')),  # DEVICE OS
                    format_value(device_info.get('device_model')),  # DEVICE MODEL
                    format_value(row_dict.get('flat_view')),  # FLAT VIEW
                    format_value(row_dict.get('property_id')),  # PROPERTY ID
                    format_value(row_dict.get('time_stamp'))  # Time Stamp
                ]
                
                writer.writerow(csv_row)
        
        logger.info(f"Successfully exported {len(rows)} records to {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        raise

def main():
    """Main function"""
    logger.info("="*60)
    logger.info("Campaign Visits Export Script")
    logger.info("="*60)
    
    # Connect to database
    conn = None
    try:
        conn = connect_db()
        logger.info("Database connection established")
        
        # Get data
        columns, rows = get_campaign_visits_data(conn)
        
        if not rows:
            logger.warning("No data found to export")
            return
        
        # Export to CSV
        output_file = export_to_csv(columns, rows)

        if os.getenv("SEND_EMAIL_AFTER_EXPORT", "true").strip().lower() in {"1", "true", "yes"}:
            logger.info("Sending export email...")
            email_success = send_export_email(output_file, len(rows))
            if not email_success:
                raise RuntimeError("Failed to send export email")
        else:
            logger.info("Email sending is disabled (SEND_EMAIL_AFTER_EXPORT=false)")
        
        logger.info("="*60)
        logger.info(f"Export completed successfully!")
        logger.info(f"Output file: {output_file}")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)
        
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    main()
