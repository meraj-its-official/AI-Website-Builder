import generateResponse from "../config/openRouter.js"

export const getCurrentUser = async (req, res) => {
    try {
        if (!req.existingUser) {
            return res.json({ existingUser: null })
        }
        return res.json(req.existingUser)
    } catch (e) {
        return res.status(500).json({
            message: `get current user ${e}`
        })
    }
}
