import stripe
import os
from datetime import datetime, timedelta
from flask import current_app, url_for
from models import db, User, Subscription, PaymentEvent

class StripeService:
    def __init__(self):
        self.stripe_key = os.getenv('STRIPE_SECRET_KEY')
        if self.stripe_key:
            stripe.api_key = self.stripe_key
        
        # Price IDs - these should be configured in Stripe Dashboard
        self.MONTHLY_PRICE_ID = os.getenv('STRIPE_MONTHLY_PRICE_ID', 'price_monthly_27')
        self.ANNUAL_PRICE_ID = os.getenv('STRIPE_ANNUAL_PRICE_ID', 'price_annual_192')
        
    def create_customer(self, user):
        """Create a Stripe customer for the user"""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={
                    'user_id': user.id
                }
            )
            
            # Save customer ID to user
            user.stripe_customer_id = customer.id
            db.session.commit()
            
            return customer
            
        except stripe.error.StripeError as e:
            current_app.logger.error(f"Failed to create Stripe customer: {str(e)}")
            raise Exception(f"Failed to create customer: {str(e)}")
    
    def create_checkout_session(self, user, plan_type):
        """Create a Stripe Checkout session"""
        try:
            # Ensure user has a Stripe customer ID
            if not user.stripe_customer_id:
                self.create_customer(user)
            
            # Determine price ID based on plan
            price_id = self.MONTHLY_PRICE_ID if plan_type == 'monthly' else self.ANNUAL_PRICE_ID
            
            # Prepare subscription data
            subscription_data = {
                'metadata': {
                    'user_id': user.id,
                    'plan_type': plan_type
                }
            }
            
            # Trial is handled locally, Stripe subscription starts immediately
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                customer=user.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=url_for('billing.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=url_for('billing.pricing', _external=True),
                metadata={
                    'user_id': user.id,
                    'plan_type': plan_type
                },
                subscription_data=subscription_data
            )
            
            return session
            
        except stripe.error.StripeError as e:
            current_app.logger.error(f"Failed to create checkout session: {str(e)}")
            raise Exception(f"Failed to create checkout session: {str(e)}")
    
    def create_billing_portal_session(self, user):
        """Create a Stripe billing portal session"""
        try:
            if not user.stripe_customer_id:
                raise Exception("No Stripe customer found")
            
            session = stripe.billing_portal.Session.create(
                customer=user.stripe_customer_id,
                return_url=url_for('billing.index', _external=True),
            )
            
            return session
            
        except stripe.error.StripeError as e:
            current_app.logger.error(f"Failed to create billing portal session: {str(e)}")
            raise Exception(f"Failed to create billing portal session: {str(e)}")
    
    def cancel_subscription(self, subscription_id):
        """Cancel a subscription at period end"""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            
            return subscription
            
        except stripe.error.StripeError as e:
            current_app.logger.error(f"Failed to cancel subscription: {str(e)}")
            raise Exception(f"Failed to cancel subscription: {str(e)}")
    
    def reactivate_subscription(self, subscription_id):
        """Reactivate a subscription that was set to cancel"""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False
            )
            
            return subscription
            
        except stripe.error.StripeError as e:
            current_app.logger.error(f"Failed to reactivate subscription: {str(e)}")
            raise Exception(f"Failed to reactivate subscription: {str(e)}")
    
    def get_subscription(self, subscription_id):
        """Retrieve a subscription from Stripe"""
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            current_app.logger.error(f"Failed to retrieve subscription: {str(e)}")
            return None
    
    def handle_checkout_completed(self, session):
        """Handle successful checkout completion - simplified version"""
        try:
            current_app.logger.info(f"Processing checkout session: {session.id}")
            
            user_id = session.metadata.get('user_id')
            plan_type = session.metadata.get('plan_type', 'monthly')
            
            user = User.query.get(user_id)
            
            if not user:
                current_app.logger.error(f"User not found for checkout session: {session.id}")
                return
            
            current_app.logger.info(f"Found user: {user.email}, plan: {plan_type}")
            
            # Simple update - just activate the user
            user.subscription_status = 'active'
            user.subscription_plan = plan_type
            
            # Set subscription end date based on plan
            if plan_type == 'monthly':
                user.subscription_ends_at = datetime.utcnow() + timedelta(days=30)
            else:  # annual
                user.subscription_ends_at = datetime.utcnow() + timedelta(days=365)
            
            # Create simple subscription record
            subscription_id = session.subscription if session.subscription else f"checkout_{session.id}"
            
            # Check if subscription record already exists
            existing_subscription = Subscription.query.filter_by(
                user_id=user.id
            ).filter_by(
                status='active'
            ).first()
            
            if not existing_subscription:
                subscription = Subscription(
                    user_id=user.id,
                    stripe_subscription_id=subscription_id,
                    stripe_price_id=self.MONTHLY_PRICE_ID if plan_type == 'monthly' else self.ANNUAL_PRICE_ID,
                    status='active',
                    plan_type=plan_type,
                    current_period_start=datetime.utcnow(),
                    current_period_end=user.subscription_ends_at
                )
                db.session.add(subscription)
            
            db.session.commit()
            current_app.logger.info(f"✅ Successfully activated user {user.email} with {plan_type} plan")
            
        except Exception as e:
            current_app.logger.error(f"❌ Error handling checkout completion: {str(e)}")
            db.session.rollback()
    
    def handle_subscription_updated(self, subscription_data):
        """Handle subscription updates"""
        try:
            subscription = Subscription.query.filter_by(
                stripe_subscription_id=subscription_data.id
            ).first()
            
            if not subscription:
                current_app.logger.error(f"Subscription not found: {subscription_data.id}")
                return
            
            # Update subscription
            subscription.status = subscription_data.status
            subscription.current_period_start = datetime.fromtimestamp(subscription_data.current_period_start)
            subscription.current_period_end = datetime.fromtimestamp(subscription_data.current_period_end)
            subscription.canceled_at = datetime.fromtimestamp(subscription_data.canceled_at) if subscription_data.canceled_at else None
            
            # Update user status
            user = subscription.user
            if subscription_data.status == 'active':
                user.subscription_status = 'active'
                user.subscription_ends_at = datetime.fromtimestamp(subscription_data.current_period_end)
            elif subscription_data.status == 'past_due':
                user.subscription_status = 'past_due'
            elif subscription_data.status == 'canceled':
                user.subscription_status = 'canceled'
            
            db.session.commit()
            current_app.logger.info(f"Successfully updated subscription {subscription_data.id}")
            
        except Exception as e:
            current_app.logger.error(f"Error handling subscription update: {str(e)}")
            db.session.rollback()
    
    def handle_invoice_payment_failed(self, invoice_data):
        """Handle failed invoice payment"""
        try:
            customer_id = invoice_data.customer
            customer = stripe.Customer.retrieve(customer_id)
            
            # Find user by customer ID
            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            if not user:
                current_app.logger.error(f"User not found for customer: {customer_id}")
                return
            
            # Update user status
            user.subscription_status = 'past_due'
            db.session.commit()
            
            current_app.logger.info(f"Updated user {user.id} status to past_due")
            
        except Exception as e:
            current_app.logger.error(f"Error handling payment failure: {str(e)}")
            db.session.rollback()
    
    def delete_customer(self, customer_id):
        """Delete a Stripe customer and cancel all subscriptions"""
        try:
            # First, cancel all active subscriptions
            subscriptions = stripe.Subscription.list(customer=customer_id, status='active')
            for subscription in subscriptions:
                stripe.Subscription.delete(subscription.id)
            
            # Delete the customer
            stripe.Customer.delete(customer_id)
            current_app.logger.info(f"Successfully deleted Stripe customer: {customer_id}")
            
        except stripe.error.StripeError as e:
            current_app.logger.error(f"Failed to delete Stripe customer {customer_id}: {str(e)}")
            raise Exception(f"Failed to delete customer: {str(e)}")
    
    def construct_event(self, payload, sig_header):
        """Construct and verify webhook event"""
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        if not webhook_secret:
            raise Exception("Webhook secret not configured")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except ValueError as e:
            current_app.logger.error(f"Invalid payload: {str(e)}")
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            current_app.logger.error(f"Invalid signature: {str(e)}")
            raise Exception("Invalid signature")

# Global service instance
stripe_service = StripeService()