export const extractJSON = (text) => {
    if (!text) {
        return
    }

    const cleanedText = text.
        replace(/```json/gi, "")
        .replace(/```/g, "")
        .trim();

    const firstBrace = cleanedText.indexOf('{')
    const lastBrace = cleanedText.lastIndexOf('}')
    if (firstBrace === -1 || lastBrace === -1) return null
    const jsonString = cleanedText.slice(firstBrace, lastBrace + 1)
    return JSON.parse(jsonString)

}