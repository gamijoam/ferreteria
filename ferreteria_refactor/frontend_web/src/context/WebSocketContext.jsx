import { createContext, useContext, useEffect, useState, useRef } from 'react';

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
    const [isConnected, setIsConnected] = useState(false);
    const ws = useRef(null);
    const listeners = useRef({});
    const reconnectTimeout = useRef(null);
    const maxRetries = 10;
    const retryCount = useRef(0);

    const connect = () => {
        // Close existing connection if any
        if (ws.current) {
            ws.current.close();
            ws.current = null;
        }

        // Connect to WebSocket
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // In development we use localhost:8000, in prod we might use relative path
        const wsUrl = `ws://localhost:8000/api/v1/ws`;

        console.log(`🔌 Attempting WebSocket connection to ${wsUrl}...`);

        ws.current = new WebSocket(wsUrl);

        ws.current.onopen = () => {
            console.log('✅ WebSocket Connected Successfully');
            setIsConnected(true);
            retryCount.current = 0;

            // Send ping every 30 seconds to keep connection alive
            setInterval(() => {
                if (ws.current?.readyState === WebSocket.OPEN) {
                    ws.current.send('ping');
                }
            }, 30000);
        };

        ws.current.onmessage = (event) => {
            if (event.data === 'pong') return;

            try {
                const message = JSON.parse(event.data);
                const { type, data } = message;

                // Log received event
                console.log(`📡 WebSocket Event Received: ${type}`, data);

                // Notify all listeners for this event type
                if (listeners.current[type]) {
                    listeners.current[type].forEach(callback => {
                        try {
                            callback(data);
                        } catch (err) {
                            console.error(`Error in listener for ${type}:`, err);
                        }
                    });
                }
            } catch (err) {
                console.warn('Received non-JSON message:', event.data);
            }
        };

        ws.current.onclose = () => {
            console.log('❌ WebSocket Disconnected');
            setIsConnected(false);

            // Attempt Reconnect with exponential backoff
            if (retryCount.current < maxRetries) {
                const timeout = Math.min(1000 * Math.pow(2, retryCount.current), 30000);
                console.log(`Reconnecting in ${timeout}ms (Attempt ${retryCount.current + 1}/${maxRetries})`);

                reconnectTimeout.current = setTimeout(() => {
                    retryCount.current++;
                    connect();
                }, timeout);
            }
        };

        ws.current.onerror = (error) => {
            console.error('WebSocket Error. Check backend is running.');
            // setIsConnected(false); // onerror is usually followed by onclose
        };
    };

    useEffect(() => {
        connect();

        return () => {
            if (ws.current) {
                ws.current.close();
            }
            if (reconnectTimeout.current) {
                clearTimeout(reconnectTimeout.current);
            }
        };
    }, []);

    const subscribe = (eventType, callback) => {
        if (!listeners.current[eventType]) {
            listeners.current[eventType] = [];
        }
        listeners.current[eventType].push(callback);
        console.log(`🎧 Subscribed to ${eventType}`);

        // Return unsubscribe function
        return () => {
            if (listeners.current[eventType]) {
                listeners.current[eventType] = listeners.current[eventType].filter(
                    cb => cb !== callback
                );
                console.log(`🔕 Unsubscribed from ${eventType}`);
            }
        };
    };

    return (
        <WebSocketContext.Provider value={{ isConnected, subscribe }}>
            {children}
            {/* Connection Status Indicator */}
            {!isConnected && (
                <div className="fixed bottom-0 right-0 m-4 p-2 bg-red-500 text-white text-xs rounded shadow-lg z-50">
                    🔴 Sin conexión en tiempo real
                </div>
            )}
        </WebSocketContext.Provider>
    );
};

export const useWebSocket = () => {
    const context = useContext(WebSocketContext);
    if (!context) {
        throw new Error('useWebSocket must be used within a WebSocketProvider');
    }
    return context;
};
