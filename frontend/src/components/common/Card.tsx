/**
 * Card.tsx - 재사용 가능한 카드 컴포넌트
 * 
 * 📊 Data Sources:
 *   - Props: title, children, padding, className
 *   - No external data fetching
 * 
 * 🔗 Dependencies:
 *   - react: HTMLAttributes type extension
 *   - Tailwind CSS: 스타일링
 * 
 * 📤 Props:
 *   - title?: string - 카드 제목 (선택)
 *   - children: ReactNode - 카드 내용
 *   - padding?: boolean (default: true) - 패딩 on/off
 *   - className?: string - 추가 CSS 클래스
 *   - ...props: HTMLDivElement 속성 전달
 * 
 * 🔄 Used By (전체 애플리케이션):
 *   - pages/Dashboard.tsx
 *   - pages/Portfolio.tsx
 *   - pages/DividendDashboard.tsx
 *   - 거의 모든 페이지와 컴포넌트
 * 
 * 📝 Notes:
 *   - 가장 많이 사용되는 공통 컴포넌트
 *   - bg-white, rounded-lg, shadow-md 스타일
 *   - 제목 표시 선택적 (title prop)
 */

import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  children: React.ReactNode;
  padding?: boolean;
}

export const Card: React.FC<CardProps> = ({
  title,
  children,
  className = '',
  padding = true,
  ...props
}) => {
  return (
    <div
      className={`bg-white rounded-lg shadow-md ${padding ? 'p-6' : ''} ${className}`}
      {...props}
    >
      {title && <h3 className="text-lg font-semibold mb-4 text-gray-900">{title}</h3>}
      {children}
    </div>
  );
};
