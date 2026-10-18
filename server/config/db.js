import dns from 'dns'
dns.setServers(['8.8.8.8', '8.8.4.4'])
import mongoose from "mongoose"

const connectDb = async () => {
    try {
        await mongoose.connect(process.env.MONGODB_URL)
        console.log("Database Connected Successfully")
    } catch (e) {
        console.log("Database Connection Error", e.message)
    }
}

export default connectDb