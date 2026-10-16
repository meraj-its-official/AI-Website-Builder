import React, { useEffect, useState } from 'react'
import { DashboardBar } from '../components/AppBar'
import { useSelector } from 'react-redux'
import { motion } from "motion/react"
import { useNavigate } from 'react-router-dom'
import Footer from '../components/Footer'
import axios from 'axios'
import { serverUrl } from '../App'
import { Rocket, Share2 } from 'lucide-react'

function Dashboard() {
    const { userData } = useSelector(state => state.user)
    const navigate = useNavigate()
    const [websites, setWebsites] = useState([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")

    useEffect(() => {
        const handleGetAllWebsites = async () => {
            try {
                setLoading(true)
                const result = await axios.get(`${serverUrl}/api/website/get-all-items`, { withCredentials: true })
                setWebsites(result.data || [])
                setLoading(false)

            } catch (e) {
                console.log(e)
                setError(e.response.data.message)
                setLoading(false)
            }
        }
        handleGetAllWebsites()
    }, [])

    return (
        <>
            <div className="relative min-h-screen bg-[#050505] text-white overflow-y-auto">
                <DashboardBar />
                <div className='max-w-full mx-auto px-62 mt-45 flex justify-start'>
                    <motion.div
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        className='mb-2'
                    >
                        <p className='text-zinc-400 mb-1 text-sm'>Welcome Back</p>
                        <h1 className='text-3xl font-bold'>{userData.name}</h1>
                    </motion.div>
                </div>

                {loading && (
                    <div className='mt-24 text-center text-zinc-400'>Loading Your Items...</div>
                )}

                {error && !loading(
                    <div className='mt-24 text-center text-red-400'>{error}</div>
                )}

                {websites?.length == 0 && (
                    <div className='mt-24 text-center text-zinc-400'>You have no items</div>
                )}

                {!loading && !error && websites.length > 0 && (
                    <div className='grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-8 px-20 mt-20'>
                        {websites.map((web, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.05 }}
                                whileHover={{ y: 6, x: 15 }}
                                className='rounded-2xl bg-white/5 border-2 border-white/10
                                overflow-hidden hover:bg-white/10 transition flex flex-col '
                            >
                                <div className='relative h-40 bg-black cursor-pointer'>
                                    <iframe srcDoc={web.latestCode} className='absolute inset-0 w-[140%] h-[140%] scale-[0.72]
                                    origin-top-left pointer-events-none bg-white' />
                                    <div className='absolute inset-0 bg-black/30' />
                                </div>
                                <div className='p-5 flex flex-col gap-4 flex-1'>
                                    <h3 className='text-base font-semibold line-clamp-2'>{web.title}</h3>
                                    <p className='text-xs text-zinc-400' >Last Updated {""}
                                        {new Date(web.updatedAt).toLocaleDateString()}
                                    </p>
                                    {!web.deployed ? (
                                        <button className='mt-auto flex items-center justify-center gap-2
                                        px-4 py-2 rounded-xl text-sm font-semibold bg-linear-to-r from-indigo-500
                                        to-purple-500 hover:scale-105 transition cursor-pointer '
                                        ><Rocket size={18} />Deploy</button>
                                    ) : (<button className=''><Share2 />Share</button>)}
                                </div>
                            </motion.div>
                        ))}
                    </div>
                )}
            </div>
            <Footer />
        </>
    )
}

export default Dashboard
