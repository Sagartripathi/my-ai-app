import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [input, setInput] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const askAI = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setAnswer("");
    try {
      const res = await axios.post("http://127.0.0.1:8000/ask", {
        text: input,
      });
      setAnswer(res.data.answer);
    } catch (err) {
      setAnswer("❌ Error connecting to AI backend");
      console.log(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="card">
        <h1 className="title">🤖 AI Assistant</h1>

        <textarea
          className="input-box"
          placeholder="Ask me anything..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />

        <button onClick={askAI} disabled={loading} className="btn">
          {loading ? "Thinking..." : "Ask AI"}
        </button>

        {answer && <div className="answer-box">{answer}</div>}
      </div>
    </div>
  );
}

export default App;
