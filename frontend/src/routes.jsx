import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "./App";
import Login from "./components/Login";

function RootError() {
  return (
    <div style={{ padding: 24, fontFamily: "sans-serif" }}>
      <h2>Something went wrong</h2>
      <p>Please refresh the page and try again.</p>
    </div>
  );
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <Login />,
    errorElement: <RootError />,
  },
  {
    path: "/app",
    element: <App />,
    errorElement: <RootError />,
  },
  {
    path: "/oauth2callback",
    element: <Login />,
    errorElement: <RootError />,
  },
  {
    path: "*",
    element: <Login />,
    errorElement: <RootError />,
  },
]);

export default function AppRoutes() {
  return <RouterProvider router={router} />;
}
