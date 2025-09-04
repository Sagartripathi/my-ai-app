import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [input, setInput] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [openAnswerId, setOpenAnswerId] = useState(null); // Track which answer is open

  // Fetch history from backend
  const fetchHistory = async () => {
    try {
      const res = await axios.get(
        "Iaappchatbot-env.eba-sxm5mvaz.us-east-1.elasticbeanstalk.com /history"
      );
      setHistory(res.data);
    } catch (err) {
      console.log("Error fetching history", err);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const askAI = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setAnswer("");
    try {
      const res = await axios.post(
        "Iaappchatbot-env.eba-sxm5mvaz.us-east-1.elasticbeanstalk.com/ask",
        {
          text: input,
        }
      );
      setAnswer(res.data.answer);
      setInput("");
      fetchHistory(); // Refresh history
    } catch (err) {
      setAnswer("❌ Error connecting to AI backend");
      console.log(err);
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
          placeholder="Ask me anything..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />

        <button onClick={askAI} disabled={loading} className="btn">
          {loading ? "Thinking..." : "Ask AI"}
        </button>

        {answer && <div className="answer-box">{answer}</div>}

        <h2 className="history-title">🕘 History</h2>
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
                <td>{item.prompt}</td>
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
      </div>
    </div>
  );
}

export default App;
