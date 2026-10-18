import dotenv from 'dotenv'
dotenv.config()
import { PLANS } from "../config/plans.js"
import razorpayKey from "../config/razorpay.js"
import User from "../models/user.model.js";
import Razorpay from 'razorpay'
import crypto from 'crypto'

export const billingOrders = async (req, res) => {
    try {
        const { planType, userId } = req.body
        const selectPlan = PLANS[planType]
        if (!selectPlan || selectPlan.price == 0) {
            return res.status(400).json({ message: "invalid paid plan" })
        }
        // 3. Configure the Razorpay order options mapping your dataset
        const options = {
            amount: Math.round(selectPlan.price * 100), // Securely pulled from backend configuration
            currency: 'INR',
            receipt: `rcpt_${Date.now()}`,
            notes: {
                userId: String(userId),
                credits: String(selectPlan.credits), // Stored as string for Razorpay compatibility
                plan: String(selectPlan.plan)
            }
        };

        const order = await razorpayKey.orders.create(options);

        return res.status(201).json({
            success: true,
            order: order,
            planType: selectPlan.plan,
            razorpayKeyId: process.env.RAZORPAY_API_KEY
        });
    } catch (e) {
        console.error('Order creation error:', e);
        return res.status(500).json({ success: false, message: 'Internal Server Error' });
    }
}

export const billingVerify = async (req, res) => {
    try {
        const { razorpay_order_id, razorpay_payment_id, razorpay_signature } = req.body;

        if (!razorpay_order_id || !razorpay_payment_id || !razorpay_signature) {
            return res.status(400).json({
                success: false,
                message: 'Missing verification parameters'
            });
        }

        const secret = String(process.env.RAZORPAY_KEY_SECRET)
        const generated_signature = crypto
            .createHmac('sha256', secret)
            .update(`${razorpay_order_id}|${razorpay_payment_id}`)
            .digest('hex');

        if (generated_signature !== razorpay_signature) {
            console.error('Signature mismatch! Potential tampering attempt.');
            return res.status(400).json({
                success: false,
                message: 'Payment verification failed. Invalid Signature.'
            });
        }
        console.log(`Payment Verified Successfully for Order ID: ${razorpay_order_id}`);

        const orderDetails = await razorpayKey.orders.fetch(razorpay_order_id);
        const { userId, credits, plan } = orderDetails.notes;

        // 2. User ka database update karein
        if (userId && credits) {
            await User.findByIdAndUpdate(userId, {
                $inc: { credits: Number(credits) },
                currentPlan: plan,
                lastPaymentStatus: 'SUCCESS'
            });
            console.log(`✅ Database successfully updated for user ${userId}. Added ${credits} credits.`);
        }

        return res.status(200).json({
            success: true,
            message: 'Payment authenticated and processed successfully.'
        });

    } catch (e) {
        console.error('Verification Route Error:', e);
        return res.status(500).json({
            success: false,
            message: 'Internal server verification error'
        });
    }

}
export const billingWebhook = async (req, res) => {
    try {

        const webhookSecret = process.env.RAZORPAY_WEBHOOK_SECRET

        const expectedSignature = crypto
            .createHmac('sha256', webhookSecret)
            .update(JSON.stringify(req.body))
            .digest('hex');

        if (expectedSignature !== req.headers['x-razorpay-signature']) {
            console.error('Unauthorized Webhook Attempt: Signature mismatch.');
            return res.status(400).json({ status: 'error', message: 'Invalid webhook signature' });
        }

        res.status(200).json({ status: 'received' });

        const { event, payload } = req.body;
        const paymentEntity = payload.payment.entity;

        const notes = paymentEntity.notes || {};
        const userId = notes.userId;
        const credits = notes.credits;
        const plan = notes.plan;

        switch (event) {
            case 'payment.captured':
                console.log(` Payment Captured! Order ID: ${paymentEntity.order_id}`);
                console.log(` User Details parsed via notes -> User: ${userId}, Plan: ${plan}, Credits: ${credits}`);

                await User.findByIdAndUpdate(userId, {
                    $inc: { credits: Number(credits) },
                    currentPlan: plan,
                    lastPaymentStatus: 'SUCCESS'
                });

                console.log(`Webhook: Database updated successfully for user ${userId}`);
                break;

            case 'payment.failed':
                console.error(` Payment Failed for Order ID: ${paymentEntity.order_id}`);
                console.error(`Reason: ${paymentEntity.error_description}`);

                break;

            default:
                console.log(`Unhandled Webhook Event Received: ${event}`);
        }

    } catch (e) {
        console.error(' Webhook processing crashed:', e);
    }
}