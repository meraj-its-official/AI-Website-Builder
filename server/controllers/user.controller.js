// import generateResponse from "../config/openRouter.js"

export const getCurrentUser = async (req, res) => {
    try {
        if (!req.user) {
            return res.json({ user: null })
        }
        return res.json(req.user)
    } catch (e) {
        return res.status(500).json({
            message: `get current user ${e}`
        })
    }
}
