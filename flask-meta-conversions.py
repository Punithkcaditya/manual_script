"""
Flask Meta Conversions API Implementation
Handles server-side conversion tracking to Meta (Facebook) for better attribution
"""

import hashlib
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests
from flask import Flask, request, jsonify

# Required packages:
# pip install flask requests

class MetaConversionsService:
    """
    Meta Conversions API Service for Flask
    Handles server-side event tracking to Meta (Facebook)
    """
    
    def __init__(self, pixel_id: str, access_token: str, api_version: str = "v19.0"):
        self.pixel_id = pixel_id
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}/{pixel_id}/events"
        
    def _hash_user_data(self, data: str) -> str:
        """Hash sensitive user data as required by Meta"""
        return hashlib.sha256(data.lower().strip().encode()).hexdigest()
    
    def _prepare_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare user data with proper hashing"""
        prepared = user_data.copy()
        
        # Hash sensitive fields
        if 'em' in prepared and prepared['em']:
            prepared['em'] = self._hash_user_data(prepared['em'])
        if 'ph' in prepared and prepared['ph']:
            # Remove non-numeric characters from phone
            phone = ''.join(filter(str.isdigit, prepared['ph']))
            prepared['ph'] = self._hash_user_data(phone)
        if 'fn' in prepared and prepared['fn']:
            prepared['fn'] = self._hash_user_data(prepared['fn'])
        if 'ln' in prepared and prepared['ln']:
            prepared['ln'] = self._hash_user_data(prepared['ln'])
        if 'ct' in prepared and prepared['ct']:
            prepared['ct'] = self._hash_user_data(prepared['ct'])
        if 'st' in prepared and prepared['st']:
            prepared['st'] = self._hash_user_data(prepared['st'])
        if 'zp' in prepared and prepared['zp']:
            prepared['zp'] = self._hash_user_data(prepared['zp'])
        if 'external_id' in prepared and prepared['external_id']:
            prepared['external_id'] = self._hash_user_data(str(prepared['external_id']))
            
        return prepared
    
    def send_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send conversion event to Meta"""
        try:
            # Prepare the event data
            prepared_event = {
                'event_name': event_data.get('event_name'),
                'event_time': event_data.get('event_time', int(time.time())),
                'user_data': self._prepare_user_data(event_data.get('user_data', {})),
                'action_source': event_data.get('action_source', 'website')
            }
            
            # Add optional fields
            if 'event_id' in event_data:
                prepared_event['event_id'] = event_data['event_id']
            if 'custom_data' in event_data:
                prepared_event['custom_data'] = event_data['custom_data']
            if 'event_source_url' in event_data:
                prepared_event['event_source_url'] = event_data['event_source_url']
            if 'opt_out' in event_data:
                prepared_event['opt_out'] = event_data['opt_out']
            
            # Prepare request payload
            payload = {
                'data': [prepared_event],
                'access_token': self.access_token
            }
            
            # Add test event code for development
            if os.getenv('FLASK_ENV') == 'development':
                payload['test_event_code'] = 'TEST12345'
            
            # Send request to Meta
            response = requests.post(
                self.base_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            print(f"Meta Conversion Event sent successfully: {event_data.get('event_name')}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Meta Conversions API Error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error in Meta tracking: {e}")
            raise

# Initialize Flask app
app = Flask(__name__)

# Configuration - get from environment variables
PIXEL_ID = os.getenv('META_PIXEL_ID', '611397144049399')  # Your pixel ID
ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN', 'EAAVeDVIwm3QBPRDGzWL6JqUCYVfcwWAb08uaZAdPQpWmyitus7BI8dWm8WoJYgsUYEaL1AOZAWIzyYHDkx5LSuxUzscqX8VRi8k4pfuqeqZAZAtYyYb37a3jIHXGrXv9wS62AQ18Q4TuY8bWNcf63KEUhWde6UXdSm2WZAjmeM4EIdYLzUHGxl2NnBtBS7gVu0AZDZD')

# Initialize Meta service
meta_service = MetaConversionsService(PIXEL_ID, ACCESS_TOKEN)

def get_client_ip():
    """Get client IP address from request headers"""
    return (
        request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or
        request.headers.get('X-Real-IP') or
        request.headers.get('CF-Connecting-IP') or
        request.remote_addr or
        '127.0.0.1'
    )

@app.route('/api/meta/track-conversion', methods=['POST'])
def track_conversion():
    """
    Track Meta conversion event
    
    Expected JSON payload:
    {
        "event_name": "Purchase",
        "user_data": {
            "em": "user@example.com",
            "ph": "+919876543210",
            "fn": "John",
            "ln": "Doe"
        },
        "custom_data": {
            "currency": "INR",
            "value": 25000,
            "order_id": "order_123"
        },
        "event_source_url": "https://yoursite.com/checkout"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Validate required fields
        if not data.get('event_name') or not data.get('user_data'):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: event_name and user_data'
            }), 400
        
        # Get client information
        client_ip = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')
        referer = request.headers.get('Referer', '')
        
        # Prepare event data
        event_data = {
            'event_name': data['event_name'],
            'event_time': data.get('event_time', int(time.time())),
            'user_data': {
                **data['user_data'],
                'client_ip_address': client_ip,
                'client_user_agent': user_agent
            },
            'action_source': data.get('action_source', 'website'),
            'event_source_url': data.get('event_source_url', referer)
        }
        
        # Add optional fields
        if 'event_id' in data:
            event_data['event_id'] = data['event_id']
        if 'custom_data' in data:
            event_data['custom_data'] = data['custom_data']
        if 'opt_out' in data:
            event_data['opt_out'] = data['opt_out']
        
        # Send to Meta
        result = meta_service.send_event(event_data)
        
        return jsonify({
            'success': True,
            'events_received': result.get('events_received', 0),
            'events_dropped': result.get('events_dropped', 0),
            'messages': result.get('messages', [])
        })
        
    except requests.exceptions.RequestException as e:
        print(f"Meta API Error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to send event to Meta'
        }), 500
        
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# Helper routes for common events

@app.route('/api/meta/track-purchase', methods=['POST'])
def track_purchase():
    """Track purchase event with simplified interface"""
    try:
        data = request.get_json()
        
        event_data = {
            'event_name': 'Purchase',
            'user_data': data.get('user_data', {}),
            'custom_data': {
                'currency': data.get('currency', 'INR'),
                'value': data.get('value', 0),
                'order_id': data.get('order_id'),
                'content_ids': data.get('content_ids', []),
                'content_type': data.get('content_type', 'product'),
                'num_items': data.get('num_items', 1)
            },
            'event_source_url': data.get('event_source_url')
        }
        
        # Use the main tracking function
        return track_conversion_internal(event_data)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/meta/track-lead', methods=['POST'])
def track_lead():
    """Track lead event with simplified interface"""
    try:
        data = request.get_json()
        
        event_data = {
            'event_name': 'Lead',
            'user_data': data.get('user_data', {}),
            'custom_data': {
                'content_name': data.get('content_name'),
                'content_category': data.get('content_category', 'lead_generation'),
                'value': data.get('value'),
                'currency': data.get('currency', 'INR')
            },
            'event_source_url': data.get('event_source_url')
        }
        
        return track_conversion_internal(event_data)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/meta/track-page-view', methods=['POST'])
def track_page_view():
    """Track page view event"""
    try:
        data = request.get_json()
        
        event_data = {
            'event_name': 'PageView',
            'user_data': data.get('user_data', {}),
            'event_source_url': data.get('event_source_url')
        }
        
        return track_conversion_internal(event_data)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def track_conversion_internal(event_data):
    """Internal function to handle conversion tracking"""
    # Get client information
    client_ip = get_client_ip()
    user_agent = request.headers.get('User-Agent', '')
    referer = request.headers.get('Referer', '')
    
    # Add client data to user_data
    if 'user_data' not in event_data:
        event_data['user_data'] = {}
    
    event_data['user_data'].update({
        'client_ip_address': client_ip,
        'client_user_agent': user_agent
    })
    
    if not event_data.get('event_source_url'):
        event_data['event_source_url'] = referer
    
    # Send to Meta
    result = meta_service.send_event(event_data)
    
    return jsonify({
        'success': True,
        'events_received': result.get('events_received', 0),
        'events_dropped': result.get('events_dropped', 0),
        'messages': result.get('messages', [])
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
