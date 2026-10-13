import { StrictMode } from 'react'
import './index.css'
import App from './App.jsx'
import { createRoot } from 'react-dom/client'
import { Provider } from 'react-redux'
import { store } from './redux/store.js'


createRoot(document.getElementById('root')).render(
  <Provider store={store}>
    <App />
  </Provider>
)
