import { NavLink, Route, Routes } from "react-router-dom";
import { AssistantPage } from "./pages/AssistantPage";
import { CallDetailPage } from "./pages/CallDetailPage";
import { CallsPage } from "./pages/CallsPage";
import { ContactsPage } from "./pages/ContactsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { PlaceholderPage } from "./pages/PlaceholderPage";

export function App() {
  return (
    <div className="shell">
      <aside className="nav">
        <p className="brand">Sheeba</p>
        <p className="brand-sub">Uday’s AI receptionist</p>
        <ul>
          <li>
            <NavLink to="/" end>
              Dashboard
            </NavLink>
          </li>
          <li>
            <NavLink to="/calls">Calls</NavLink>
          </li>
          <li>
            <NavLink to="/contacts">Contacts</NavLink>
          </li>
          <li>
            <NavLink to="/callbacks">Callbacks</NavLink>
          </li>
          <li>
            <NavLink to="/appointments">Appointments</NavLink>
          </li>
          <li>
            <NavLink to="/knowledge">Knowledge</NavLink>
          </li>
          <li>
            <NavLink to="/assistant">Assistant</NavLink>
          </li>
          <li>
            <NavLink to="/notifications">Notifications</NavLink>
          </li>
          <li>
            <NavLink to="/analytics">Analytics</NavLink>
          </li>
        </ul>
      </aside>
      <main className="main">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/calls" element={<CallsPage />} />
          <Route path="/calls/:id" element={<CallDetailPage />} />
          <Route path="/contacts" element={<ContactsPage />} />
          <Route path="/assistant" element={<AssistantPage />} />
          <Route path="/callbacks" element={<PlaceholderPage title="Callback Requests" />} />
          <Route path="/appointments" element={<PlaceholderPage title="Appointments" />} />
          <Route path="/knowledge" element={<PlaceholderPage title="Knowledge Base" />} />
          <Route path="/notifications" element={<PlaceholderPage title="Notification Settings" />} />
          <Route path="/analytics" element={<PlaceholderPage title="Analytics" />} />
        </Routes>
      </main>
    </div>
  );
}
