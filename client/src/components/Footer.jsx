import React from 'react'

function Footer() {
    return (
        <>
            <div className='"relative min-w-screen bg-[#050505]'>
                <footer className="border-t border-white/10 py-10 text-center text-sm text-zinc-500">
                    &copy; {new Date().getFullYear()} ConTex.ai. All rights reserved. ~ Developed by M.M.ALAM
                </footer>
            </div>
        </>
    )
}

export default Footer
