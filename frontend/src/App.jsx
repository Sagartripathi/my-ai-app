import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [input, setInput] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [openAnswerId, setOpenAnswerId] = useState(null);
  const [error, setError] = useState("");

  // Fetch history from backend
  const fetchHistory = async () => {
    try {
      setError("");
      const res = await axios.get(
        "http://aichatbot-env.eba-erm5a6hf.us-east-1.elasticbeanstalk.com/history"
      );
      setHistory(res.data);
    } catch (err) {
      console.log("Error fetching history", err);
      setError("Failed to load chat history");
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const askAI = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setAnswer("");
    setError("");
    try {
      const res = await axios.post("http://127.0.0.1:8000/ask", {
        text: input,
      });
      setAnswer(res.data.answer);
      setInput("");
      fetchHistory(); // Refresh history
    } catch (err) {
      console.log(err);
      if (err.response?.data?.error) {
        setError(`❌ ${err.response.data.error}`);
      } else if (
        err.code === "NETWORK_ERROR" ||
        err.message.includes("Network Error")
      ) {
        setError(
          "❌ Cannot connect to AI backend. Please check your internet connection."
        );
      } else {
        setError("❌ Error connecting to AI backend. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const toggleAnswer = (id) => {
    setOpenAnswerId(openAnswerId === id ? null : id);
  };

  return (
    <div className="app">
      <div className="card">
        <h1 className="title">🤖 AI Assistant</h1>

        <textarea
          className="input-box"
          placeholder="Ask me anything... (Press Ctrl+Enter to send)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.ctrlKey && e.key === "Enter") {
              askAI();
            }
          }}
        />

        <button onClick={askAI} disabled={loading} className="btn">
          {loading ? "Thinking..." : "Ask AI"}
        </button>

        {answer && <div className="answer-box">{answer}</div>}

        {error && <div className="error-box">{error}</div>}

        <h2 className="history-title">🕘 Chat History</h2>
        {history.length === 0 ? (
          <div className="no-history">
            No chat history yet. Start a conversation!
          </div>
        ) : (
          <table className="history-table">
            <thead>
              <tr>
                <th>Question</th>
                <th>Answer</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.id}>
                  <td className="question-cell">{item.prompt}</td>
                  <td>
                    <button
                      onClick={() => toggleAnswer(item.id)}
                      className="show-answer-btn"
                    >
                      {openAnswerId === item.id ? "Hide" : "Show"} Answer
                    </button>
                    {openAnswerId === item.id && (
                      <div className="dropdown-answer">{item.response}</div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default App;
