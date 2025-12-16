import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">Ferretería Web</h1>
        <button className="bg-blue-600 text-white p-4 rounded hover:bg-blue-700 transition">
          Sistema Web Iniciado
        </button>
      </div>
    </div>
  )
}

export default App
