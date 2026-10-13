import React, { useState } from 'react'
import { AnimatePresence, motion } from "motion/react"
import { Link } from 'react-router-dom'
import SignIn from '../pages/SignIn'
import { useSelector } from 'react-redux'
import { Coins } from 'lucide-react'

function Appbar() {
    const [openLogin, setOpenLogin] = useState(false)
    const { userData } = useSelector(state => state.user)
    const [openProfile, setOpenProfile] = useState(false)
    return (
        <div>
            <motion.div
                initial={{ y: -40, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-black/40 border-b
                 border-white/10 ">
                <div className='max-w-full mx-auto px-6 sm:px-6 lg:px-8 py-6 flex justify-between items-center'>
                    <Link className='font-bold text-3xl' to={'/'}>
                        ConTex.Ai
                    </Link>
                    <div className='flex items-center gap-5'>
                        <div className='hidden md:inline font-medium text-lg text-zinc-400 hover:text-white cursor-pointer'>
                            Price
                        </div>
                        {userData && <div className='hidden md:flex items-center gap-2.5 px-3 py-1.5 rounded-full
                        bg-white/5 border border-white/10 text-sm cursor-pointer hover:bg-white/10 transition'>
                            <Coins size={14} className="text-yellow-400" />
                            <span className="text-zinc-300">Credits</span>
                            <span className='font-light'>{userData.credits}+</span>
                        </div>}
                        {!userData ? <button onClick={() => setOpenLogin(true)} className="px-4 py-2 rounded-lg cursor-pointer 
                        border-solid border-2 hover:bg-white/10
                         hover:border-slate-400 text-sm ">
                            Get Started
                        </button>
                            :
                            <div className='relative'>
                                <button className='flex items-center' onClick={() => setOpenProfile(!openProfile)}>
                                    <img src={userData.avatar || `https://ui-avatars.com/api/?name=${userData.name}`} alt="" className="w-9 h-9 rounded-full border cursor-pointer border-white/20 object-cover" />
                                </button>
                                <AnimatePresence>
                                    {openProfile && (
                                        <>
                                            <motion.div
                                                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                                                className='absolute right-0 mt-3 w-60 z-50 rounded-xl
                                                bg-[#0b0b0b] border border-white/10 shadow-2xl overflow-hidden '
                                            >
                                                <div className='px-4 py-3 border-b border-white/10  '>
                                                    <p className="text-sm font-medium truncate">
                                                        {userData.name}
                                                    </p>
                                                    <p className="text-xs text-zinc-500 truncate">
                                                        {userData.email}
                                                    </p>
                                                </div>

                                                <button className="md:hidden w-full px-4 py-3 flex justify-center cursor-pointer 
                                                 gap-2 text-sm border-b border-white/10 hover:bg-white/5">
                                                    <Coins size={14} className="text-yellow-400" />
                                                    <span className="text-zinc-300">Credits</span>
                                                    <span className='font-light'>{userData.credits}+</span>
                                                </button>

                                                <button className="md:hidden w-full px-4 py-3 flex justify-center cursor-pointer 
                                                 gap-2 text-sm font-medium border-b border-white/10 hover:bg-white/5">Dashboard</button>
                                                <button className="md:hidden w-full px-4 py-3 flex justify-center cursor-pointer 
                                                 gap-2 text-sm font-bold  text-red-500 border-b border-white/10 hover:bg-red-950">Logout</button>
                                            </motion.div>
                                        </>
                                    )}
                                </AnimatePresence>
                            </div>}
                    </div>
                </div>
            </motion.div>
            {openLogin && <SignIn open={openLogin} onClose={() => setOpenLogin(false)} />}
        </div>
    )
}

export default Appbar
