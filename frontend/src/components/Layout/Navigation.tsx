/**
 * Navigation - 상단 네비게이션 바
 *
 * Phase 27: Frontend Router Integration
 * Date: 2025-12-23
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navigation.css';

const Navigation: React.FC = () => {
    const location = useLocation();

    const isActive = (path: string) => {
        return location.pathname === path;
    };

    return (
        <nav className="navigation">
            <div className="nav-container">
                {/* Logo */}
                <div className="nav-logo">
                    <Link to="/">
                        <span className="logo-icon">🤖</span>
                        <span className="logo-text">AI Trading System</span>
                    </Link>
                </div>

                {/* Navigation Links */}
                <div className="nav-links">
                    <Link
                        to="/war-room"
                        className={`nav-link ${isActive('/war-room') ? 'active' : ''}`}
                    >
                        <span className="nav-icon">🏛️</span>
                        <span className="nav-label">War Room</span>
                    </Link>

                    <Link
                        to="/portfolio"
                        className={`nav-link ${isActive('/portfolio') ? 'active' : ''}`}
                    >
                        <span className="nav-icon">💼</span>
                        <span className="nav-label">Portfolio</span>
                    </Link>

                    <Link
                        to="/orders"
                        className={`nav-link ${isActive('/orders') ? 'active' : ''}`}
                    >
                        <span className="nav-icon">📋</span>
                        <span className="nav-label">Orders</span>
                    </Link>

                    <Link
                        to="/performance"
                        className={`nav-link ${isActive('/performance') ? 'active' : ''}`}
                    >
                        <span className="nav-icon">📊</span>
                        <span className="nav-label">Performance</span>
                    </Link>
                </div>

                {/* Status Indicator */}
                <div className="nav-status">
                    <div className="status-indicator">
                        <div className="status-dot active"></div>
                        <span className="status-text">Live</span>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navigation;
