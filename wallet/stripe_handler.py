import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from decimal import Decimal
import json
import time
import logging

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

# ✅ CRITICAL: Set API version to match webhook configuration
stripe.api_version = "2025-05-28.basil"

logger = logging.getLogger('wallet.payments')


class StripePaymentHandler:
    def __init__(self):
        self.allowed_amounts = [10, 50, 100, 500]
    
    def create_checkout_session(self, user, amount, request=None):
        """Create a Stripe checkout session for wallet top-up (Modern Integration)"""
        if amount not in self.allowed_amounts:
            raise ValueError(f"Invalid amount: {amount}. Allowed amounts: {self.allowed_amounts}")
        
        # Build URLs with session_id parameter for payment verification
        if request:
            success_url = request.build_absolute_uri('/wallet/top-up/success/') + '?session_id={CHECKOUT_SESSION_ID}'
            cancel_url = request.build_absolute_uri('/wallet/top-up/cancel/')
        else:
            # Fallback URLs
            success_url = 'https://www.quantumtaskai.com/wallet/top-up/success/?session_id={CHECKOUT_SESSION_ID}'
            cancel_url = 'https://www.quantumtaskai.com/wallet/top-up/cancel/'
        
        try:
            logger.info(f"Creating checkout session for user {user.id}, amount: {amount} AED")
            environment = 'production' if 'railway.app' in (request.get_host() if request else '') else 'development'
            logger.debug(f"Environment: {environment}, API version: {stripe.api_version}")
            
            # Create session with modern Stripe practices
            session = stripe.checkout.Session.create(
                # Modern payment method configuration
                payment_method_types=['card'],
                
                # Line items configuration
                line_items=[{
                    'price_data': {
                        'currency': 'aed',
                        'product_data': {
                            'name': 'Quantum Tasks AI Wallet Top-up',
                            'description': f'Add {amount} AED to your wallet balance',
                            'metadata': {
                                'service': 'quantumtaskai_wallet',
                                'user_id': str(user.id)
                            }
                        },
                        'unit_amount': int(amount * 100),  # Convert to fils (AED cents)
                    },
                    'quantity': 1,
                }],
                
                # Payment configuration
                mode='payment',
                
                # URLs with session ID parameter
                success_url=success_url,
                cancel_url=cancel_url,
                
                # Customer and reference data
                client_reference_id=str(user.id),
                customer_email=user.email,
                
                # Comprehensive metadata for webhook processing
                metadata={
                    'user_id': str(user.id),
                    'user_email': user.email,
                    'amount': str(amount),
                    'currency': 'aed',
                    'type': 'wallet_topup',
                    'service': 'quantumtaskai',
                    'environment': 'production' if 'railway.app' in (request.get_host() if request else '') else 'development',
                    'created_at': str(int(time.time())),
                    'app_version': '1.0'
                },
                
                # Modern Stripe features
                payment_intent_data={
                    'metadata': {
                        'user_id': str(user.id),
                        'amount': str(amount),
                        'service': 'quantumtaskai_wallet'
                    }
                },
                
                # Automatic tax and billing
                automatic_tax={'enabled': False},
                
                # Expiration
                expires_at=int(time.time()) + (30 * 60),  # 30 minutes from now
            )
            
            logger.info(f"Checkout session created successfully: {session.id}")
            logger.debug(f"Session details - Amount: {session.amount_total / 100} AED, Status: {session.status}")
            
            # Verify session was created in correct Stripe account
            try:
                verification_session = stripe.checkout.Session.retrieve(session.id)
                logger.debug(f"Session verification successful: {verification_session.id}")
            except Exception as verify_error:
                logger.error(f"Session verification failed: {verify_error}")
                raise ValueError("Session creation verification failed")
            
            return {
                'payment_url': session.url,
                'session_id': session.id,
                'amount': amount,
                'currency': 'aed',
                'expires_at': session.expires_at
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            raise ValueError(f"Failed to create checkout session")
    
    def verify_payment(self, session_id):
        """Verify payment directly from Stripe (bypasses webhook issues)"""
        try:
            logger.info(f"Starting payment verification for session: {session_id}")
            
            session = stripe.checkout.Session.retrieve(session_id)
            
            logger.debug(f"Session retrieved - Status: {session.status}, Payment Status: {session.payment_status}")
            logger.debug(f"Amount: {session.amount_total / 100} AED, User: {session.client_reference_id}")
            
            # Check if payment was actually completed
            if hasattr(session, 'payment_intent') and session.payment_intent:
                try:
                    payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
                    logger.debug(f"Payment intent status: {payment_intent.status}")
                except Exception as pi_error:
                    logger.warning(f"Could not retrieve payment intent: {pi_error}")
            
            if session.payment_status == 'paid' and session.status == 'complete':
                user_id = session.client_reference_id
                amount = session.amount_total / 100  # Convert from cents
                
                logger.info(f"Payment successful - User: {user_id}, Amount: {amount} AED")
                
                # Process the payment manually (bypass webhook)
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        
                        # Check if already processed to avoid double-charging
                        from wallet.models import WalletTransaction
                        existing = WalletTransaction.objects.filter(stripe_session_id=session_id).first()
                        
                        if not existing:
                            logger.info(f"Processing payment for user {user_id}")
                            user.add_balance(
                                amount=amount,
                                description=f"Wallet top-up via Stripe",
                                stripe_session_id=session_id
                            )
                            logger.info(f"Balance updated successfully for user {user_id}")
                            return {
                                'success': True,
                                'amount': amount,
                                'user_id': user_id,
                                'processed': True,
                                'message': 'Payment processed via manual verification'
                            }
                        else:
                            logger.info(f"Payment already processed for session {session_id}")
                            return {
                                'success': True,
                                'amount': amount,
                                'user_id': user_id,
                                'processed': False,
                                'message': 'Payment already processed'
                            }
                            
                    except Exception as e:
                        logger.error(f"Error processing payment for user {user_id}: {e}")
                        return {'success': False, 'error': 'Processing error'}
                else:
                    return {'success': False, 'error': 'No user ID in session'}
                    
            elif session.payment_status == 'unpaid':
                return {'success': False, 'error': 'Payment not completed yet'}
            else:
                return {'success': False, 'error': f'Payment status: {session.payment_status}'}
                
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error during payment verification: {e}")
            return {'success': False, 'error': 'Payment verification failed'}
    
    def handle_webhook(self, payload, signature):
        """Handle Stripe webhook events"""
        logger.info("Processing webhook event")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
            logger.info(f"Webhook event type: {event['type']}")
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            return {'success': False, 'error': 'Invalid payload'}
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            return {'success': False, 'error': 'Invalid signature'}
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            session_id = session['id']
            logger.info(f"Processing checkout session completion: {session_id}")
            
            # Process successful payment
            user_id = session.get('client_reference_id')
            amount = session['amount_total'] / 100  # Convert from cents
            
            logger.info(f"Webhook payment - User: {user_id}, Amount: {amount} AED")
            
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    logger.info(f"Found user for webhook payment: {user_id}")
                    
                    # Check if already processed to avoid double-charging
                    from wallet.models import WalletTransaction
                    existing = WalletTransaction.objects.filter(stripe_session_id=session_id).first()
                    
                    if not existing:
                        user.add_balance(
                            amount=amount,
                            description=f"Wallet top-up via Stripe",
                            stripe_session_id=session_id
                        )
                        logger.info(f"Webhook payment processed for user {user_id}")
                    else:
                        logger.info(f"Webhook payment already processed: {session_id}")
                    
                    return {'success': True, 'message': 'Payment processed successfully'}
                except User.DoesNotExist:
                    logger.error(f"User not found for webhook: {user_id}")
                    return {'success': False, 'error': 'User not found'}
                except Exception as e:
                    logger.error(f"Error processing webhook payment: {e}")
                    return {'success': False, 'error': 'Processing error'}
            else:
                logger.error("No user ID in webhook session")
                return {'success': False, 'error': 'No user reference'}
        else:
            logger.debug(f"Ignored webhook event type: {event['type']}")
        
        return {'success': True, 'message': 'Event processed'}
    
    def process_refund(self, session_id, amount=None):
        """Process refund for a payment"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            payment_intent = session.payment_intent
            
            if amount:
                refund = stripe.Refund.create(
                    payment_intent=payment_intent,
                    amount=int(amount * 100)  # Convert to cents
                )
            else:
                refund = stripe.Refund.create(payment_intent=payment_intent)
            
            return {
                'success': True,
                'refund_id': refund.id,
                'amount': refund.amount / 100,
                'status': refund.status
            }
            
        except stripe.error.StripeError as e:
            return {'success': False, 'error': str(e)}