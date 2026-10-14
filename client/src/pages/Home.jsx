import React, { useState } from 'react'
import { motion } from "motion/react"
import { Link, useNavigate } from 'react-router-dom'
import SignIn from './SignIn'
import { useSelector } from 'react-redux'
import { HomeBar } from '../components/AppBar'

function Home() {

    const highlightCard = [
        "AI Generated Code",
        "Fully Responsive Layouts",
        "Production Ready Output"
    ]
    const navigate = useNavigate()
    const { userData } = useSelector(state => state.user)
    const [openLogin, setOpenLogin] = useState(false)
    return (
        <div className="relative min-h-screen bg-[#040404] text-white overflow-y-auto">
            <HomeBar />
            <section className="pt-44 pb-32 px-6 text-center">
                <motion.h1
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-5xl md:text-7xl font-bold tracking-tight"
                >
                    Build Sleek Websites <br />
                    <span className="bg-linear-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                        with AI
                    </span>
                </motion.h1>
                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-8 max-w-2xl mx-auto text-zinc-400 text-lg"
                >
                    Describe your idea into Prompt and let AI generate a modern, responsive, production-ready website.
                </motion.p>
                <button onClick={() => userData ? navigate("/dashboard") : setOpenLogin(true)} className="px-10 py-4 mt-12 rounded-xl bg-white text-black
                 font-semibold hover:scale-105 transition cursor-pointer">
                    {userData ? "Go to Dashboard" : "Get Started"}
                </button>
            </section>

            <section className="max-w-7xl mx-auto px-6 pb-32">
                <div className='grid grid-cols-1 md:grid-cols-3 gap-8'>
                    {highlightCard.map((h, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 40 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            className="rounded-2xl bg-white/5 border border-white/10 p-8"
                        >
                            <h1 className="text-xl font-semibold mb-3">{h}</h1>
                            <p className='text-sm text-zinc-400'>
                                ConTex.ai builds real websites — clean code,
                                animations, responsiveness and scalable structure.
                            </p>
                        </motion.div>
                    ))}
                </div>
            </section>

            <footer className="border-t border-white/10 py-10 text-center text-sm text-zinc-500">
                &copy; {new Date().getFullYear()} ConTex.ai
            </footer>

            {openLogin && <SignIn open={openLogin} onClose={() => setOpenLogin(false)} />}
        </div>
    )
}

export default Home
