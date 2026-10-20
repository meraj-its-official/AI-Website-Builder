import User from "../models/user.model.js"
import jwt from "jsonwebtoken"
import cookieParser from "cookie-parser";

export const googleAuth = async (req, res) => {
    try {
        const { name, email, avatar } = req.body
        if (!email) {
            return res.status(400).json({
                message: "email is required"
            })
        }
        let user = await User.findOne({ email })
        if (!user) {
            user = await User.create({ name, email, avatar })
        }
        const token = await jwt.sign({ id: user._id }, process.env.JWT_SECRET,
            { expiresIn: "7d" })

        res.cookie("token", token, {
            httpOnly: true,
            secure: true,
            sameSite: "none",
            maxAge: 7 * 24 * 60 * 60 * 1000
        })

        return res.status(200).json(user)
    } catch (e) {
        console.log(e)
        return res.status(500).json({ message: `google auth error ${e}` })
    }
}

export const logOut = async (req, res) => {
    try {
        res.clearCookie("token", {
            httpOnly: true,
            secure: true,
            sameSite: "none",
        })

        return res.status(200).json({
            message: "logout successful"
        })
    } catch (e) {
        return res.status(500).json({ message: `logout error ${e}` })
    }
}