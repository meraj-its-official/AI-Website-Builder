import React, { useEffect } from 'react'
import { GenerateBar } from '../components/AppBar'
import { motion } from 'motion/react'
import { useState } from 'react'
import axios from 'axios'
import { serverUrl } from '../App'
import { useNavigate } from 'react-router-dom'
import Footer from '../components/Footer'

const PHASES = [
    "Analyzing your idea...",
    "Designing layout & structure...",
    "Writing HTML & CSS...",
    "Adding animations & interactions...",
    "Final quality checks..."
];

function Generate() {
    const navigate = useNavigate()
    const [prompt, setPrompt] = useState("")
    const [loading, setLoading] = useState(false)
    const [progress, setProgress] = useState(0)
    const [phaseIndex, setPhaseIndex] = useState(0)
    const [error, setError] = useState("")

    const handleGenerateWebsite = async () => {
        setLoading(true)
        try {
            const result = await axios.post(`${serverUrl}/api/website/generate`, { prompt },
                { withCredentials: true })
            console.log(result)
            setProgress(100)
            setLoading(false)
            navigate(`/editor/${result.data.websiteId}`)
        } catch (e) {
            setLoading(false)
            setError(e.response.data.message || "something went wrong")
            console.log(e)
        }
    }
    useEffect(() => {
        if (!loading) {
            setPhaseIndex(0)
            setProgress(0)
            return
        }

        let value = 0
        let phase = 0

        const interval = setInterval(() => {
            const increment = value < 20
                ? Math.random() * 1.5
                : value < 60
                    ? Math.random() * 1.2
                    : Math.random() * 0.6

            value += increment

            if (value >= 93) value = 93;

            phase = Math.min(
                Math.floor((value / 100) * PHASES.length), PHASES.length - 1
            )

            setProgress(Math.floor(value))
            setPhaseIndex(phase)
        }, 1200)
        return () => clearInterval(interval)
    }, [loading])


    return (
        <>
            <div className="relative min-h-screen bg-linear-to-br from-[#050505] via-slate-950 to-[#050505] text-white overflow-y-auto">
                <GenerateBar />
                <div className='max-w-6xl mx-auto px-10'>
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        className='text-center mx-auto my-25'
                    >
                        <h1 className='text-4xl md:text-8xl font-bold m-5 leading-tight'>
                            Build Websites with
                            <span className='block bg-linear-to-r from-white to-zinc-400 
                        bg-clip-text text-transparent'>Real AI Power</span>
                        </h1>
                        <p className='text-zinc-400 max-w-2xl mx-auto'>
                            This Process may take several minutes - <span className='font-medium text-white'>ConTex.ai</span> focuses on quality
                            not shortcuts.
                        </p>
                    </motion.div>
                    <div className='px-5'>
                        <h1 className='text-xl font-semibold mb-4'>Describe your website</h1>
                        <div className='relative'>
                            <textarea
                                onChange={(e) => setPrompt(e.target.value)}
                                value={prompt}
                                placeholder='Describe your website in detail...'
                                className='w-full h-56 p-6 rounded-3xl bg-black/60 border border-white/10
                            outline-none resize-non text-sm leading-relaxed focus:ring-2 focus:ring-white/20'
                            />
                        </div>
                        {error && <p className='mt-4 text-sm text-red-400'>{error}</p>}
                    </div>
                    <div className='my-15 flex justify-center'>
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.96 }}
                            disabled={!prompt.trim() && loading}
                            onClick={handleGenerateWebsite}
                            className={`px-14 py-4 rounded-2xl font-semibold text-lg ${prompt.trim() && !loading
                                ? "bg-white text-black cursor-pointer"
                                : "bg-white/20 text-zinc-400 cursor-not-allowed"
                                }`}
                        >
                            Generate Website
                        </motion.button>

                    </div>
                    {loading && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className='max-w-xl mx-auto mt-12'
                        >
                            <div className='flex justify-between mb-2 text-xs text-zinc-400'>
                                <span>{PHASES[phaseIndex]}</span>
                                <span>{progress}%</span>
                            </div>
                            <div className='h-2 w-full bg-white/10 rounded-full overflow-hidden'>
                                <motion.div
                                    animate={{ width: `${progress}%` }}
                                    transition={{ ease: "easeOut", duration: 0.8 }}
                                    className='h-full bg-linear-to-r from-white to-zinc-300'
                                >
                                </motion.div>
                            </div>
                            <div className='text-center text-xs text-zinc-400 mt-4'>
                                Estimated time remaining:{" "}
                                <span className='text-white font-medium'>
                                    ~10-15 minutes
                                </span>
                            </div>
                        </motion.div>
                    )}
                </div>
            </div>
            <Footer />
        </>
    )
}

export default Generate
