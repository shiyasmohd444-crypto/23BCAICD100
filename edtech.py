import json
import secrets
import time
import webbrowser
from datetime import datetime
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = 5001

users = {
    "admin": "admin123",
    "student": "learn2025",
    "shiyas": "2026"
}

responses = [
    (["help"], "You can ask:\n- status\n- course\n- exam\n- attendance\n- history\n- clear\n- exit"),
    (["status", "system"], "All EdTech systems are running normally."),
    (["course", "subject"], "Courses: AI, Data Science, Cloud Computing."),
    (["exam", "test"], "Exams start from 10th April."),
    (["attendance", "present"], "Your attendance is 85%."),
    (["hi", "hello"], "Hello! How can I assist you?")
]

sessions = {}

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edtech Assistant </title>
    <style>
        :root {
            --bg-top: #fff4d6;
            --bg-bottom: #d8ecff;
            --panel: rgba(255, 255, 255, 0.9);
            --text-main: #17385c;
            --text-soft: #5f7390;
            --accent: #0f8c95;
            --accent-dark: #0a6770;
            --bot-bg: #edf8f9;
            --user-bg: #17385c;
            --shadow: 0 24px 60px rgba(23, 56, 92, 0.18);
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, var(--bg-top), var(--bg-bottom));
            color: var(--text-main);
        }

        .shell {
            min-height: 100vh;
            display: grid;
            place-items: center;
            padding: 24px;
        }

        .hero-card {
            width: min(920px, 100%);
            background: var(--panel);
            border-radius: 24px;
            box-shadow: var(--shadow);
            padding: 32px;
        }

        .eyebrow {
            margin: 0 0 10px;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.75rem;
            color: var(--accent);
            font-weight: bold;
        }

        h1 {
            margin: 0;
            font-size: 2.5rem;
        }

        .hero-copy {
            max-width: 620px;
            line-height: 1.6;
            color: var(--text-soft);
            margin: 16px 0 24px;
        }

        .login-panel,
        .chat-section {
            background: #ffffff;
            border-radius: 18px;
            padding: 24px;
        }

        .login-form {
            display: grid;
            gap: 14px;
            margin-top: 16px;
        }

        label {
            display: grid;
            gap: 6px;
            font-weight: bold;
        }

        input {
            width: 100%;
            border: 1px solid #cfd8dc;
            border-radius: 12px;
            padding: 12px 14px;
            font-size: 16px;
            outline: none;
        }

        input:focus {
            border-color: var(--accent);
        }

        .primary-btn,
        .ghost-btn,
        .chip {
            border: none;
            cursor: pointer;
            font-size: 15px;
        }

        .primary-btn {
            background: linear-gradient(135deg, var(--accent), var(--accent-dark));
            color: white;
            border-radius: 12px;
            padding: 12px 16px;
            font-weight: bold;
        }

        .ghost-btn {
            background: #e8eef2;
            color: var(--text-main);
            border-radius: 12px;
            padding: 10px 16px;
            font-weight: bold;
        }

        .chat-topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            margin-bottom: 18px;
        }

        .chat-label {
            margin: 0 0 4px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.75rem;
            color: var(--text-soft);
        }

        .chat-display {
            height: 340px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
            padding: 18px;
            border-radius: 16px;
            background: #f7fbfc;
            border: 1px solid #dfe8ec;
        }

        .message {
            max-width: 85%;
            padding: 12px 14px;
            border-radius: 14px;
            line-height: 1.5;
            white-space: pre-wrap;
            word-break: break-word;
        }

        .bot-message {
            align-self: flex-start;
            background: var(--bot-bg);
            color: var(--text-main);
        }

        .user-message {
            align-self: flex-end;
            background: var(--user-bg);
            color: white;
        }

        .quick-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 18px 0;
        }

        .chip {
            background: #ffe4cf;
            color: #b45a1d;
            padding: 10px 14px;
            border-radius: 999px;
            font-weight: bold;
        }

        .chat-input-area {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 12px;
        }

        .send-btn { min-width: 100px; }
        .hidden { display: none; }

        .status-text {
            min-height: 1.4em;
            margin: 0;
            color: #c0392b;
        }

        @media (max-width: 720px) {
            .hero-card { padding: 22px; }
            .chat-input-area { grid-template-columns: 1fr; }
            .chat-display { height: 300px; }
            .message { max-width: 100%; }
        }
    </style>
