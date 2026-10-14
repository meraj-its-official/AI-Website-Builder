import React from 'react'
import { DashboardBar } from '../components/AppBar'
import { useSelector } from 'react-redux'
import { motion } from "motion/react"
import { useNavigate } from 'react-router-dom'

function Dashboard() {
    const { userData } = useSelector(state => state.user)
    const navigate = useNavigate()
    return (
        <div className="relative min-h-screen bg-[#050505] text-white overflow-y-auto">
            <DashboardBar />
            <section className='max-w-full mx-auto pt-55 pb-32 px-62 flex justify-start'>
                <motion.div
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    className='mb-10'
                >
                    <p className='text-zinc-400 mb-1 text-sm'>Welcome Back</p>
                    <h1 className='text-3xl font-bold'>{userData.name}</h1>
                </motion.div>
            </section>
        </div>
    )
}

export default Dashboard
