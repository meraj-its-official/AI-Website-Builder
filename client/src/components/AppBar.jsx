import React, { useEffect, useState } from 'react'
import { AnimatePresence, motion } from "motion/react"
import { Link, useNavigate, useParams } from 'react-router-dom'
import SignIn from '../pages/SignIn.jsx'
import { useDispatch, useSelector } from 'react-redux'
import { ArrowLeft, Coins, X } from 'lucide-react'
import axios from 'axios'
import { serverUrl } from '../App.jsx'
import { setUserData } from '../redux/userSlice'

export const HomeBar = () => {
    const [openLogin, setOpenLogin] = useState(false)
    const { userData } = useSelector(state => state.user)
    const [openProfile, setOpenProfile] = useState(false)
    const dispatch = useDispatch()
    const navigate = useNavigate()
    const handleLogOut = async () => {
        try {
            await axios.get(`${serverUrl}/api/auth/logout`, {
                withCredentials: true
            })
            dispatch(setUserData(null))
            setOpenProfile(false)
        } catch (e) {
            console.log(e)
        }
    }
    return (
        <div>
            <motion.div
                initial={{ y: -40, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-black/40 border-b
                 border-white/10">
                <div className='max-w-full mx-auto px-6 sm:px-6 lg:px-8 py-6 flex justify-between items-center'>
                    <Link className='font-bold text-3xl' to={'/'}>
                        ConTex<span className='text-zinc-400'>.ai</span>
                    </Link>
                    <div className='flex items-center gap-5'>
                        <div className='hidden md:inline font-medium text-lg text-zinc-400 hover:text-white cursor-pointer'
                            onClick={() => navigate('/pricing')}>
                            {userData ? "  Upgrade" : "Price"}
                        </div>
                        {userData && <div className='hidden md:flex items-center gap-2.5 px-3 py-1.5 rounded-full
                        bg-white/5 border border-white/10 text-sm cursor-pointer hover:bg-white/10 transition'
                            onClick={() => navigate('/pricing')}>
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
                                    <img src={userData.avatar || `https://ui-avatars.com/api/?name=${userData.name}`} alt="" referrerPolicy='no-referrer'
                                        className="w-9 h-9 rounded-full border cursor-pointer border-white/20 object-cover" />
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
                                                    <Coins size={14} className="text-yellow-400"
                                                        onClick={() => navigate('/pricing')} />
                                                    <span className="text-zinc-300">Credits</span>
                                                    <span className='font-light'>{userData.credits}+</span>
                                                </button>

                                                <button onClick={() => navigate("/dashboard")} className="w-full px-4 py-3 flex justify-center cursor-pointer 
                                                 gap-2 text-sm font-medium border-b border-white/10 hover:bg-white/5">
                                                    Dashboard
                                                </button>

                                                <button onClick={handleLogOut} className="w-full px-4 py-3 flex justify-center cursor-pointer 
                                                 gap-2 text-sm font-bold  text-red-500 border-b border-white/10 hover:bg-red-950">
                                                    Logout
                                                </button>
                                            </motion.div>
                                        </>
                                    )}
                                </AnimatePresence>
                            </div>}
                    </div>
                </div>
            </motion.div >
            {openLogin && <SignIn open={openLogin} onClose={() => setOpenLogin(false)} />
            }
        </div >
    )
}


export const DashboardBar = () => {
    const navigate = useNavigate()
    return (
        <div>
            <div className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-black/40 border-b
                 border-white/10">
                <div className='max-w-full mx-auto px-6 my-4 h-16 flex items-center justify-between'>
                    <div className='flex items-center gap-4'>
                        <button onClick={() => navigate('/')} className='p-2 rounded-lg cursor-pointer hover:bg-white/10 transition'>
                            <ArrowLeft size={16} /></button>
                        <h1 className='font-semibold text-lg'>Dashboard</h1>
                    </div>
                    <button onClick={() => navigate('/generate')} className="px-4 py-2 rounded-lg bg-white text-black text-sm font-semibold hover:scale-105
                    transition cursor-pointer items-center"> + New Website </button>
                </div>
            </div >
        </div >
    )
}