</head>
<body>
    <main class="shell">
        <section class="hero-card">
            <p class="eyebrow">Smart campus support</p>
            <h1>EdutechAssistant</h1>
            <p class="hero-copy">Log in and chat with your assistant for course updates, exam details, attendance info, and saved chat history.</p>

            <div id="login-panel" class="login-panel">
                <h2>Login Required</h2>
                <p>Use one of the registered accounts to start chatting.</p>

                <form id="login-form" class="login-form">
                    <label>
                        <span>Username</span>
                        <input type="text" id="username" placeholder="Enter username" autocomplete="username" required>
                    </label>

                    <label>
                        <span>Password</span>
                        <input type="password" id="password" placeholder="Enter password" autocomplete="current-password" required>
                    </label>

                    <button type="submit" class="primary-btn">Login</button>
                    <p id="login-message" class="status-text"></p>
                </form>
            </div>

            <div id="chat-section" class="chat-section hidden">
                <div class="chat-topbar">
                    <div>
                        <p class="chat-label">Active session</p>
                        <h2 id="welcome-text">Welcome</h2>
                    </div>
                    <button id="logout-btn" class="ghost-btn" type="button">Exit</button>
                </div>

                <div id="chat-display" class="chat-display">
                    <div class="message bot-message">Type <strong>help</strong> to see available commands.</div>
                </div>

                <div class="quick-actions">
                    <button type="button" class="chip" data-message="help">help</button>
                    <button type="button" class="chip" data-message="status">status</button>
                    <button type="button" class="chip" data-message="course">course</button>
                    <button type="button" class="chip" data-message="exam">exam</button>
                    <button type="button" class="chip" data-message="attendance">attendance</button>
                    <button type="button" class="chip" data-message="history">history</button>
                    <button type="button" class="chip" data-message="clear">clear</button>
                </div>

                <div class="chat-input-area">
                    <input type="text" id="chat-input" placeholder="Ask something..." autocomplete="off">
                    <button id="send-btn" class="primary-btn send-btn" type="button">Send</button>
                </div>
            </div>
        </section>
    </main>

    <script>
        document.addEventListener("DOMContentLoaded", function () {
            const loginForm = document.getElementById("login-form");
            const loginPanel = document.getElementById("login-panel");
            const usernameInput = document.getElementById("username");
            const passwordInput = document.getElementById("password");
            const loginMessage = document.getElementById("login-message");
            const chatSection = document.getElementById("chat-section");
            const welcomeText = document.getElementById("welcome-text");
            const chatDisplay = document.getElementById("chat-display");
            const chatInput = document.getElementById("chat-input");
            const sendBtn = document.getElementById("send-btn");
            const logoutBtn = document.getElementById("logout-btn");
            const quickActions = document.querySelectorAll(".chip");
            const loginButton = loginForm.querySelector("button[type='submit']");

            function appendMessage(sender, text) {
                const message = document.createElement("div");
                message.className = "message " + sender + "-message";
                message.innerHTML = text.replace(/\\n/g, "<br>");
                chatDisplay.appendChild(message);
                chatDisplay.scrollTop = chatDisplay.scrollHeight;
            }

            function resetChat() {
                chatDisplay.innerHTML = '<div class="message bot-message">Type <strong>help</strong> to see available commands.</div>';
            }

            function restoreHistory(history) {
                resetChat();
                history.forEach(function (entry) {
                    if (entry.indexOf("You:") === 0) {
                        appendMessage("user", entry.replace(/^You:\\s*/, ""));
                    } else {
                        appendMessage("bot", entry.replace(/^Bot\\s*\\[[^\\]]+\\]:\\s*/, ""));
                    }
                });
            }

            function setLoggedInState(user, history) {
                loginPanel.classList.add("hidden");
                chatSection.classList.remove("hidden");
                welcomeText.textContent = "Welcome " + user + "!";
                restoreHistory(history || []);
                usernameInput.disabled = false;
                passwordInput.disabled = false;
                loginButton.disabled = false;
                chatInput.focus();
            }

            function setLoggedOutState() {
                loginPanel.classList.remove("hidden");
                chatSection.classList.add("hidden");
                loginMessage.textContent = "";
                passwordInput.value = "";
                resetChat();
            }

            function setLockedState(message) {
                setLoggedOutState();
                usernameInput.disabled = true;
                passwordInput.disabled = true;
                loginButton.disabled = true;
                loginMessage.textContent = message;
            }

            async function sendMessage(customMessage) {
                const text = customMessage || chatInput.value.trim();
                if (!text) return;

                appendMessage("user", text);
                chatInput.value = "";

                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: text })
                });

                const data = await response.json();

                if (data.requiresLogin || data.ended) {
                    appendMessage("bot", data.response);
                    setLoggedOutState();
                    return;
                }

                if (data.showHistory) {
                    if (!data.history.length) {
                        appendMessage("bot", "No chat history yet.");
                    } else {
                        appendMessage("bot", data.history.join("\\n"));
                    }
                    return;
                }

                if (data.historyCleared) {
                    resetChat();
                }

                appendMessage("bot", data.timestamp ? "[" + data.timestamp + "] " + data.response : data.response);
            }

            loginForm.addEventListener("submit", async function (event) {
                event.preventDefault();

                const response = await fetch("/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        username: usernameInput.value.trim(),
                        password: passwordInput.value.trim()
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    if (data.locked) {
                        setLockedState(data.message);
                    } else {
                        loginMessage.textContent = data.message;
                    }
                    return;
                }

                loginMessage.textContent = "";
                passwordInput.value = "";
                setLoggedInState(data.user, []);
                appendMessage("bot", data.message);
            });

            sendBtn.addEventListener("click", function () {
                sendMessage();
            });

            chatInput.addEventListener("keydown", function (event) {
                if (event.key === "Enter") {
                    sendMessage();
                }
            });

            logoutBtn.addEventListener("click", function () {
                sendMessage("exit");
            });

            quickActions.forEach(function (button) {
                button.addEventListener("click", function () {
                    sendMessage(button.getAttribute("data-message"));
                });
            });

            fetch("/session")
                .then(function (response) { return response.json(); })
                .then(function (data) {
                    if (data.loggedIn) {
                        setLoggedInState(data.user, data.history);
                    } else if (data.locked) {
                        setLockedState("Too many attempts. Exiting...");
                    } else {
                        setLoggedOutState();
                    }
                })
                .catch(function () {
                    setLoggedOutState();
                });
        });
    </script>
