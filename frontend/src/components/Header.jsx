import { IconSearch } from "./Icons";

export default function Header({ title, subtitle, search, onSearchChange, user }) {
  const displayName = user?.name || user?.email || "User";
  const initial = displayName?.trim()?.charAt(0)?.toUpperCase() || "U";

  return (
    <header className="top-header">
      <div className="header-left">
        <div>
          <h1 className="header-title">{title}</h1>
          {subtitle && <div className="header-subtitle">{subtitle}</div>}
        </div>
      </div>

      <div className="header-right">
        {/* <div className="header-search">
          <IconSearch />
          <input
            type="text"
            placeholder="Search documents..."
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>  */}
        <div className="avatar-chip">
          <div className="avatar">{initial}</div>
          <span>{displayName}</span>
        </div>
      </div>
    </header>
  );
}
