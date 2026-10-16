const openRouterUrl = "https://openrouter.ai/api/v1/chat/completions"
const model = "nvidia/nemotron-3-ultra-550b-a55b:free"

const generateResponse = async (prompt) => {
    let response = await fetch(openRouterUrl, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${process.env.OPEN_ROUTER_API_KEY}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            model: model,
            messages: [
                { role: "system", content: "You must return ONLY valid raw JSON" },
                {
                    role: 'user',
                    content: prompt
                }
            ],
            temperature: 0.2,
            reasoning: { enabled: true }
        })
    });
    if (!response.ok) {
        const err = await response.text()
        throw new Error("openRouter err" + err)
    }
    const data = await response.json()
    return data.choices[0].message.content;
}

export default generateResponse

// Google Gemini API

// const generateResponse = async (prompt) => {
//     const geminiApi = process.env.GOOGLE_GEMINI_API_KEY;
//     const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key=${geminiApi}`;

//     let response = await fetch(geminiUrl, {
//         method: "POST",
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({
//             systemInstruction: {
//                 parts: [{ text: "You must return ONLY valid raw JSON. Do not wrap in markdown or backticks." }]
//             },
//             contents: [
//                 {
//                     role: 'user',
//                     parts: [{ text: prompt }]
//                 }
//             ],
//             generationConfig: {
//                 temperature: 0.2,
//                 responseMimeType: "application/json" // Force strict JSON output
//             }
//         })
//     });
//     if (!response.ok) {
//         const err = await response.text()
//         throw new Error("Gemini API error: " + err)
//     }
//     const data = await response.json()
//     return data.candidates[0].content.parts[0].text;
// }