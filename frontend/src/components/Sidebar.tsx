import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, BarChart3, Settings } from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
  return (
    <aside className="sidebar glass">
      <div className="sidebar-brand">
        <div className="brand-logo" />
        <h1 className="text-xl font-semibold text-gradient">Apollo OS</h1>
      </div>
      
      <nav className="sidebar-nav">
        <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <LayoutDashboard size={20} />
          <span>Overview</span>
        </NavLink>
        <NavLink to="/leads" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Users size={20} />
          <span>Leads Directory</span>
        </NavLink>
        <a href="#" className="nav-item">
          <BarChart3 size={20} />
          <span>Analytics</span>
        </a>
        <a href="#" className="nav-item">
          <Settings size={20} />
          <span>Settings</span>
        </a>
      </nav>
      
      <div className="sidebar-footer">
        <div className="user-profile card">
          <div className="avatar" />
          <div className="user-info">
            <span className="user-name">Sales Team</span>
            <span className="user-role">Administrator</span>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
