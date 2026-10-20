import jwt from "jsonwebtoken"
import User from "../models/user.model.js"

const isAuth = async (req, res, next) => {
    const token = req.cookies?.token;

    if (!token) {
        return res.status(401).json({
            message: "Token not found"
        });
    }

    let decoded;

    try {
        if (!process.env.JWT_SECRET) {
            console.error("JWT_SECRET is missing");

            return res.status(500).json({
                message: "Server authentication configuration error"
            });
        }

        decoded = jwt.verify(token, process.env.JWT_SECRET);
    } catch (error) {
        console.error("JWT verification failed:", error.name);

        return res.status(401).json({
            message: "Invalid or expired token"
        });
    }

    try {
        if (!decoded.id) {
            return res.status(401).json({
                message: "Invalid token payload"
            });
        }

        const user = await User.findById(decoded.id);

        if (!user) {
            return res.status(401).json({
                message: "User not found"
            });
        }

        req.user = user;
        return next();

    } catch (error) {
        console.error("User lookup failed:", error.message);

        return res.status(500).json({
            message: "Authentication check failed"
        });
    }
}

export default isAuth