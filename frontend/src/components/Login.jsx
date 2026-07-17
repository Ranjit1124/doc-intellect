import { useEffect, useState } from "react";
import { googleCallback, login, signup } from "../api/api";

export default function Login({ onAuth }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [isSignup, setIsSignup] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    if (!code) return;

    const finishGoogleLogin = async () => {
      try {
        setLoading(true);
        const res = await googleCallback(code);
        if (res?.access_token) {
          localStorage.setItem("access_token", res.access_token);
          onAuth(res.user);
          window.history.replaceState({}, "", "/");
        } else {
          alert(res?.detail || "Google sign-in failed");
        }
      } catch (err) {
        console.error(err);
        alert("Google sign-in failed");
      } finally {
        setLoading(false);
      }
    };

    finishGoogleLogin();
  }, [onAuth]);

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
      <div className="login-card">
        <div className="login-brand">
          <div className="login-brand-icon">DI</div>
          <div>
            <h1>Doc Intellect</h1>
            <p>Secure access to your workspace</p>
          </div>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <h2>{isSignup ? "Create your account" : "Welcome back"}</h2>
          {isSignup && (
            <input placeholder="Full name" value={name} onChange={(e) => setName(e.target.value)} />
          )}
          <input placeholder="Email address" value={email} onChange={(e) => setEmail(e.target.value)} />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Please wait..." : isSignup ? "Create account" : "Sign in"}
          </button>
          <button className="btn btn-ghost" type="button" onClick={() => setIsSignup(!isSignup)}>
            {isSignup ? "Already have an account? Sign in" : "New here? Create an account"}
          </button>
          <div className="login-divider">or</div>
          <button className="btn btn-accent" type="button" onClick={handleGoogle} disabled={loading}>
            Continue with Google
          </button>
        </form>
      </div>
    </div>
  );
}
