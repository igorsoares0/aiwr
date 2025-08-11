from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, current_app
from flask_login import login_required, current_user
from models import db, PaymentEvent
from stripe_service import stripe_service
from subscription_middleware import subscription_required

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/pricing')
def pricing():
    """Pricing page with plan selection"""
    return render_template('pricing.html')

@billing_bp.route('/billing')
@login_required
def index():
    """Billing management page"""
    subscription_context = {}
    
    # Get current subscription details
    current_subscription = current_user.get_current_subscription()
    if current_subscription:
        subscription_context = {
            'subscription': current_subscription,
            'status': current_subscription.status,
            'plan_type': current_subscription.plan_type,
            'current_period_end': current_subscription.current_period_end,
            'is_canceled': current_subscription.is_canceled,
            'days_until_renewal': current_subscription.days_until_renewal
        }
    
    return render_template('billing.html', **subscription_context)

@billing_bp.route('/api/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create a Stripe Checkout session"""
    try:
        data = request.get_json()
        plan_type = data.get('plan_type')
        
        if plan_type not in ['monthly', 'annual']:
            return jsonify({'error': 'Invalid plan type'}), 400
        
        # Create checkout session
        session = stripe_service.create_checkout_session(current_user, plan_type)
        
        return jsonify({
            'checkout_url': session.url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/api/create-billing-portal-session', methods=['POST'])
@login_required
def create_billing_portal_session():
    """Create a Stripe billing portal session"""
    try:
        if not current_user.stripe_customer_id:
            return jsonify({'error': 'No billing information found'}), 404
        
        session = stripe_service.create_billing_portal_session(current_user)
        
        return jsonify({
            'portal_url': session.url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/api/subscription/cancel', methods=['POST'])
@login_required
def cancel_subscription():
    """Cancel subscription at period end"""
    try:
        subscription = current_user.get_current_subscription()
        if not subscription:
            return jsonify({'error': 'No active subscription found'}), 404
        
        # Cancel at period end
        stripe_service.cancel_subscription(subscription.stripe_subscription_id)
        
        flash('Your subscription has been canceled and will end at the current billing period.', 'info')
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/api/subscription/reactivate', methods=['POST'])
@login_required
def reactivate_subscription():
    """Reactivate a canceled subscription"""
    try:
        subscription = current_user.get_current_subscription()
        if not subscription:
            return jsonify({'error': 'No subscription found'}), 404
        
        # Reactivate subscription
        stripe_service.reactivate_subscription(subscription.stripe_subscription_id)
        
        flash('Your subscription has been reactivated.', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/api/subscription/status')
@login_required
def subscription_status():
    """Get current subscription status"""
    try:
        status_data = {
            'user_status': current_user.subscription_status,
            'plan': current_user.subscription_plan,
            'is_trial_active': current_user.is_trial_active,
            'is_subscription_active': current_user.is_subscription_active,
            'has_valid_access': current_user.has_valid_access,
            'days_left_in_trial': current_user.days_left_in_trial,
            'trial_ends_at': current_user.trial_ends_at.isoformat() if current_user.trial_ends_at else None,
            'subscription_ends_at': current_user.subscription_ends_at.isoformat() if current_user.subscription_ends_at else None,
        }
        
        # Add subscription details if available
        current_subscription = current_user.get_current_subscription()
        if current_subscription:
            status_data['subscription'] = {
                'id': current_subscription.id,
                'status': current_subscription.status,
                'plan_type': current_subscription.plan_type,
                'current_period_start': current_subscription.current_period_start.isoformat(),
                'current_period_end': current_subscription.current_period_end.isoformat(),
                'is_canceled': current_subscription.is_canceled,
                'canceled_at': current_subscription.canceled_at.isoformat() if current_subscription.canceled_at else None,
                'days_until_renewal': current_subscription.days_until_renewal
            }
        
        return jsonify(status_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/success')
@login_required
def success():
    """Checkout success page"""
    session_id = request.args.get('session_id')
    
    if session_id:
        try:
            # Retrieve the session to get details
            import stripe
            session = stripe.checkout.Session.retrieve(session_id)
            
            return render_template('billing_success.html', 
                                 session=session,
                                 plan_type=session.metadata.get('plan_type', 'monthly'))
        except Exception as e:
            flash('There was an issue retrieving your payment information.', 'warning')
    
    return render_template('billing_success.html')

@billing_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe webhooks"""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        # Construct event
        event = stripe_service.construct_event(payload, sig_header)
        
        # Check if event already processed
        existing_event = PaymentEvent.query.filter_by(
            stripe_event_id=event['id']
        ).first()
        
        if existing_event and existing_event.is_processed:
            return jsonify({'status': 'already_processed'}), 200
        
        # Create event record
        if not existing_event:
            payment_event = PaymentEvent(
                stripe_event_id=event['id'],
                event_type=event['type'],
                data=event['data']
            )
            db.session.add(payment_event)
        else:
            payment_event = existing_event
        
        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            stripe_service.handle_checkout_completed(event['data']['object'])
            
        elif event['type'] == 'customer.subscription.updated':
            stripe_service.handle_subscription_updated(event['data']['object'])
            
        elif event['type'] == 'customer.subscription.deleted':
            stripe_service.handle_subscription_updated(event['data']['object'])
            
        elif event['type'] == 'invoice.payment_succeeded':
            # Handle successful payment
            pass  # Usually handled by subscription.updated
            
        elif event['type'] == 'invoice.payment_failed':
            stripe_service.handle_invoice_payment_failed(event['data']['object'])
        
        # Mark event as processed
        payment_event.mark_processed()
        db.session.commit()
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Error handlers for billing routes
@billing_bp.errorhandler(404)
def billing_not_found(error):
    return render_template('errors/404.html'), 404

@billing_bp.errorhandler(500)
def billing_server_error(error):
    return render_template('errors/500.html'), 500