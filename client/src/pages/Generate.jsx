import React from 'react'
import { GenerateBar } from '../components/AppBar'
import { motion } from 'motion/react'
import { useState } from 'react'
import axios from 'axios'
import { serverUrl } from '../App'
import { useNavigate } from 'react-router-dom'
import Footer from '../components/Footer'

function Generate() {
    // const navigate = useNavigate()
    const [prompt, setPrompt] = useState("")
    const handleGenerateWebsite = async () => {
        try {
            const result = await axios.post(`${serverUrl}/api/website/generate`, { prompt },
                {
                    withCredentials: true
                })
            console.log(result)
        } catch (e) {
            console.log(e)
        }
    }

    return (
        <>
            <div className="relative min-h-screen bg-linear-to-br from-[#050505] via-slate-950 to-[#050505] text-white overflow-y-auto">
                <GenerateBar />
                <div className='max-w-6xl mx-auto p-10'>
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
                    <div className='mx-25'>
                        <h1 className='text-xl font-semibold mb-4'>Describe your website</h1>
                        <div className='relative'>
                            <textarea
                                onChange={(e) => setPrompt(e.target.value)}
                                value={prompt}
                                placeholder='Describe your website in detail...'
                                className='w-full h-56 p-6 rounded-3xl bg-black/60 border border-white/10
                            outline-none resize-non text-sm leading-relaxed focus:ring-2 focus:ring-white/20'
                            >
                            </textarea>
                        </div>
                    </div>
                    <div className='my-15 flex justify-center'>
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.96 }}
                            className='cursor-pointer px-14 py-4 rounded-2xl font-semibold text-lg bg-white text-black'
                            onClick={handleGenerateWebsite}
                        >
                            Generate Website
                        </motion.button>
                    </div>
                </div>
            </div>
            <Footer />
        </>
    )
}

export default Generate
