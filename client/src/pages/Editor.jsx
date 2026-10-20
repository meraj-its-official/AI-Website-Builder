import axios from 'axios'
import React, { useCallback, useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { serverUrl } from '../App.jsx'
import { EditorBar } from '../components/AppBar.jsx'
import { Code2, MessageSquare, Monitor, Rocket, Send, X } from 'lucide-react'
import { animate, AnimatePresence, motion } from 'motion/react'
import Editor from '@monaco-editor/react';

const thinkingSteps = [
    "Understanding your request...",
    "Planning layout changes...",
    "Improving responsiveness...",
    "Applying animations...",
    "Finalizing update..."
]

function WebsiteEditor() {
    const { id } = useParams()
    const [website, setWebsite] = useState(null)
    const [error, setError] = useState("")
    const [code, setCode] = useState("")
    const [messages, setMessages] = useState([])
    const [prompt, setPrompt] = useState("")
    const iframeRef = useRef(null)
    const [updateLoading, setUpdateLoading] = useState(false)
    const [thinkingIndex, setThinkingIndex] = useState(0)
    const [sidebarWidth, setSidebarWidth] = useState(400);
    const isDragging = useRef(false);
    const [activeDrag, setActiveDrag] = useState(false);
    const [showCode, setShowCode] = useState(false)
    const [showPreview, setShowPreview] = useState(false)
    const [showChat, setShowChat] = useState(false)
    const [deployingId, setDeployingId] = useState(null);

    const handleUpdate = async () => {
        if (!prompt) return
        setUpdateLoading(true)
        try {
            const text = prompt
            setPrompt("")
            setMessages((m) => [...m, { role: "user", content: prompt }])
            const result = await axios.post(`${serverUrl}/api/website/update/${id}`, { prompt: text },
                { withCredentials: true })
            setUpdateLoading(false)
            setMessages((m) => [...m, { role: "ai", content: result.data.message }])
            setCode(result.data.code)
        } catch (e) {
            setUpdateLoading(false)
            console.log(e)
        }
    }

    const handleDeploy = async (id) => {
        setDeployingId(id);
        try {
            const result = await axios.get(`${serverUrl}/api/website/deploy/${id}`, { withCredentials: true })
            if (result.data?.url) {
                window.open(`${result.data.url}`, "_blank")
                setWebsite((prev) => (prev ? { ...prev, deployed: true, deployedUrl: result.data.url } : prev));
            }
        } catch (e) {
            console.log(e)
        } finally {
            setDeployingId(null);
        }
    }

    const handleMouseMove = useCallback((e) => {
        if (!isDragging.current) return;

        requestAnimationFrame(() => {
            const newWidth = e.clientX;
            if (newWidth >= 200 && newWidth <= 600) {
                setSidebarWidth(newWidth);
            }
        });
    }, []);

    const handleMouseUp = useCallback(() => {
        isDragging.current = false;
        setActiveDrag(false);
        document.body.style.cursor = 'default';
    }, []);

    useEffect(() => {
        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('mouseup', handleMouseUp);
        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        };
    }, [handleMouseMove, handleMouseUp]);

    const startResize = (e) => {
        e.preventDefault();
        isDragging.current = true;
        setActiveDrag(true);
        document.body.style.cursor = 'col-resize';
    };


    useEffect(() => {
        if (!updateLoading) return;
        const i = setInterval(() => {
            setThinkingIndex((i) => (i + 1) % thinkingSteps.length)
        }, 1500)

        return () => clearInterval(i)
    }, [updateLoading])

    useEffect(() => {
        const handleGetWebsite = async () => {
            try {
                const result = await axios.get(`${serverUrl}/api/website/get-by-id/${id}`,
                    { withCredentials: true })
                setWebsite(result.data)
                setCode(result.data.latestCode)
                setMessages(result.data.conversation)
            } catch (e) {
                setError(e.response.data.message)
            }
        }
        handleGetWebsite()
    }, [id])

    useEffect(() => {
        if (!iframeRef.current || !code) return;
        const blob = new Blob([code], { type: "text/html" })
        const url = URL.createObjectURL(blob)
        iframeRef.current.src = url
        return () => URL.revokeObjectURL(url)
    }, [code])

    if (error) {
        return (
            <div className="h-screen flex items-center justify-center bg-black text-red-400">
                {error}
            </div>
        )
    }
    if (!website) {
        return (
            <div className="h-screen flex items-center justify-center bg-black text-white">
                Loading...
            </div>
        )
    }

    return (
        <div className="h-screen w-screen bg-linear-to-br from-[#050505] via-slate-950 to-[#050505] text-white">
            <EditorBar />
            <div className='h-full max-w-full flex pt-17 px-2 '>
                <aside style={{ width: `${sidebarWidth}px` }}
                    className={`shrink-0 hidden md:flex w-95 flex-col mr-2 mb-4 rounded-2xl bg-black/80 border-r border-white/10 
                    ${!activeDrag ? 'transition-all duration-75' : ''}`}>
                    <>
                        <div className='flex-1 px-4 py-4 space-y-4 overflow-y-auto'>
                            {messages.map((m, i) => (
                                <div
                                    key={i}
                                    className={`max-w-[85%] ${m.role === "user" ? "ml-auto" : "mr-auto"}`}
                                >
                                    <div
                                        className={`px-4 py-2.5 rounded-2xl text-sm leading-relaxed
                                 ${m.role === "user"
                                                ? "bg-white text-black"
                                                : "bg-white/5 border border-white/10 text-zinc-200"
                                            }`}
                                    >
                                        {m.content}
                                    </div>
                                </div>
                            ))}
                            {updateLoading &&
                                <div className='max-w-[85%] mr-auto'>
                                    <div className='px-4 p-2.5 rounded-2xl text-xs border
                                    border-white/10 text-zinc-400 italic bg-transparent'
                                    >{thinkingSteps[thinkingIndex]}</div>
                                </div>
                            }
                        </div>
                        <div className='p-3 border-t border-white/10 rounded-b-lg'>
                            <div className='flex gap-2'>
                                <textarea
                                    row="1" placeholder='Describe Changes...' className='flex-1 resize-none rounded-2xl px-3 py-1 border-2
                                     border-white/10 text-sm focus:ring-2 focus:ring-white/20 outline-none '
                                    onChange={(e) => setPrompt(e.target.value)} value={prompt}
                                ></textarea>
                                <button className='px-5 py-1 cursor-pointer rounded-xl bg-white text-black'
                                    onClick={handleUpdate}
                                > <Send size={14} /> </button>
                            </div>
                        </div>
                    </>
                </aside>
                <div
                    onMouseDown={startResize}
                    className={`w-1.5 h-full cursor-col-resize hover:bg-blue-600 transition-colors z-30 relative shrink-0
          ${activeDrag ? 'bg-blue-500 w-2' : 'bg-transparent'}`}
                ></div>
                <div className='flex-1 flex flex-col'>
                    <div className='h-14 px-4 flex justify-between items-center border-b border-white/10 bg-black/80'>
                        <span className='text-xs text-zinc-400'>Live Preview</span>
                        <div className='flex gap-2'>
                            {!website?.deployed && (
                                <button className='flex items-center gap-2 px-6 py-1.5 rounded-lg bg-linear-to-r cursor-pointer
                             from-indigo-500 to-purple-500 text-sm font-semibold hover:scale-105 transition'
                                    disabled={deployingId === website?._id}
                                    onClick={() => handleDeploy(website?._id)}
                                ><Rocket size={16} />{deployingId === website?._id ? "Deploying..." : "Deploy"}</button>)}
                            <button className='p-2 md:hidden cursor-pointer' onClick={() => setShowChat(true)}><MessageSquare size={18} /> </button>
                            <button className='cursor-pointer gap-2' onClick={() => setShowCode(true)}
                            ><Code2 size={18} /> </button>
                            <button className='cursor-pointer gap-2' onClick={() => setShowPreview(true)} ><Monitor size={18} /> </button>
                        </div>
                    </div>
                    <iframe ref={iframeRef} className='flex-1 w-full mb-4 rounded-2xl border border-white/10 bg-white'
                        sandbox='allow-scripts allow-same-origin allow-forms' />
                    <AnimatePresence>
                        {showCode && (
                            <motion.div
                                initial={{ x: "100%" }}
                                animate={{ x: 0 }}
                                exit={{ x: "100%" }}
                                className='fixed inset-y-0 right-0 w-full mt-31 mb-4 lg:w-[45%] z-9999 bg-transparent 
                               rounded-tl-xl flex flex-col border-2 border-slate-600'
                            >
                                <div className='h-12 px-4 flex justify-between items-center bg-[#1e1e1e] rounded-tl-xl'>
                                    <span className='text-sm font-medium'>index.html</span>
                                    <button className='cursor-pointer' onClick={() => setShowCode(false)} ><X size={18} /></button>
                                </div>
                                <Editor
                                    theme='vs-dark'
                                    value={code}
                                    language='html'
                                    onChange={(v) => setCode(v)}
                                />
                            </motion.div>
                        )}
                    </AnimatePresence>
                    <AnimatePresence>
                        {showPreview && (
                            <motion.div
                                className='fixed inset-0 z-9999 bg-black'
                            >
                                <iframe className='w-full h-full bg-white' srcDoc={code}
                                    sandbox='allow-scripts allow-same-origin allow-forms' />
                                <button className='cursor-pointer absolute top-4 right-4 p-2 mr-2 rounded-lg bg-black/70 hover:bg-white/20
                                border-2 border-white'
                                    onClick={() => setShowPreview(false)} ><X size={20} /></button>
                            </motion.div>
                        )}
                    </AnimatePresence>
                    <AnimatePresence>
                        {showChat && (
                            <motion.div
                                initial={{ y: "100%" }}
                                animate={{ y: 0 }}
                                exit={{ y: "100%" }}
                                className='fixed inset-0 z-9999 bg-black flex flex-col'
                            >
                                <EditorBar onclose={() => setShowChat(false)} />
                                <>
                                    <div className='flex-1 px-4 py-4 space-y-4 overflow-y-auto'>
                                        {messages.map((m, i) => (
                                            <div
                                                key={i}
                                                className={`max-w-[85%] ${m.role === "user" ? "ml-auto" : "mr-auto"}`}
                                            >
                                                <div
                                                    className={`px-4 py-2.5 rounded-2xl text-sm leading-relaxed
                                 ${m.role === "user"
                                                            ? "bg-white text-black"
                                                            : "bg-white/5 border border-white/10 text-zinc-200"
                                                        }`}
                                                >
                                                    {m.content}
                                                </div>
                                            </div>
                                        ))}
                                        {updateLoading &&
                                            <div className='max-w-[85%] mr-auto'>
                                                <div className='px-4 p-2.5 rounded-2xl text-xs border
                                    border-white/10 text-zinc-400 italic bg-transparent'
                                                >{thinkingSteps[thinkingIndex]}</div>
                                            </div>
                                        }
                                    </div>
                                    <div className='p-3 border-t border-white/10 rounded-b-lg'>
                                        <div className='flex gap-2'>
                                            <textarea
                                                row="1" placeholder='Describe Changes...' className='flex-1 resize-none rounded-2xl px-3 py-1 border-2
                                     border-white/10 text-sm focus:ring-2 focus:ring-white/20 outline-none '
                                                onChange={(e) => setPrompt(e.target.value)} value={prompt}
                                            ></textarea>
                                            <button className='px-5 py-1 cursor-pointer rounded-xl bg-white text-black'
                                                onClick={handleUpdate}
                                            > <Send size={14} /> </button>
                                        </div>
                                    </div>
                                </>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div >
    )
}

export default WebsiteEditor
