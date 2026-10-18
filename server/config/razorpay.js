import dotenv from 'dotenv'
dotenv.config()
import Razorpay from 'razorpay'
const razorpayKey = new Razorpay({
    key_id: process.env.RAZORPAY_API_KEY,
    key_secret: process.env.RAZORPAY_KEY_SECRET
});

export default razorpayKey