export const GenerateBar = () => {
    const navigate = useNavigate()
    const { userData } = useSelector(state => state.user)
    return (
        <div>
            <div className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl border-b
                 border-white/20 bg-transparent">
                <div className='max-w-full mx-auto px-15 my-4 h-16 flex items-center justify-between'>
                    <div className='flex items-center gap-4'>
                        <button onClick={() => navigate('/dashboard')} className='p-2 rounded-lg cursor-pointer hover:bg-white/10 transition'>
                            <ArrowLeft size={16} /></button>
                        <Link className='font-bold text-3xl' to={'/'}>
                            ConTex<span className='text-zinc-400'>.ai</span>
                        </Link>
                    </div>
                    <div className='flex items-center gap-5'>
                        <div className='hidden md:inline font-medium text-lg text-zinc-400 hover:text-white cursor-pointer'
                            onClick={() => navigate('/pricing')}>
                            Upgrade
                        </div>
                        {userData && <div className='hidden md:flex items-center gap-2.5 px-3 py-1.5 rounded-full
                        bg-white/5 border border-white/10 text-sm cursor-pointer hover:bg-white/10 transition'
                            onClick={() => navigate('/pricing')}>
                            <Coins size={14} className="text-yellow-400" />
                            <span className="text-zinc-300">Credits</span>
                            <span className='font-light'>{userData.credits}+</span>
                        </div>}
                    </div>
                </div>
            </div >
        </div >
    )
}


export const EditorBar = ({ onclose }) => {
    const navigate = useNavigate()
    const { userData } = useSelector(state => state.user)
    const { id } = useParams()
    const [website, setWebsite] = useState(null)
    const [error, setError] = useState("")
    useEffect(() => {
        const handleGetWebsite = async () => {
            try {
                const result = await axios.get(`${serverUrl}/api/website/get-by-id/${id}`,
                    { withCredentials: true })
                setWebsite(result.data)
            } catch (e) {
                setError(e.response.data.message)
            }
        }
        handleGetWebsite()
    }, [id])

    return (
        <div>
            <div className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl border-b
                 border-white/20 bg-transparent">
                <div className='max-w-full mx-auto px-15 my-2 h-12 flex items-center justify-between'>
                    <div className='flex items-center gap-4'>
                        <button onClick={() => navigate('/dashboard')} className='p-2 rounded-lg cursor-pointer hover:bg-white/10 transition'>
                            <ArrowLeft size={16} /></button>
                        <Link className='font-medium text-2xl' to={'/'}>
                            ConTex<span className='text-zinc-400'>.ai</span>
                        </Link>
                    </div>
                    <Header />
                    <div className='flex items-center gap-5'>
                        <div className='hidden md:inline font-medium text-lg text-zinc-400 hover:text-white cursor-pointer'
                            onClick={() => navigate('/pricing')}>
                            Upgrade
                        </div>
                        {userData && <div className='hidden md:flex items-center gap-2.5 px-3 py-1.5 rounded-full
                        bg-white/5 border border-white/10 text-sm cursor-pointer hover:bg-white/10 transition'
                            onClick={() => navigate('/pricing')}>
                            <Coins size={14} className="text-yellow-400" />
                            <span className="text-zinc-300">Credits</span>
                            <span className='font-light'>{userData.credits}+</span>
                        </div>}
                    </div>
                    {onclose && <button className='cursor-pointer absolute top-4 right-4 p-2 mr-2 rounded-lg bg-black/70 hover:bg-white/20
                                border-2 border-white md:hidden' onClick={onclose}><X size={18} /> </button>}
                </div>
            </div >
        </div >
    )

    function Header() {
        return (
            <div className='h-14 px-6 flex items-center justify-between'>
                <span className="font-semibold truncate bg-linear-to-r from-purple-400 to-blue-400 bg-clip-text 
                text-transparent hidden md:block"> {website?.title}</span>
            </div>
        )
    }
}

