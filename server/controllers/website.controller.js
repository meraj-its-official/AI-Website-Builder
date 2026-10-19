import generateResponse from "../config/openRouter.js";
import { extractJSON } from "../utils/extractJSON.js";
import Website from '../models/website.model.js'
import User from "../models/user.model.js";

const masterPrompt = `YOU ARE A PRINCIPAL FRONTEND ARCHITECT
AND A SENIOR UI/UX ENGINEER
SPECIALIZED IN RESPONSIVE DESIGN SYSTEMS.

YOU BUILD HIGH-END, REAL-WORLD, PRODUCTION-GRADE WEBSITES
USING ONLY HTML, CSS, AND JAVASCRIPT
THAT WORK PERFECTLY ON ALL SCREEN SIZES.

THE OUTPUT MUST BE CLIENT-DELIVERABLE WITHOUT ANY MODIFICATION.

❌ NO FRAMEWORKS
❌ NO LIBRARIES
❌ NO BASIC SITES
❌ NO PLACEHOLDERS
❌ NO NON-RESPONSIVE LAYOUTS

--------------------------------------------------
USER REQUIREMENT:
{USER_PROMPT}
--------------------------------------------------

GLOBAL QUALITY BAR (NON-NEGOTIABLE)
--------------------------------------------------
- Premium, modern UI (2026–2027)
- Professional typography & spacing
- Clean visual hierarchy
- Business-ready content (NO lorem ipsum)
- Smooth transitions & hover effects
- SPA-style multi-page experience
- Production-ready, readable code

--------------------------------------------------
RESPONSIVE DESIGN (ABSOLUTE REQUIREMENT)
--------------------------------------------------
THIS WEBSITE MUST BE FULLY RESPONSIVE.

YOU MUST IMPLEMENT:

✔ Mobile-first CSS approach
✔ Responsive layout for:cd
  - Mobile (<768px)
  - Tablet (768px–1024px)
  - Desktop (>1024px)

✔ Use:
  - CSS Grid / FlexBx
  - Relative units (%, rem, vw)
  - Media queries

✔ REQUIRED RESPONSIVE BEHAVIOR:
  - Navbar collapses / stacks on mobile
  - Sections stack vertically on mobile
  - Multi-column layouts become single-column on small screens
  - Images scale proportionally
  - Text remains readable on all devices
  - No horizontal scrolling on mobile
  - Touch-friendly buttons on mobile

IF THE WEBSITE IS NOT RESPONSIVE → RESPONSE IS INVALID.

--------------------------------------------------
IMAGES (MANDATORY & RESPONSIVE)
--------------------------------------------------
- Use high-quality images ONLY from:
  https://images.unsplash.com/
- EVERY image URL MUST include:
  ?auto=format&fit=crop&w=1200&q=80

- Images must:
  - Be responsive (max-width: 100%)
  - Resize correctly on mobile
  - Never overflow containers

--------------------------------------------------
TECHNICAL RULES (VERY IMPORTANT)
--------------------------------------------------
- Output ONE single HTML file
- Exactly ONE <style> tag
- Exactly ONE <script> tag
- NO external CSS / JS / fonts
- Use system fonts only
- iframe srcdoc compatible
- SPA-style navigation using JavaScript
- No page reloads
- No dead UI
- No broken buttons
--------------------------------------------------
SPA VISIBILITY RULE (MANDATORY)
--------------------------------------------------
- Pages MUST NOT be hidden permanently
- If .page { display: none } is used,
  then .page.active { display: block } is REQUIRED
- At least ONE page MUST be visible on initial load
- Hiding all content is INVALID


--------------------------------------------------
REQUIRED SPA PAGES
--------------------------------------------------
- Home
- About
- Services / Features
- Contact

--------------------------------------------------
FUNCTIONAL REQUIREMENTS
--------------------------------------------------
- Navigation must switch pages using JS
- Active nav state must update
- Forms must have JS validation
- Buttons must show hover + active states
- Smooth section/page transitions

--------------------------------------------------
FINAL SELF-CHECK (MANDATORY)
--------------------------------------------------
BEFORE RESPONDING, ENSURE:

1. Layout works on mobile, tablet, desktop
2. No horizontal scroll on mobile
3. All images are responsive
4. All sections adapt properly
5. Media queries are present and used
6. Navigation works on all screen sizes
7. At least ONE page is visible without user interaction

IF ANY CHECK FAILS → RESPONSE IS INVALID

--------------------------------------------------
OUTPUT FORMAT (RAW JSON ONLY)
--------------------------------------------------
{
  "message": "Short professional confirmation sentence",
  "code": "<FULL VALID HTML DOCUMENT>"
}

--------------------------------------------------
ABSOLUTE RULES
--------------------------------------------------
- RETURN RAW JSON ONLY
- NO markdown
- NO explanations
- NO extra text
- FORMAT MUST MATCH EXACTLY
- IF FORMAT IS BROKEN → RESPONSE IS INVALID
`;

