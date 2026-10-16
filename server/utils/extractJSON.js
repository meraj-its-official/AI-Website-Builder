export const extractJSON = (text) => {
    if (!text) return null;

    // 1. Clean markdown code blocks
    const cleanedText = text
        .replace(/```json/gi, "")
        .replace(/```/g, "")
        .trim();

    const firstBrace = cleanedText.indexOf('{');
    const lastBrace = cleanedText.lastIndexOf('}');

    if (firstBrace === -1 || lastBrace === -1) return null;

    const jsonString = cleanedText.slice(firstBrace, lastBrace + 1);

    // 🛠️ FIX 1: Direct Parsing with try...catch
    try {
        return JSON.parse(jsonString);
    } catch (e1) {
        // 🛠️ FIX 2: Auto-sanitize bad escaped backslashes (\d, \w, \s etc.)
        try {
            const sanitizedString = jsonString
                .replace(/\\(?!["\\\/bfnrtu]|u[0-9a-fA-F]{4})/g, "\\\\");

            return JSON.parse(sanitizedString);
        } catch (e2) {
            console.error("JSON parsing failed after sanitization:", e2.message);
            // Error throw karne ke bajaye null return karein taaki controller ka retry loop chal sake
            return null;
        }
    }
}