from playwright.sync_api import sync_playwright
import websocket

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.on("request", lambda request: print(">>", request.method, request.url))
    page.on("response", lambda response: print("<<", response.status, response.url))
    page.goto("http://playwright.dev")
    print(page.title())
    browser.close()

    def on_message(ws, message):
        print("Received message:", message)

    def on_error(ws, error):
        print("Error:", error)

    def on_close(ws):
        print("Connection closed")

    def on_open(ws):
        print("Connection opened")
        # Send a message to the WebSocket server
        ws.send("Hello, server!")

    # Create a WebSocket connection
    ws = websocket.WebSocketApp("ws://your-websocket-server-url",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open

    # Start the WebSocket connection
    ws.run_forever()