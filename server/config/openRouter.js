const openRouterUrl = "https://openrouter.ai/api/v1/chat/completions"
const model = "nvidia/nemotron-3.5-lightning"

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