</body>
</html>
"""


def get_session(handler):
    sid = None
    cookie_header = handler.headers.get("Cookie")
    if cookie_header:
        jar = cookies.SimpleCookie()
        jar.load(cookie_header)
        if "sid" in jar:
            sid = jar["sid"].value

    if not sid or sid not in sessions:
        sid = secrets.token_hex(16)
        sessions[sid] = {
            "user": None,
            "login_attempts": 0,
            "history": []
        }
        handler.new_sid = sid

    return sid, sessions[sid]


class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="text/html; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        if hasattr(self, "new_sid"):
            self.send_header("Set-Cookie", f"sid={self.new_sid}; Path=/; HttpOnly")
        self.end_headers()

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def _send_json(self, data, status=200):
        self._set_headers(status, "application/json; charset=utf-8")
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        sid, state = get_session(self)

        if self.path == "/":
            self._set_headers(200, "text/html; charset=utf-8")
            self.wfile.write(HTML.encode("utf-8"))
            return

        if self.path == "/session":
            self._send_json({
                "loggedIn": bool(state["user"]),
                "user": state["user"],
                "locked": state["login_attempts"] >= 3,
                "history": state["history"] if state["user"] else []
            })
            return

        self._set_headers(404, "text/plain; charset=utf-8")
        self.wfile.write(b"Not Found")

    def do_POST(self):
        sid, state = get_session(self)

        if self.path == "/login":
            data = self._read_json()
            username = (data.get("username") or "").strip()
            password = (data.get("password") or "").strip()

            if state["login_attempts"] >= 3:
                self._send_json({
                    "success": False,
                    "locked": True,
                    "message": "Too many attempts. Exiting..."
                }, 403)
                return

            if username in users and users[username] == password:
                state["user"] = username
                state["login_attempts"] = 0
                state["history"] = []
                self._send_json({
                    "success": True,
                    "message": f"Welcome {username}!",
                    "user": username
                })
                return

            state["login_attempts"] += 1

            if state["login_attempts"] >= 3:
                self._send_json({
                    "success": False,
                    "locked": True,
                    "message": "Too many attempts. Exiting..."
                }, 403)
                return

            self._send_json({
                "success": False,
                "message": "Invalid credentials."
            }, 401)
            return

        if self.path == "/chat":
            if not state["user"]:
                self._send_json({
                    "response": "Login required.",
                    "requiresLogin": True
                }, 401)
                return

            data = self._read_json()
            user_input = (data.get("message") or "").strip()

            if not user_input:
                self._send_json({"response": "Please enter a message."}, 400)
                return

            lowered = user_input.lower()
            now = datetime.now().strftime("%H:%M:%S")

            if lowered == "clear":
                state["history"] = []
                self._send_json({
                    "response": "Chat history cleared.",
                    "timestamp": now,
                    "historyCleared": True
                })
                return

            if lowered == "history":
                self._send_json({
                    "response": "History loaded.",
                    "timestamp": now,
                    "history": state["history"],
                    "showHistory": True
                })
                return

            if lowered == "exit":
                state["user"] = None
                state["history"] = []
                self._send_json({
                    "response": "Goodbye",
                    "timestamp": now,
                    "ended": True
                })
                return

            reply = "Sorry, I didn't understand that."
            for keys, response in responses:
                if any(key in lowered for key in keys):
                    reply = response
                    break

            time.sleep(0.5)
            state["history"].append(f"You: {user_input}")
            state["history"].append(f"Bot [{now}]: {reply}")

            self._send_json({
                "response": reply,
                "timestamp": now
            })
            return

        self._set_headers(404, "text/plain; charset=utf-8")
        self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    webbrowser.open(f"http://{HOST}:{PORT}")
    print(f"Server running at http://{HOST}:{PORT}")
    server.serve_forever()