export const generateWebsite = async (req, res) => {
    try {

        const { prompt } = req.body
        if (!prompt) {
            return res.status(400).json({ message: "prompt is required" })
        }

        if (!req.user || !req.user._id) {
            return res.status(401).json({ message: "Unauthorized: User not authenticated" });
        }

        const user = await User.findById(req.user._id)
        if (!user) {
            return res.status(400).json({ message: "user not found" })
        }

        if (user.credits < 50) {
            return res.status(400).json({ message: "you have not enough credits to generate a website" })
        }

        const finalPrompt = masterPrompt.replace("USER_PROMPT", prompt)

        let raw = ''
        let parsed = null

        for (let i = 0; i < 2 && !parsed; i++) {
            raw = await generateResponse(finalPrompt)
            parsed = await extractJSON(raw)

            if (!parsed) {
                raw = await generateResponse(finalPrompt + "\n\nRETURN ONLY RAW JSON.")
                parsed = await extractJSON(raw)
            }
        }

        if (!parsed.code) {
            console.log('ai returned invalid response', raw)
            return res.status(500).json({
                message: "ai returned invalid response"
            })
        }

        const website = await Website.create({
            user: user._id,
            title: prompt.slice(0, 70),
            latestCode: parsed.code,
            conversation: [
                {
                    role: 'user',
                    content: prompt
                },
                {
                    role: 'ai',
                    content: parsed.message
                }

            ]
        })

        user.credits -= 50
        await user.save()

        return res.status(201).json({
            websiteId: website._id,
            remainingCredits: user.credits
        })

    } catch (e) {
        return res.status(500).json({
            message: `Error while generating website ${e}`
        })
    }
}


export const getWebsiteById = async (req, res) => {
    try {
        const website = await Website.findOne({
            _id: req.params.id,
            user: req.user._id
        })
        if (!website) {
            return res.status(404).json({
                message: "website not found"
            })
        }
        return res.status(200).json(website)
    } catch (e) {
        return res.status(500).json({
            message: `get website by id error ${e}`
        })
    }
}

export const updateWebsite = async (req, res) => {
    try {
        const { prompt } = req.body
        if (!prompt) {
            return res.status(400).json({ message: "prompt is required" })
        }

        if (!req.user || !req.user._id) {
            return res.status(401).json({ message: "Unauthorized: User not authenticated" });
        }

        const website = await Website.findOne({
            _id: req.params.id,
            user: req.user._id
        })

        if (!website) {
            return res.status(404).json({
                message: "website not found"
            })
        }
        const user = await User.findById(req.user._id)
        if (!user) {
            return res.status(400).json({ message: "user not found" })
        }

        if (user.credits < 25) {
            return res.status(400).json({ message: "you have not enough credits to generate a website" })
        }

        const updatePrompt = `
        UPDATE THIS HTML WEBSITE.

        CURRENT CODE:
        ${website.latestCode}

        USER REQUEST:
        ${prompt}

        RETURN RAW JSON ONLY:
        {
        "message":"Short confirmation",
        "code":"<UPDATED FULL HTML>"
        }
        `
        let raw = ''
        let parsed = null

        for (let i = 0; i < 2 && !parsed; i++) {
            raw = await generateResponse(updatePrompt)
            parsed = await extractJSON(raw)

            if (!parsed) {
                raw = await generateResponse(updatePrompt + "\n\nRETURN ONLY RAW JSON.")
                parsed = await extractJSON(raw)
            }
        }

        if (!parsed.code) {
            console.log('ai returned invalid response', raw)
            return res.status(500).json({
                message: "ai returned invalid response"
            })
        }

        website.conversation.push(
            { role: "user", content: prompt },
            { role: "ai", content: parsed.message }
        )

        website.latestCode = parsed.code

        await website.save()
        user.credits -= 25
        await user.save()

        return res.status(200).json({
            message: parsed.message,
            code: parsed.code,
            remainingCredits: user.credits
        })
    } catch (e) {
        return res.status(500).json({
            message: `Error while updating website ${e}`
        })
    }
}

export const getAllWebsites = async (req, res) => {
    try {
        const website = await Website.find({ user: req.user._id })
        return res.status(200).json(website)
    } catch (e) {
        return res.status(500).json({
            message: `Error while fetching all the websites ${e}`
        })
    }
}


export const deploy = async (req, res) => {
    try {
        const website = await Website.findOne({
            _id: req.params.id,
            user: req.user._id
        })

        if (!website) {
            return res.status(404).json({
                message: "website not found"
            })
        }

        if (!website.slug) {
            website.slug = website.title.toLowerCase().replace(/[^a-z0-9]/g, "").slice(0, 50) + website._id.toString().slice(-17)
        }

        website.deployed = true
        website.deployedUrl = `${process.env.FRONTEND_URL}/site/${website.slug}`
        await website.save()

        return res.status(200).json({
            url: website.deployedUrl
        })
    } catch (e) {
        return res.status(500).json({
            message: `Error while deploying website ${e}`
        })
    }
}

export const getBySlug = async (req, res) => {
    try {
        const website = await Website.findOne({
            slug: req.params.slug,
        })

        if (!website) {
            return res.status(404).json({
                message: "website not found"
            })
        }
        return res.status(200).json(website)
    } catch (e) {
        return res.status(500).json({
            message: `Error while deploying website by slug ${e}`
        })
    }
}