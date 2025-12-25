/**
 * Layout.tsx - 전체 애플리케이션 레이아웃
 * 
 * 📊 Data Sources:
 *   - Props: children (React.ReactNode) - 렌더링할 페이지 컴포넌트
 *   - State: isMobileMenuOpen - 모바일 메뉴 열림/닫힘 상태
 * 
 * 🔗 Dependencies:
 *   - react: useState hook
 *   - ./Header: 헤더 컴포넌트
 *   - ./Sidebar: 사이드바 컴포넌트
 * 
 * 📤 Components Used:
 *   - Header: 상단 헤더 (메뉴 버튼 포함)
 *   - Sidebar: 좌측 네비게이션 (모바일 반응형)
 * 
 * 🔄 Used By:
 *   - App.tsx: 모든 페이지를 감싸는 최상위 레이아웃
 *   - 모든 페이지 컴포넌트 (Dashboard, Portfolio, etc.)
 * 
 * 📝 Notes:
 *   - Tailwind CSS 사용 (flex layout)
 *   - 모바일 반응형: 사이드바 on/off 토글
 *   - 전체 화면 높이 (h-screen) 고정
 */

import React, { useState } from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuClick={() => setIsMobileMenuOpen(true)} />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
};
