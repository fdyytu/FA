import midtransclient
from app.core.config import settings
from typing import Dict, Any
import uuid
from decimal import Decimal

class MidtransService:
    def __init__(self):
        self.snap = midtransclient.Snap(
            is_production=settings.MIDTRANS_IS_PRODUCTION,
            server_key=settings.MIDTRANS_SERVER_KEY,
            client_key=settings.MIDTRANS_CLIENT_KEY
        )
        
        self.core_api = midtransclient.CoreApi(
            is_production=settings.MIDTRANS_IS_PRODUCTION,
            server_key=settings.MIDTRANS_SERVER_KEY,
            client_key=settings.MIDTRANS_CLIENT_KEY
        )
    
    def create_payment_token(
        self, 
        order_id: str, 
        amount: Decimal, 
        customer_details: Dict[str, Any],
        item_details: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create payment token for Snap payment"""
        
        if item_details is None:
            item_details = [{
                'id': 'topup',
                'price': int(amount),
                'quantity': 1,
                'name': 'Wallet Top Up'
            }]
        
        transaction_details = {
            'order_id': order_id,
            'gross_amount': int(amount)
        }
        
        param = {
            'transaction_details': transaction_details,
            'customer_details': customer_details,
            'item_details': item_details,
            'credit_card': {
                'secure': True
            }
        }
        
        try:
            transaction = self.snap.create_transaction(param)
            return {
                'success': True,
                'token': transaction['token'],
                'redirect_url': transaction['redirect_url'],
                'order_id': order_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_transaction_status(self, order_id: str) -> Dict[str, Any]:
        """Get transaction status from Midtrans"""
        try:
            status_response = self.core_api.transactions.status(order_id)
            return {
                'success': True,
                'data': status_response
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify notification from Midtrans webhook"""
        try:
            status_response = self.core_api.transactions.notification(notification_data)
            
            order_id = status_response['order_id']
            transaction_status = status_response['transaction_status']
            fraud_status = status_response.get('fraud_status')
            
            if transaction_status == 'capture':
                if fraud_status == 'challenge':
                    status = 'challenge'
                elif fraud_status == 'accept':
                    status = 'success'
                else:
                    status = 'pending'
            elif transaction_status == 'settlement':
                status = 'success'
            elif transaction_status in ['cancel', 'deny', 'expire']:
                status = 'failed'
            elif transaction_status == 'pending':
                status = 'pending'
            else:
                status = 'unknown'
            
            return {
                'success': True,
                'order_id': order_id,
                'status': status,
                'transaction_status': transaction_status,
                'fraud_status': fraud_status,
                'raw_data': status_response
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Singleton instance
midtrans_service = MidtransService()
