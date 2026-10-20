import React, { useEffect } from 'react'
import { useDispatch } from "react-redux"
import axios from "axios"
import { serverUrl } from '../App.jsx'
import { setUserData } from '../redux/userSlice'

function useGetCurrentUser() {
    const dispatch = useDispatch()
    useEffect(() => {
        const getCurrentUser = async () => {
            try {
                const result = await axios.get(`${serverUrl}/api/user/me`, {

                    withCredentials: true
                })
                dispatch(setUserData(result.data))
            } catch (e) {
                console.log(e)
            }
        }
        getCurrentUser()
    }, [])
}

export default useGetCurrentUser
