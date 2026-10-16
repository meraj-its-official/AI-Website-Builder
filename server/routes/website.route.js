import express from "express"
import isAuth from "../middlewares/isAuth.js"
import { generateWebsite, getAllWebsites, getWebsiteById, updateWebsite } from "../controllers/website.controller.js"

const websiteRouter = express.Router()

websiteRouter.post("/generate", isAuth, generateWebsite)
websiteRouter.post("/update/:id", isAuth, updateWebsite)
websiteRouter.get("/get-by-id/:id", isAuth, getWebsiteById)
websiteRouter.get("/get-all-items", isAuth, getAllWebsites)

export default websiteRouter