import { useState } from "react";
import { login, signup } from "../api/api";

export default function Login({ onAuth }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [isSignup, setIsSignup] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = isSignup ? { email, password, name } : { email, password };
      const res = isSignup ? await signup(payload) : await login(payload);
      if (res && res.access_token) {
        localStorage.setItem("access_token", res.access_token);
        onAuth(res.user);
      } else {
        alert(res.detail || "Auth failed");
      }
    } catch (err) {
      console.error(err);
      alert("Auth error");
    }
  };

  const handleGoogle = async () => {
    try {
      const r = await fetch(`/auth/google`);
      const data = await r.json();
      if (data?.auth_url) {
        window.location.href = data.auth_url;
      } else {
        alert("Google auth not configured");
      }
    } catch (err) {
      console.error(err);
      alert("Google auth error");
    }
  };

  return (
    <div className="login-screen">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>{isSignup ? "Sign up" : "Sign in"}</h2>
        {isSignup && (
          <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
        )}
        <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">{isSignup ? "Create account" : "Sign in"}</button>
        <button type="button" onClick={() => setIsSignup(!isSignup)}>
          {isSignup ? "Have an account? Sign in" : "New here? Create account"}
        </button>
        <hr />
        <button type="button" onClick={handleGoogle}>Sign in with Google</button>
      </form>
    </div>
  );
}
