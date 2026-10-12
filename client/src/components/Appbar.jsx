import React, { useState } from 'react'
import { motion } from "motion/react"
import { Link } from 'react-router-dom'
import SignIn from '../pages/SignIn'

function Appbar() {
    const [openLogin, setOpenLogin] = useState(false)
    return (
        <div>
            <motion.div
                initial={{ y: -40, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-black/40 border-b
                 border-white/10 ">
                <div className='min-w-7xl mx-auto px-15 py-6 flex justify-between items-center'>
                    <Link className='font-bold text-3xl' to={'/'}>
                        ConTex.Ai
                    </Link>
                    <div className='flex items-center gap-5'>
                        <div className='hidden md:inline font-medium text-lg text-zinc-400 hover:text-white cursor-pointer'>
                            Price
                        </div>
                        <button onClick={() => setOpenLogin(true)} className="px-4 py-2 rounded-lg cursor-pointer border-solid border-2 hover:bg-white/10
                         hover:border-slate-400 text-sm ">
                            Get Started
                        </button>
                    </div>
                </div>
            </motion.div>
            {openLogin && <SignIn open={openLogin} onClose={() => setOpenLogin(false)} />}
        </div>
    )
}

export default Appbar
