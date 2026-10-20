import { ArrowLeft, Check, Coins } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'motion/react'
import { useState } from 'react'
import { useSelector } from 'react-redux'
import { serverUrl } from '../App.jsx'
import axios from 'axios'
import SignIn from './SignIn.jsx'

const plans = [
    {
        keys: "free",
        name: "Free",
        price: "\u20B9 0",
        credits: 100,
        description: "Perfect to explore ConTex.ai",
        features: [
            "AI Website generation",
            "Responsive HTML output",
            "Basic animations",
            "Download source code"
        ],
        popular: false,
        button: "Get Started"
    },
    {
        keys: "pro",
        name: "Pro",
        price: "\u20B9 499",
        credits: 700,
        description: "For serious creators & freelancers",
        features: [
            "Everything is Free ",
            "Fast generation",
            "Edit & regenerate",
            "Download source code"
        ],
        popular: true,
        button: "Upgrade to Pro"
    },
    {
        keys: "enterprise",
        name: "Enterprise",
        price: "\u20B9 1499",
        credits: 3000,
        description: "For team & power users",
        features: [
            "Unlimited iterations",
            "Download source code",
            "Highest priority",
            "Team collaboration",
            "Dedicated support"
        ],
        popular: false,
        button: "Build with Team"
    }

]

