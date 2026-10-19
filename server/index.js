import express from "express"
import dotenv from "dotenv"
dotenv.config()
import connectDb from "./config/db.js";
import authRouter from "./routes/auth.route.js";
import userRouter from "./routes/user.route.js";
import cookieParser from "cookie-parser";
import cors from "cors"
import websiteRouter from "./routes/website.route.js";
import paymentRouter from "./routes/payment.route.js";

const app = express();
const port = process.env.PORT || 5000
app.use(express.json())
app.use(cookieParser())
app.use(cors({
    origin: "http://localhost:5174",
    credentials: true
}))

app.use((req, res, next) => {
    res.setHeader('Cross-Origin-Opener-Policy', 'same-origin-allow-popups');
    next();
});

app.use("/api/auth", authRouter)
app.use("/api/user", userRouter)
app.use("/api/website", websiteRouter)
app.use("/api/payment", paymentRouter)

app.listen(port, () => {
    console.log(`Server is Running on ${port}`);
    connectDb()
});