import { useEffect, useState } from 'react'
import { motion } from "motion/react"
import { Link, useNavigate } from 'react-router-dom'
import SignIn from './SignIn'
import { useSelector } from 'react-redux'
import { HomeBar } from '../components/AppBar'
import Footer from '../components/Footer'
import axios from 'axios'
import { serverUrl } from '../App'

function Home() {

    const highlightCard = [
        "AI Generated Code",
        "Fully Responsive Layouts",
        "Production Ready Output"
    ]
    const navigate = useNavigate()
    const { userData } = useSelector(state => state.user)
    const [openLogin, setOpenLogin] = useState(false)
    const [websites, setWebsites] = useState([])

    useEffect(() => {
        if (!userData) return;
        const handleGetAllWebsites = async () => {
            try {
                const result = await axios.get(`${serverUrl}/api/website/get-all-items`, { withCredentials: true })
                setWebsites(result.data || [])

            } catch (e) {
                console.log(e)
            }
        }
        handleGetAllWebsites()
    }, [userData])


    return (
        <>
            <div className="relative min-h-screen bg-[#040404] text-white overflow-hidden">
                <HomeBar />
                <section className=" my-40 p-2 text-center">
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
                    <button onClick={() => userData ? navigate("/dashboard") : setOpenLogin(true)}
                        className="px-10 py-4 mt-12 rounded-xl bg-white text-black
                 font-semibold hover:scale-105 transition cursor-pointer">
                        {userData ? "Go to Dashboard" : "Get Started"}
                    </button>
                </section>
                {!userData && (
                    <section className="max-w-7xl mx-auto my-15 p-8">
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
                )}

                {userData && websites?.length > 0 && (
                    <div className='relative max-w-full mx-auto px-20 my-5 flex justify-start items-start'>
                        <motion.div
                            initial={{ opacity: 0, y: 12 }}
                            animate={{ opacity: 1, y: 0 }}
                            className='mb-2'
                        >
                            <h1 className='text-3xl font-bold'>Your Websites</h1>
                        </motion.div>
                    </div>

                )}
                {userData && websites?.length > 0 && (
                    <div className='relative grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-8 px-20 mt-5'>
                        {websites.map((web, i) => {
                            return <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 40 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.15 }}
                                whileHover={{ y: -14, scale: 1.03 }}
                                className='rounded-2xl bg-white/5 border-2 border-white/10
                                 hover:bg-white/10 transition flex flex-col '
                            >
                                <div className='relative h-60 bg-black'>
                                    <iframe srcDoc={web.latestCode} className='absolute inset-0 w-[140%] h-[140%] scale-[0.72]
                                    origin-top-left pointer-events-none bg-white' />
                                    <div className='absolute inset-0 bg-black/30' />
                                </div>
                            </motion.div>
                        })}

                    </div>
                )}
            </div>
            <Footer />
            {openLogin && <SignIn open={openLogin} onClose={() => setOpenLogin(false)} />}
        </>
    )
}

export default Home
