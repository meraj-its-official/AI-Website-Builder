import express from "express"
import { billingOrders, billingVerify, } from "../controllers/billing.controller.js"
import isAuth from "../middlewares/isAuth.js"


const paymentRouter = express.Router()
paymentRouter.post("/orders", isAuth, billingOrders)
paymentRouter.post("/verify", isAuth, billingVerify)

export default paymentRouter