function Pricing() {
    const navigate = useNavigate()
    const [openLogin, setOpenLogin] = useState(false)
    const [loadingPlan, setLoadingPlan] = useState(null)
    const { userData } = useSelector(state => state.user)
    const loadRazorpayScript = () => {
        return new Promise((resolve) => {
            if (window.Razorpay) {
                resolve(true);
                return;
            }
            const script = document.createElement('script');
            script.src = 'https://checkout.razorpay.com/v1/checkout.js';
            script.onload = () => resolve(true);
            script.onerror = () => resolve(false);
            document.body.appendChild(script);
        });
    };

    const handleSubscription = async (planKey) => {
        if (planKey === 'free') {
            navigate('/dashboard');
            return;
        }
        setLoadingPlan(planKey);
        if (!userData || !userData._id) {
            setOpenLogin(true);
            return;
        }

        try {
            setLoadingPlan(planKey);

            const scriptLoaded = await loadRazorpayScript();
            if (!scriptLoaded) {
                alert('Razorpay Payment Gateway failed to load. Are you online?');
                return;
            }

            const response = await axios.post(`${serverUrl}/api/payment/orders`, {
                planType: planKey,
                userId: userData._id
            }, { withCredentials: true });


            const data = response.data
            if (!data.success) throw new Error(data.message || 'Order request processing error');

            const { order, planType, razorpayKeyId } = data;
            const startupName = "ConTex.ai";

            const options = {
                key: import.meta.env.VITE_RAZORPAY_API_KEY,
                amount: order.amount,
                currency: order.currency,
                name: startupName,
                description: `${startupName} ${planType.toUpperCase()} plan`,
                order_id: order.id,

                handler: async function (response) {
                    try {
                        const verifyRes = await axios.post(`${serverUrl}/api/payment/verify`, {
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_signature: response.razorpay_signature
                        }, { withCredentials: true });

                        const verifyData = verifyRes.data
                        if (verifyData.success) {
                            alert('Payment Verification Successful!');
                            navigate('/dashboard');
                        } else {
                            alert('Verification Failed. Contact Support.');
                            navigate('/pricing');
                        }
                    } catch (err) {
                        console.error("Verification processing crash:", err);
                        navigate('/pricing');
                    }
                },
                prefill: {
                    name: userData.name || '',
                    email: userData.email || '',
                },
                theme: { color: '#4F46E5' },
                modal: {
                    ondismiss: function () {
                        console.log("Modal display forcefully exited by terminal window action.");
                        navigate('/pricing');
                    }
                }
            };

            const rzp = new window.Razorpay(options);

            rzp.on('payment.failed', function (failPayload) {
                console.error("Internal processing channel connection failure:", failPayload.error);
                navigate('/pricing');
            });

            rzp.open();

        } catch (e) {
            console.error('Checkout Workflow Terminal Crash Exception:', e);
            alert('Initialization Error. Payment routing request interrupted.');
            navigate('/pricing');
        } finally {
            setLoadingPlan(null);
        }
    };
    return (
        <div className="relative min-h-screen overflow-hidden bg-[#050505] text-white px-6 pt-16 pb-24">
            <div className='absolute inset-0 pointer-events-none'>
                <div className='absolute -top-40 -left-40 w-125 h-125 bg-indigo-600/20 rounded-full blur-[120px]'></div>
                <div className='absolute bottom-0 right-0 w-100 h-100 bg-purple-600/20 rounded-full blur-[120px]'></div>
            </div>
            <button className='relative z-10 mb-8 mx-15 flex items-center gap-2 text-sm text-zinc-400 cursor-pointer hover:text-white transition'
                onClick={() => navigate('/')}>
                <ArrowLeft size={16} />
                Back
            </button>
            <motion.div
                initial={{ opacity: 0, y: 24 }}
                animate={{ opacity: 1, y: 0 }}
                className='relative z-10 max-w-4xl mx-auto text-center mb-14'
            >
                <h1 className='text-4xl md:text-5xl font-bold mb-4'
                >Simple, transparent pricing</h1>
                <p className='text-zinc-400 text-lg'>Buy credits once. Build anytime.</p>
            </motion.div>
            <div className='relative z-10 max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8'>
                {plans.map((p, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.12 }}
                        whileHover={{ y: -14, scale: 1.03 }}
                        className={`relative rounded-3xl items-center p-8 border backdrop-blur-xl transition-all
                            ${p.popular
                                ? "border-indigo-500 bg-linear-to-b from-indigo-500/20 to-transparent shows-2xl shadow-indigo-500/30"
                                : "border-white/10 bg-white/5 hover:border-indigo-400 hover:bg-white/10"
                            }`}
                    >
                        {p.popular && (
                            <span className='absolute top-5 right-5 px-3 py-1 text-xs rounded-full
                            bg-indigo-500'>Most Popular</span>
                        )}
                        <h3 className='text-xl font-semibold mb-2'>{p.name}</h3>
                        <h3 className='text-zinc-400 text-sm mb-6'>{p.description}</h3>
                        <div className='flex items-end gap-1 mb-4'>
                            <span className='text-4xl font-bold'>{p.price}</span>
                            <span className='text-sm text-zinc-400 mb-1'>/one-time</span>
                        </div>
                        <div className='flex items-center gap-2 mb-8'>
                            <Coins size={18} className='text-yellow-400' />
                            <span className='font-semibold'>{p.credits}Credits</span>
                        </div>
                        <ul className='space-y-3 mb-15'>
                            {p.features.map((f) => (
                                <li
                                    key={f}
                                    className='flex items-center gap-2 text-sm text-zinc-300'
                                >
                                    <Check size={16} className='text-green-400' />
                                    {f}
                                </li>
                            ))}
                        </ul>
                        <motion.div
                            whileTap={{ scale: 0.96 }}
                            onClick={() => handleSubscription(p.keys)}
                            disabled={loadingPlan !== null}
                            className={`w-full py-3 flex justify-center rounded-xl font-semibold transition
                                cursor-pointer
                                ${p.popular
                                    ? "bg-indigo-500 hover:bg-indigo-600"
                                    : "bg-white/10 hover:bg-white/20"
                                } disabled:opacity-60`}
                        >
                            {loadingPlan === p.keys ? 'Processing Configuration...' : p.button}
                        </motion.div>
                    </motion.div>
                ))}
            </div>
            {openLogin && <SignIn open={openLogin} onClose={() => setOpenLogin(false)} />}
        </div>
    )
}

export default Pricing
