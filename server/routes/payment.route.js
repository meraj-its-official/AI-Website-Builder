import express from "express"
import { billingOrders, billingVerify, billingWebhook } from "../controllers/billing.controller.js"
import isAuth from "../middlewares/isAuth.js"


const paymentRouter = express.Router()
paymentRouter.post("/orders", isAuth, billingOrders)
paymentRouter.post("/verify", isAuth, billingVerify)
paymentRouter.post("/razorpay/webhook", express.raw({ type: "application/json" }), billingWebhook)

export default paymentRouter